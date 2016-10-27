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

"""VPP counters utilities library."""

import time

from robot.api import logger

from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal


class VppCounters(object):
    """VPP counters utilities."""

    def __init__(self):
        self._stats_table = None

    def vpp_nodes_clear_interface_counters(self, nodes):
        """Clear interface counters on all VPP nodes in topology.

        :param nodes: Nodes in topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                self.vpp_clear_interface_counters(node)

    @staticmethod
    def vpp_show_errors(node):
        """Run "show errors" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_errors.vat", node, json_out=False)

    @staticmethod
    def vpp_show_errors_verbose(node):
        """Run "show errors verbose" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_errors_verbose.vat", node, json_out=False)

    @staticmethod
    def vpp_show_errors_on_all_duts(nodes, verbose=False):
        """Show errors on all DUTs.

        :param nodes: VPP nodes
        :param verbose: If True show verbose output.
        :type nodes: dict
        :type verbose: bool
        """

        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                if verbose:
                    VppCounters.vpp_show_errors_verbose(node)
                else:
                    VppCounters.vpp_show_errors(node)

    @staticmethod
    def vpp_show_runtime(node):
        """Run "show runtime" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_runtime.vat", node, json_out=False)

    @staticmethod
    def vpp_show_runtime_verbose(node):
        """Run "show runtime verbose" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_runtime_verbose.vat", node, json_out=False)

    @staticmethod
    def vpp_show_hardware_detail(node):
        """Run "show hardware-interfaces detail" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_hardware_detail.vat", node, json_out=False)

    @staticmethod
    def vpp_clear_runtime(node):
        """Run "clear runtime" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("clear_runtime.vat", node, json_out=False)

    @staticmethod
    def vpp_clear_interface_counters(node):
        """Clear interface counters on VPP node.

        :param node: Node to clear interface counters on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script('clear_interface.vat', node)
        vat.script_should_have_passed()

    @staticmethod
    def vpp_clear_hardware_counters(node):
        """Clear interface hardware counters on VPP node.

        :param node: Node to clear hardware counters on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script('clear_hardware.vat', node)
        vat.script_should_have_passed()

    @staticmethod
    def vpp_clear_errors_counters(node):
        """Clear errors counters on VPP node.

        :param node: Node to clear errors counters on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script('clear_errors.vat', node)
        vat.script_should_have_passed()

    def vpp_dump_stats_table(self, node):
        """Dump stats table on VPP node.

        :param node: Node to dump stats table on.
        :type node: dict
        :return: Stats table.
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd('want_stats enable')
            for _ in range(0, 12):
                stats_table = vat.vat_terminal_exec_cmd('dump_stats_table')
                if_counters = stats_table['interface_counters']
                if len(if_counters) > 0:
                    self._stats_table = stats_table
                    return stats_table
                time.sleep(1)
            return None

    def vpp_get_ipv4_interface_counter(self, node, interface):
        return self.vpp_get_ipv46_interface_counter(node, interface, False)

    def vpp_get_ipv6_interface_counter(self, node, interface):
        return self.vpp_get_ipv46_interface_counter(node, interface, True)

    def vpp_get_ipv46_interface_counter(self, node, interface, is_ipv6=True):
        """Return interface IPv4/IPv6 counter.

        :param node: Node to get interface IPv4/IPv6 counter on.
        :param interface: Interface name.
        :param is_ipv6: Specify IP version.
        :type node: dict
        :type interface: str
        :type is_ipv6: bool
        :return: Interface IPv4/IPv6 counter.
        :rtype: int
        """
        version = 'ip6' if is_ipv6 else 'ip4'
        topo = Topology()
        if_index = topo.get_interface_sw_index(node, interface)
        if if_index is None:
            logger.trace('{i} sw_index not found.'.format(i=interface))
            return 0

        if_counters = self._stats_table.get('interface_counters')
        if if_counters is None or len(if_counters) == 0:
            logger.trace('No interface counters.')
            return 0
        for counter in if_counters:
            if counter['vnet_counter_type'] == version:
                data = counter['data']
                return data[if_index]
        logger.trace('{i} {v} counter not found.'.format(i=interface,
                                                         v=version))
        return 0
