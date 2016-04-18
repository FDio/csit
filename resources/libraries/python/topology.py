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

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword
from yaml import load

__all__ = ["DICT__nodes", 'Topology']


def load_topo_from_yaml():
    """Load topology from file defined in "${TOPOLOGY_PATH}" variable

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
    # Virtual Machine (this node running on DUT node)
    VM = 'VM'


class NodeSubTypeTG(object):
    #T-Rex traffic generator
    TREX = 'TREX'
    # Moongen
    MOONGEN = 'MOONGEN'
    # IxNetwork
    IXNET = 'IXNET'

DICT__nodes = load_topo_from_yaml()


class Topology(object):
    """Topology data manipulation and extraction methods

    Defines methods used for manipulation and extraction of data from
    the used topology.
    """

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
        """Return node interface name according to key and value

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
    def get_interface_sw_index(node, interface):
        """Get VPP sw_if_index for the interface.

        :param node: Node to get interface sw_if_index on.
        :param interface: Interface identifier.
        :type node: dict
        :type interface: str or int
        :return: Return sw_if_index or None if not found.
        """
        try:
            return int(interface)
        except ValueError:
            for port in node['interfaces'].values():
                port_name = port.get('name')
                if port_name == interface:
                    return port.get('vpp_sw_index')
            return None

    @staticmethod
    def get_interface_mtu(node, interface):
        """Get interface MTU.

        Returns physical layer MTU (max. size of Ethernet frame).
        :param node: Node to get interface MTU on.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        :return: MTU or None if not found.
        :rtype: int
        """
        for port in node['interfaces'].values():
            port_name = port.get('name')
            if port_name == interface:
                return port.get('mtu')

        return None

    @staticmethod
    def get_interface_mac_by_port_key(node, port_key):
        """Get MAC address for the interface based on port key.

        :param node: Node to get interface mac on.
        :param port_key: Dictionary key name of interface.
        :type node: dict
        :type port_key: str
        :return: Return MAC or None if not found.
        """
        for port_name, port_data in node['interfaces'].iteritems():
            if port_name == port_key:
                return port_data['mac_address']

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
            if port_name == interface:
                return port.get('mac_address')

        return None

    @staticmethod
    def get_adjacent_node_and_interface_by_key(nodes_info, node, port_key):
        """Get node and interface adjacent to specified interface
        on local network.

        :param nodes_info: Dictionary containing information on all nodes
        in topology.
        :param node: Node that contains specified interface.
        :param port_key: Interface port key.
        :type nodes_info: dict
        :type node: dict
        :type port_key: str
        :return: Return (node, interface info) tuple or None if not found.
        :rtype: (dict, dict)
        """
        link_name = None
        # get link name where the interface belongs to
        for port_name, port_data in node['interfaces'].iteritems():
            if port_name == 'mgmt':
                continue
            if port_name == port_key:
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
    def _get_node_active_link_names(node, filter_list=None):
        """Return list of link names that are other than mgmt links

        :param node: node topology dictionary
        :param filter_list: Link filter criteria.
        :type node: dict
        :type filter_list: list of strings
        :return: list of strings that represent link names occupied by the node
        """
        interfaces = node['interfaces']
        link_names = []
        for interface in interfaces.values():
            if 'link' in interface:
                if (filter_list is not None) and ('model' in interface):
                    for filt in filter_list:
                        logger.trace("filt: {} == {}".format(filt, interface['model']))
                        if filt == interface['model']:
                            link_names.append(interface['link'])
                elif (filter_list is not None) and ('model' not in interface):
                    logger.trace("Cannot aply filter on interface: {}" \
                                 .format(interface))
                else:
                    link_names.append(interface['link'])
        if len(link_names) == 0:
            link_names = None
        return link_names

    @keyword('Get active links connecting "${node1}" and "${node2}"')
    def get_active_connecting_links(self, node1, node2,
                                    filter_list_node1=None,
                                    filter_list_node2=None):
        """Return list of link names that connect together node1 and node2

        :param node1: node topology dictionary
        :param node2: node topology dictionary
        :param filter_list_node1: Link filter criteria for node1
        :param filter_list_node2: Link filter criteria for node2
        :type node1: dict
        :type node2: dict
        :type filter_list1: list of strings
        :type filter_list2: list of strings
        :return: list of strings that represent connecting link names
        """

        logger.trace("node1: {}".format(str(node1)))
        logger.trace("node2: {}".format(str(node2)))
        node1_links = self._get_node_active_link_names(node1, filter_list=filter_list_node1)
        node2_links = self._get_node_active_link_names(node2, filter_list=filter_list_node2)

        connecting_links = None
        if (node1_links is None):
            logger.error("Unable to find active links for node1")
        elif (node2_links is None):
            logger.error("Unable to find active links for node2")
        else:
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
        :return: Egress interfaces.
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
        :return: Egress interface.
        :rtype: str
        """
        interfaces = self.get_egress_interfaces_for_nodes(node1, node2)
        if not interfaces:
            raise RuntimeError('No egress interface for nodes')
        return interfaces[0]

    @keyword('Get link data useful in circular topology test from tg "${tgen}"'
             ' dut1 "${dut1}" dut2 "${dut2}"')
    def get_links_dict_from_nodes(self, tgen, dut1, dut2):
        """Return link combinations used in tests in circular topology.

        For the time being it returns links from the Node path:
        TG->DUT1->DUT2->TG
        :param tgen: traffic generator node data
        :param dut1: DUT1 node data
        :param dut2: DUT2 node data
        :type tgen: dict
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

    @staticmethod
    def is_tg_node(node):
        """Find out whether the node is TG

        :param node: node to examine
        :return: True if node is type of TG; False otherwise
        """
        return node['type'] == NodeType.TG

    @staticmethod
    def get_node_hostname(node):
        """Return host (hostname/ip address) of the node.

        :param node: Node created from topology.
        :type node: dict
        :return: host as 'str' type
        """
        return node['host']
