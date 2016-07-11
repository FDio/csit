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

"""Path utilities library for nodes in the topology."""

from resources.libraries.python.topology import Topology


class NodePath(object):
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

    def append_nodes(self, *nodes):
        """Append nodes to the path.

        :param nodes: Nodes to append to the path.
        :type nodes: dict

        .. note:: Node order does matter.
        """
        for node in nodes:
            self.append_node(node)

    def clear_path(self):
        """Clear path."""
        self._nodes = []
        self._nodes_filter = []
        self._links = []
        self._path = []
        self._path_iter = []

    def compute_path(self, always_same_link=True):
        """Compute path for added nodes.

        :param always_same_link: If True use always same link between two nodes
        in path. If False use different link (if available) between two
        nodes if one link was used before.
        :type always_same_link: bool

        .. note:: First add at least two nodes to the topology.
        """
        nodes = self._nodes
        if len(nodes) < 2:
            raise RuntimeError('Not enough nodes to compute path')

        for idx in range(0, len(nodes) - 1):
            topo = Topology()
            node1 = nodes[idx]
            node2 = nodes[idx + 1]
            n1_list = self._nodes_filter[idx]
            n2_list = self._nodes_filter[idx + 1]
            links = topo.get_active_connecting_links(node1, node2,
                                                     filter_list_node1=n1_list,
                                                     filter_list_node2=n2_list)
            if not links:
                raise RuntimeError('No link between {0} and {1}'.format(
                    node1['host'], node2['host']))

            if always_same_link:
                l_set = set(links).intersection(self._links)
            else:
                l_set = set(links).difference(self._links)
                if not l_set:
                    raise RuntimeError(
                        'No free link between {0} and {1}, all links already '
                        'used'.format(node1['host'], node2['host']))

            if not l_set:
                link = links.pop()
            else:
                link = l_set.pop()

            self._links.append(link)
            interface1 = topo.get_interface_by_link_name(node1, link)
            interface2 = topo.get_interface_by_link_name(node2, link)
            self._path.append((interface1, node1))
            self._path.append((interface2, node2))

        self._path_iter.extend(self._path)
        self._path_iter.reverse()

    def next_interface(self):
        """Path interface iterator.

        :return: Interface and node or None if not next interface.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path_iter:
            return None, None
        else:
            return self._path_iter.pop()

    def first_interface(self):
        """Return first interface on the path.

        :return: Interface and node.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path:
            raise RuntimeError('No path for topology')
        return self._path[0]

    def last_interface(self):
        """Return last interface on the path.

        :return: Interface and node.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path:
            raise RuntimeError('No path for topology')
        return self._path[-1]

    def first_ingress_interface(self):
        """Return first ingress interface on the path.

        :return: Interface and node.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path:
            raise RuntimeError('No path for topology')
        return self._path[1]

    def last_egress_interface(self):
        """Return last egress interface on the path.

        :return: Interface and node.
        :rtype: tuple (str, dict)

        .. note:: Call compute_path before.
        """
        if not self._path:
            raise RuntimeError('No path for topology')
        return self._path[-2]
