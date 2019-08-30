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

from pprint import pformat

from robot.api import logger
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import NodeType, Topology


class VppCounters(object):
    """VPP counters utilities."""

    def __init__(self):
        self._stats_table = None

    @staticmethod
    def vpp_show_errors(node):
        """Run "show errors" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node, 'show errors')

    @staticmethod
    def vpp_show_errors_on_all_duts(nodes):
        """Show errors on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
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

        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node, 'show runtime')

    @staticmethod
    def vpp_show_runtime_counters_on_all_duts(nodes):
        """Clear VPP runtime counters on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.vpp_show_runtime(node)

    @staticmethod
    def vpp_show_hardware_verbose(node):
        """Run "show hardware-interfaces verbose" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node, 'show hardware verbose')

    @staticmethod
    def vpp_show_memory(node):
        """Run "show memory" debug CLI command.

        Currently, every flag is hardcoded, giving the longest output.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd(
            node, 'show memory verbose api-segment stats-segment main-heap')

    @staticmethod
    def vpp_clear_runtime(node):
        """Run "clear runtime" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node, 'clear runtime', log=False)

    @staticmethod
    def vpp_clear_runtime_counters_on_all_duts(nodes):
        """Run "clear runtime" CLI command on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.vpp_clear_runtime(node)

    @staticmethod
    def vpp_clear_hardware_counters(node):
        """Run "clear hardware" CLI command.

        :param node: Node to run command on.
        :type node: dict
        :returns: Verified data from PAPI response.
        :rtype: dict
        """
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node, 'clear hardware', log=False)

    @staticmethod
    def vpp_clear_hardware_counters_on_all_duts(nodes):
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
        """
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node, 'clear errors', log=False)

    @staticmethod
    def vpp_clear_error_counters_on_all_duts(nodes):
        """Clear VPP errors counters on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.vpp_clear_errors_counters(node)

    @staticmethod
    def show_vpp_statistics(node):
        """Show [error, hardware, interface] stats.

        :param node: VPP node.
        :type node: dict
        """
        VppCounters.vpp_show_errors(node)
        VppCounters.vpp_show_hardware_verbose(node)
        VppCounters.vpp_show_runtime(node)
        VppCounters.vpp_show_memory(node)

    @staticmethod
    def show_statistics_on_all_duts(nodes):
        """Show statistics on all DUTs.

        :param nodes: DUT nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.show_vpp_statistics(node)

    @staticmethod
    def clear_vpp_statistics(node):
        """Clear [error, hardware, interface] stats.

        :param node: VPP node.
        :type node: dict
        """
        VppCounters.vpp_clear_errors_counters(node)
        VppCounters.vpp_clear_hardware_counters(node)
        VppCounters.vpp_clear_runtime(node)

    @staticmethod
    def clear_statistics_on_all_duts(nodes):
        """Clear statistics on all DUTs.

        :param nodes: DUT nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VppCounters.clear_vpp_statistics(node)
