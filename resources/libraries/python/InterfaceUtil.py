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

"""Interface util library"""

from time import time, sleep
from robot.api import logger
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal


class InterfaceUtil(object):
    """General utilities for managing interfaces"""

    @staticmethod
    def set_interface_state(node, interface, state):
        """Set interface state on a node.

        Function can be used for DUTs as well as for TGs.

        :param node: node where the interface is
        :param interface: interface name or sw_if_index
        :param state: one of 'up' or 'down'
        :type node: dict
        :type interface: str or int
        :type state: str
        :return: nothing
        """
        if node['type'] == NodeType.DUT:
            if state == 'up':
                state = 'admin-up'
            elif state == 'down':
                state = 'admin-down'
            else:
                raise ValueError('Unexpected interface state: {}'.format(state))

            if isinstance(interface, basestring):
                sw_if_index = Topology.get_interface_sw_index(node, interface)
            else:
                sw_if_index = interface

            VatExecutor.cmd_from_template(node, 'set_if_state.vat',
                                          sw_if_index=sw_if_index, state=state)

        elif node['type'] == NodeType.TG or node['type'] == NodeType.VM:
            cmd = 'ip link set {} {}'.format(interface, state)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise Exception('Node {} has unknown NodeType: "{}"'.
                            format(node['host'], node['type']))

    @staticmethod
    def set_interface_ethernet_mtu(node, interface, mtu):
        """Set Ethernet MTU for specified interface.

        Function can be used only for TGs.

        :param node: node where the interface is
        :param interface: interface name
        :param mtu: MTU to set
        :type node: dict
        :type interface: str
        :type mtu: int
        :return: nothing
        """
        if node['type'] == NodeType.DUT:
            ValueError('Node {}: Setting Ethernet MTU for interface '
                       'on DUT nodes not supported', node['host'])
        elif node['type'] == NodeType.TG:
            cmd = 'ip link set {} mtu {}'.format(interface, mtu)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise ValueError('Node {} has unknown NodeType: "{}"'.
                             format(node['host'], node['type']))

    @staticmethod
    def set_default_ethernet_mtu_on_all_interfaces_on_node(node):
        """Set default Ethernet MTU on all interfaces on node.

        Function can be used only for TGs.

        :param node: node where to set default MTU
        :type node: dict
        :return: nothing
        """
        for ifc in node['interfaces'].values():
            InterfaceUtil.set_interface_ethernet_mtu(node, ifc['name'], 1500)

    @staticmethod
    def vpp_node_interfaces_ready_wait(node, timeout=10):
        """Wait until all interfaces with admin-up are in link-up state.

        :param node: Node to wait on.
        :param timeout: Waiting timeout in seconds (optional, default 10s)
        :type node: dict
        :type timeout: int
        :raises: RuntimeError if the timeout period value has elapsed.
        """
        if_ready = False
        with VatTerminal(node) as vat:
            not_ready = []
            start = time()
            while not if_ready:
                out = vat.vat_terminal_exec_cmd('sw_interface_dump')
                if time() - start > timeout:
                    for interface in out:
                        if interface.get('admin_up_down') == 1:
                            if interface.get('link_up_down') != 1:
                                logger.debug('{0} link-down'.format(
                                    interface.get('interface_name')))
                    raise RuntimeError('timeout, not up {0}'.format(not_ready))
                not_ready = []
                for interface in out:
                    if interface.get('admin_up_down') == 1:
                        if interface.get('link_up_down') != 1:
                            not_ready.append(interface.get('interface_name'))
                if not not_ready:
                    if_ready = True
                else:
                    logger.debug('Interfaces still in link-down state: {0}, '
                                 'waiting...'.format(not_ready))
                    sleep(1)

    @staticmethod
    def vpp_nodes_interfaces_ready_wait(nodes, timeout=10):
        """Wait until all interfaces with admin-up are in link-up state for
        listed nodes.

        :param nodes: List of nodes to wait on.
        :param timeout: Seconds to wait per node for all interfaces to come up.
        :type nodes: list
        :type timeout: int
        :raises: RuntimeError if the timeout period value has elapsed.
        """
        for node in nodes:
            InterfaceUtil.vpp_node_interfaces_ready_wait(node, timeout)

    @staticmethod
    def all_vpp_interfaces_ready_wait(nodes, timeout=10):
        """Wait until all interfaces with admin-up are in link-up state for all
        nodes in the topology.

        :param nodes: Nodes in the topology.
        :param timeout: Seconds to wait per node for all interfaces to come up.
        :type nodes: dict
        :type timeout: int
        :raises: RuntimeError if the timeout period value has elapsed.
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                InterfaceUtil.vpp_node_interfaces_ready_wait(node, timeout)

    @staticmethod
    def create_subinterface(node, interface, sub_id, outer_vlan_id,
                            inner_vlan_id, type_subif):
        """Create sub-interface on node.

        :param node: Node to add sub-interface.
        :param interface: Interface name on which create sub-interface.
        :param sub_id: ID of the sub-interface to be created.
        :param outer_vlan_id: Outer VLAN ID.
        :param inner_vlan_id: Inner VLAN ID.
        :param type_subif: Type of sub-interface.
        :type node: dict
        :type interface: str or int
        :type sub_id: int
        :type outer_vlan_id: int
        :type inner_vlan_id: int
        :type type_subif: str
        :return: name and index of created sub-interface
        :rtype: tuple
        """

        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        output = VatExecutor.cmd_from_template(node, "create_sub_interface.vat",
                                               sw_if_index=sw_if_index,
                                               sub_id=sub_id,
                                               outer_vlan_id=outer_vlan_id,
                                               inner_vlan_id=inner_vlan_id,
                                               type_subif=type_subif)

        if output[0]["retval"] == 0:
            sw_subif_index = output[0]["sw_if_index"]
            logger.trace('Created subinterface with index {}'
                         .format(sw_subif_index))
        else:
            raise RuntimeError('Unable to create subinterface on node {}'
                               .format(node['host']))

        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd('exec show interfaces')

        return '{}.{}'.format(interface, sub_id), sw_subif_index
