# Copyright (c) 2021 Cisco and/or its affiliates.
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

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import Topology, SocketType, NodeType


class VPPUtil:
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
            u"IPv6 FIB": u"ip6 fib",
            u"IPv4 FIB": u"ip fib",
            u"Interface IP": u"int addr",
            u"Interfaces": u"int",
            u"ARP": u"ip arp",
            u"Errors": u"err"
        }

        if additional_cmds:
            for cmd in additional_cmds:
                def_setting_tb_displayed[f"Custom Setting: {cmd}"] = cmd

        for _, cmd in def_setting_tb_displayed.items():
            command = f"vppctl sh {cmd}"
            exec_cmd_no_error(node, command, timeout=30, sudo=True)

    @staticmethod
    def restart_vpp_service(node, node_key=None):
        """Restart VPP service on the specified topology node.

        Disconnect possibly connected PAPI executor.

        :param node: Topology node.
        :param node_key: Topology node key.
        :type node: dict
        :type node_key: str
        """
        # Containers have a separate lifecycle, but better be safe.
        PapiSocketExecutor.disconnect_all_sockets_by_node(node)
        DUTSetup.restart_service(node, Constants.VPP_UNIT)
        if node_key:
            Topology.add_new_socket(
                node, SocketType.PAPI, node_key, Constants.SOCKSVR_PATH)
            Topology.add_new_socket(
                node, SocketType.STATS, node_key, Constants.SOCKSTAT_PATH)

    @staticmethod
    def restart_vpp_service_on_all_duts(nodes):
        """Restart VPP service on all DUT nodes.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node_key, node in nodes.items():
            if node[u"type"] == NodeType.DUT:
                VPPUtil.restart_vpp_service(node, node_key)

    @staticmethod
    def stop_vpp_service(node, node_key=None):
        """Stop VPP service on the specified topology node.

        Disconnect possibly connected PAPI executor.

        :param node: Topology node.
        :param node_key: Topology node key.
        :type node: dict
        :type node_key: str
        """
        # Containers have a separate lifecycle, but better be safe.
        PapiSocketExecutor.disconnect_all_sockets_by_node(node)
        DUTSetup.stop_service(node, Constants.VPP_UNIT)
        if node_key:
            Topology.del_node_socket_id(node, SocketType.PAPI, node_key)
            Topology.del_node_socket_id(node, SocketType.STATS, node_key)

    @staticmethod
    def stop_vpp_service_on_all_duts(nodes):
        """Stop VPP service on all DUT nodes.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node_key, node in nodes.items():
            if node[u"type"] == NodeType.DUT:
                VPPUtil.stop_vpp_service(node, node_key)

    @staticmethod
    def verify_vpp_installed(node):
        """Verify that VPP is installed on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        DUTSetup.verify_program_installed(node, u"vpp")

    @staticmethod
    def adjust_privileges(node):
        """Adjust privileges to control VPP without sudo.

        :param node: Topology node.
        :type node: dict
        """
        cmd = u"chmod -R o+rwx /run/vpp"
        exec_cmd_no_error(
            node, cmd, sudo=True, message=u"Failed to adjust privileges!",
            retries=120)

    @staticmethod
    def verify_vpp_started(node):
        """Verify that VPP is started on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        cmd = u"echo \"show pci\" | sudo socat - UNIX-CONNECT:/run/vpp/cli.sock"
        exec_cmd_no_error(
            node, cmd, sudo=False, message=u"VPP failed to start!", retries=120
        )

        cmd = u"vppctl show pci 2>&1 | fgrep -v \"Connection refused\" | " \
              u"fgrep -v \"No such file or directory\""
        exec_cmd_no_error(
            node, cmd, sudo=True, message=u"VPP failed to start!", retries=120
        )

        # Properly enable cards in case they were disabled. This will be
        # followed in https://jira.fd.io/browse/VPP-1934.
        cmd = u"for i in $(sudo vppctl sho int | grep Eth | cut -d' ' -f1); do"\
              u" sudo vppctl set int sta $i up; done"
        exec_cmd(node, cmd, sudo=False)

    @staticmethod
    def verify_vpp(node):
        """Verify that VPP is installed and started on the specified topology
        node. Adjust privileges so user can connect without sudo.

        :param node: Topology node.
        :type node: dict
        :raises RuntimeError: If VPP service fails to start.
        """
        DUTSetup.verify_program_installed(node, 'vpp')
        try:
            # Verify responsiveness of vppctl.
            VPPUtil.verify_vpp_started(node)
            # Adjust privileges.
            VPPUtil.adjust_privileges(node)
            # Verify responsiveness of PAPI.
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
            if node[u"type"] == NodeType.DUT:
                VPPUtil.verify_vpp(node)

    @staticmethod
    def vpp_show_version(
            node, remote_vpp_socket=Constants.SOCKSVR_PATH, log=True):
        """Run "show_version" PAPI command.

        Socket is configurable, so VPP inside container can be accessed.

        :param node: Node to run command on.
        :param remote_vpp_socket: Path to remote socket to target VPP.
        :param log: If true, show the result in Robot log.
        :type node: dict
        :type remote_vpp_socket: str
        :type log: bool
        :returns: VPP version.
        :rtype: str
        :raises RuntimeError: If PAPI connection fails.
        :raises AssertionError: If PAPI retcode is nonzero.
        """
        cmd = u"show_version"
        with PapiSocketExecutor(node, remote_vpp_socket) as papi_exec:
            reply = papi_exec.add(cmd).get_reply()
        if log:
            logger.info(f"VPP version: {reply[u'version']}\n")
        return f"{reply[u'version']}"

    @staticmethod
    def show_vpp_version_on_all_duts(nodes):
        """Show VPP version verbose on all DUTs.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                VPPUtil.vpp_show_version(node)

    @staticmethod
    def vpp_show_interfaces(node):
        """Run "show interface" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """

        cmd = u"sw_interface_dump"
        args = dict(
            name_filter_valid=False,
            name_filter=u""
        )
        err_msg = f"Failed to get interface dump on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        for if_dump in details:
            if_dump[u"l2_address"] = str(if_dump[u"l2_address"])
            if_dump[u"b_dmac"] = str(if_dump[u"b_dmac"])
            if_dump[u"b_smac"] = str(if_dump[u"b_smac"])
            if_dump[u"flags"] = if_dump[u"flags"].value
            if_dump[u"type"] = if_dump[u"type"].value
            if_dump[u"link_duplex"] = if_dump[u"link_duplex"].value
            if_dump[u"sub_if_flags"] = if_dump[u"sub_if_flags"].value \
                if hasattr(if_dump[u"sub_if_flags"], u"value") \
                else int(if_dump[u"sub_if_flags"])
        # TODO: return only base data
        logger.trace(f"Interface data of host {node[u'host']}:\n{details}")

    @staticmethod
    def vpp_enable_traces_on_dut(node, fail_on_error=False):
        """Enable vpp packet traces on the DUT node.

        :param node: DUT node to set up.
        :param fail_on_error: If True, keyword fails if an error occurs,
            otherwise passes.
        :type node: dict
        :type fail_on_error: bool
        """
        cmds = [
            u"trace add dpdk-input 500",
            u"trace add vhost-user-input 500",
            u"trace add memif-input 500",
            u"trace add avf-input 500"
        ]

        for cmd in cmds:
            try:
                PapiSocketExecutor.run_cli_cmd_on_all_sockets(node, cmd)
            except AssertionError:
                if fail_on_error:
                    raise

    @staticmethod
    def vpp_enable_traces_on_all_duts(nodes, fail_on_error=False):
        """Enable vpp packet traces on all DUTs in the given topology.

        :param nodes: Nodes in the topology.
        :param fail_on_error: If True, keyword fails if an error occurs,
            otherwise passes.
        :type nodes: dict
        :type fail_on_error: bool
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                VPPUtil.vpp_enable_traces_on_dut(node, fail_on_error)

    @staticmethod
    def vpp_enable_elog_traces(node):
        """Enable API/CLI/Barrier traces on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        try:
            PapiSocketExecutor.run_cli_cmd_on_all_sockets(
                node, u"event-logger trace api cli barrier")
        except AssertionError:
            # Perhaps an older VPP build is tested.
            PapiSocketExecutor.run_cli_cmd_on_all_sockets(
                node, u"elog trace api cli barrier")

    @staticmethod
    def vpp_enable_elog_traces_on_all_duts(nodes):
        """Enable API/CLI/Barrier traces on all DUTs in the given topology.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                VPPUtil.vpp_enable_elog_traces(node)

    @staticmethod
    def show_event_logger(node):
        """Show event logger on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node, u"show event-logger")

    @staticmethod
    def show_event_logger_on_all_duts(nodes):
        """Show event logger on all DUTs in the given topology.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                VPPUtil.show_event_logger(node)

    @staticmethod
    def show_log(node):
        """Show logging on the specified topology node.

        :param node: Topology node.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd(node, u"show logging")

    @staticmethod
    def show_log_on_all_duts(nodes):
        """Show logging on all DUTs in the given topology.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                VPPUtil.show_log(node)

    @staticmethod
    def vpp_show_threads(node):
        """Show VPP threads on node.

        :param node: Node to run command on.
        :type node: dict
        :returns: VPP thread data.
        :rtype: list
        """
        cmd = u"show_threads"
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply()

        threads_data = reply[u"thread_data"]
        logger.trace(f"show threads:\n{threads_data}")

        return threads_data

    @staticmethod
    def vpp_add_graph_node_next(node, graph_node_name, graph_next_name):
        """Set the next node for a given node.

        :param node: Node to run command on.
        :param graph_node_name: Graph node to add the next node on.
        :param graph_next_name: Graph node to add as the next node.
        :type node: dict
        :type graph_node_name: str
        :type graph_next_name: str
        :returns: The index of the next graph node.
        :rtype: int
        """
        cmd = u"add_node_next"
        args = dict(
            node_name=graph_node_name,
            next_name=graph_next_name
        )
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply()

        return reply[u"next_index"]
