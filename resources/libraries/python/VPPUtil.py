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

import time

from robot.api import logger

from resources.libraries.python.constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.PapiErrors import PapiError
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
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
    def start_vpp_service(node, retries=60):
        """Start VPP service on the specified node.

        :param node: VPP node.
        :param retries: Number of times (default 60) to re-try waiting.
        :type node: dict
        :type retries: int
        :raises RuntimeError: If VPP service fails to start.
        """
        DUTSetup.start_service(node, Constants.VPP_UNIT)
        # Sleep 1 second, up to <retry> times,
        # and verify if VPP is running.
        for _ in range(retries):
            time.sleep(1)
            command = 'vppctl show pci'
            ret, stdout, _ = exec_cmd(node, command, timeout=30, sudo=True)
            if not ret and 'Connection refused' not in stdout:
                break
        else:
            raise RuntimeError('VPP failed to start on host {name}'.
                               format(name=node['host']))
        DUTSetup.get_service_logs(node, Constants.VPP_UNIT)

    @staticmethod
    def start_vpp_service_on_all_duts(nodes):
        """Start up the VPP service on all nodes.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.start_vpp_service(node)

    @staticmethod
    def stop_vpp_service(node):
        """Stop VPP service on the specified node.

        :param node: VPP node.
        :type node: dict
        :raises RuntimeError: If VPP service fails to stop.
        """
        DUTSetup.stop_service(node, Constants.VPP_UNIT)

    @staticmethod
    def stop_vpp_service_on_all_duts(nodes):
        """Stop VPP service on all nodes.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.stop_vpp_service(node)

    @staticmethod
    def verify_vpp_on_dut(node):
        """Verify that VPP is installed on DUT node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If failed to restart VPP, get VPP version
            or get VPP interfaces.
        """
        VPPUtil.vpp_show_version_verbose(node)
        VPPUtil.vpp_show_interfaces(node)

    @staticmethod
    def verify_vpp_on_all_duts(nodes):
        """Verify that VPP is installed on all DUT nodes.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.start_vpp_service(node)
                VPPUtil.verify_vpp_on_dut(node)

    @staticmethod
    def vpp_show_version(node, verbose=False):
        """Run "show_version" API command.

        :param node: Node to run command on.
        :param verbose: Show version, compile date and compile location if True
            otherwise show only version.
        :type node: dict
        :type verbose: bool
        :raises PapiError: If no reply received for show_version API command.
        """
        # TODO: move composition of api data to separate method
        api_data = list()
        api = dict(api_name='show_version')
        api_args = dict()
        api['api_args'] = api_args
        api_data.append(api)

        api_reply = None
        with PapiExecutor(node) as papi_executor:
            papi_executor.execute_papi(api_data)
            try:
                papi_executor.papi_should_have_passed()
            except AssertionError:
                raise RuntimeError('Failed to get VPP version on host: {host}'.
                                   format(host=node['host']))
            api_reply = papi_executor.get_papi_reply()

        if api_reply is not None:
            version_data = api_reply[0]['api_reply']['show_version_reply']
            ver = version_data['version'].rstrip('\0x00')
            if verbose:
                date = version_data['build_date'].rstrip('\0x00')
                loc = version_data['build_directory'].rstrip('\0x00')
                version = \
                    'VPP Version:        {ver}\n' \
                    'Compile date:       {date}\n' \
                    'Compile location:   {loc}\n '\
                    .format(ver=ver, date=date, loc=loc)
            else:
                version = 'VPP version:{ver}'.format(ver=ver)
            logger.info(version)
        else:
            raise PapiError('No reply received for show_version API command on '
                            'host {host}'.format(host=node['host']))

    @staticmethod
    def vpp_show_version_verbose(node):
        """Run "show_version" API command and return verbose string of version
        data.

        :param node: Node to run command on.
        :type node: dict
        """
        VPPUtil.vpp_show_version(node, verbose=True)

    @staticmethod
    def show_vpp_version_on_all_duts(nodes):
        """Show VPP version on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VPPUtil.vpp_show_version_verbose(node)

    @staticmethod
    def vpp_show_interfaces(node):
        """Run "show interface" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_interface.vat", node, json_out=False)

        try:
            vat.script_should_have_passed()
        except AssertionError:
            raise RuntimeError('Failed to get VPP interfaces on host: {name}'.
                               format(name=node['host']))

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
    def vpp_api_trace_dump(node):
        """Run "api trace custom-dump" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("api_trace_dump.vat", node, json_out=False)

    @staticmethod
    def vpp_api_trace_save(node):
        """Run "api trace save" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("api_trace_save.vat", node, json_out=False)

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
