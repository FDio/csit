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
import prettytable

from robot.api import logger
from pprint import pformat
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.topology import NodeType, Topology

# TODO: Remove, it is here to compare outputs form VAT and PAPI.
from resources.libraries.python.VatExecutor import VatExecutor


class VppCounters(object):
    """VPP counters utilities.

    # TODO: Remove unnecessary logging.

    """

    def __init__(self):
        self._stats_table = None

    @staticmethod
    def _run_cli_cmd(node, cmd, log=True):
        """Run a CLI command.

        :param node: Node to run command on.
        :param cmd: The CLI command to be run on the node.
        :param log: If True, the response is logged.
        :type node: dict
        :type cmd: str
        :type log: bool
        :returns: Verified data from PAPI response.
        :rtype: dict
        """

        logger.info("Command: {cmd}".format(cmd=cmd))

        cli = 'cli_inband'
        args = dict(cmd=cmd)
        err_msg = "Failed to run 'cli_inband {cmd}' PAPI command on host " \
                  "{host}".format(host=node['host'], cmd=cmd)

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cli, **args).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)

        if log:
            logger.info("{cmd}:\n{data}".format(cmd=cmd, data=data["reply"]))

        return data

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
    def _pprint_errors(data):
        """Pretty print the table with errors.

        :param data: Errors to print.
        :type data: dict
        :returns: String representation of the pretty table.
        :rtype: str
        """

        if not data:
            return ""

        table = prettytable.PrettyTable(["Count", "Node", "Reason"])

        for key, count in data.iteritems():
            node = "/".join(key.split("/")[2:-1])
            reason = key.split("/")[-1]
            table.add_row([count, node, reason])
        table.set_style(prettytable.prettytable.PLAIN_COLUMNS)
        table.align["Count"] = "r"
        table.align["Node"] = "l"
        table.align["Reason"] = "l"

        return table.get_string()

    @staticmethod
    def _pprint_runtime(data, remove_zeros=False):
        """Pretty print the table with runtime data.

        :param data: Data to print.
        :param remove_zeros: If True, only non-zero items are included.
        :type data: list
        :type remove_zeros: bool
        :returns: String representation of the pretty table.
        :rtype: str
        """

        if not data:
            return ""

        if remove_zeros:
            items = []
            for item in data:
                if (sum(item["calls"]) or sum(item["vectors"]) or
                        sum(item["suspends"]) or sum(item["clocks"])):
                    items.append(item)
        else:
            items = data

        table = prettytable.PrettyTable(
            ["Name", "Calls", "Vectors", "Suspends", "Clocks"]
        )

        for item in items:
            table.add_row([item["name"],
                           item["calls"],
                           item["vectors"],
                           item["suspends"],
                           item["clocks"]])

        table.set_style(prettytable.prettytable.PLAIN_COLUMNS)
        table.align["name"] = "l"
        table.align["calls"] = "r"
        table.align["vectors"] = "r"
        table.align["suspends"] = "r"
        table.align["clocks"] = "r"

        return table.get_string()

    @staticmethod
    def vpp_show_errors(node):
        """Run "show errors" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """

        logger.info("PAPI CLI")
        VppCounters._run_cli_cmd(node, 'show errors')

        logger.info("PAPI VPPStats")
        cmd = "vpp-stats"
        args = dict(path='^/err')
        with PapiExecutor(node) as papi_exec:
            stats = papi_exec.add(cmd, **args).get_stats()

        errors = VppCounters._get_non_zero_items(stats[0])

        logger.info("Errors:\n{err}".format(
            err=pformat({str("/".join(k.split('/')[2:])): errors[k]
                         for k in errors.keys()})))

        logger.info("Errors:\n{err}".format(
            err=VppCounters._pprint_errors(errors)))

        # TODO: Remove, it is here to compare outputs form VAT and PAPI.
        logger.info("VAT")
        vat = VatExecutor()
        vat.execute_script("show_errors.vat", node, json_out=False)
        vat.script_should_have_passed()

    @staticmethod
    def vpp_show_errors_verbose(node):
        """Run "show errors verbose" debug CLI command.

        # TODO: Remove? Or how to get verbose output?

        :param node: Node to run command on.
        :type node: dict
        """
        VppCounters.vpp_show_errors(node)

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
    def vpp_show_runtime(node):
        """Run "show runtime" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """

        logger.info("PAPI CLI")
        VppCounters._run_cli_cmd(node, 'show runtime')

        logger.info("PAPI VPPStats")
        cmd = "vpp-stats"
        args = dict(path='^/sys/node')
        with PapiExecutor(node) as papi_exec:
            stats = papi_exec.add(cmd, **args).get_stats()[0]

        names = stats['/sys/node/names']

        if not names:
            return

        calls = stats['/sys/node/calls']
        clocks = stats['/sys/node/clocks']
        vectors = stats['/sys/node/vectors']
        suspends = stats['/sys/node/suspends']

        runtime = []

        for name in names:
            runtime.append({'name': name})

        # for idx in range(len(calls[0])):
        for idx in range(len(runtime)):

            calls_th = []
            for thread in calls:
                calls_th.append(thread[idx])
            runtime[idx]["calls"] = calls_th

            vectors_th = []
            for thread in vectors:
                vectors_th.append(thread[idx])
            runtime[idx]["vectors"] = vectors_th

            suspends_th = []
            for thread in suspends:
                suspends_th.append(thread[idx])
            runtime[idx]["suspends"] = suspends_th

            clocks_th = []
            for thread in clocks:
                clocks_th.append(thread[idx])
            runtime[idx]["clocks"] = clocks_th

        logger.info("Runtime:\n{runtime}".format(
            runtime=pformat(runtime)))

        logger.info("Runtime:\n{runtime}".format(
            runtime=VppCounters._pprint_runtime(runtime)))
        logger.info("Runtime:\n{runtime}".format(
            runtime=VppCounters._pprint_runtime(runtime, remove_zeros=True)))

        # TODO: Remove, it is here to compare outputs form VAT and PAPI.
        logger.info("VAT")
        vat = VatExecutor()
        vat.execute_script("show_runtime.vat", node, json_out=False)
        logger.info(vat.get_script_stdout())
        vat.script_should_have_passed()

    @staticmethod
    def vpp_show_runtime_verbose(node):
        """Run "show runtime verbose" CLI command.

        # TODO: Remove? Or how to get verbose output?

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

        logger.info("PAPI CLI")
        VppCounters._run_cli_cmd(node, 'show hardware detail')

        # TODO: Remove, it is here to compare outputs form VAT and PAPI.
        logger.info("VAT")
        vat = VatExecutor()
        vat.execute_script("show_hardware_detail.vat", node, json_out=False)
        vat.script_should_have_passed()

    @staticmethod
    def vpp_clear_runtime(node):
        """Run "clear runtime" CLI command.

        :param node: Node to run command on.
        :type node: dict
        :returns: Verified data from PAPI response.
        :rtype: dict
        """
        return VppCounters._run_cli_cmd(node, 'clear runtime', log=False)

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
        return VppCounters._run_cli_cmd(node, 'clear interfaces', log=False)

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
        return VppCounters._run_cli_cmd(node, 'clear hardware', log=False)

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
        return VppCounters._run_cli_cmd(node, 'clear errors', log=False)

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
        if_index = topo.get_interface_sw_index(node, interface)
        if if_index is None:
            logger.trace('{i} sw_index not found.'.format(i=interface))
            return 0

        if_counters = self._stats_table.get('interface_counters')
        if not if_counters:
            logger.trace('No interface counters.')
            return 0
        for counter in if_counters:
            if counter['vnet_counter_type'] == version:
                data = counter['data']
                return data[if_index]
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
