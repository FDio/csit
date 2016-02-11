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

from socket import inet_ntoa
from struct import pack
from abc import ABCMeta, abstractmethod
import copy

from robot.api import logger as log
from robot.api.deco import keyword
from robot.utils.asserts import assert_not_equal

import resources.libraries.python.ssh as ssh
from resources.libraries.python.topology import Topology
from resources.libraries.python.topology import NodeType
from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.TrafficScriptExecutor\
    import TrafficScriptExecutor


class IPv4Node(object):
    """Abstract class of a node in a topology."""
    __metaclass__ = ABCMeta

    def __init__(self, node_info):
        self.node_info = node_info

    @staticmethod
    def _get_netmask(prefix_length):
        bits = 0xffffffff ^ (1 << 32 - prefix_length) - 1
        return inet_ntoa(pack('>I', bits))

    @abstractmethod
    def set_ip(self, interface, address, prefix_length):
        """Configure IPv4 address on interface

        :param interface: interface name
        :param address:
        :param prefix_length:
        :type interface: str
        :type address: str
        :type prefix_length: int
        :return: nothing
        """
        pass

    @abstractmethod
    def set_interface_state(self, interface, state):
        """Set interface state

        :param interface: interface name string
        :param state: one of following values: "up" or "down"
        :return: nothing
        """
        pass

    @abstractmethod
    def set_route(self, network, prefix_length, gateway, interface):
        """Configure IPv4 route

        :param network: network IPv4 address
        :param prefix_length: mask length
        :param gateway: IPv4 address of the gateway
        :param interface: interface name
        :type network: str
        :type prefix_length: int
        :type gateway: str
        :type interface: str
        :return: nothing
        """
        pass

    @abstractmethod
    def unset_route(self, network, prefix_length, gateway, interface):
        """Remove specified IPv4 route

        :param network: network IPv4 address
        :param prefix_length: mask length
        :param gateway: IPv4 address of the gateway
        :param interface: interface name
        :type network: str
        :type prefix_length: int
        :type gateway: str
        :type interface: str
        :return: nothing
        """
        pass

    @abstractmethod
    def flush_ip_addresses(self, interface):
        """Flush all IPv4 addresses from specified interface

        :param interface: interface name
        :type interface: str
        :return: nothing
        """
        pass

    @abstractmethod
    def ping(self, destination_address, source_interface):
        """Send an ICMP request to destination node

        :param destination_address: address to send the ICMP request
        :param source_interface:
        :type destination_address: str
        :type source_interface: str
        :return: nothing
        """
        pass


class Tg(IPv4Node):
    """Traffic generator node"""
    def __init__(self, node_info):
        super(Tg, self).__init__(node_info)

    def _execute(self, cmd):
        return ssh.exec_cmd_no_error(self.node_info, cmd)

    def _sudo_execute(self, cmd):
        return ssh.exec_cmd_no_error(self.node_info, cmd, sudo=True)

    def set_ip(self, interface, address, prefix_length):
        cmd = 'ip -4 addr flush dev {}'.format(interface)
        self._sudo_execute(cmd)
        cmd = 'ip addr add {}/{} dev {}'.format(address, prefix_length,
                                                interface)
        self._sudo_execute(cmd)

    # TODO: not ipv4-specific, move to another class
    def set_interface_state(self, interface, state):
        cmd = 'ip link set {} {}'.format(interface, state)
        self._sudo_execute(cmd)

    def set_route(self, network, prefix_length, gateway, interface):
        netmask = self._get_netmask(prefix_length)
        cmd = 'route add -net {} netmask {} gw {}'.\
            format(network, netmask, gateway)
        self._sudo_execute(cmd)

    def unset_route(self, network, prefix_length, gateway, interface):
        self._sudo_execute('ip route delete {}/{}'.
                           format(network, prefix_length))

    def arp_ping(self, destination_address, source_interface):
        self._sudo_execute('arping -c 1 -I {} {}'.format(source_interface,
                                                         destination_address))

    def ping(self, destination_address, source_interface):
        self._execute('ping -c 1 -w 5 -I {} {}'.format(source_interface,
                                                       destination_address))

    def flush_ip_addresses(self, interface):
        self._sudo_execute('ip addr flush dev {}'.format(interface))


class Dut(IPv4Node):
    """Device under test"""
    def __init__(self, node_info):
        super(Dut, self).__init__(node_info)

    def get_sw_if_index(self, interface):
        """Get sw_if_index of specified interface from current node

        :param interface: interface name
        :type interface: str
        :return: sw_if_index of 'int' type
        """
        return Topology().get_interface_sw_index(self.node_info, interface)

    def exec_vat(self, script, **args):
        """Wrapper for VAT executor.

        :param script: script to execute
        :param args: parameters to the script
        :type script: str
        :type args: dict
        :return: nothing
        """
        # TODO: check return value
        VatExecutor.cmd_from_template(self.node_info, script, **args)

    def set_arp(self, interface, ip_address, mac_address):
        """Set entry in ARP cache.

        :param interface: Interface name.
        :param ip_address: IP address.
        :param mac_address: MAC address.
        :type interface: str
        :type ip_address: str
        :type mac_address: str
        """
        self.exec_vat('add_ip_neighbor.vat',
                      sw_if_index=self.get_sw_if_index(interface),
                      ip_address=ip_address, mac_address=mac_address)

    def set_ip(self, interface, address, prefix_length):
        self.exec_vat('add_ip_address.vat',
                      sw_if_index=self.get_sw_if_index(interface),
                      address=address, prefix_length=prefix_length)

    def set_interface_state(self, interface, state):
        if state == 'up':
            state = 'admin-up link-up'
        elif state == 'down':
            state = 'admin-down link-down'
        else:
            raise Exception('Unexpected interface state: {}'.format(state))

        self.exec_vat('set_if_state.vat',
                      sw_if_index=self.get_sw_if_index(interface), state=state)

    def set_route(self, network, prefix_length, gateway, interface):
        sw_if_index = self.get_sw_if_index(interface)
        self.exec_vat('add_route.vat',
                      network=network, prefix_length=prefix_length,
                      gateway=gateway, sw_if_index=sw_if_index)

    def unset_route(self, network, prefix_length, gateway, interface):
        self.exec_vat('del_route.vat', network=network,
                      prefix_length=prefix_length, gateway=gateway,
                      sw_if_index=self.get_sw_if_index(interface))

    def arp_ping(self, destination_address, source_interface):
        pass

    def flush_ip_addresses(self, interface):
        self.exec_vat('flush_ip_addresses.vat',
                      sw_if_index=self.get_sw_if_index(interface))

    def ping(self, destination_address, source_interface):
        pass


def get_node(node_info):
    """Creates a class instance derived from Node based on type.

    :param node_info: dictionary containing information on nodes in topology
    :return: Class instance that is derived from Node
    """
    if node_info['type'] == NodeType.TG:
        return Tg(node_info)
    elif node_info['type'] == NodeType.DUT:
        return Dut(node_info)
    else:
        raise NotImplementedError('Node type "{}" unsupported!'.
                                  format(node_info['type']))


def get_node_hostname(node_info):
    """Get string identifying specifed node.

    :param node_info: Node in the topology.
    :type node_info: Dict
    :return: String identifying node.
    """
    return node_info['host']


class IPv4Util(object):
    """Implements keywords for IPv4 tests."""

    ADDRESSES = {}   # holds configured IPv4 addresses
    PREFIXES = {}  # holds configured IPv4 addresses' prefixes
    SUBNETS = {}  # holds configured IPv4 addresses' subnets

    """
    Helper dictionary used when setting up ipv4 addresses in topology

    Example value:
    'link1': {  b'port1': {b'addr': b'192.168.3.1'},
                b'port2': {b'addr': b'192.168.3.2'},
                b'prefix': 24,
                b'subnet': b'192.168.3.0'}
    """
    topology_helper = None

    @staticmethod
    def setup_arp_on_all_duts(nodes_info):
        """For all DUT nodes extract MAC and IP addresses of adjacent interfaces
        from topology and use them to setup ARP entries.

        :param nodes_info: Dictionary containing information on all nodes
        in topology.
        :type nodes_info: dict
        """
        for node in nodes_info.values():
            if node['type'] == NodeType.TG:
                continue
            for interface, interface_data in node['interfaces'].iteritems():
                if interface == 'mgmt':
                    continue
                interface_name = interface_data['name']
                adj_node, adj_int = Topology.\
                    get_adjacent_node_and_interface(nodes_info, node,
                                                    interface_name)
                ip_address = IPv4Util.get_ip_addr(adj_node, adj_int['name'])
                mac_address = adj_int['mac_address']
                get_node(node).set_arp(interface_name, ip_address, mac_address)

    @staticmethod
    def next_address(subnet):
        """Get next unused IPv4 address from a subnet

        :param subnet: holds available IPv4 addresses
        :return: tuple (ipv4_address, prefix_length)
        """
        for i in range(1, 4):
            # build a key and try to get it from address dictionary
            interface = 'port{}'.format(i)
            if interface in subnet:
                addr = subnet[interface]['addr']
                del subnet[interface]
                return addr, subnet['prefix']
        raise Exception('Not enough ipv4 addresses in subnet')

    @staticmethod
    def next_network(nodes_addr):
        """Get next unused network from dictionary

        :param nodes_addr: dictionary of available networks
        :return: dictionary describing an IPv4 subnet with addresses
        """
        assert_not_equal(len(nodes_addr), 0, 'Not enough networks')
        _, subnet = nodes_addr.popitem()
        return subnet

    @staticmethod
    def configure_ipv4_addr_on_node(node, nodes_addr):
        """Configure IPv4 address for all non-management interfaces
        on a node in topology.

        :param node: dictionary containing information about node
        :param nodes_addr: dictionary containing IPv4 addresses
        :return:
        """
        for interface, interface_data in node['interfaces'].iteritems():
            if interface == 'mgmt':
                continue
            if interface_data['link'] not in IPv4Util.topology_helper:
                IPv4Util.topology_helper[interface_data['link']] = \
                    IPv4Util.next_network(nodes_addr)

            network = IPv4Util.topology_helper[interface_data['link']]
            address, prefix = IPv4Util.next_address(network)

            if node['type'] != NodeType.TG:
                get_node(node).set_ip(interface_data['name'], address, prefix)
                get_node(node).set_interface_state(interface_data['name'], 'up')

            key = (get_node_hostname(node), interface_data['name'])
            IPv4Util.ADDRESSES[key] = address
            IPv4Util.PREFIXES[key] = prefix
            IPv4Util.SUBNETS[key] = network['subnet']

    @staticmethod
    def dut_nodes_setup_ipv4_addresses(nodes_info, nodes_addr):
        """Configure IPv4 addresses on all non-management interfaces for each
        node in nodes_info if node type is not traffic generator

        :param nodes_info: dictionary containing information on all nodes
        in topology
        :param nodes_addr: dictionary containing IPv4 addresses
        :return: nothing
        """
        IPv4Util.topology_helper = {}
        # make a deep copy of nodes_addr because of modifications
        nodes_addr_copy = copy.deepcopy(nodes_addr)
        for node in nodes_info.values():
            IPv4Util.configure_ipv4_addr_on_node(node, nodes_addr_copy)

    @staticmethod
    def nodes_clear_ipv4_addresses(nodes):
        """Clear all addresses from all nodes in topology

        :param nodes: dictionary containing information on all nodes
        :return: nothing
        """
        for node in nodes.values():
            for interface, interface_data in node['interfaces'].iteritems():
                if interface == 'mgmt':
                    continue
                IPv4Util.flush_ip_addresses(interface_data['name'], node)

    # TODO: not ipv4-specific, move to another class
    @staticmethod
    @keyword('Node "${node}" interface "${interface}" is in "${state}" state')
    def set_interface_state(node, interface, state):
        """See IPv4Node.set_interface_state for more information.

        :param node:
        :param interface:
        :param state:
        :return:
        """
        log.debug('Node {} interface {} is in {} state'.format(
            get_node_hostname(node), interface, state))
        get_node(node).set_interface_state(interface, state)

    @staticmethod
    @keyword('Node "${node}" interface "${port}" has IPv4 address '
             '"${address}" with prefix length "${prefix_length}"')
    def set_interface_address(node, interface, address, length):
        """See IPv4Node.set_ip for more information.

        :param node:
        :param interface:
        :param address:
        :param length:
        :return:
        """
        log.debug('Node {} interface {} has IPv4 address {} with prefix '
                  'length {}'.format(get_node_hostname(node), interface,
                                     address, length))
        get_node(node).set_ip(interface, address, int(length))
        hostname = get_node_hostname(node)
        IPv4Util.ADDRESSES[hostname, interface] = address
        IPv4Util.PREFIXES[hostname, interface] = int(length)
        # TODO: Calculate subnet from ip address and prefix length.
        # IPv4Util.SUBNETS[hostname, interface] =

    @staticmethod
    @keyword('From node "${node}" interface "${port}" ARP-ping '
             'IPv4 address "${ip_address}"')
    def arp_ping(node, interface, ip_address):
        log.debug('From node {} interface {} ARP-ping IPv4 address {}'.
                  format(get_node_hostname(node), interface, ip_address))
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
                  'via {} interface {}'.format(get_node_hostname(node),
                                               network, prefix_length,
                                               gateway, interface))
        get_node(node).set_route(network, int(prefix_length),
                                 gateway, interface)

    @staticmethod
    @keyword('Remove IPv4 route from "${node}" to network "${network}" with '
             'prefix length "${prefix_length}" interface "${interface}" via '
             '"${gateway}"')
    def unset_route(node, network, prefix_length, interface, gateway):
        """See IPv4Node.unset_route for more information.

        :param node:
        :param network:
        :param prefix_length:
        :param interface:
        :param gateway:
        :return:
        """
        get_node(node).unset_route(network, prefix_length, gateway, interface)

    @staticmethod
    @keyword('After ping is sent in topology "${nodes_info}" from node '
             '"${src_node}" interface "${src_port}" with destination IPv4 '
             'address of node "${dst_node}" interface "${dst_port}" a ping '
             'response arrives and TTL is decreased by "${hops}"')
    def send_ping(nodes_info, src_node, src_port, dst_node, dst_port, hops):
        """Send IPv4 ping and wait for response.

        :param nodes_info: Dictionary containing information on all nodes
        in topology.
        :param src_node: Source node.
        :param src_port: Source interface.
        :param dst_node: Destination node.
        :param dst_port: Destination interface.
        :param hops: Number of hops between src_node and dst_node.
        """
        log.debug('After ping is sent from node "{}" interface "{}" '
                  'with destination IPv4 address of node "{}" interface "{}" '
                  'a ping response arrives and TTL is decreased by "${}"'.
                  format(get_node_hostname(src_node), src_port,
                         get_node_hostname(dst_node), dst_port, hops))
        node = src_node
        src_mac = Topology.get_interface_mac(src_node, src_port)
        if dst_node['type'] == NodeType.TG:
            dst_mac = Topology.get_interface_mac(src_node, src_port)
        _, adj_int = Topology.\
            get_adjacent_node_and_interface(nodes_info, src_node, src_port)
        first_hop_mac = adj_int['mac_address']
        src_ip = IPv4Util.get_ip_addr(src_node, src_port)
        dst_ip = IPv4Util.get_ip_addr(dst_node, dst_port)
        args = '--src_if "{}" --src_mac "{}" --first_hop_mac "{}" ' \
               '--src_ip "{}" --dst_ip "{}" --hops "{}"'\
            .format(src_port, src_mac, first_hop_mac, src_ip, dst_ip, hops)
        if dst_node['type'] == NodeType.TG:
            args += ' --dst_if "{}" --dst_mac "{}"'.format(dst_port, dst_mac)
        TrafficScriptExecutor.run_traffic_script_on_node(
            "ipv4_ping_ttl_check.py", node, args)

    @staticmethod
    @keyword('Get IPv4 address of node "${node}" interface "${port}"')
    def get_ip_addr(node, port):
        """Get IPv4 address configured on specified interface

        :param node: node dictionary
        :param port: interface name
        :return: IPv4 address of specified interface as a 'str' type
        """
        log.debug('Get IPv4 address of node {} interface {}'.
                  format(get_node_hostname(node), port))
        return IPv4Util.ADDRESSES[(get_node_hostname(node), port)]

    @staticmethod
    @keyword('Get IPv4 address prefix of node "${node}" interface "${port}"')
    def get_ip_addr_prefix(node, port):
        """ Get IPv4 address prefix for specified interface.

        :param node: Node dictionary.
        :param port: Interface name.
        """
        log.debug('Get IPv4 address prefix of node {} interface {}'.
                  format(get_node_hostname(node), port))
        return IPv4Util.PREFIXES[(get_node_hostname(node), port)]

    @staticmethod
    @keyword('Get IPv4 subnet of node "${node}" interface "${port}"')
    def get_ip_addr_subnet(node, port):
        """ Get IPv4 subnet of specified interface.

        :param node: Node dictionary.
        :param port: Interface name.
        """
        log.debug('Get IPv4 subnet of node {} interface {}'.
                  format(get_node_hostname(node), port))
        return IPv4Util.SUBNETS[(get_node_hostname(node), port)]

    @staticmethod
    @keyword('Flush IPv4 addresses "${port}" "${node}"')
    def flush_ip_addresses(port, node):
        """See IPv4Node.flush_ip_addresses for more information.

        :param port:
        :param node:
        :return:
        """
        key = (get_node_hostname(node), port)
        del IPv4Util.ADDRESSES[key]
        del IPv4Util.PREFIXES[key]
        del IPv4Util.SUBNETS[key]
        get_node(node).flush_ip_addresses(port)
