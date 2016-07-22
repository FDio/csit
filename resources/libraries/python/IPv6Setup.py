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

"""Library to set up IPv6 in topology."""

from robot.api import logger
from ipaddress import IPv6Network

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.constants import Constants
from resources.libraries.python.VatExecutor import VatTerminal, VatExecutor


class IPv6Networks(object):
    """IPv6 network iterator.

    :param networks: List of the available IPv6 networks.
    :type networks: list
    """
    def __init__(self, networks):
        self._networks = list()
        for network in networks:
            net = IPv6Network(unicode(network))
            self._networks.append(net)
        num = len(self._networks)
        if num == 0:
            raise Exception('No IPv6 networks')

    def next_network(self):
        """Get the next element of the iterator.

        :return: IPv6 network.
        :rtype: IPv6Network object
        :raises: StopIteration if there is no more elements.
        """
        if len(self._networks):
            return self._networks.pop()
        else:
            raise StopIteration()


class IPv6Setup(object):
    """IPv6 setup in topology."""

    def __init__(self):
        pass

    def nodes_set_ipv6_addresses(self, nodes, nodes_addr):
        """Set IPv6 addresses on all VPP nodes in topology.

        :param nodes: Nodes of the test topology.
        :param nodes_addr: Available nodes IPv6 addresses.
        :type nodes: dict
        :type nodes_addr: dict
        :return: Affected interfaces as list of (node, interface) tuples.
        :rtype: list
        """
        interfaces = []

        for net in nodes_addr.values():
            for port in net['ports'].values():
                host = port.get('node')
                if host is None:
                    continue
                topo = Topology()
                node = topo.get_node_by_hostname(nodes, host)
                if node is None:
                    continue
                if node['type'] == NodeType.DUT:
                    port_key = topo.get_interface_by_name(node, port['if'])
                    self.vpp_set_if_ipv6_addr(node, port_key, port['addr'],
                                              net['prefix'])

                    interfaces.append((node, port['if']))
        return interfaces

    def nodes_clear_ipv6_addresses(self, nodes, nodes_addr):
        """Remove IPv6 addresses from all VPP nodes in topology.

        :param nodes: Nodes of the test topology.
        :param nodes_addr: Available nodes IPv6 addresses.
        :type nodes: dict
        :type nodes_addr: dict
        """
        for net in nodes_addr.values():
            for port in net['ports'].values():
                host = port.get('node')
                if host is None:
                    continue
                topo = Topology()
                node = topo.get_node_by_hostname(nodes, host)
                if node is None:
                    continue
                if node['type'] == NodeType.DUT:
                    self.vpp_del_if_ipv6_addr(node, port['if'], port['addr'],
                                              net['prefix'])

    @staticmethod
    def linux_set_if_ipv6_addr(node, interface, addr, prefix):
        """Set IPv6 address on linux host.

        :param node: Linux node.
        :param interface: Node interface.
        :param addr: IPv6 address.
        :param prefix: IPv6 address prefix.
        :type node: dict
        :type interface: str
        :type addr: str
        :type prefix: str
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = "ifconfig {dev} inet6 add {ip}/{p} up".format(dev=interface,
                                                            ip=addr, p=prefix)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise Exception('TG ifconfig failed')

    @staticmethod
    def linux_del_if_ipv6_addr(node, interface, addr, prefix):
        """Delete IPv6 address on linux host.

        :param node: Linux node.
        :param interface: Node interface.
        :param addr: IPv6 address.
        :param prefix: IPv6 address prefix.
        :type node: dict
        :type interface: str
        :type addr: str
        :type prefix: str
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = "ifconfig {dev} inet6 del {ip}/{p}".format(dev=interface,
                                                         ip=addr,
                                                         p=prefix)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise Exception('TG ifconfig failed')

        cmd = "ifconfig {dev} down".format(dev=interface)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise Exception('TG ifconfig failed')

    @staticmethod
    def vpp_set_if_ipv6_addr(node, iface_key, addr, prefix):
        """Set IPv6 address on VPP.

        :param node: VPP node.
        :param iface_key: Node interface key.
        :param addr: IPv6 address.
        :param prefix: IPv6 address prefix.
        :type node: dict
        :type iface_key: str
        :type addr: str
        :type prefix: str
        """
        topo = Topology()
        sw_if_index = Topology.get_interface_sw_index(node, iface_key)
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template('add_ip_address.vat',
                                                    sw_if_index=sw_if_index,
                                                    address=addr,
                                                    prefix_length=prefix)
            vat.vat_terminal_exec_cmd_from_template('set_if_state.vat',
                                                    sw_if_index=sw_if_index,
                                                    state='admin-up')

        ssh = SSH()
        ssh.connect(node)
        cmd_input = 'exec show int'
        (ret_code, stdout, stderr) = ssh.exec_command_sudo(
            Constants.VAT_BIN_NAME, cmd_input)
        logger.debug('ret: {0}'.format(ret_code))
        logger.debug('stdout: {0}'.format(stdout))
        logger.debug('stderr: {0}'.format(stderr))

    @staticmethod
    def vpp_del_if_ipv6_addr(node, interface, addr, prefix):
        """Delete IPv6 address on VPP.

        :param node: VPP node.
        :param interface: Node interface.
        :param addr: IPv6 address.
        :param prefix: IPv6 address prefix.
        :type node: dict
        :type interface: str
        :type addr: str
        :type prefix: str
        """
        sw_if_index = Topology.get_interface_sw_index(node, interface)
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template('del_ip_address.vat',
                                                    sw_if_index=sw_if_index,
                                                    address=addr,
                                                    prefix_length=prefix)
            vat.vat_terminal_exec_cmd_from_template('set_if_state.vat',
                                                    sw_if_index=sw_if_index,
                                                    state='admin-down')

    @staticmethod
    def vpp_ra_suppress_link_layer(node, interface):
        """Suppress ICMPv6 router advertisement message for link scope address.

        :param node: VPP node.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        """
        sw_if_index = Topology.get_interface_sw_index(node, interface)
        VatExecutor.cmd_from_template(node,
                                      'sw_interface_ip6nd_ra_config.vat',
                                      sw_if_id=sw_if_index,
                                      param='surpress')

    @staticmethod
    def vpp_ra_send_after_interval(node, interface, interval=2):
        """Setup vpp router advertisement(RA) in such way it sends RA packet
        after and every interval value.

        :param node: VPP node.
        :param interface: Interface name.
        :param interval: Interval for RA resend
        :type node: dict
        :type interface: str
        :type interval: int
        """
        sw_if_index = Topology.get_interface_sw_index(node, interface)
        VatExecutor.cmd_from_template(node,
                                      'sw_interface_ip6nd_ra_config.vat',
                                      sw_if_id=sw_if_index,
                                      param='interval {0}'.format(interval))

    def vpp_all_ra_suppress_link_layer(self, nodes):
        """Suppress ICMPv6 router advertisement message for link scope address
        on all VPP nodes in the topology.

        :param nodes: Nodes of the test topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.TG:
                continue
            for port_k in node['interfaces'].keys():
                self.vpp_ra_suppress_link_layer(node, port_k)

    @staticmethod
    def get_link_address(link, nodes_addr):
        """Get link IPv6 address.

        :param link: Link name.
        :param nodes_addr: Available nodes IPv6 addresses.
        :type link: str
        :type nodes_addr: dict
        :return: Link IPv6 address.
        :rtype: str
        """
        net = nodes_addr.get(link)
        if net is None:
            raise ValueError('Link "{0}" address not found'.format(link))
        return net.get('net_addr')

    @staticmethod
    def get_link_prefix(link, nodes_addr):
        """Get link IPv6 address prefix.

        :param link: Link name.
        :param nodes_addr: Available nodes IPv6 addresses.
        :type link: str
        :type nodes_addr: dict
        :return: Link IPv6 address prefix.
        :rtype: int
        """
        net = nodes_addr.get(link)
        if net is None:
            raise ValueError('Link "{0}" address not found'.format(link))
        return net.get('prefix')
