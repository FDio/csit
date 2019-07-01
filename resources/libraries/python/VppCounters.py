# Copyright (c) 2019 Cisco and/or its affiliates.
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

from pprint import pformat

from robot.api import logger
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.topology import NodeType, Topology


class VppCounters(object):
    """VPP counters utilities."""

    def __init__(self):
        self._stats_table = None

    @staticmethod
    def _get_non_zero_items(data):
        """Extract and return non-zero items from the input data.

        :param data: Data to filter.
        :type data: dict
        :returns: Dictionary with non-zero items.
        :rtype dict
        """
        return {k: data[k] for k in data.keys() if sum(data[k])}

    @staticmethod
    def vpp_show_errors(node):
        """Run "show errors" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiExecutor.run_cli_cmd(node, 'show errors')

    @staticmethod
    def vpp_show_errors_verbose(node):
        """Run "show errors verbose" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiExecutor.run_cli_cmd(node, 'show errors verbose')

    @staticmethod
    def vpp_show_errors_on_all_duts(nodes, verbose=False):
        """Show errors on all DUTs.

        :param nodes: VPP nodes.
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
    def vpp_show_runtime(node, log_zeros=False):
        """Run "show runtime" CLI command.

        :param node: Node to run command on.
        :param log_zeros: Log also items with zero values.
        :type node: dict
        :type log_zeros: bool
        """
        args = dict(path='^/sys/node')
        with PapiExecutor(node) as papi_exec:
            stats = papi_exec.add("vpp-stats", **args).get_stats()[0]
            # TODO: Introduce get_stat?

        names = stats['/sys/node/names']

        if not names:
            return

        runtime = []
        runtime_non_zero = []

        for name in names:
            runtime.append({'name': name})

        for idx, runtime_item in enumerate(runtime):

            calls_th = []
            for thread in stats['/sys/node/calls']:
                calls_th.append(thread[idx])
            runtime_item["calls"] = calls_th

            vectors_th = []
            for thread in stats['/sys/node/vectors']:
                vectors_th.append(thread[idx])
            runtime_item["vectors"] = vectors_th

            suspends_th = []
            for thread in stats['/sys/node/suspends']:
                suspends_th.append(thread[idx])
            runtime_item["suspends"] = suspends_th

            clocks_th = []
            for thread in stats['/sys/node/clocks']:
                clocks_th.append(thread[idx])
            runtime_item["clocks"] = clocks_th

            if (sum(calls_th) or sum(vectors_th) or
                    sum(suspends_th) or sum(clocks_th)):
                runtime_non_zero.append(runtime_item)

        if log_zeros:
            logger.info("Runtime:\n{runtime}".format(
                runtime=pformat(runtime)))
        else:
            logger.info("Runtime:\n{runtime}".format(
                runtime=pformat(runtime_non_zero)))

    @staticmethod
    def vpp_show_runtime_verbose(node):
        """Run "show runtime verbose" CLI command.

        TODO: Remove?
              Only verbose output is possible to get using VPPStats.

        :param node: Node to run command on.
        :type node: dict
        """
        VppCounters.vpp_show_runtime(node)

    @staticmethod
    def show_runtime_counters_on_all_duts(nodes):
        """Clear VPP runtime counters on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.vpp_show_runtime(node)

    @staticmethod
    def vpp_show_hardware_detail(node):
        """Run "show hardware-interfaces detail" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiExecutor.run_cli_cmd(node, 'show hardware detail')

    @staticmethod
    def vpp_clear_runtime(node):
        """Run "clear runtime" CLI command.

        :param node: Node to run command on.
        :type node: dict
        :returns: Verified data from PAPI response.
        :rtype: dict
        """
        return PapiExecutor.run_cli_cmd(node, 'clear runtime', log=False)

    @staticmethod
    def clear_runtime_counters_on_all_duts(nodes):
        """Run "clear runtime" CLI command on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.vpp_clear_runtime(node)

    @staticmethod
    def vpp_clear_interface_counters(node):
        """Run "clear interfaces" CLI command.

        :param node: Node to run command on.
        :type node: dict
        :returns: Verified data from PAPI response.
        :rtype: dict
        """
        return PapiExecutor.run_cli_cmd(node, 'clear interfaces', log=False)

    @staticmethod
    def clear_interface_counters_on_all_duts(nodes):
        """Clear interface counters on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.vpp_clear_interface_counters(node)

    @staticmethod
    def vpp_clear_hardware_counters(node):
        """Run "clear hardware" CLI command.

        :param node: Node to run command on.
        :type node: dict
        :returns: Verified data from PAPI response.
        :rtype: dict
        """
        return PapiExecutor.run_cli_cmd(node, 'clear hardware', log=False)

    @staticmethod
    def clear_hardware_counters_on_all_duts(nodes):
        """Clear hardware counters on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.vpp_clear_hardware_counters(node)

    @staticmethod
    def vpp_clear_errors_counters(node):
        """Run "clear errors" CLI command.

        :param node: Node to run command on.
        :type node: dict
        :returns: Verified data from PAPI response.
        :rtype: dict
        """
        return PapiExecutor.run_cli_cmd(node, 'clear errors', log=False)

    @staticmethod
    def clear_error_counters_on_all_duts(nodes):
        """Clear VPP errors counters on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.vpp_clear_errors_counters(node)

    def vpp_get_ipv4_interface_counter(self, node, interface):
        """

        :param node: Node to get interface IPv4 counter on.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        :returns: Interface IPv4 counter.
        :rtype: int
        """
        return self.vpp_get_ipv46_interface_counter(node, interface, False)

    def vpp_get_ipv6_interface_counter(self, node, interface):
        """

        :param node: Node to get interface IPv6 counter on.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        :returns: Interface IPv6 counter.
        :rtype: int
        """
        return self.vpp_get_ipv46_interface_counter(node, interface, True)

    def vpp_get_ipv46_interface_counter(self, node, interface, is_ipv6=True):
        """Return interface IPv4/IPv6 counter.

        :param node: Node to get interface IPv4/IPv6 counter on.
        :param interface: Interface name.
        :param is_ipv6: Specify IP version.
        :type node: dict
        :type interface: str
        :type is_ipv6: bool
        :returns: Interface IPv4/IPv6 counter.
        :rtype: int
        """
        version = 'ip6' if is_ipv6 else 'ip4'
        topo = Topology()
        sw_if_index = topo.get_interface_sw_index(node, interface)
        if sw_if_index is None:
            logger.trace('{i} sw_if_index not found.'.format(i=interface))
            return 0

        if_counters = self._stats_table.get('interface_counters')
        if not if_counters:
            logger.trace('No interface counters.')
            return 0
        for counter in if_counters:
            if counter['vnet_counter_type'] == version:
                data = counter['data']
                return data[sw_if_index]
        logger.trace('{i} {v} counter not found.'.format(
            i=interface, v=version))
        return 0

    @staticmethod
    def show_vpp_statistics(node):
        """Show [error, hardware, interface] stats.

        :param node: VPP node.
        :type node: dict
        """
        VppCounters.vpp_show_errors(node)
        VppCounters.vpp_show_hardware_detail(node)
        VppCounters.vpp_show_runtime(node)

    @staticmethod
    def show_statistics_on_all_duts(nodes, sleeptime=5):
        """Show VPP statistics on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        :param sleeptime: Time to wait for traffic to arrive back to TG.
        :type sleeptime: int
        """
        logger.trace('Waiting for statistics to be collected')
        time.sleep(sleeptime)
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.show_vpp_statistics(node)
