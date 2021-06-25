# Copyright (c) 2021 Cisco and/or its affiliates.
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

import re

from collections import Counter
from collections.abc import Mapping

from yaml import safe_load, YAMLError

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.frozen_dict import FrozenDict
from resources.libraries.python.robot_interaction import get_variable

__all__ = [
    u"DICT__nodes", u"Topology", u"NodeType", u"SocketType", u"NodeSubTypeTG"
]


class NodeType:
    """Defines node types used in topology dictionaries."""
    # Device Under Test (this node has VPP running on it)
    DUT = u"DUT"
    # Traffic Generator (this node has traffic generator on it)
    # pylint: disable=invalid-name
    TG = u"TG"
    # Virtual Machine (this node running on DUT node)
    # pylint: disable=invalid-name
    VM = u"VM"


class NodeSubTypeTG:
    """Defines node sub-type TG - traffic generator."""
    # T-Rex traffic generator
    TREX = u"TREX"
    # Moongen
    MOONGEN = u"MOONGEN"
    # IxNetwork
    IXNET = u"IXNET"


class SocketType:
    """Defines socket types used in topology dictionaries."""
    # VPP Socket PAPI
    PAPI = u"PAPI"
    # VPP PAPI Stats (legacy option until stats are migrated to Socket PAPI)
    STATS = u"STATS"


class SubNodeDict(FrozenDict):
    """FrozenDict with string keys and values of int, string or SubNodeDict.

    Topology node substructures are intended to be if this type.
    Current implementation uses FrozenDict everywhere instead,
    this class definition is just to make docstrings more expressive.
    """
    pass


class NodeDict(SubNodeDict):
    """FrozenDict with string keys and values of string or SubNodeDict.

    Topology node structure is intended to be if this type.
    Current implementation uses FrozenDict everywhere instead,
    this class definition is just to make docstrings more expressive.
    """
    pass


class NodesDict(NodeDict):
    """FrozenDict with string keys and values of string or NodeDict.

    Topology "nodes" structure is intended to be if this type.
    Current implementation uses FrozenDict everywhere instead,
    this class definition is just to make docstrings more expressive.
    """
    pass

# TODO: Use real *Type types in the code, instead of FrozenDict everywhere.


DICT__nodes = None


def _replace_nodes(new_nodes, reason="unknown", log_level=u"TRACE"):
    """Set global nodes structure to the new value, log it.

    :param new_nodes: Set global nodes structure to this value.
    :param reason: Message explaining why the update is made.
    :param log_level: Importance of the update, expressed as log level.
    :type new_nodes: topology.NodesDict
    :type reason: str
    :type log_level: str
    """
    global DICT__nodes
    # One more freeze to be extra sure.
    new_nodes = FrozenDict(new_nodes)
    # TODO: Skip or tweak reason/log_level if new_nodes==DICT__nodes?
    logger.write(
        msg=f"Nodes structure updated. Reason: {reason}\n{new_nodes}",
        level=log_level,
    )
    # TODO: Add JSON export here.
    # TODO: Export diff instead/alongside whole new state?
    DICT__nodes = new_nodes


def _get_nodes():
    """Return cached value, initialize from file on first access.

    Load topology from file defined in "${TOPOLOGY_PATH}" variable.
    If the path is not defined or load fail, initialize as empty.

    :returns: Complete "nodes" scructure.
    :rtype: topology.NodesDict
    """
    global DICT__nodes
    if DICT__nodes is None:
        topo_path = get_variable(u"${TOPOLOGY_PATH}", u"")
        try:
            with open(topo_path, u"r") as work_file:
                new_nodes = FrozenDict(safe_load(work_file)[u"nodes"])
        except (IOError, YAMLError, KeyError):
            new_nodes = FrozenDict({})
        _replace_nodes(new_nodes, reason=u"initial read", log_level=u"INFO")
    # TODO: Return a shallow copy to be extra sure?
    return DICT__nodes


class Topology:
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

    ROBOT_LIBRARY_SCOPE = u"GLOBAL"
    # TODO: Move DICT__nodes here?

    @staticmethod
    def _add_node_item_recursive(cursor, value, path):
        """Add string value anywhere into nodes structure.

        If a key on a path does not exist, it is created.
        If a middle of a path contains an empty string (instead of sub-mapping),
        it is overwritten with empty sub-mapping (to add the rest of path).
        If a middle of a path contains a non-empty string,
        a sub-mapping is still created, but with the string as additional
        key (and empty string value).

        Implementation recursively tracks a cursor and returns updated subtrees.
        This in the recursive part of the implementation,
        not updating the global nodes state yet.

        :param cursor: Reference to the "cursor" structure.
        :param value: Value to insert.
        :param path: Remaining path from cursor.
        :type cursor: topology.SubNodeDict
        :type value: Union[str, int, topology.SubNodeDict]
        :type path: Sequence[str]
        :returns: Modified structure, cursor remains unmodified.
        :rtype: topology.SubNodeDict
        :raises KeyError: If path is empty.
        """
        if not path:
            raise KeyError(u"Empty path!")
        key, *rest = path
        if not rest:
            # End of the path, add/replace the value.
            return cursor.including(key, value)
        # Middle of path. Is sub-structure ready?
        sub_cursor = FrozenDict({})
        if key in cursor:
            middle_val = cursor[key]
            # TODO: What if middle_val is a list/tuple?
            if isinstance(middle_val, Mapping):
                # Sub-structure is ready.
                sub_cursor = middle_val
            elif isinstance(middle_val, str) and middle_val:
                # Save old string as a key.
                sub_cursor = FrozenDict({middle_val: u""})
            # Replace with empty sub-structure.
        # Else use empty sub-structure for the rest of the path.
        sub_cursor = Topology._add_node_item_recursive(sub_cursor, value, rest)
        return cursor.including(key, sub_cursor)

    @staticmethod
    def add_node_item(node, value, path, reason=u"unknown", log_level=u"TRACE"):
        """Add item to one of topology nodes, return the updated node.

        TODO: Refactor keywords to use node key (e.g. "TG") instead of "node".

        This is the non-recursive part, updating global nodes content,
        after checking the "node" argument really is one of nodes.

        :param node: Topology node.
        :param value: Value to insert.
        :param path: Path where to insert item.
        :param reason: Message explaining why the update is made.
        :param log_level: Importance of the update, expressed as log level.
        :type node: topology.NodeDict
        :type value: str
        :type path: Sequence[str]
        :type reason: str
        :type log_level: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        :raises KeyError: If path is empty.
        :raises ValueError: If node is not found in nodes.
        """
        if not path:
            raise KeyError(u"Empty path!")
        nodes = _get_nodes()
        for node_key, node_struct in nodes:
            if node_struct == node:
                break
        else:
            raise ValueError(f"Node not found: {node}")
        full_path = node_key, *path
        new_nodes = Topology._add_node_item_recursive(nodes, value, full_path)
        _replace_nodes(new_nodes=new_nodes, reason=reason, log_level=log_level)
        return new_nodes[node_key]

    @staticmethod
    def add_new_port(node, ptype):
        """Add new port to the node to active topology.

        :param node: Node to add new port on.
        :param ptype: Port type, used as key prefix.
        :type node: topology.NodeDict
        :type ptype: str
        :returns: Port key or None
        :rtype: string or None
        """
        max_ports = 1000000
        iface = None
        for i in range(1, max_ports):
            if node[u"interfaces"].get(str(ptype) + str(i)) is None:
                iface = str(ptype) + str(i)
                path = [u"interfaces", iface]
                Topology.add_node_item(node, dict(), path, u"add_new_port")
                break
        return iface

    @staticmethod
    def remove_port(node, iface_key):
        """Remove required port from active topology.

        Any KeyError silently aborts the operation.

        :param node: Node to remove port on.
        :param: iface_key: Topology key of the interface.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Node structure after removal, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        # TODO: Implement del_node_item(node, path, reason, log_level)?
        try:
            interfaces = node[u"interfaces"].copy()
            interfaces.pop(iface_key)
            node_after_removal = Topology.add_node_item(
                node, interfaces, [u"interfaces"], u"remove_port"
            )
            return node_after_removal
        except KeyError:
            return node

    @staticmethod
    def remove_all_ports(node, ptype):
        """Remove all ports with ptype as prefix.

        :param node: Node to remove ports on.
        :param: ptype: Port type, used as key prefix.
        :type node: topology.NodeDict
        :type ptype: str
        :returns: Node structure after removal, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        interfaces = {
            if_key: if_val for if_key, if_val in node[u"interfaces"].items()
            if not if_key.startswith(str(ptype))
        }
        node_after_removal = Topology.add_node_item(
            node, interfaces, [u"interfaces"], u"remove_all_ports"
        )
        return node_after_removal

    @staticmethod
    def remove_all_added_ports_on_all_duts_from_topology(nodes):
        """Remove all added ports on all DUT nodes in the topology.

        The nodes argument is ignored, operating on the global variable instead.

        :param nodes: Nodes in the topology.
        :type nodes: topology.NodesDict
        """
        port_types = (
            u"subinterface", u"vlan_subif", u"memif", u"tap", u"vhost",
            u"loopback", u"gre_tunnel", u"vxlan_tunnel", u"eth_bond",
            u"eth_avf", u"eth_rdma", u"geneve_tunnel", u"eth_af_xdp",
            u"gtpu_tunnel"
        )

        # Implementation compares node_data, so it has to be updated frequently.
        for node_key in _get_nodes().copy():
            node_data = _get_nodes()[node_key]
            if node_data[u"type"] == NodeType.DUT:
                for ptype in port_types:
                    # TODO: Avoid logging one by one?
                    node_data = Topology.remove_all_ports(node_data, ptype)
                    # TODO: Override reason?

    @staticmethod
    def remove_all_vif_ports(node):
        """Remove all Virtual Interfaces on DUT node.

        :param node: Node to remove VIF ports on.
        :type node: topology.NodeDict
        :returns: Node structure after removal, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        reg_ex = re.compile(r"port\d+_vif\d+")
        interfaces = {
            if_key: if_val for if_key, if_val in node[u"interfaces"].items()
            if not re.match(reg_ex, if_key)
        }
        return Topology.add_node_item(
            node, interfaces, [u"interfaces"], u"remove_all_vif_ports"
        )

    @staticmethod
    def remove_all_added_vif_ports_on_all_duts_from_topology(nodes):
        """Remove all added Virtual Interfaces on all DUT nodes in
        the topology.

        The nodes argument is ignored, operating on the global variable instead.

        :param nodes: Nodes in the topology.
        :type nodes: topology.NodesDict
        """
        # Each node is edited only once, so we do not need to track.
        for node_data in _get_nodes().copy().values():
            if node_data[u"type"] == NodeType.DUT:
                Topology.remove_all_vif_ports(node_data)

    @staticmethod
    def update_interface_sw_if_index(node, iface_key, sw_if_index):
        """Update sw_if_index on the interface from the node.

        :param node: Node to update sw_if_index on.
        :param iface_key: Topology key of the interface.
        :param sw_if_index: Internal index to store.
        :type node: topology.NodeDict
        :type iface_key: str
        :type sw_if_index: int
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"vpp_sw_index"]
        return Topology.add_node_item(
            node, int(sw_if_index), path, u"update_interface_sw_if_index"
        )

    @staticmethod
    def update_interface_name(node, iface_key, name):
        """Update name on the interface from the node.

        :param node: Node to update name on.
        :param iface_key: Topology key of the interface.
        :param name: Interface name to store.
        :type node: topology.NodeDict
        :type iface_key: str
        :type name: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"name"]
        return Topology.add_node_item(
            node, str(name), path, u"update_interface_name"
        )

    @staticmethod
    def update_interface_mac_address(node, iface_key, mac_address):
        """Update mac_address on the interface from the node.

        :param node: Node to update MAC on.
        :param iface_key: Topology key of the interface.
        :param mac_address: MAC address.
        :type node: topology.NodeDict
        :type iface_key: str
        :type mac_address: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"mac_address"]
        return Topology.add_node_item(
            node, str(mac_address), path, u"update_interface_mac_address"
        )

    @staticmethod
    def update_interface_pci_address(node, iface_key, pci_address):
        """Update pci_address on the interface from the node.

        :param node: Node to update PCI on.
        :param iface_key: Topology key of the interface.
        :param pci_address: PCI address.
        :type node: topology.NodeDict
        :type iface_key: str
        :type pci_address: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"pci_address"]
        return Topology.add_node_item(
            node, str(pci_address), path, u"update_interface_pci_address"
        )

    @staticmethod
    def update_interface_vlan(node, iface_key, vlan):
        """Update VLAN on the interface from the node.

        :param node: Node to update VLAN on.
        :param iface_key: Topology key of the interface.
        :param vlan: VLAN ID.
        :type node: topology.NodeDict
        :type iface_key: str
        :type vlan: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"vlan"]
        return Topology.add_node_item(
            node, int(vlan), path, u"update_interface_vlan"
        )

    @staticmethod
    def update_interface_vhost_socket(node, iface_key, vhost_socket):
        """Update vhost socket name on the interface from the node.

        :param node: Node to update socket name on.
        :param iface_key: Topology key of the interface.
        :param vhost_socket: Path to named socket on node.
        :type node: topology.NodeDict
        :type iface_key: str
        :type vhost_socket: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"vhost_socket"]
        return Topology.add_node_item(
            node, str(vhost_socket), path, u"update_interface_vhost_socket"
        )

    @staticmethod
    def update_interface_memif_socket(node, iface_key, memif_socket):
        """Update memif socket name on the interface from the node.

        :param node: Node to update socket name on.
        :param iface_key: Topology key of the interface.
        :param memif_socket: Path to named socket on node.
        :type node: topology.NodeDict
        :type iface_key: str
        :type memif_socket: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"memif_socket"]
        return Topology.add_node_item(
            node, str(memif_socket), path, u"update_interface_memif_socket"
        )

    @staticmethod
    def update_interface_memif_id(node, iface_key, memif_id):
        """Update memif ID on the interface from the node.

        :param node: Node to update memif ID on.
        :param iface_key: Topology key of the interface.
        :param memif_id: Memif interface ID.
        :type node: topology.NodeDict
        :type iface_key: str
        :type memif_id: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"memif_id"]
        return Topology.add_node_item(
            node, str(memif_id), path, u"update_interface_memif_id"
        )

    @staticmethod
    def update_interface_memif_role(node, iface_key, memif_role):
        """Update memif role on the interface from the node.

        :param node: Node to update memif role on.
        :param iface_key: Topology key of the interface.
        :param memif_role: Memif role.
        :type node: topology.NodeDict
        :type iface_key: str
        :type memif_role: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"memif_role"]
        return Topology.add_node_item(
            node, str(memif_role), path, u"update_interface_memif_role"
        )

    @staticmethod
    def update_interface_tap_dev_name(node, iface_key, dev_name):
        """Update device name on the tap interface from the node.

        :param node: Node to update tap device name on.
        :param iface_key: Topology key of the interface.
        :param dev_name: Device name of the tap interface.
        :type node: topology.NodeDict
        :type iface_key: str
        :type dev_name: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"interfaces", iface_key, u"dev_name"]
        return Topology.add_node_item(
            node, str(dev_name), path, u"update_interface_tap_dev_name"
        )

    @staticmethod
    def get_node_by_hostname(nodes, hostname):
        """Get node from nodes of the topology by hostname.

        The nodes argument is ignored, operating on the global variable instead.

        :param nodes: Nodes of the test topology.
        :param hostname: Host name.
        :type nodes: topology.NodesDict
        :type hostname: str
        :returns: Node dictionary or None if not found.
        :rtype: Optional[NodeDict]
        """
        for node in _get_nodes().values():
            if node[u"host"] == hostname:
                return node

        return None

    @staticmethod
    def get_links(nodes):
        """Get list of links(networks) in the topology.

        The nodes argument is ignored, operating on the global variable instead.

        :param nodes: Nodes of the test topology.
        :type nodes: topology.NodesDict
        :returns: Links in the topology.
        :rtype: list
        """
        links = list()

        for node in _get_nodes().values():
            for interface in node[u"interfaces"].values():
                link = interface.get(u"link")
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
        :type node: topology.NodeDict
        :type key: string
        :type value: string
        :returns: Interface key from topology file
        :rtype: string
        """
        interfaces = node[u"interfaces"]
        retval = None
        for if_key, if_val in interfaces.items():
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
        :type node: topology.NodeDict
        :type iface_name: string
        :returns: Interface key.
        :rtype: str
        """
        return Topology._get_interface_by_key_value(node, u"name", iface_name)

    @staticmethod
    def get_interface_by_link_name(node, link_name):
        """Return interface key of link on node.

        This method returns the interface name associated with a given link
        for a given node.

        :param node: The node topology dictionary.
        :param link_name: Name of the link that a interface is connected to.
        :type node: topology.NodeDict
        :type link_name: string
        :returns: Interface key of the interface connected to the given link.
        :rtype: str
        """
        return Topology._get_interface_by_key_value(node, u"link", link_name)

    def get_interfaces_by_link_names(self, node, link_names):
        """Return dictionary of dictionaries {"interfaceN", interface name}.

        This method returns the interface names associated with given links
        for a given node.

        :param node: The node topology directory.
        :param link_names: List of names of the link that a interface is
            connected to.
        :type node: topology.NodeDict
        :type link_names: list
        :returns: Dictionary of interface names that are connected to the given
            links.
        :rtype: dict
        """
        retval = dict()
        interface_number = 1
        for link_name in link_names:
            interface = self.get_interface_by_link_name(node, link_name)
            retval[f"interface{str(interface_number)}"] = \
                self.get_interface_name(node, interface)
            interface_number += 1
        return retval

    @staticmethod
    def get_interface_by_sw_index(node, sw_if_index):
        """Return interface name of link on node.

        This method returns the interface name associated with a software
        interface index assigned to the interface by vpp for a given node.

        :param node: The node topology dictionary.
        :param sw_if_index: sw_if_index of the link that a interface is
            connected to.
        :type node: topology.NodeDict
        :type sw_if_index: int
        :returns: Interface name of the interface connected to the given link.
        :rtype: str
        """
        return Topology._get_interface_by_key_value(
            node, u"vpp_sw_index", sw_if_index
        )

    @staticmethod
    def get_interface_sw_index(node, iface_key):
        """Get VPP sw_if_index for the interface using interface key.

        :param node: Node to get interface sw_if_index on.
        :param iface_key: Interface key from topology file, or sw_if_index.
        :type node: topology.NodeDict
        :type iface_key: str/int
        :returns: Return sw_if_index or None if not found.
        :rtype: int or None
        """
        try:
            if isinstance(iface_key, str):
                return node[u"interfaces"][iface_key].get(u"vpp_sw_index")
            # TODO: use only iface_key, do not use integer
            return int(iface_key)
        except (KeyError, ValueError):
            return None

    @staticmethod
    def get_interface_sw_index_by_name(node, iface_name):
        """Get VPP sw_if_index for the interface using interface name.

        :param node: Node to get interface sw_if_index on.
        :param iface_name: Interface name.
        :type node: topology.NodeDict
        :type iface_name: str
        :returns: Return sw_if_index or None if not found.
        :raises TypeError: If provided interface name is not a string.
        """
        try:
            if not isinstance(iface_name, str):
                raise TypeError(u"Interface name must be a string.")
            iface_key = Topology.get_interface_by_name(node, iface_name)
            return node[u"interfaces"][iface_key].get(u"vpp_sw_index")
        except (KeyError, ValueError):
            return None

    @staticmethod
    def get_interface_mtu(node, iface_key):
        """Get interface MTU.

        Returns physical layer MTU (max. size of Ethernet frame).
        :param node: Node to get interface MTU on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: MTU or None if not found.
        :rtype: int
        """
        try:
            return node[u"interfaces"][iface_key].get(u"mtu")
        except KeyError:
            return None

    @staticmethod
    def get_interface_name(node, iface_key):
        """Get interface name (retrieved from DUT/TG).

        Returns name in string format, retrieved from the node.
        :param node: Node to get interface name on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Interface name or None if not found.
        :rtype: str
        """
        try:
            return node[u"interfaces"][iface_key].get(u"name")
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
        :type node: topology.NodeDict
        :type interface: str or int
        :returns: Interface key.
        :rtype: str
        :raises TypeError: If provided with invalid interface argument.
        :raises RuntimeError: If the interface does not exist in topology.
        """

        if isinstance(interface, int):
            key = Topology.get_interface_by_sw_index(node, interface)
            if key is None:
                raise RuntimeError(
                    f"Interface with sw_if_index={interface} does not exist "
                    f"in topology."
                )
        elif interface in Topology.get_node_interfaces(node):
            key = interface
        elif interface in Topology.get_links({u"dut": node}):
            key = Topology.get_interface_by_link_name(node, interface)
        elif isinstance(interface, str):
            key = Topology.get_interface_by_name(node, interface)
            if key is None:
                raise RuntimeError(
                    f"Interface with key, name or link name \"{interface}\" "
                    f"does not exist in topology."
                )
        else:
            raise TypeError(
                u"Type of interface argument must be integer or string."
            )
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
        :type node: topology.NodeDict
        :type interface: str or int
        :type wanted_format: str
        :returns: Interface name, interface key or sw_if_index.
        :rtype: str or int
        :raises TypeError, ValueError: If provided with invalid arguments.
        :raises RuntimeError: If the interface does not exist in topology.
        """

        key = Topology.convert_interface_reference_to_key(node, interface)

        conversions = {
            u"key": lambda x, y: y,
            u"name": Topology.get_interface_name,
            u"sw_if_index": Topology.get_interface_sw_index
        }

        try:
            return conversions[wanted_format](node, key)
        except KeyError:
            raise ValueError(
                f"Unrecognized return value wanted: {wanted_format}."
                f"Valid options are key, name, sw_if_index"
            )

    @staticmethod
    def get_interface_numa_node(node, iface_key):
        """Get interface numa node.

        Returns physical relation to numa node, numa_id.

        :param node: Node to get numa id on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: numa node id, None if not available.
        :rtype: int
        """
        try:
            return node[u"interfaces"][iface_key].get(u"numa_node")
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
        :type node: topology.NodeDict
        :type iface_keys: strings
        :returns: Numa node of most given interfaces or 0.
        :rtype: int
        """
        numa_list = []
        for if_key in iface_keys:
            try:
                numa_list.append(node[u"interfaces"][if_key].get(u"numa_node"))
            except KeyError:
                pass

        numa_cnt_mc = Counter(numa_list).most_common()

        if numa_cnt_mc and numa_cnt_mc[0][0] != -1:
            return numa_cnt_mc[0][0]
        if len(numa_cnt_mc) > 1 and numa_cnt_mc[0][0] == -1:
            return numa_cnt_mc[1][0]
        return 0

    @staticmethod
    def get_interface_mac(node, iface_key):
        """Get MAC address for the interface.

        :param node: Node to get interface mac on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Return MAC or None if not found.
        """
        try:
            return node[u"interfaces"][iface_key].get(u"mac_address")
        except KeyError:
            return None

    @staticmethod
    def get_interface_ip4(node, iface_key):
        """Get IP4 address for the interface.

        :param node: Node to get interface mac on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Return IP4 or None if not found.
        """
        try:
            return node[u"interfaces"][iface_key].get(u"ip4_address")
        except KeyError:
            return None

    @staticmethod
    def get_interface_ip4_prefix_length(node, iface_key):
        """Get IP4 address prefix length for the interface.

        :param node: Node to get prefix length on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Prefix length from topology file or the default
            IP4 prefix length if not found.
        :rtype: int
        :raises: KeyError if iface_key is not found.
        """
        return node[u"interfaces"][iface_key].get(u"ip4_prefix_length", \
            Constants.DEFAULT_IP4_PREFIX_LENGTH)

    @staticmethod
    def get_adjacent_node_and_interface(nodes_info, node, iface_key):
        """Get node and interface adjacent to specified interface
        on local network.

        The nodes argument is ignored, operating on the global variable instead.

        :param nodes_info: Dictionary containing information on all nodes
            in topology.
        :param node: Node that contains specified interface.
        :param iface_key: Interface key from topology file.
        :type nodes_info: topology.NodesDict
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Return (node, interface_key) tuple or None if not found.
        :rtype: (dict, str)
        """
        link_name = None
        # get link name where the interface belongs to
        for if_key, if_val in node[u"interfaces"].items():
            if if_key == u"mgmt":
                continue
            if if_key == iface_key:
                link_name = if_val[u"link"]
                break

        if link_name is None:
            return None

        # find link
        for node_data in _get_nodes().values():
            # skip self
            if node_data[u"host"] == node[u"host"]:
                continue
            for if_key, if_val \
                    in node_data[u"interfaces"].items():
                if u"link" not in if_val:
                    continue
                if if_val[u"link"] == link_name:
                    return node_data, if_key
        return None

    @staticmethod
    def get_interface_pci_addr(node, iface_key):
        """Get interface PCI address.

        :param node: Node to get interface PCI address on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Return PCI address or None if not found.
        """
        try:
            return node[u"interfaces"][iface_key].get(u"pci_address")
        except KeyError:
            return None

    @staticmethod
    def get_interface_driver(node, iface_key):
        """Get interface driver.

        :param node: Node to get interface driver on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Return interface driver or None if not found.
        """
        try:
            return node[u"interfaces"][iface_key].get(u"driver")
        except KeyError:
            return None

    @staticmethod
    def get_interface_vlan(node, iface_key):
        """Get interface vlan.

        :param node: Node to get interface driver on.
        :param iface_key: Interface key from topology file.
        :type node: topology.NodeDict
        :type iface_key: str
        :returns: Return interface vlan or None if not found.
        """
        try:
            return node[u"interfaces"][iface_key].get(u"vlan")
        except KeyError:
            return None

    @staticmethod
    def get_node_interfaces(node):
        """Get all node interfaces.

        :param node: Node to get list of interfaces from.
        :type node: topology.NodeDict
        :returns: Return list of keys of all interfaces.
        :rtype: list
        """
        return node[u"interfaces"].keys()

    @staticmethod
    def get_node_link_mac(node, link_name):
        """Return interface mac address by link name.

        :param node: Node to get interface sw_if_index on.
        :param link_name: Link name.
        :type node: topology.NodeDict
        :type link_name: str
        :returns: MAC address string.
        :rtype: str
        """
        for port in node[u"interfaces"].values():
            if port.get(u"link") == link_name:
                return port.get(u"mac_address")
        return None

    @staticmethod
    def _get_node_active_link_names(node, filter_list=None):
        """Return list of link names that are other than mgmt links.

        :param node: Node topology dictionary.
        :param filter_list: Link filter criteria.
        :type node: topology.NodeDict
        :type filter_list: list of strings
        :returns: List of link names occupied by the node.
        :rtype: None or list of string
        """
        interfaces = node[u"interfaces"]
        link_names = []
        for interface in interfaces.values():
            if u"link" in interface:
                if (filter_list is not None) and (u"model" in interface):
                    for filt in filter_list:
                        if filt == interface[u"model"]:
                            link_names.append(interface[u"link"])
                elif (filter_list is not None) and (u"model" not in interface):
                    logger.trace(
                        f"Cannot apply filter on interface: {str(interface)}"
                    )
                else:
                    link_names.append(interface[u"link"])
        if not link_names:
            link_names = None
        return link_names

    def get_active_connecting_links(
            self, node1, node2, filter_list_node1=None, filter_list_node2=None):
        """Return list of link names that connect together node1 and node2.

        :param node1: Node topology dictionary.
        :param node2: Node topology dictionary.
        :param filter_list_node1: Link filter criteria for node1.
        :param filter_list_node2: Link filter criteria for node2.
        :type node1: topology.NodeDict
        :type node2: topology.NodeDict
        :type filter_list_node1: list of strings
        :type filter_list_node2: list of strings
        :returns: List of strings that represent connecting link names.
        :rtype: list
        """

        node1_links = self._get_node_active_link_names(
            node1, filter_list=filter_list_node1
        )
        node2_links = self._get_node_active_link_names(
            node2, filter_list=filter_list_node2
        )

        connecting_links = None
        if node1_links is None:
            logger.error(u"Unable to find active links for node1")
        elif node2_links is None:
            logger.error(u"Unable to find active links for node2")
        else:
            # Not using set operations, as we need deterministic order.
            connecting_links = [
                link for link in node1_links if link in node2_links
            ]

        return connecting_links

    def get_first_active_connecting_link(self, node1, node2):
        """Get first link connecting the two nodes together.

        :param node1: Connected node.
        :param node2: Connected node.
        :type node1: topology.NodeDict
        :type node2: topology.NodeDict
        :returns: Name of a link connecting the two nodes together.
        :rtype: str
        :raises RuntimeError: If no links are found.
        """
        connecting_links = self.get_active_connecting_links(node1, node2)
        if not connecting_links:
            raise RuntimeError(u"No links connecting the nodes were found")
        return connecting_links[0]

    def get_egress_interfaces_name_for_nodes(self, node1, node2):
        """Get egress interfaces on node1 for link with node2.

        :param node1: First node, node to get egress interface on.
        :param node2: Second node.
        :type node1: topology.NodeDict
        :type node2: topology.NodeDict
        :returns: Egress interfaces.
        :rtype: list
        """
        interfaces = list()
        links = self.get_active_connecting_links(node1, node2)
        if not links:
            raise RuntimeError(u"No link between nodes")
        for interface in node1[u"interfaces"].values():
            link = interface.get(u"link")
            if link is None:
                continue
            if link in links:
                continue
            name = interface.get(u"name")
            if name is None:
                continue
            interfaces.append(name)
        return interfaces

    def get_first_egress_interface_for_nodes(self, node1, node2):
        """Get first egress interface on node1 for link with node2.

        :param node1: First node, node to get egress interface name on.
        :param node2: Second node.
        :type node1: topology.NodeDict
        :type node2: topology.NodeDict
        :returns: Egress interface name.
        :rtype: str
        """
        interfaces = self.get_egress_interfaces_name_for_nodes(node1, node2)
        if not interfaces:
            raise RuntimeError(u"No egress interface for nodes")
        return interfaces[0]

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
        :type tgen: topology.NodeDict
        :type dut1: topology.NodeDict
        :type dut2: topology.NodeDict
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
        topology_links = {
            u"DUT1_DUT2_LINK": dut1_dut2_link,
            u"DUT1_TG_LINK": dut1_tg_link,
            u"DUT2_TG_LINK": dut2_tg_link,
            u"TG_TRAFFIC_LINKS": tg_traffic_links,
            u"DUT1_BD_LINKS": dut1_bd_links,
            u"DUT2_BD_LINKS": dut2_bd_links
        }
        return topology_links

    @staticmethod
    def is_tg_node(node):
        """Find out whether the node is TG.

        :param node: Node to examine.
        :type node: topology.NodeDict
        :returns: True if node is type of TG, otherwise False.
        :rtype: bool
        """
        return node[u"type"] == NodeType.TG

    @staticmethod
    def get_node_hostname(node):
        """Return host (hostname/ip address) of the node.

        :param node: Node created from topology.
        :type node: topology.NodeDict
        :returns: Hostname or IP address.
        :rtype: str
        """
        return node[u"host"]

    @staticmethod
    def get_node_arch(node):
        """Return arch of the node.
           Default to x86_64 if no arch present

        :param node: Node created from topology.
        :type node: topology.NodeDict
        :returns: Node architecture
        :rtype: str
        """
        try:
            return node[u"arch"]
        except KeyError:
            node[u"arch"] = u"x86_64"
            return u"x86_64"

    @staticmethod
    def get_cryptodev(node):
        """Return Crytodev configuration of the node.

        :param node: Node created from topology.
        :type node: topology.NodeDict
        :returns: Cryptodev configuration string.
        :rtype: str
        """
        try:
            return node[u"cryptodev"]
        except KeyError:
            return None

    @staticmethod
    def get_uio_driver(node):
        """Return uio-driver configuration of the node.

        :param node: Node created from topology.
        :type node: topology.NodeDict
        :returns: uio-driver configuration string.
        :rtype: str
        """
        try:
            return node[u"uio_driver"]
        except KeyError:
            return None

    @staticmethod
    def set_interface_numa_node(node, iface_key, numa_node_id):
        """Set interface numa_node location.

        :param node: Node to set numa_node on.
        :param iface_key: Interface key from topology file.
        :param numa_node_id: Num_node ID.
        :type node: topology.NodeDict
        :type iface_key: str
        :type numa_node_id: int
        :returns: Return iface_key or None if not found.
        :rtype: Optional[str]
        """
        try:
            node[u"interfaces"][iface_key][u"numa_node"] = numa_node_id
            # No KeyError, meaning it is safe to update real nodes.
            path = [u"interfaces", iface_key, u"numa_node"]
            Topology.add_node_item(
                node, numa_node_id, path, u"set_interface_numa_node"
            )
            return iface_key
        except KeyError:
            return None

    @staticmethod
    def add_new_socket(node, socket_type, socket_id, socket_path):
        """Add socket file of specific SocketType and ID to node.

        :param node: Node to add socket on.
        :param socket_type: Socket type.
        :param socket_id: Socket id, currently equals to unique node key.
        :param socket_path: Socket absolute path.
        :type node: topology.NodeDict
        :type socket_type: SocketType
        :type socket_id: str
        :type socket_path: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        path = [u"sockets", socket_type, socket_id]
        return Topology.add_node_item(
            node, socket_path, path, u"add_new_socket"
        )

    @staticmethod
    def del_node_socket_id(node, socket_type, socket_id):
        """Delete socket of specific SocketType and ID from node.

        :param node: Node to delete socket from.
        :param socket_type: Socket type.
        :param socket_id: Socket id, currently equals to unique node key.
        :type node: topology.NodeDict
        :type socket_type: SocketType
        :type socket_id: str
        :returns: Node structure after update, useful for subsequent calls.
        :rtype: topology.NodeDict
        """
        subnode = node[u"sockets"][socket_type]
        subnode.pop(socket_id)
        path = [u"sockets", socket_type]
        return Topology.add_node_item(
            node, subnode, path, u"del_node_socket_id"
        )

    @staticmethod
    def get_node_sockets(node, socket_type=None):
        """Get node socket files.

        :param node: Node to get sockets from.
        :param socket_type: Socket type or None for all sockets.
        :type node: topology.NodeDict
        :type socket_type: SocketType
        :returns: Node sockets or None if not found.
        :rtype: Optional[topology.SubNodeDict]
        """
        try:
            if socket_type:
                return node[u"sockets"][socket_type]
            return node[u"sockets"]
        except KeyError:
            return None

    @staticmethod
    def clean_sockets_on_all_nodes(nodes):
        """Remove temporary socket files from topology file.

        The nodes argument is ignored, operating on the global variable instead.

        :param nodes: SUT nodes.
        :type node: topology.NodesDict
        """
        new_nodes = {
            # Containers are disconnected and destroyed already.
            node_key: node_struct.excluding(u"sockets")
            for node_key, node_struct in _get_nodes().items()
        }
        _replace_nodes(new_nodes, reason="clean_sockets_on_all_nodes")
