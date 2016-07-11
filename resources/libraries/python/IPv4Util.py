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
from resources.libraries.python.IPv4Setup import get_node
from resources.libraries.python.ssh import exec_cmd


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
    def set_interface_address(node, interface, address, prefix_length):
        """See IPv4Node.set_ip for more information.

        :param node: Node where IP address should be set to.
        :param interface: Interface name.
        :param address: IP address.
        :param prefix_length: Prefix length.
        :type node: dict
        :type interface: str
        :type address: str
        :type prefix_length: int
        """
        log.debug('Node {} interface {} has IPv4 address {} with prefix '
                  'length {}'.format(Topology.get_node_hostname(node),
                                     interface, address, prefix_length))
        get_node(node).set_ip(interface, address, int(prefix_length))

    @staticmethod
    def set_route(node, network, prefix_length, interface, gateway):
        """See IPv4Node.set_route for more information.

        :param node: Node where IP address should be set to.
        :param network: IP network.
        :param prefix_length: Prefix length.
        :param interface: Interface name.
        :param gateway: Gateway.
        :type node: dict
        :type network: str
        :type prefix_length: int
        :type interface: str
        :type gateway: str
        """
        log.debug('Node {} routes to network {} with prefix length {} '
                  'via {} interface {}'.format(Topology.get_node_hostname(node),
                                               network, prefix_length,
                                               gateway, interface))
        get_node(node).set_route(network, int(prefix_length),
                                 gateway, interface)

    @staticmethod
    @keyword('Get IPv4 address prefix of node "${node}" interface "${port}" '
             'from "${nodes_addr}"')
    def get_ip_addr_prefix_length(node, port, nodes_addr):
        """ Get IPv4 address prefix for specified interface.

        :param node: Node dictionary.
        :param port: Interface name.
        :param nodes_addr: Available nodes IPv4 addresses.
        :type node: dict
        :type port: str
        :type nodes_addr: dict
        :return: IPv4 prefix length.
        :rtype: int
        """
        for net in nodes_addr.values():
            for net_port in net['ports'].values():
                if net_port['node'] == node['host'] and net_port['if'] == port:
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
        :param nodes_addr: Available nodes IPv4 addresses.
        :type node: dict
        :type port: int
        :type nodes_addr: dict
        :return: IPv4 subnet.
        :rtype: str
        """
        for net in nodes_addr.values():
            for net_port in net['ports'].values():
                if net_port['node'] == node['host'] and net_port['if'] == port:
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
        :param nodes_addr: Available nodes IPv4 addresses.
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
        :param nodes_addr: Available nodes IPv4 addresses.
        :type link: str
        :type nodes_addr: dict
        :return: Link IPv4 address prefix.
        :rtype: int
        """
        net = nodes_addr.get(link)
        if net is None:
            raise ValueError('Link "{0}" not found'.format(link))
        return net.get('prefix')

    @staticmethod
    def send_ping_from_node_to_dst(node, destination, namespace=None,
                                   ping_count=3):
        """Send a ping from node to destination. Optionally, you can define a
        namespace from where to send a ping.

        :param node: Node to start ping on.
        :param destination: IPv4 address where to send ping.
        :param namespace: Namespace to send ping from.
        :param ping_count: Number of pings to send.
        :type node: dict
        :type destination: str
        :type namespace: str
        :type ping_count: int
        :raises RuntimeError: If no response for ping, raise error
        """
        if namespace is not None:
            cmd = 'ip netns exec {0} ping -c{1} {2}'.format(
                namespace, ping_count, destination)
        else:
            cmd = 'ping -c{0} {1}'.format(ping_count, destination)
        ret_code, _, _ = exec_cmd(node, cmd, sudo=True)
        if ret_code != 0:
            raise RuntimeError("Ping Not Successful")
