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

"""Implements IPv4 RobotFramework keywords"""

from robot.api import logger as log
from robot.api.deco import keyword

from resources.libraries.python.topology import Topology
from resources.libraries.python.topology import NodeType
from resources.libraries.python.TrafficScriptExecutor\
    import TrafficScriptExecutor
from resources.libraries.python.IPv4Setup import get_node


class IPv4Util(object):
    """Implements keywords for IPv4 tests."""

    @staticmethod
    @keyword('From node "${node}" interface "${port}" ARP-ping '
             'IPv4 address "${ip_address}"')
    def arp_ping(node, interface, ip_address):
        log.debug('From node {} interface {} ARP-ping IPv4 address {}'.
                  format(Topology.get_node_hostname(node),
                         interface, ip_address))
        get_node(node).arp_ping(ip_address, interface)

    @staticmethod
    @keyword('Node "${node}" routes to IPv4 network "${network}" with prefix '
             'length "${prefix_length}" using interface "${interface}" via '
             '"${gateway}"')
    def set_route(node, network, prefix_length, interface, gateway):
        """See IPv4Node.set_route for more information.

        :param node:
        :param network:
        :param prefix_length:
        :param interface:
        :param gateway:
        :return:
        """
        log.debug('Node {} routes to network {} with prefix length {} '
                  'via {} interface {}'.format(Topology.get_node_hostname(node),
                                               network, prefix_length,
                                               gateway, interface))
        get_node(node).set_route(network, int(prefix_length),
                                 gateway, interface)

    @staticmethod
    @keyword('After ping is sent in topology "${nodes_info}" from node '
             '"${src_node}" interface "${src_port}" "${src_ip}" with '
             'destination IPv4 address "${dst_ip}" of node "${dst_node}" '
             'interface "${dst_port}" a ping response arrives and TTL is '
             'decreased by "${hops}"')
    def send_ping(nodes_info, src_node, src_port, src_ip, dst_ip, dst_node,
                  dst_port, hops):
        """Send IPv4 ping and wait for response.

        :param nodes_info: Dictionary containing information on all nodes
        in topology.
        :param src_node: Source node.
        :param src_port: Source interface.
        :param src_ip: Source ipv4 address.
        :param dst_ip: Destination ipv4 address.
        :param dst_node: Destination node.
        :param dst_port: Destination interface.
        :param hops: Number of hops between src_node and dst_node.
        """
        log.debug('After ping is sent from node "{}" interface "{}" '
                  'with destination IPv4 address of node "{}" interface "{}" '
                  'a ping response arrives and TTL is decreased by "${}"'.
                  format(Topology.get_node_hostname(src_node), src_port,
                         Topology.get_node_hostname(dst_node), dst_port, hops))
        dst_mac = None
        src_mac = Topology.get_interface_mac(src_node, src_port)
        if dst_node['type'] == NodeType.TG:
            dst_mac = Topology.get_interface_mac(src_node, src_port)
        _, adj_int = Topology.\
            get_adjacent_node_and_interface(nodes_info, src_node, src_port)
        first_hop_mac = adj_int['mac_address']
        args = '--src_if "{}" --src_mac "{}" --first_hop_mac "{}" ' \
               '--src_ip "{}" --dst_ip "{}" --hops "{}"'\
            .format(src_port, src_mac, first_hop_mac, src_ip, dst_ip, hops)
        if dst_node['type'] == NodeType.TG:
            args += ' --dst_if "{}" --dst_mac "{}"'.format(dst_port, dst_mac)
        TrafficScriptExecutor.run_traffic_script_on_node(
            "ipv4_ping_ttl_check.py", src_node, args)

    @staticmethod
    @keyword('Get IPv4 address prefix of node "${node}" interface "${port}" '
             'from "${nodes_addr}"')
    def get_ip_addr_prefix_length(node, port, nodes_addr):
        """ Get IPv4 address prefix for specified interface.

        :param node: Node dictionary.
        :param port: Interface name.
        :return: IPv4 prefix length
        """
        for net in nodes_addr.values():
            for p in net['ports'].values():
                if p['node'] == node['host'] and p['if'] == port:
                    return net['prefix']

        raise Exception('Subnet not found for node {n} port {p}'.
                        format(n=node['host'], p=port))

    @staticmethod
    @keyword('Get IPv4 subnet of node "${node}" interface "${port}" from '
             '"${nodes_addr}"')
    def get_ip_addr_subnet(node, port, nodes_addr):
        """ Get IPv4 subnet of specified interface.

        :param node: Node dictionary.
        :param port: Interface name.
        :return: IPv4 subnet of 'str' type
        """
        for net in nodes_addr.values():
            for p in net['ports'].values():
                if p['node'] == node['host'] and p['if'] == port:
                    return net['net_addr']

        raise Exception('Subnet not found for node {n} port {p}'.
                        format(n=node['host'], p=port))

    @staticmethod
    @keyword('Flush IPv4 addresses "${port}" "${node}"')
    def flush_ip_addresses(port, node):
        """See IPv4Node.flush_ip_addresses for more information.

        :param port:
        :param node:
        :return:
        """
        get_node(node).flush_ip_addresses(port)

    @staticmethod
    def get_link_address(link, nodes_addr):
        """Get link IPv4 address.

        :param link: Link name.
        :param nodes_addr: Available nodes IPv4 adresses.
        :type link: str
        :type nodes_addr: dict
        :return: Link IPv4 address.
        :rtype: str
        """
        net = nodes_addr.get(link)
        if net is None:
            raise ValueError('Link "{0}" not found'.format(link))
        return net.get('net_addr')

    @staticmethod
    def get_link_prefix(link, nodes_addr):
        """Get link IPv4 address prefix.

        :param link: Link name.
        :param nodes_addr: Available nodes IPv4 adresses.
        :type link: str
        :type nodes_addr: dict
        :return: Link IPv4 address prefix.
        :rtype: int
        """
        net = nodes_addr.get(link)
        if net is None:
            raise ValueError('Link "{0}" not found'.format(link))
        return net.get('prefix')
