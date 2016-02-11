# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines nodes and topology structure."""

from resources.libraries.python.parsers.JsonParser import JsonParser
from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.ssh import SSH
from resources.libraries.python.InterfaceSetup import InterfaceSetup
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword
from yaml import load

__all__ = ["DICT__nodes", 'Topology']


def load_topo_from_yaml():
    """Loads topology from file defined in "${TOPOLOGY_PATH}" variable

    :return: nodes from loaded topology
    """
    topo_path = BuiltIn().get_variable_value("${TOPOLOGY_PATH}")

    with open(topo_path) as work_file:
        return load(work_file.read())['nodes']


class NodeType(object):
    """Defines node types used in topology dictionaries"""
    # Device Under Test (this node has VPP running on it)
    DUT = 'DUT'
    # Traffic Generator (this node has traffic generator on it)
    TG = 'TG'

DICT__nodes = load_topo_from_yaml()


class Topology(object):
    """Topology data manipulation and extraction methods

    Defines methods used for manipulation and extraction of data from
    the used topology.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_node_by_hostname(nodes, hostname):
        """Get node from nodes of the topology by hostname.

        :param nodes: Nodes of the test topology.
        :param hostname: Host name.
        :type nodes: dict
        :type hostname: str
        :return: Node dictionary or None if not found.
        """
        for node in nodes.values():
            if node['host'] == hostname:
                return node

        return None

    @staticmethod
    def get_links(nodes):
        """Get list of links(networks) in the topology.

        :param nodes: Nodes of the test topology.
        :type nodes: dict
        :return: Links in the topology.
        :rtype: list
        """
        links = []

        for node in nodes.values():
            for interface in node['interfaces'].values():
                link = interface.get('link')
                if link is not None:
                    if link not in links:
                        links.append(link)

        return links

    @staticmethod
    def _get_interface_by_key_value(node, key, value):
        """ Return node interface name according to key and value

        :param node: :param node: the node dictionary
        :param key: key by which to select the interface.
        :param value: value that should be found using the key.
        :return:
        """

        interfaces = node['interfaces']
        retval = None
        for interface in interfaces.values():
            k_val = interface.get(key)
            if k_val is not None:
                if k_val == value:
                    retval = interface['name']
                    break
        return retval

    def get_interface_by_link_name(self, node, link_name):
        """Return interface name of link on node.

        This method returns the interface name asociated with a given link
        for a given node.
        :param link_name: name of the link that a interface is connected to.
        :param node: the node topology dictionary
        :return: interface name of the interface connected to the given link
        """

        return self._get_interface_by_key_value(node, "link", link_name)

    def get_interfaces_by_link_names(self, node, link_names):
        """Return dictionary of dicitonaries {"interfaceN", interface name}.

        This method returns the interface names asociated with given links
        for a given node.
        The resulting dictionary can be then used to with VatConfigGenerator
        to generate a VAT script with proper interface names.
        :param link_names: list of names of the link that a interface is
        connected to.
        :param node: the node topology directory
        :return: dictionary of interface names that are connected to the given
        links
        """

        retval = {}
        interface_key_tpl = "interface{}"
        interface_number = 1
        for link_name in link_names:
            interface_name = self.get_interface_by_link_name(node, link_name)
            interface_key = interface_key_tpl.format(str(interface_number))
            retval[interface_key] = interface_name
            interface_number += 1
        return retval

    def get_interface_by_sw_index(self, node, sw_index):
        """Return interface name of link on node.

        This method returns the interface name asociated with a software index
        assigned to the interface by vpp for a given node.
        :param sw_index: sw_index of the link that a interface is connected to.
        :param node: the node topology dictionary
        :return: interface name of the interface connected to the given link
        """

        return self._get_interface_by_key_value(node, "vpp_sw_index", sw_index)

    @staticmethod
    def convert_mac_to_number_list(mac_address):
        """Convert mac address string to list of decimal numbers.

        Converts a : separated mac address to decimal number list as used
        in json interface dump.
        :param mac_address: string mac address
        :return: list representation of mac address
        """

        list_mac = []
        for num in mac_address.split(":"):
            list_mac.append(int(num, 16))
        return list_mac

    def _extract_vpp_interface_by_mac(self, interfaces_list, mac_address):
        """Returns interface dictionary from interface_list by mac address.

        Extracts interface dictionary from all of the interfaces in interfaces
        list parsed from json according to mac_address of the interface
        :param interfaces_list: dictionary of all interfaces parsed from json
        :param mac_address: string mac address of interface we are looking for
        :return: interface dictionary from json
        """

        interface_dict = {}
        list_mac_address = self.convert_mac_to_number_list(mac_address)
        logger.trace(list_mac_address.__str__())
        for interface in interfaces_list:
            # TODO: create vat json integrity checking and move there
            if "l2_address" not in interface:
                raise KeyError(
                    "key l2_address not found in interface dict."
                    "Probably input list is not parsed from correct VAT "
                    "json output.")
            if "l2_address_length" not in interface:
                raise KeyError(
                    "key l2_address_length not found in interface "
                    "dict. Probably input list is not parsed from correct "
                    "VAT json output.")
            mac_from_json = interface["l2_address"][:6]
            if mac_from_json == list_mac_address:
                if interface["l2_address_length"] != 6:
                    raise ValueError("l2_address_length value is not 6.")
                interface_dict = interface
                break
        return interface_dict

    def vpp_interface_name_from_json_by_mac(self, json_data, mac_address):
        """Return vpp interface name string from VAT interface dump json output

        Extracts the name given to an interface by VPP.
        These interface names differ from what you would see if you
        used the ipconfig or similar command.
        Required json data can be obtained by calling :
        VatExecutor.execute_script_json_out("dump_interfaces.vat", node)
        :param json_data: string json data from sw_interface_dump VAT command
        :param mac_address: string containing mac address of interface
        whose vpp name we wish to discover.
        :return: string vpp interface name
        """

        interfaces_list = JsonParser().parse_data(json_data)
        # TODO: checking if json data is parsed correctly
        interface_dict = self._extract_vpp_interface_by_mac(interfaces_list,
                                                            mac_address)
        interface_name = interface_dict["interface_name"]
        return interface_name

    def _update_node_interface_data_from_json(self, node, interface_dump_json):
        """ Update node vpp data in node__DICT from json interface dump.

        This method updates vpp interface names and sw indexexs according to
        interface mac addresses found in interface_dump_json
        :param node: node dictionary
        :param interface_dump_json: json output from dump_interface_list VAT
        command
        """

        interface_list = JsonParser().parse_data(interface_dump_json)
        for ifc in node['interfaces'].values():
            if 'link' not in ifc:
                continue
            if_mac = ifc['mac_address']
            interface_dict = self._extract_vpp_interface_by_mac(interface_list,
                                                                if_mac)
            ifc['name'] = interface_dict["interface_name"]
            ifc['vpp_sw_index'] = interface_dict["sw_if_index"]

    def update_vpp_interface_data_on_node(self, node):
        """Update vpp generated interface data for a given node in DICT__nodes

        Updates interface names, software index numbers and any other details
        generated specifically by vpp that are unknown before testcase run.
        :param node: Node selected from DICT__nodes
        """

        vat_executor = VatExecutor()
        vat_executor.execute_script_json_out("dump_interfaces.vat", node)
        interface_dump_json = vat_executor.get_script_stdout()
        self._update_node_interface_data_from_json(node,
                                                   interface_dump_json)

    @staticmethod
    def update_tg_interface_data_on_node(node):
        """Update interface name for TG/linux node in DICT__nodes

        :param node: Node selected from DICT__nodes.
        :type node: dict

        .. note::
            # for dev in `ls /sys/class/net/`;
            > do echo "\"`cat /sys/class/net/$dev/address`\": \"$dev\""; done
            "52:54:00:9f:82:63": "eth0"
            "52:54:00:77:ae:a9": "eth1"
            "52:54:00:e1:8a:0f": "eth2"
            "00:00:00:00:00:00": "lo"

        .. todo:: parse lshw -json instead
        """
        # First setup interface driver specified in yaml file
        InterfaceSetup.tg_set_interfaces_default_driver(node)

        # Get interface names
        ssh = SSH()
        ssh.connect(node)

        cmd = 'for dev in `ls /sys/class/net/`; do echo "\\"`cat ' \
              '/sys/class/net/$dev/address`\\": \\"$dev\\""; done;'

        (ret_code, stdout, _) = ssh.exec_command(cmd)
        if int(ret_code) != 0:
            raise Exception('Get interface name and MAC failed')
        tmp = "{" + stdout.rstrip().replace('\n', ',') + "}"
        interfaces = JsonParser().parse_data(tmp)
        for if_k, if_v in node['interfaces'].items():
            if if_k == 'mgmt':
                continue
            name = interfaces.get(if_v['mac_address'])
            if name is None:
                continue
            if_v['name'] = name

        # Set udev rules for interfaces
        InterfaceSetup.tg_set_interfaces_udev_rules(node)

    def update_all_interface_data_on_all_nodes(self, nodes):
        """ Update interface names on all nodes in DICT__nodes

        :param nodes: Nodes in the topology.
        :type nodes: dict

        This method updates the topology dictionary by querying interface lists
        of all nodes mentioned in the topology dictionary.
        It does this by dumping interface list to json output from all devices
        using vpe_api_test, and pairing known information from topology
        (mac address/pci address of interface) to state from VPP.
        For TG/linux nodes add interface name only.
        """

        for node_data in nodes.values():
            if node_data['type'] == NodeType.DUT:
                self.update_vpp_interface_data_on_node(node_data)
            elif node_data['type'] == NodeType.TG:
                self.update_tg_interface_data_on_node(node_data)

    @staticmethod
    def get_interface_sw_index(node, interface):
        """Get VPP sw_index for the interface.

        :param node: Node to get interface sw_index on.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        :return: Return sw_index or None if not found.
        """
        for port in node['interfaces'].values():
            port_name = port.get('name')
            if port_name is None:
                continue
            if port_name == interface:
                return port.get('vpp_sw_index')

        return None

    @staticmethod
    def get_interface_mac(node, interface):
        """Get MAC address for the interface.

        :param node: Node to get interface sw_index on.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        :return: Return MAC or None if not found.
        """
        for port in node['interfaces'].values():
            port_name = port.get('name')
            if port_name is None:
                continue
            if port_name == interface:
                return port.get('mac_address')

        return None

    @staticmethod
    def get_adjacent_node_and_interface(nodes_info, node, interface_name):
        """Get node and interface adjacent to specified interface
        on local network.

        :param nodes_info: Dictionary containing information on all nodes
        in topology.
        :param node: Node that contains specified interface.
        :param interface_name: Interface name.
        :type nodes_info: dict
        :type node: dict
        :type interface_name: str
        :return: Return (node, interface info) tuple or None if not found.
        :rtype: (dict, dict)
        """
        link_name = None
        # get link name where the interface belongs to
        for port_name, port_data in node['interfaces'].iteritems():
            if port_name == 'mgmt':
                continue
            if port_data['name'] == interface_name:
                link_name = port_data['link']
                break

        if link_name is None:
            return None

        # find link
        for node_data in nodes_info.values():
            # skip self
            if node_data['host'] == node['host']:
                continue
            for interface, interface_data \
                    in node_data['interfaces'].iteritems():
                if 'link' not in interface_data:
                    continue
                if interface_data['link'] == link_name:
                    return node_data, node_data['interfaces'][interface]

    @staticmethod
    def get_interface_pci_addr(node, interface):
        """Get interface PCI address.

        :param node: Node to get interface PCI address on.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        :return: Return PCI address or None if not found.
        """
        for port in node['interfaces'].values():
            if interface == port.get('name'):
                return port.get('pci_address')
        return None

    @staticmethod
    def get_interface_driver(node, interface):
        """Get interface driver.

        :param node: Node to get interface driver on.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        :return: Return interface driver or None if not found.
        """
        for port in node['interfaces'].values():
            if interface == port.get('name'):
                return port.get('driver')
        return None

    @staticmethod
    def get_node_link_mac(node, link_name):
        """Return interface mac address by link name

        :param node: Node to get interface sw_index on
        :param link_name: link name
        :type node: dict
        :type link_name: string
        :return: mac address string
        """
        for port in node['interfaces'].values():
            if port.get('link') == link_name:
                return port.get('mac_address')
        return None

    @staticmethod
    def _get_node_active_link_names(node):
        """Returns list of link names that are other than mgmt links

        :param node: node topology dictionary
        :return: list of strings that represent link names occupied by the node
        """
        interfaces = node['interfaces']
        link_names = []
        for interface in interfaces.values():
            if 'link' in interface:
                link_names.append(interface['link'])
        if len(link_names) == 0:
            link_names = None
        return link_names

    @keyword('Get active links connecting "${node1}" and "${node2}"')
    def get_active_connecting_links(self, node1, node2):
        """Returns list of link names that connect together node1 and node2

        :param node1: node topology dictionary
        :param node2: node topology dictionary
        :return: list of strings that represent connecting link names
        """

        logger.trace("node1: {}".format(str(node1)))
        logger.trace("node2: {}".format(str(node2)))
        node1_links = self._get_node_active_link_names(node1)
        node2_links = self._get_node_active_link_names(node2)
        connecting_links = list(set(node1_links).intersection(node2_links))

        return connecting_links

    @keyword('Get first active connecting link between node "${node1}" and '
             '"${node2}"')
    def get_first_active_connecting_link(self, node1, node2):
        """

        :param node1: Connected node
        :type node1: dict
        :param node2: Connected node
        :type node2: dict
        :return: name of link connecting the two nodes together
        :raises: RuntimeError
        """

        connecting_links = self.get_active_connecting_links(node1, node2)
        if len(connecting_links) == 0:
            raise RuntimeError("No links connecting the nodes were found")
        else:
            return connecting_links[0]

    @keyword('Get egress interfaces on "${node1}" for link with "${node2}"')
    def get_egress_interfaces_for_nodes(self, node1, node2):
        """Get egress interfaces on node1 for link with node2.

        :param node1: First node, node to get egress interface on.
        :param node2: Second node.
        :type node1: dict
        :type node2: dict
        :return: Engress interfaces.
        :rtype: list
        """
        interfaces = []
        links = self.get_active_connecting_links(node1, node2)
        if len(links) == 0:
            raise RuntimeError('No link between nodes')
        for interface in node1['interfaces'].values():
            link = interface.get('link')
            if link is None:
                continue
            if link in links:
                continue
            name = interface.get('name')
            if name is None:
                continue
            interfaces.append(name)
        return interfaces

    @keyword('Get first egress interface on "${node1}" for link with '
             '"${node2}"')
    def get_first_egress_interface_for_nodes(self, node1, node2):
        """Get first egress interface on node1 for link with node2.

        :param node1: First node, node to get egress interface on.
        :param node2: Second node.
        :type node1: dict
        :type node2: dict
        :return: Engress interface.
        :rtype: str
        """
        interfaces = self.get_egress_interfaces_for_nodes(node1, node2)
        if not interfaces:
            raise RuntimeError('No engress interface for nodes')
        return interfaces[0]

    @keyword('Get link data useful in circular topology test from tg "${tgen}"'
             ' dut1 "${dut1}" dut2 "${dut2}"')
    def get_links_dict_from_nodes(self, tgen, dut1, dut2):
        """Returns link combinations used in tests in circular topology.

        For the time being it returns links from the Node path:
        TG->DUT1->DUT2->TG
        :param tg: traffic generator node data
        :param dut1: DUT1 node data
        :param dut2: DUT2 node data
        :type tg: dict
        :type dut1: dict
        :type dut2: dict
        :return: dictionary of possible link combinations
        the naming convention until changed to something more general is
        implemented is this:
        DUT1_DUT2_LINK: link name between DUT! and DUT2
        DUT1_TG_LINK: link name between DUT1 and TG
        DUT2_TG_LINK: link name between DUT2 and TG
        TG_TRAFFIC_LINKS: list of link names that generated traffic is sent
        to and from
        DUT1_BD_LINKS: list of link names that will be connected by the bridge
        domain on DUT1
        DUT2_BD_LINKS: list of link names that will be connected by the bridge
        domain on DUT2
        """
        # TODO: replace with generic function.
        dut1_dut2_link = self.get_first_active_connecting_link(dut1, dut2)
        dut1_tg_link = self.get_first_active_connecting_link(dut1, tgen)
        dut2_tg_link = self.get_first_active_connecting_link(dut2, tgen)
        tg_traffic_links = [dut1_tg_link, dut2_tg_link]
        dut1_bd_links = [dut1_dut2_link, dut1_tg_link]
        dut2_bd_links = [dut1_dut2_link, dut2_tg_link]
        topology_links = {'DUT1_DUT2_LINK': dut1_dut2_link,
                          'DUT1_TG_LINK': dut1_tg_link,
                          'DUT2_TG_LINK': dut2_tg_link,
                          'TG_TRAFFIC_LINKS': tg_traffic_links,
                          'DUT1_BD_LINKS': dut1_bd_links,
                          'DUT2_BD_LINKS': dut2_bd_links}
        return topology_links
