# Copyright (c) 2018 Cisco and/or its affiliates.
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

from collections import Counter

from yaml import load

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robot.api.deco import keyword

__all__ = ["DICT__nodes", 'Topology', 'NodeType']


def load_topo_from_yaml():
    """Load topology from file defined in "${TOPOLOGY_PATH}" variable.

    :returns: Nodes from loaded topology.
    """
    try:
        topo_path = BuiltIn().get_variable_value("${TOPOLOGY_PATH}")
    except RobotNotRunningError:
        return ''

    with open(topo_path) as work_file:
        return load(work_file.read())['nodes']


# pylint: disable=invalid-name

class NodeType(object):
    """Defines node types used in topology dictionaries."""
    # Device Under Test (this node has VPP running on it)
    DUT = 'DUT'
    # Traffic Generator (this node has traffic generator on it)
    TG = 'TG'
    # Virtual Machine (this node running on DUT node)
    VM = 'VM'


class NodeSubTypeTG(object):
    """Defines node sub-type TG - traffic generator."""
    # T-Rex traffic generator
    TREX = 'TREX'
    # Moongen
    MOONGEN = 'MOONGEN'
    # IxNetwork
    IXNET = 'IXNET'

DICT__nodes = load_topo_from_yaml()


class Topology(object):
    """Topology data manipulation and extraction methods.

    Defines methods used for manipulation and extraction of data from
    the active topology.

    "Active topology" contains initially data from the topology file and can be
    extended with additional data from the DUTs like internal interface indexes
    or names. Additional data which can be filled to the active topology are

        - additional internal representation (index, name, ...)
        - operational data (dynamic ports)

    To access the port data it is recommended to use a port key because the key
    does not rely on the data retrieved from nodes, this allows to call most of
    the methods without having filled active topology with internal nodes data.
    """

    @staticmethod
    def add_new_port(node, ptype):
        """Add new port to the node to active topology.

        :param node: Node to add new port on.
        :param ptype: Port type, used as key prefix.
        :type node: dict
        :type ptype: str
        :returns: Port key or None
        :rtype: string or None
        """
        max_ports = 1000000
        iface = None
        for i in range(1, max_ports):
            if node['interfaces'].get(str(ptype) + str(i)) is None:
                iface = str(ptype) + str(i)
                node['interfaces'][iface] = dict()
                break
        return iface

    @staticmethod
    def remove_port(node, iface_key):
        """Remove required port from active topology.

        :param node: Node to remove port on.
        :param: iface_key: Topology key of the interface.
        :type node: dict
        :type iface_key: str
        :returns: Nothing
        """
        try:
            node['interfaces'].pop(iface_key)
        except KeyError:
            pass

    @staticmethod
    def remove_all_ports(node, ptype):
        """Remove all ports with ptype as prefix.

        :param node: Node to remove ports on.
        :param: ptype: Port type, used as key prefix.
        :type node: dict
        :type ptype: str
        :returns: Nothing
        """
        for if_key in list(node['interfaces']):
            if if_key.startswith(str(ptype)):
                node['interfaces'].pop(if_key)

    @staticmethod
    def remove_all_added_ports_on_all_duts_from_topology(nodes):
        """Remove all added ports on all DUT nodes in the topology.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        :returns: Nothing
        """
        port_types = ('subinterface', 'vlan_subif', 'memif', 'tap', 'vhost',
                      'loopback', 'gre_tunnel', 'vxlan_tunnel', 'eth_bond')

        for node_data in nodes.values():
            if node_data['type'] == NodeType.DUT:
                for ptype in port_types:
                    Topology.remove_all_ports(node_data, ptype)

    @staticmethod
    def update_interface_sw_if_index(node, iface_key, sw_if_index):
        """Update sw_if_index on the interface from the node.

        :param node: Node to update sw_if_index on.
        :param iface_key: Topology key of the interface.
        :param sw_if_index: Internal index to store.
        :type node: dict
        :type iface_key: str
        :type sw_if_index: int
        """
        node['interfaces'][iface_key]['vpp_sw_index'] = int(sw_if_index)

    @staticmethod
    def update_interface_name(node, iface_key, name):
        """Update name on the interface from the node.

        :param node: Node to update name on.
        :param iface_key: Topology key of the interface.
        :param name: Interface name to store.
        :type node: dict
        :type iface_key: str
        :type name: str
        """
        node['interfaces'][iface_key]['name'] = str(name)

    @staticmethod
    def update_interface_mac_address(node, iface_key, mac_address):
        """Update mac_address on the interface from the node.

        :param node: Node to update MAC on.
        :param iface_key: Topology key of the interface.
        :param mac_address: MAC address.
        :type node: dict
        :type iface_key: str
        :type mac_address: str
        """
        node['interfaces'][iface_key]['mac_address'] = str(mac_address)

    @staticmethod
    def update_interface_pci_address(node, iface_key, pci_address):
        """Update pci_address on the interface from the node.

        :param node: Node to update PCI on.
        :param iface_key: Topology key of the interface.
        :param pci_address: PCI address.
        :type node: dict
        :type iface_key: str
        :type mac_address: str
        """
        node['interfaces'][iface_key]['pci_address'] = str(pci_address)

    @staticmethod
    def update_interface_vhost_socket(node, iface_key, vhost_socket):
        """Update vhost socket name on the interface from the node.

        :param node: Node to update socket name on.
        :param iface_key: Topology key of the interface.
        :param vhost_socket: Path to named socket on node.
        :type node: dict
        :type iface_key: str
        :type vhost_socket: str
        """
        node['interfaces'][iface_key]['vhost_socket'] = str(vhost_socket)

    @staticmethod
    def update_interface_memif_socket(node, iface_key, memif_socket):
        """Update memif socket name on the interface from the node.

        :param node: Node to update socket name on.
        :param iface_key: Topology key of the interface.
        :param memif_socket: Path to named socket on node.
        :type node: dict
        :type iface_key: str
        :type memif_socket: str
        """
        node['interfaces'][iface_key]['memif_socket'] = str(memif_socket)

    @staticmethod
    def update_interface_memif_id(node, iface_key, memif_id):
        """Update memif ID on the interface from the node.

        :param node: Node to update memif ID on.
        :param iface_key: Topology key of the interface.
        :param memif_id: Memif interface ID.
        :type node: dict
        :type iface_key: str
        :type memif_id: str
        """
        node['interfaces'][iface_key]['memif_id'] = str(memif_id)

    @staticmethod
    def update_interface_memif_role(node, iface_key, memif_role):
        """Update memif role on the interface from the node.

        :param node: Node to update memif role on.
        :param iface_key: Topology key of the interface.
        :param memif_role: Memif role.
        :type node: dict
        :type iface_key: str
        :type memif_role: str
        """
        node['interfaces'][iface_key]['memif_role'] = str(memif_role)

    @staticmethod
    def update_interface_tap_dev_name(node, iface_key, dev_name):
        """Update device name on the tap interface from the node.

        :param node: Node to update tap device name on.
        :param iface_key: Topology key of the interface.
        :param dev_name: Device name of the tap interface.
        :type node: dict
        :type iface_key: str
        :type dev_name: str
        :returns: Nothing
        """
        node['interfaces'][iface_key]['dev_name'] = str(dev_name)

    @staticmethod
    def get_node_by_hostname(nodes, hostname):
        """Get node from nodes of the topology by hostname.

        :param nodes: Nodes of the test topology.
        :param hostname: Host name.
        :type nodes: dict
        :type hostname: str
        :returns: Node dictionary or None if not found.
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
        :returns: Links in the topology.
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
        """Return node interface key from topology file
        according to key and value.

        :param node: The node dictionary.
        :param key: Key by which to select the interface.
        :param value: Value that should be found using the key.
        :type node: dict
        :type key: string
        :type value: string
        :returns: Interface key from topology file
        :rtype: string
        """
        interfaces = node['interfaces']
        retval = None
        for if_key, if_val in interfaces.iteritems():
            k_val = if_val.get(key)
            if k_val is not None:
                if k_val == value:
                    retval = if_key
                    break
        return retval

    @staticmethod
    def get_interface_by_name(node, iface_name):
        """Return interface key based on name from DUT/TG.

        This method returns interface key based on interface name
        retrieved from the DUT, or TG.

        :param node: The node topology dictionary.
        :param iface_name: Interface name (string form).
        :type node: dict
        :type iface_name: string
        :returns: Interface key.
        :rtype: str
        """
        return Topology._get_interface_by_key_value(node, "name", iface_name)

    @staticmethod
    def get_interface_by_link_name(node, link_name):
        """Return interface key of link on node.

        This method returns the interface name associated with a given link
        for a given node.

        :param node: The node topology dictionary.
        :param link_name: Name of the link that a interface is connected to.
        :type node: dict
        :type link_name: string
        :returns: Interface key of the interface connected to the given link.
        :rtype: str
        """
        return Topology._get_interface_by_key_value(node, "link", link_name)

    def get_interfaces_by_link_names(self, node, link_names):
        """Return dictionary of dictionaries {"interfaceN", interface name}.

        This method returns the interface names associated with given links
        for a given node.

        :param node: The node topology directory.
        :param link_names: List of names of the link that a interface is
            connected to.
        :type node: dict
        :type link_names: list
        :returns: Dictionary of interface names that are connected to the given
            links.
        :rtype: dict
        """
        retval = {}
        interface_key_tpl = "interface{}"
        interface_number = 1
        for link_name in link_names:
            interface = self.get_interface_by_link_name(node, link_name)
            interface_name = self.get_interface_name(node, interface)
            interface_key = interface_key_tpl.format(str(interface_number))
            retval[interface_key] = interface_name
            interface_number += 1
        return retval

    @staticmethod
    def get_interface_by_sw_index(node, sw_index):
        """Return interface name of link on node.

        This method returns the interface name associated with a software
        interface index assigned to the interface by vpp for a given node.

        :param node: The node topology dictionary.
        :param sw_index: Sw_index of the link that a interface is connected to.
        :type node: dict
        :type sw_index: int
        :returns: Interface name of the interface connected to the given link.
        :rtype: str
        """
        return Topology._get_interface_by_key_value(node, "vpp_sw_index",
                                                    sw_index)

    @staticmethod
    def get_interface_sw_index(node, iface_key):
        """Get VPP sw_if_index for the interface using interface key.

        :param node: Node to get interface sw_if_index on.
        :param iface_key: Interface key from topology file, or sw_index.
        :type node: dict
        :type iface_key: str/int
        :returns: Return sw_if_index or None if not found.
        """
        try:
            if isinstance(iface_key, basestring):
                return node['interfaces'][iface_key].get('vpp_sw_index')
            # TODO: use only iface_key, do not use integer
            else:
                return int(iface_key)
        except (KeyError, ValueError):
            return None

    @staticmethod
    def get_interface_sw_index_by_name(node, iface_name):
        """Get VPP sw_if_index for the interface using interface name.

        :param node: Node to get interface sw_if_index on.
        :param iface_name: Interface name.
        :type node: dict
        :type iface_name: str
        :returns: Return sw_if_index or None if not found.
        :raises TypeError: If provided interface name is not a string.
        """
        try:
            if isinstance(iface_name, basestring):
                iface_key = Topology.get_interface_by_name(node, iface_name)
                return node['interfaces'][iface_key].get('vpp_sw_index')
            else:
                raise TypeError("Interface name must be a string.")
        except (KeyError, ValueError):
            return None

    @staticmethod
    def get_interface_mtu(node, iface_key):
        """Get interface MTU.

        Returns physical layer MTU (max. size of Ethernet frame).
        :param node: Node to get interface MTU on.
        :param iface_key: Interface key from topology file.
        :type node: dict
        :type iface_key: str
        :returns: MTU or None if not found.
        :rtype: int
        """
        try:
            return node['interfaces'][iface_key].get('mtu')
        except KeyError:
            return None

    @staticmethod
    def get_interface_name(node, iface_key):
        """Get interface name (retrieved from DUT/TG).

        Returns name in string format, retrieved from the node.
        :param node: Node to get interface name on.
        :param iface_key: Interface key from topology file.
        :type node: dict
        :type iface_key: str
        :returns: Interface name or None if not found.
        :rtype: str
        """
        try:
            return node['interfaces'][iface_key].get('name')
        except KeyError:
            return None

    @staticmethod
    def convert_interface_reference_to_key(node, interface):
        """Takes interface reference in any format
        (name, link name, interface key or sw_if_index)
        and converts to interface key using Topology methods.

        :param node: Node in topology.
        :param interface: Name, sw_if_index, link name or key of an interface
            on the node.
        :type node: dict
        :type interface: str or int

        :returns: Interface key.
        :rtype: str

        :raises TypeError: If provided with invalid interface argument.
        :raises RuntimeError: If the interface does not exist in topology.
        """

        if isinstance(interface, int):
            key = Topology.get_interface_by_sw_index(node, interface)
            if key is None:
                raise RuntimeError("Interface with sw_if_index={0} does not "
                                   "exist in topology.".format(interface))
        elif interface in Topology.get_node_interfaces(node):
            key = interface
        elif interface in Topology.get_links({"dut": node}):
            key = Topology.get_interface_by_link_name(node, interface)
        elif isinstance(interface, basestring):
            key = Topology.get_interface_by_name(node, interface)
            if key is None:
                raise RuntimeError("Interface with key, name or link name "
                                   "\"{0}\" does not exist in topology."
                                   .format(interface))
        else:
            raise TypeError("Type of interface argument must be integer"
                            " or string.")
        return key

    @staticmethod
    def convert_interface_reference(node, interface, wanted_format):
        """Takes interface reference in any format
        (name, link name, topology key or sw_if_index) and returns
        its equivalent in the desired format.

        :param node: Node in topology.
        :param interface: Name, sw_if_index, link name or key of an interface
            on the node.
        :param wanted_format: Format of return value wanted.
            Valid options are: sw_if_index, key, name.
        :type node: dict
        :type interface: str or int
        :type wanted_format: str
        :returns: Interface name, interface key or sw_if_index.
        :rtype: str or int
        :raises TypeError, ValueError: If provided with invalid arguments.
        :raises RuntimeError: If the interface does not exist in topology.
        """

        key = Topology.convert_interface_reference_to_key(node, interface)

        conversions = {
            "key": lambda x, y: y,
            "name": Topology.get_interface_name,
            "sw_if_index": Topology.get_interface_sw_index
        }

        try:
            return conversions[wanted_format](node, key)
        except KeyError:
            raise ValueError("Unrecognized return value wanted: {0}."
                             "Valid options are key, name, sw_if_index"
                             .format(wanted_format))

    @staticmethod
    def get_interface_numa_node(node, iface_key):
        """Get interface numa node.

        Returns physical relation to numa node, numa_id.

        :param node: Node to get numa id on.
        :param iface_key: Interface key from topology file.
        :type node: dict
        :type iface_key: str
        :returns: numa node id, None if not available.
        :rtype: int
        """
        try:
            return node['interfaces'][iface_key].get('numa_node')
        except KeyError:
            return None

    @staticmethod
    def get_interfaces_numa_node(node, *iface_keys):
        """Get numa node on which are located most of the interfaces.

        Return numa node with highest count of interfaces provided as arguments.
        Return 0 if the interface does not have numa_node information available.
        If all interfaces have unknown location (-1), then return 0.
        If most of interfaces have unknown location (-1), but there are
        some interfaces with known location, then return the second most
        location of the provided interfaces.

        :param node: Node from DICT__nodes.
        :param iface_keys: Interface keys for lookup.
        :type node: dict
        :type iface_keys: strings
        """
        numa_list = []
        for if_key in iface_keys:
            try:
                numa_list.append(node['interfaces'][if_key].get('numa_node'))
            except KeyError:
                pass

        numa_cnt_mc = Counter(numa_list).most_common()

        if len(numa_cnt_mc) > 0 and numa_cnt_mc[0][0] != -1:
            return numa_cnt_mc[0][0]
        elif len(numa_cnt_mc) > 1 and numa_cnt_mc[0][0] == -1:
            return numa_cnt_mc[1][0]
        else:
            return 0

    @staticmethod
    def get_interface_mac(node, iface_key):
        """Get MAC address for the interface.

        :param node: Node to get interface mac on.
        :param iface_key: Interface key from topology file.
        :type node: dict
        :type iface_key: str
        :returns: Return MAC or None if not found.
        """
        try:
            return node['interfaces'][iface_key].get('mac_address')
        except KeyError:
            return None

    @staticmethod
    def get_interface_ip4(node, iface_key):
        """Get IP4 address for the interface.

        :param node: Node to get interface mac on.
        :param iface_key: Interface key from topology file.
        :type node: dict
        :type iface_key: str
        :returns: Return IP4 or None if not found.
        """
        try:
            return node['interfaces'][iface_key].get('ip4_address', None)
        except KeyError:
            return None

    @staticmethod
    def get_adjacent_node_and_interface(nodes_info, node, iface_key):
        """Get node and interface adjacent to specified interface
        on local network.

        :param nodes_info: Dictionary containing information on all nodes
            in topology.
        :param node: Node that contains specified interface.
        :param iface_key: Interface key from topology file.
        :type nodes_info: dict
        :type node: dict
        :type iface_key: str
        :returns: Return (node, interface_key) tuple or None if not found.
        :rtype: (dict, str)
        """
        link_name = None
        # get link name where the interface belongs to
        for if_key, if_val in node['interfaces'].iteritems():
            if if_key == 'mgmt':
                continue
            if if_key == iface_key:
                link_name = if_val['link']
                break

        if link_name is None:
            return None

        # find link
        for node_data in nodes_info.values():
            # skip self
            if node_data['host'] == node['host']:
                continue
            for if_key, if_val \
                    in node_data['interfaces'].iteritems():
                if 'link' not in if_val:
                    continue
                if if_val['link'] == link_name:
                    return node_data, if_key

    @staticmethod
    def get_interface_pci_addr(node, iface_key):
        """Get interface PCI address.

        :param node: Node to get interface PCI address on.
        :param iface_key: Interface key from topology file.
        :type node: dict
        :type iface_key: str
        :returns: Return PCI address or None if not found.
        """
        try:
            return node['interfaces'][iface_key].get('pci_address')
        except KeyError:
            return None

    @staticmethod
    def get_interface_driver(node, iface_key):
        """Get interface driver.

        :param node: Node to get interface driver on.
        :param iface_key: Interface key from topology file.
        :type node: dict
        :type iface_key: str
        :returns: Return interface driver or None if not found.
        """
        try:
            return node['interfaces'][iface_key].get('driver')
        except KeyError:
            return None

    @staticmethod
    def get_node_interfaces(node):
        """Get all node interfaces.

        :param node: Node to get list of interfaces from.
        :type node: dict
        :returns: Return list of keys of all interfaces.
        :rtype: list
        """
        return node['interfaces'].keys()

    @staticmethod
    def get_node_link_mac(node, link_name):
        """Return interface mac address by link name.

        :param node: Node to get interface sw_index on.
        :param link_name: Link name.
        :type node: dict
        :type link_name: str
        :returns: MAC address string.
        :rtype: str
        """
        for port in node['interfaces'].values():
            if port.get('link') == link_name:
                return port.get('mac_address')
        return None

    @staticmethod
    def _get_node_active_link_names(node, filter_list=None):
        """Return list of link names that are other than mgmt links.

        :param node: Node topology dictionary.
        :param filter_list: Link filter criteria.
        :type node: dict
        :type filter_list: list of strings
        :returns: List of strings representing link names occupied by the node.
        :rtype: list
        """
        interfaces = node['interfaces']
        link_names = []
        for interface in interfaces.values():
            if 'link' in interface:
                if (filter_list is not None) and ('model' in interface):
                    for filt in filter_list:
                        if filt == interface['model']:
                            link_names.append(interface['link'])
                elif (filter_list is not None) and ('model' not in interface):
                    logger.trace('Cannot apply filter on interface: {}'
                                 .format(str(interface)))
                else:
                    link_names.append(interface['link'])
        if len(link_names) == 0:
            link_names = None
        return link_names

    @keyword('Get active links connecting "${node1}" and "${node2}"')
    def get_active_connecting_links(self, node1, node2,
                                    filter_list_node1=None,
                                    filter_list_node2=None):
        """Return list of link names that connect together node1 and node2.

        :param node1: Node topology dictionary.
        :param node2: Node topology dictionary.
        :param filter_list_node1: Link filter criteria for node1.
        :param filter_list_node2: Link filter criteria for node2.
        :type node1: dict
        :type node2: dict
        :type filter_list_node1: list of strings
        :type filter_list_node2: list of strings
        :returns: List of strings that represent connecting link names.
        :rtype: list
        """

        logger.trace("node1: {}".format(str(node1)))
        logger.trace("node2: {}".format(str(node2)))
        node1_links = self._get_node_active_link_names(
            node1,
            filter_list=filter_list_node1)
        node2_links = self._get_node_active_link_names(
            node2,
            filter_list=filter_list_node2)

        connecting_links = None
        if node1_links is None:
            logger.error("Unable to find active links for node1")
        elif node2_links is None:
            logger.error("Unable to find active links for node2")
        else:
            connecting_links = list(set(node1_links).intersection(node2_links))

        return connecting_links

    @keyword('Get first active connecting link between node "${node1}" and '
             '"${node2}"')
    def get_first_active_connecting_link(self, node1, node2):
        """

        :param node1: Connected node.
        :param node2: Connected node.
        :type node1: dict
        :type node2: dict
        :returns: Name of link connecting the two nodes together.
        :rtype: str
        :raises RuntimeError: If no links are found.
        """
        connecting_links = self.get_active_connecting_links(node1, node2)
        if len(connecting_links) == 0:
            raise RuntimeError("No links connecting the nodes were found")
        else:
            return connecting_links[0]

    @keyword('Get egress interfaces name on "${node1}" for link with '
             '"${node2}"')
    def get_egress_interfaces_name_for_nodes(self, node1, node2):
        """Get egress interfaces on node1 for link with node2.

        :param node1: First node, node to get egress interface on.
        :param node2: Second node.
        :type node1: dict
        :type node2: dict
        :returns: Egress interfaces.
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

    @keyword('Get first egress interface name on "${node1}" for link with '
             '"${node2}"')
    def get_first_egress_interface_for_nodes(self, node1, node2):
        """Get first egress interface on node1 for link with node2.

        :param node1: First node, node to get egress interface name on.
        :param node2: Second node.
        :type node1: dict
        :type node2: dict
        :returns: Egress interface name.
        :rtype: str
        """
        interfaces = self.get_egress_interfaces_name_for_nodes(node1, node2)
        if not interfaces:
            raise RuntimeError('No egress interface for nodes')
        return interfaces[0]

    @keyword('Get link data useful in circular topology test from tg "${tgen}"'
             ' dut1 "${dut1}" dut2 "${dut2}"')
    def get_links_dict_from_nodes(self, tgen, dut1, dut2):
        """Return link combinations used in tests in circular topology.

        For the time being it returns links from the Node path:
        TG->DUT1->DUT2->TG
        The naming convention until changed to something more general is
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

        :param tgen: Traffic generator node data.
        :param dut1: DUT1 node data.
        :param dut2: DUT2 node data.
        :type tgen: dict
        :type dut1: dict
        :type dut2: dict
        :returns: Dictionary of possible link combinations.
        :rtype: dict
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
        """Find out whether the node is TG.

        :param node: Node to examine.
        :type node: dict
        :returns: True if node is type of TG, otherwise False.
        :rtype: bool
        """
        return node['type'] == NodeType.TG

    @staticmethod
    def get_node_hostname(node):
        """Return host (hostname/ip address) of the node.

        :param node: Node created from topology.
        :type node: dict
        :returns: Hostname or IP address.
        :rtype: str
        """
        return node['host']

    @staticmethod
    def get_node_arch(node):
        """Return arch of the node.
           Default to x86_64 if no arch present

        :param node: Node created from topology.
        :type node: dict
        :returns: Node architecture
        :rtype: str
        """
        try:
            return node['arch']
        except KeyError:
            node['arch'] = 'x86_64'
            return 'x86_64'

    @staticmethod
    def get_cryptodev(node):
        """Return Crytodev configuration of the node.

        :param node: Node created from topology.
        :type node: dict
        :returns: Cryptodev configuration string.
        :rtype: str
        """
        try:
            return node['cryptodev']
        except KeyError:
            return None

    @staticmethod
    def get_uio_driver(node):
        """Return uio-driver configuration of the node.

        :param node: Node created from topology.
        :type node: dict
        :returns: uio-driver configuration string.
        :rtype: str
        """
        try:
            return node['uio_driver']
        except KeyError:
            return None

    @staticmethod
    def set_interface_numa_node(node, iface_key, numa_node_id):
        """Set interface numa_node location.

        :param node: Node to set numa_node on.
        :param iface_key: Interface key from topology file.
        :type node: dict
        :type iface_key: str
        :returns: Return iface_key or None if not found.
        """
        try:
            node['interfaces'][iface_key]['numa_node'] = numa_node_id
            return iface_key
        except KeyError:
            return None
