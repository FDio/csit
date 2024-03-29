# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""Path utilities library for nodes in the topology."""

from resources.libraries.python.topology import Topology


class NodePath:
    """Path utilities for nodes in the topology.

    :Example:

    node1--link1-->node2--link2-->node3--link3-->node2--link4-->node1
    RobotFramework:
    | Library | resources/libraries/python/NodePath.py

    | Path test
    | | [Arguments] | ${node1} | ${node2} | ${node3}
    | | Append Node | ${nodes1}
    | | Append Node | ${nodes2}
    | | Append Nodes | ${nodes3} | ${nodes2}
    | | Append Node | ${nodes1}
    | | Compute Path | ${FALSE}
    | | ${first_int} | ${node}= | First Interface
    | | ${last_int} | ${node}= | Last Interface
    | | ${first_ingress} | ${node}= | First Ingress Interface
    | | ${last_egress} | ${node}= | Last Egress Interface
    | | ${next} | ${node}= | Next Interface

    Python:
    >>> from NodePath import NodePath
    >>> path = NodePath()
    >>> path.append_node(node1)
    >>> path.append_node(node2)
    >>> path.append_nodes(node3, node2)
    >>> path.append_node(node1)
    >>> path.compute_path()
    >>> (interface, node) = path.first_interface()
    >>> (interface, node) = path.last_interface()
    >>> (interface, node) = path.first_ingress_interface()
    >>> (interface, node) = path.last_egress_interface()
    >>> (interface, node) = path.next_interface()
    """

    def __init__(self):
        self._nodes = []
        self._nodes_filter = []
        self._links = []
        self._path = []
        self._path_iter = []

    def append_node(self, node, filter_list=None):
        """Append node to the path.

        :param node: Node to append to the path.
        :param filter_list: Filter criteria list.
        :type node: dict
        :type filter_list: list of strings
        """
        self._nodes_filter.append(filter_list)
        self._nodes.append(node)

    def append_nodes(self, *nodes, filter_list=None):
        """Append nodes to the path.

        :param nodes: Nodes to append to the path.
        :param filter_list: Filter criteria list.
        :type nodes: dict
        :type filter_list: list of strings

        .. note:: Node order does matter.
        """
        for node in nodes:
            self.append_node(node, filter_list=filter_list)

    def clear_path(self):
        """Clear path."""
        self._nodes = []
        self._nodes_filter = []
        self._links = []
        self._path = []
        self._path_iter = []

    def compute_path(self, always_same_link=True, topo_has_dut=True):
        """Compute path for added nodes.

        .. note:: First add at least two nodes to the topology.

        :param always_same_link: If True use always same link between two nodes
            in path. If False use different link (if available)
            between two nodes if one link was used before.
        :param topo_has_dut: If False we want to test back to back test on TG.
        :type always_same_link: bool
        :type topo_has_dut: bool
        :raises RuntimeError: If not enough nodes for path.
        """
        nodes = self._nodes
        if len(nodes) < 2 and topo_has_dut:
            raise RuntimeError(u"Not enough nodes to compute path")

        for idx in range(0, len(nodes) - 1):
            topo = Topology()
            node1 = nodes[idx]
            n1_list = self._nodes_filter[idx]
            if topo_has_dut:
                node2 = nodes[idx + 1]
                n2_list = self._nodes_filter[idx + 1]
            else:
                node2 = node1
                n2_list = n1_list

            links = topo.get_active_connecting_links(
                node1, node2, filter_list_node1=n1_list,
                filter_list_node2=n2_list
            )
            if not links:
                raise RuntimeError(
                    f"No link between {node1[u'host']} and {node2[u'host']}"
                )

            # Not using set operations, as we need deterministic order.
            if always_same_link:
                l_set = [link for link in links if link in self._links]
            else:
                l_set = [link for link in links if link not in self._links]
                if not l_set:
                    raise RuntimeError(
                        f"No free link between {node1[u'host']} and "
                        f"{node2[u'host']}, all links already used"
                    )

            if not l_set:
                link = links[0]
            else:
                link = l_set[0]

            self._links.append(link)

            use_subsequent = not topo_has_dut
            interface1 = topo.get_interface_by_link_name(node1, link)
            interface2 = topo.get_interface_by_link_name(node2, link,
                                                         use_subsequent)
            self._path.append((interface1, node1))
            self._path.append((interface2, node2))

        self._path_iter.extend(self._path)
        self._path_iter.reverse()

    def next_interface(self):
        """Path interface iterator.

        :returns: Interface and node or None if not next interface.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path_iter:
            return None, None
        return self._path_iter.pop()

    def first_interface(self):
        """Return first interface on the path.

        :returns: Interface and node.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path:
            raise RuntimeError(u"No path for topology")
        return self._path[0]

    def last_interface(self):
        """Return last interface on the path.

        :returns: Interface and node.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path:
            raise RuntimeError(u"No path for topology")
        return self._path[-1]

    def first_ingress_interface(self):
        """Return first ingress interface on the path.

        :returns: Interface and node.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path:
            raise RuntimeError(u"No path for topology")
        return self._path[1]

    def last_egress_interface(self):
        """Return last egress interface on the path.

        :returns: Interface and node.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path:
            raise RuntimeError(u"No path for topology")
        return self._path[-2]

    def compute_circular_topology(
            self, nodes, filter_list=None, nic_pfs=1,
            always_same_link=False, topo_has_tg=True, topo_has_dut=True):
        """Return computed circular path.

        :param nodes: Nodes to append to the path.
        :param filter_list: Filter criteria list.
        :param nic_pfs: Number of PF of NIC.
        :param always_same_link: If True use always same link between two nodes
            in path. If False use different link (if available)
            between two nodes if one link was used before.
        :param topo_has_tg: If True, the topology has a TG node. If False,
            the topology consists entirely of DUT nodes.
        :param topo_has_dut: If True, the topology has a DUT node(s). If False,
            the topology consists entirely of TG nodes.
        :type nodes: dict
        :type filter_list: list of strings
        :type nic_pfs: int
        :type always_same_link: bool
        :type topo_has_tg: bool
        :type topo_has_dut: bool
        :returns: Topology information dictionary.
        :rtype: dict
        :raises RuntimeError: If unsupported combination of parameters.
        """
        t_dict = dict()
        t_dict[u"hosts"] = set()
        if topo_has_dut:
            duts = [key for key in nodes if u"DUT" in key]
            for host in [nodes[dut][u"host"] for dut in duts]:
                t_dict[u"hosts"].add(host)
            t_dict[u"duts"] = duts
            t_dict[u"duts_count"] = len(duts)
            t_dict[u"int"] = u"pf"

        for _ in range(0, nic_pfs // 2):
            if topo_has_tg:
                if topo_has_dut:
                    self.append_node(nodes[u"TG"])
                else:
                    self.append_node(nodes[u"TG"], filter_list=filter_list)
            if topo_has_dut:
                for dut in duts:
                    self.append_node(nodes[dut], filter_list=filter_list)
        if topo_has_tg:
            t_dict[u"hosts"].add(nodes[u"TG"][u"host"])
            if topo_has_dut:
                self.append_node(nodes[u"TG"])
            else:
                self.append_node(nodes[u"TG"], filter_list=filter_list)
        self.compute_path(always_same_link, topo_has_dut)

        n_idx = 0 # node index
        t_idx = 1 # TG interface index
        d_idx = 0 # DUT interface index
        prev_host = None
        while True:
            interface, node = self.next_interface()
            if not interface:
                break
            if topo_has_tg and node.get(u"type") == u"TG":
                n_pfx = f"TG" # node prefix
                p_pfx = f"pf{t_idx}" # physical interface prefix
                i_pfx = f"if{t_idx}" # [backwards compatible] interface prefix
                n_idx = 0
                t_idx = t_idx + 1
            elif topo_has_tg and topo_has_dut:
                # Each node has 2 interfaces, starting with 1
                # Calculate prefixes appropriately for current
                # path topology nomenclature:
                #   tg1_if1 -> dut1_if1 -> dut1_if2 ->
                #        [dut2_if1 -> dut2_if2 ...] -> tg1_if2
                n_pfx = f"DUT{n_idx // 2 + 1}"
                p_pfx = f"pf{d_idx % 2 + t_idx - 1}"
                i_pfx = f"if{d_idx % 2 + t_idx - 1}"
                n_idx = n_idx + 1
                d_idx = d_idx + 1
            elif not topo_has_tg and always_same_link:
                this_host = node.get(u"host")
                if prev_host != this_host:
                    # When moving to a new host in the path,
                    # increment the node index (n_idx) and
                    # reset DUT interface index (d_idx) to 1.
                    n_idx = n_idx + 1
                    d_idx = 1
                n_pfx = f"DUT{n_idx}"
                p_pfx = f"pf{d_idx}"
                i_pfx = f"if{d_idx}"
                d_idx = d_idx + 1
            else:
                raise RuntimeError(u"Unsupported combination of paramters")

            t_dict[f"{n_pfx}"] = node
            t_dict[f"{n_pfx}_{p_pfx}"] = [interface]
            t_dict[f"{n_pfx}_{p_pfx}_mac"] = \
                [Topology.get_interface_mac(node, interface)]
            t_dict[f"{n_pfx}_{p_pfx}_vlan"] = \
                [Topology.get_interface_vlan(node, interface)]
            t_dict[f"{n_pfx}_{p_pfx}_pci"] = \
                [Topology.get_interface_pci_addr(node, interface)]
            t_dict[f"{n_pfx}_{p_pfx}_ip4_addr"] = \
                [Topology.get_interface_ip4(node, interface)]
            t_dict[f"{n_pfx}_{p_pfx}_ip4_prefix"] = \
                [Topology.get_interface_ip4_prefix_length(node, interface)]
            if f"{n_pfx}_pf_pci" not in t_dict:
                t_dict[f"{n_pfx}_pf_pci"] = []
            t_dict[f"{n_pfx}_pf_pci"].append(
                Topology.get_interface_pci_addr(node, interface))
            if f"{n_pfx}_pf_keys" not in t_dict:
                t_dict[f"{n_pfx}_pf_keys"] = []
            t_dict[f"{n_pfx}_pf_keys"].append(interface)
            # Backward compatibility below
            t_dict[f"{n_pfx.lower()}_{i_pfx}"] = interface
            t_dict[f"{n_pfx.lower()}_{i_pfx}_mac"] = \
                Topology.get_interface_mac(node, interface)
            t_dict[f"{n_pfx.lower()}_{i_pfx}_pci"] = \
                Topology.get_interface_pci_addr(node, interface)
            t_dict[f"{n_pfx.lower()}_{i_pfx}_ip4_addr"] = \
                Topology.get_interface_ip4(node, interface)
            t_dict[f"{n_pfx.lower()}_{i_pfx}_ip4_prefix"] = \
                Topology.get_interface_ip4_prefix_length(node, interface)

        self.clear_path()
        return t_dict
