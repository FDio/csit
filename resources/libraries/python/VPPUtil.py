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

"""VPP util library."""

import binascii

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType
from resources.libraries.python.VatExecutor import VatExecutor


class VPPUtil(object):
    """General class for any VPP related methods/functions."""

    @staticmethod
    def show_vpp_settings(node, *additional_cmds):
        """Print default VPP settings. In case others are needed, can be
        accepted as next parameters (each setting one parameter), preferably
        in form of a string.

        :param node: VPP node.
        :param additional_cmds: Additional commands that the vpp should print
            settings for.
        :type node: dict
        :type additional_cmds: tuple
        """
        def_setting_tb_displayed = {
            'IPv6 FIB': 'ip6 fib',
            'IPv4 FIB': 'ip fib',
            'Interface IP': 'int addr',
            'Interfaces': 'int',
            'ARP': 'ip arp',
            'Errors': 'err'
        }

        if additional_cmds:
            for cmd in additional_cmds:
                def_setting_tb_displayed['Custom Setting: {}'.format(cmd)] = cmd

        for _, cmd in def_setting_tb_displayed.items():
            command = 'vppctl sh {cmd}'.format(cmd=cmd)
            exec_cmd_no_error(node, command, timeout=30, sudo=True)

    @staticmethod
    def restart_vpp_service(node):
        """Restart VPP service on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        DUTSetup.restart_service(node, Constants.VPP_UNIT)

    @staticmethod
    def restart_vpp_service_on_all_duts(nodes):
        """Restart VPP service on all DUT nodes.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.restart_vpp_service(node)

    @staticmethod
    def stop_vpp_service(node):
        """Stop VPP service on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        DUTSetup.stop_service(node, Constants.VPP_UNIT)

    @staticmethod
    def stop_vpp_service_on_all_duts(nodes):
        """Stop VPP service on all DUT nodes.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.stop_vpp_service(node)

    @staticmethod
    def verify_vpp_installed(node):
        """Verify that VPP is installed on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        cmd = 'command -v vpp'
        exec_cmd_no_error(
            node, cmd, message='VPP is not installed!')

    @staticmethod
    def verify_vpp_started(node):
        """Verify that VPP is started on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        cmd = ('vppctl show pci 2>&1 | '
               'fgrep -v "Connection refused" | '
               'fgrep -v "No such file or directory"')
        exec_cmd_no_error(
            node, cmd, sudo=True, message='VPP failed to start!', retries=120)

    @staticmethod
    def verify_vpp(node):
        """Verify that VPP is installed and started on the specified topology
        node.

        :param node: Topology node.
        :type node: dict
        :raises RuntimeError: If VPP service fails to start.
        """
        VPPUtil.verify_vpp_installed(node)
        try:
            # Verify responsivness of vppctl.
            VPPUtil.verify_vpp_started(node)
            # Verify responsivness of PAPI.
#            # Not importing at top due to https://stackoverflow.com/a/746067
#            from resources.libraries.python.InterfaceUtil import InterfaceUtil
#            # Just for debugging the following call.
#            node['interfaces'] = {1: {"vpp_sw_index": 1}, 2: {"vpp_sw_index": 2}}
#            InterfaceUtil.vpp_sw_interface_rx_placement_dump(node)
            VPPUtil.show_log(node)
            VPPUtil.vpp_show_version(node)
        finally:
            DUTSetup.get_service_logs(node, Constants.VPP_UNIT)

    @staticmethod
    def verify_vpp_on_all_duts(nodes):
        """Verify that VPP is installed and started on all DUT nodes.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.verify_vpp(node)

    @staticmethod
    def vpp_show_version(node, verbose=True):
        """Run "show_version" PAPI command.

        :param node: Node to run command on.
        :param verbose: Show version, compile date and compile location if True
            otherwise show only version.
        :type node: dict
        :type verbose: bool
        :returns: VPP version.
        :rtype: str
        """
        with PapiSocketExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').get_replies().verify_reply()
        logger.debug(repr(data))
        logger.debug(dir(data))
        version = ('VPP version:      {ver}\n'.
                   format(ver=data['version'].rstrip('\0x00')))
        if verbose:
            version += ('Compile date:     {date}\n'
                        'Compile location: {cl}\n '.
                        format(date=data['build_date'].rstrip('\0x00'),
                               cl=data['build_directory'].rstrip('\0x00')))
        logger.info(version)
        return data['version'].rstrip('\0x00')

    @staticmethod
    def show_vpp_version_on_all_duts(nodes):
        """Show VPP version verbose on all DUTs.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.vpp_show_version(node)

    @staticmethod
    def vpp_show_interfaces(node):
        """Run "show interface" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """

        cmd = 'sw_interface_dump'
        cmd_reply = 'sw_interface_details'
        args = dict(name_filter_valid=0, name_filter='')
        err_msg = 'Failed to get interface dump on host {host}'.format(
            host=node['host'])
        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, **args).execute_should_pass(err_msg)

        papi_if_dump = papi_resp.reply[0]['api_reply']

        if_data = list()
        for item in papi_if_dump:
            data = item[cmd_reply]
            data['interface_name'] = data['interface_name'].rstrip('\x00')
            data['tag'] = data['tag'].rstrip('\x00')
            data['l2_address'] = str(':'.join(binascii.hexlify(
                data['l2_address'])[i:i + 2] for i in range(0, 12, 2)).
                                     decode('ascii'))
            if_data.append(data)
        # TODO: return only base data
        logger.trace('Interface data of host {host}:\n{if_data}'.format(
            host=node['host'], if_data=if_data))

    @staticmethod
    def vpp_show_crypto_device_mapping(node):
        """Run "show crypto device mapping" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_crypto_device_mapping.vat", node,
                           json_out=False)

    @staticmethod
    def vpp_enable_traces_on_dut(node):
        """Enable vpp packet traces on the DUT node.

        :param node: DUT node to set up.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("enable_dpdk_traces.vat", node, json_out=False)
        vat.execute_script("enable_vhost_user_traces.vat", node, json_out=False)
        vat.execute_script("enable_memif_traces.vat", node, json_out=False)

    @staticmethod
    def vpp_enable_traces_on_all_duts(nodes):
        """Enable vpp packet traces on all DUTs in the given topology.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.vpp_enable_traces_on_dut(node)

    @staticmethod
    def vpp_enable_elog_traces_on_dut(node):
        """Enable API/CLI/Barrier traces on the DUT node.

        :param node: DUT node to set up.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("elog_trace_api_cli_barrier.vat", node,
                           json_out=False)

    @staticmethod
    def vpp_enable_elog_traces_on_all_duts(nodes):
        """Enable API/CLI/Barrier traces on all DUTs in the given topology.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.vpp_enable_elog_traces_on_dut(node)

    @staticmethod
    def show_event_logger_on_dut(node):
        """Show event logger on the DUT node.

        :param node: DUT node to show traces on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_event_logger.vat", node, json_out=False)

    @staticmethod
    def show_event_logger_on_all_duts(nodes):
        """Show event logger on all DUTs in the given topology.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.show_event_logger_on_dut(node)

    @staticmethod
    def show_log(node):
        """Show log on the specified topology node.

        :param node: Topology node.
        :type node: dict
        :returns: VPP log data.
        :rtype: list
        """
        with PapiSocketExecutor(node) as papi_exec:
            return papi_exec.add('cli_inband', cmd='show log').get_replies().\
                verify_reply()["reply"]

    @staticmethod
    def vpp_show_threads(node):
        """Show VPP threads on node.

        :param node: Node to run command on.
        :type node: dict
        :returns: VPP thread data.
        :rtype: list
        """
        with PapiSocketExecutor(node) as papi_exec:
            return papi_exec.add('show_threads').get_replies().\
                verify_reply()["thread_data"]
