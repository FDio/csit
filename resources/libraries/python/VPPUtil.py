# Copyright (c) 2024 Cisco and/or its affiliates.
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
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.model.ExportResult import (
    export_dut_type_and_version
)
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import Topology, SocketType, NodeType


class VPPUtil:
    """General class for any VPP related methods/functions."""

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

        VPPUtil.stop_vpp_service(node)
        command = "/usr/bin/vpp -c /etc/vpp/startup.conf"
        message = f"Node {node[u'host']} failed to start VPP!"
        exec_cmd_no_error(
            node, command, timeout=180, sudo=True, message=message
        )

        if node_key:
            Topology.add_new_socket(
                node, SocketType.CLI, node_key, Constants.SOCKCLI_PATH)
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
        PapiSocketExecutor.disconnect_all_sockets_by_node(node)
        command = "pkill -9 vpp; sleep 1"
        exec_cmd(node, command, timeout=180, sudo=True)
        command = (
            "/bin/rm -f /dev/shm/db /dev/shm/global_vm /dev/shm/vpe-api"
        )
        exec_cmd(node, command, timeout=180, sudo=True)

        if node_key:
            if Topology.get_node_sockets(node, socket_type=SocketType.PAPI):
                Topology.del_node_socket_id(node, SocketType.PAPI, node_key)
            if Topology.get_node_sockets(node, socket_type=SocketType.STATS):
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
    def install_vpp_on_all_duts(nodes, vpp_pkg_dir):
        """Install VPP on all DUT nodes.

        :param nodes: Nodes in the topology.
        :param vpp_pkg_dir: Path to directory where VPP packages are stored.
        :type nodes: dict
        :type vpp_pkg_dir: str
        """
        VPPUtil.stop_vpp_service_on_all_duts(nodes)
        for node in nodes.values():
            message = f"Failed to install VPP on host {node['host']}!"
            if node["type"] == NodeType.DUT:
                command = "mkdir -p /var/log/vpp/"
                exec_cmd(node, command, sudo=True)

                command = "ln -s /dev/null /etc/systemd/system/vpp.service"
                exec_cmd(node, command, sudo=True)

                command = "ln -s /dev/null /etc/sysctl.d/80-vpp.conf"
                exec_cmd(node, command, sudo=True)

                command = "apt-get purge -y '*vpp*' || true"
                exec_cmd_no_error(node, command, timeout=120, sudo=True)

                command = f"dpkg -i --force-all {vpp_pkg_dir}*.deb"
                exec_cmd_no_error(
                    node, command, timeout=120, sudo=True, message=message
                )

                command = "dpkg -l | grep vpp"
                exec_cmd_no_error(node, command, sudo=True)

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
    def verify_vpp(node, api_trace=False):
        """Verify that VPP is installed and started on the specified topology
        node. Adjust privileges so user can connect without sudo.

        :param node: Topology node.
        :param api_trace: Whether to enable API trace.
            Only the tested VPP instance should attempt this,
            e.g. not in suite setup when determining interfaces.
        :type node: dict
        :type api_trace: bool
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
            if api_trace and Constants.USE_VPP_API_TRACE:
                # All subsequent PAPI interaction may need to be traced.
                VPPUtil.enable_vpp_api_trace(node)
        finally:
            DUTSetup.get_service_logs(node, Constants.VPP_UNIT)

    @staticmethod
    def vpp_show_version(
            node, remote_vpp_socket=Constants.SOCKSVR_PATH, log=True):
        """Run "show_version" PAPI command.

        Socket is configurable, so VPP inside container can be accessed.
        The result is exported to JSON UTI output as "dut-version".

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
        version = f"{reply[u'version']}"
        export_dut_type_and_version(u"VPP", version)
        return version

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
    def enable_vpp_api_trace(node):
        """Enable API tracing on VPP.

        Only call when allowed by Constants.USE_VPP_API_TRACE please.

        :param node: Topology node.
        :type node: dict
        """
        # TODO: Support non-primary VPP instances,
        # e.g. inside container if reachable via SocketType.PAPI in topology.
        PapiSocketExecutor.run_cli_cmd(node, "api trace on")

    # There is chicken-or-egg problem between this PapiExecutor and PapiHistory.
    # The following keyword needs to acces both.
    # It cannot be in PapiHistory because that would cause an import loop.
    # It cannot be in PapiExecutor, as that is imported per-node,
    # so not directly importable from default.robot resource.
    # Putting this keyword here is ugly, but it works.
    @staticmethod
    def show_papi_history_on_all_duts(nodes):
        """Show PAPI command history for all DUT nodes.

        :param nodes: Nodes to show PAPI command history for.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                PapiHistory.show_papi_history(node)
                # TODO: Also support containers via sockets here.
                if Constants.USE_VPP_API_TRACE:
                    PapiSocketExecutor.run_cli_cmd(node, "api trace dump-json")

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
            u"trace add dpdk-input 50",
            u"trace add vhost-user-input 50",
            u"trace add memif-input 50",
            u"trace add avf-input 50"
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

    @staticmethod
    def vpp_set_neighbor_limit_on_all_duts(nodes, count):
        """VPP set neighbor count limit on all DUTs in the given topology.

        :param nodes: Nodes in the topology.
        :param count: Neighbor count need to set.
        :type nodes: dict
        :type count: int
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                cmd = f"set ip neighbor-config ip4 limit {count}"
                PapiSocketExecutor.run_cli_cmd(node, cmd)

                cmd = f"set ip neighbor-config ip6 limit {count}"
                PapiSocketExecutor.run_cli_cmd(node, cmd)
