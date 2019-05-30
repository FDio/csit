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

"""Implements IPv4 RobotFramework keywords"""

from robot.api import logger as log
from robot.api.deco import keyword

from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.ssh import exec_cmd


class IPv4Util(object):
    """Implements keywords for IPv4 tests."""

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
        :returns: IPv4 prefix length.
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
        :returns: IPv4 subnet.
        :rtype: str
        """
        for net in nodes_addr.values():
            for net_port in net['ports'].values():
                if net_port['node'] == node['host'] and net_port['if'] == port:
                    return net['net_addr']

        raise Exception('Subnet not found for node {n} port {p}'.
                        format(n=node['host'], p=port))

    @staticmethod
    def get_link_address(link, nodes_addr):
        """Get link IPv4 address.

        :param link: Link name.
        :param nodes_addr: Available nodes IPv4 addresses.
        :type link: str
        :type nodes_addr: dict
        :returns: Link IPv4 address.
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
        :returns: Link IPv4 address prefix.
        :rtype: int
        """
        net = nodes_addr.get(link)
        if net is None:
            raise ValueError('Link "{0}" not found'.format(link))
        return net.get('prefix')

    @staticmethod
    def send_ping_from_node_to_dst(node, destination, namespace=None,
                                   ping_count=3, interface=None):
        """Send a ping from node to destination. Optionally, you can define a
        namespace and interface from where to send a ping.

        :param node: Node to start ping on.
        :param destination: IPv4 address where to send ping.
        :param namespace: Namespace to send ping from. Optional
        :param ping_count: Number of pings to send. Default 3
        :param interface: Interface from where to send ping. Optional
        :type node: dict
        :type destination: str
        :type namespace: str
        :type ping_count: int
        :type interface: str
        :raises RuntimeError: If no response for ping, raise error
        """
        if namespace is not None:
            cmd = 'ip netns exec {0} ping -c{1} {2}'.format(
                namespace, ping_count, destination)
        elif interface is not None:
            cmd = 'ping -I {0} -c{1} {2}'.format(
                interface, ping_count, destination)
        else:
            cmd = 'ping -c{0} {1}'.format(ping_count, destination)
        ret_code, _, _ = exec_cmd(node, cmd, sudo=True)
        if ret_code != 0:
            raise RuntimeError("Ping Not Successful")

    @staticmethod
    def set_linux_interface_arp(node, interface, ip_addr, mac, namespace=None):
        """Set arp on interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param ip_addr: IP address for ARP entry.
        :param mac: MAC address.
        :param namespace: Execute command in namespace. Optional
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type mac: str
        :type namespace: str
        :raises RuntimeError: Could not set ARP properly.
        """
        if namespace is not None:
            cmd = 'ip netns exec {} arp -i {} -s {} {}'.format(
                namespace, interface, ip_addr, mac)
        else:
            cmd = 'arp -i {} -s {} {}'.format(interface, ip_addr, mac)
        ret_code, _, stderr = exec_cmd(node, cmd, sudo=True)
        if ret_code != 0:
            raise RuntimeError("Arp set not successful, reason:{}".
                               format(stderr))

    @staticmethod
    def vpp_show_ip_table(node):
        """Get IP FIB table data from a VPP node.

        :param node: VPP node.
        :type node: dict
        """
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template("show_ip_fib.vat")
