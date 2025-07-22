# Copyright (c) 2025 Cisco and/or its affiliates.
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

"""Host Stack util library."""

import json
from time import sleep

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.model.ExportResult import (
    export_hoststack_results,
)
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import Topology


class HoststackUtil:
    """Utilities for Host Stack tests."""

    @staticmethod
    def _get_ldpreload_path(node):
        """Return the absolute path to VCL LD_PRELOAD library.

        If Constants override the path, return that.
        Otherwise return the default pattern, with arch value from topology.

        :param node: Topology node to decide architecture.
        :type node: dict
        :returns: Path to correct VCL preload library.
        :rtype: str
        """
        if ret := Constants.VCL_LDPRELOAD_LIBRARY:
            return ret
        arch = Topology.get_node_arch(node)
        return f"/usr/lib/{arch}-linux-gnu/libvcl_ldpreload.so"

    @staticmethod
    def get_vpp_echo_command(vpp_echo_attributes):
        """Construct the vpp_echo command using the specified attributes.

        :param vpp_echo_attributes: vpp_echo test program attributes.
        :type vpp_echo_attributes: dict
        :returns: Command line components of the vpp_echo command
            'name' - program name
            'args' - command arguments.
        :rtype: dict
        """
        proto = vpp_echo_attributes["uri_protocol"]
        addr = vpp_echo_attributes["uri_ip4_addr"]
        port = vpp_echo_attributes["uri_port"]
        vpp_echo_cmd = {}
        vpp_echo_cmd["name"] = "vpp_echo"
        vpp_echo_cmd["args"] = (
            f"{vpp_echo_attributes['role']} "
            f"socket-name {vpp_echo_attributes['app_api_socket']} "
            f"{vpp_echo_attributes['json_output']} "
            f"uri {proto}://{addr}/{port} "
            f"nthreads {vpp_echo_attributes['nthreads']} "
            f"mq-size {vpp_echo_attributes['mq_size']} "
            f"nclients {vpp_echo_attributes['nclients']} "
            f"quic-streams {vpp_echo_attributes['quic_streams']} "
            f"time {vpp_echo_attributes['time']} "
            f"fifo-size {vpp_echo_attributes['fifo_size']} "
            f"TX={vpp_echo_attributes['tx_bytes']} "
            f"RX={vpp_echo_attributes['rx_bytes']}"
        )
        if vpp_echo_attributes["rx_results_diff"]:
            vpp_echo_cmd["args"] += " rx-results-diff"
        if vpp_echo_attributes["tx_results_diff"]:
            vpp_echo_cmd["args"] += " tx-results-diff"
        if vpp_echo_attributes["use_app_socket_api"]:
            vpp_echo_cmd["args"] += " use-app-socket-api"
        return vpp_echo_cmd

    @staticmethod
    def get_iperf3_command(iperf3_attributes, node):
        """Construct the iperf3 command using the specified attributes.

        :param iperf3_attributes: iperf3 test program attributes.
        :param node: Topology node (architecture implies ldpreload path).
        :type iperf3_attributes: dict
        :type node: dict
        :returns: Command line components of the iperf3 command
            'env_vars' - environment variables
            'name' - program name
            'args' - command arguments.
        :rtype: dict
        """
        iperf3_cmd = {}
        iperf3_cmd["env_vars"] = (
            f"VCL_CONFIG={Constants.REMOTE_FW_DIR}/"
            f"{Constants.RESOURCES_TPL_VCL}/"
            f"{iperf3_attributes['vcl_config']}"
        )
        if iperf3_attributes["ld_preload"]:
            ldpreload = HoststackUtil._get_ldpreload_path(node)
            iperf3_cmd["env_vars"] += f" LD_PRELOAD={ldpreload}"
        if iperf3_attributes["transparent_tls"]:
            iperf3_cmd["env_vars"] += " LDP_ENV_TLS_TRANS=1"

        json_results = " --json" if iperf3_attributes["json"] else ""
        ip_address = (
            f" {iperf3_attributes['ip_address']}"
            if "ip_address" in iperf3_attributes
            else ""
        )
        iperf3_cmd["name"] = "iperf3"
        iperf3_cmd["args"] = (
            f"--{iperf3_attributes['role']}{ip_address} "
            f"--interval 0{json_results} "
            f"--version{iperf3_attributes['ip_version']}"
        )

        if iperf3_attributes["role"] == "server":
            iperf3_cmd["args"] += " --one-off"
        else:
            iperf3_cmd["args"] += " --get-server-output"
            if "parallel" in iperf3_attributes:
                iperf3_cmd[
                    "args"
                ] += f" --parallel {iperf3_attributes['parallel']}"
            if "time" in iperf3_attributes:
                iperf3_cmd["args"] += f" --time {iperf3_attributes['time']}"
            if iperf3_attributes["udp"]:
                iperf3_cmd["args"] += " --udp"
                iperf3_cmd[
                    "args"
                ] += f" --bandwidth {iperf3_attributes['bandwidth']}"
            if iperf3_attributes["length"] > 0:
                iperf3_cmd[
                    "args"
                ] += f" --length {iperf3_attributes['length']}"
        return iperf3_cmd

    @staticmethod
    def set_hoststack_quic_fifo_size(node, fifo_size):
        """Set the QUIC protocol fifo size.

        :param node: Node to set the QUIC fifo size on.
        :param fifo_size: fifo size, passed to the quic set fifo-size command.
        :type node: dict
        :type fifo_size: str
        """
        cmd = f"quic set fifo-size {fifo_size}"
        PapiSocketExecutor.run_cli_cmd(node, cmd)

    @staticmethod
    def set_hoststack_quic_crypto_engine(
        node, quic_crypto_engine, fail_on_error=False
    ):
        """Set the Hoststack QUIC crypto engine on node

        :param node: Node to enable/disable HostStack.
        :param quic_crypto_engine: type of crypto engine
        :type node: dict
        :type quic_crypto_engine: str
        """
        vpp_crypto_engines = {"openssl", "native", "ipsecmb"}
        if quic_crypto_engine == "nocrypto":
            logger.trace("No QUIC crypto engine.")
            return

        if quic_crypto_engine in vpp_crypto_engines:
            cmds = [
                "quic set crypto api vpp",
                f"set crypto handler aes-128-gcm {quic_crypto_engine}",
                f"set crypto handler aes-256-gcm {quic_crypto_engine}",
            ]
        elif quic_crypto_engine == "picotls":
            cmds = ["quic set crypto api picotls"]
        else:
            raise ValueError(f"Unknown QUIC crypto_engine {quic_crypto_engine}")

        for cmd in cmds:
            try:
                PapiSocketExecutor.run_cli_cmd(node, cmd)
            except AssertionError:
                if fail_on_error:
                    raise

    @staticmethod
    def _get_hoststack_test_program_logs(node, program_name):
        """Get HostStack test program stdout log.

        :param node: DUT node.
        :param program_name: test program.
        :type node: dict
        :type program_name: str
        """
        cmd = f"sh -c 'cat /tmp/{program_name}_stdout.log'"
        stdout_log, _ = exec_cmd_no_error(
            node,
            cmd,
            sudo=True,
            message=f"Get {program_name} stdout log failed!",
        )

        cmd = f"sh -c 'cat /tmp/{program_name}_stderr.log'"
        stderr_log, _ = exec_cmd_no_error(
            node,
            cmd,
            sudo=True,
            message=f"Get {program_name} stderr log failed!",
        )

        return stdout_log, stderr_log

    @staticmethod
    def get_hoststack_test_program_logs(node, program):
        """Get HostStack test program stdout log.

        :param node: DUT node.
        :param program: test program.
        :type node: dict
        :type program: dict
        """
        program_name = program["name"]
        program_stdout_log, program_stderr_log = (
            HoststackUtil._get_hoststack_test_program_logs(node, program_name)
        )
        if len(program_stdout_log) == 0 and len(program_stderr_log) == 0:
            logger.trace(f"Retrying {program_name} log retrieval")
            program_stdout_log, program_stderr_log = (
                HoststackUtil._get_hoststack_test_program_logs(
                    node, program_name
                )
            )
        return program_stdout_log, program_stderr_log

    @staticmethod
    def get_nginx_command(nginx_attributes, nginx_version, nginx_ins_dir, node):
        """Construct the NGINX command using the specified attributes.

        :param nginx_attributes: NGINX test program attributes.
        :param nginx_version: NGINX version.
        :param nginx_ins_dir: NGINX install dir.
        :param node: Topology node (architecture implies ldpreload path).
        :type nginx_attributes: dict
        :type nginx_version: str
        :type nginx_ins_dir: str
        :type node: dict
        :returns: Command line components of the NGINX command
            'env_vars' - environment variables
            'name' - program name
            'args' - command arguments.
            'path' - program path.
        :rtype: dict
        """
        nginx_cmd = dict()
        nginx_cmd["env_vars"] = (
            f"VCL_CONFIG={Constants.REMOTE_FW_DIR}/"
            f"{Constants.RESOURCES_TPL_VCL}/"
            f"{nginx_attributes['vcl_config']}"
        )
        if nginx_attributes["ld_preload"]:
            ldpreload = HoststackUtil._get_ldpreload_path(node)
            nginx_cmd["env_vars"] += f" LD_PRELOAD={ldpreload}"
        if nginx_attributes["transparent_tls"]:
            nginx_cmd["env_vars"] += " LDP_ENV_TLS_TRANS=1"

        nginx_cmd["name"] = "nginx"
        nginx_cmd["path"] = f"{nginx_ins_dir}nginx-{nginx_version}/sbin/"
        nginx_cmd["args"] = (
            f"-c {nginx_ins_dir}/" f"nginx-{nginx_version}/conf/nginx.conf"
        )
        return nginx_cmd

    @staticmethod
    def start_hoststack_test_program(node, namespace, core_list, program):
        """Start the specified HostStack test program.

        :param node: DUT node.
        :param namespace: Net Namespace to run program in.
        :param core_list: List of cpu's to pass to taskset to pin the test
            program to a different set of cores on the same numa node as VPP.
        :param program: Test program.
        :type node: dict
        :type namespace: str
        :type core_list: str
        :type program: dict
        :returns: Process ID
        :rtype: int
        :raises RuntimeError: If node subtype is not a DUT or startup failed.
        """
        if node["type"] != "DUT":
            raise RuntimeError("Node type is not a DUT!")

        program_name = program["name"]
        DUTSetup.kill_program(node, program_name, namespace)

        if namespace == "default":
            shell_cmd = "sh -c"
        else:
            shell_cmd = f"ip netns exec {namespace} sh -c"

        env_vars = f"{program['env_vars']} " if "env_vars" in program else ""
        args = program["args"]
        program_path = program.get("path", "")
        # NGINX used `worker_cpu_affinity` in configuration file
        taskset_cmd = ""
        if program_name != "nginx":
            taskset_cmd = f"taskset --cpu-list {core_list} chrt -r 99 "
        cmd = (
            f"nohup {taskset_cmd}{shell_cmd} '{env_vars} "
            f"{program_path}{program_name} {args} >/tmp/{program_name}_"
            f"stdout.log 2>/tmp/{program_name}_stderr.log &'"
        )
        try:
            exec_cmd_no_error(node, cmd, sudo=True)
            return DUTSetup.get_pid(node, program_name)[0]
        except RuntimeError:
            stdout_log, stderr_log = (
                HoststackUtil.get_hoststack_test_program_logs(node, program)
            )
            raise RuntimeError(
                f"Start {program_name} failed!\nSTDERR:\n"
                f"{stderr_log}\nSTDOUT:\n{stdout_log}"
            )
        return None

    @staticmethod
    def stop_hoststack_test_program(node, program, pid):
        """Stop the specified Hoststack test program.

        :param node: DUT node.
        :param program: Test program.
        :param pid: Process ID of test program.
        :type node: dict
        :type program: dict
        :type pid: int
        """
        program_name = program["name"]
        if program_name == "nginx":
            cmd = "nginx -s quit"
            errmsg = "Quit nginx failed!"
        else:
            cmd = (
                f'if [ -n "$(ps {pid} | grep {program_name})" ] ; '
                f"then kill -s SIGTERM {pid}; fi"
            )
            errmsg = f"Kill {program_name} ({pid}) failed!"

        exec_cmd_no_error(node, cmd, message=errmsg, sudo=True)

    @staticmethod
    def sleep_for_hoststack_test_duration(sleep_time):
        """Wait for the HostStack test program process to complete.

        :param sleep_time: waiting stecific time.
        """
        logger.info(f"Sleeping for {sleep_time} seconds")
        sleep(sleep_time + 1)

    @staticmethod
    def hoststack_test_program_finished(
        node, program_pid, program, other_node, other_program
    ):
        """Wait for the specified HostStack test program process to complete.

        :param node: DUT node.
        :param program_pid: test program pid.
        :param program: test program
        :param other_node: DUT node of other hoststack program
        :param other_program: other test program
        :type node: dict
        :type program_pid: str
        :type program: dict
        :type other_node: dict
        :type other_program: dict
        :raises RuntimeError: If node subtype is not a DUT.
        """
        if node["type"] != "DUT":
            raise RuntimeError("Node type is not a DUT!")
        if other_node["type"] != "DUT":
            raise RuntimeError("Other node type is not a DUT!")

        cmd = f"sh -c 'strace -qqe trace=none -p {program_pid}'"
        try:
            exec_cmd(node, cmd, sudo=True)
        except:
            sleep(180)
            if "client" in program["args"]:
                role = "client"
            else:
                role = "server"
            program_stdout, program_stderr = (
                HoststackUtil.get_hoststack_test_program_logs(node, program)
            )
            if len(program_stdout) > 0:
                logger.debug(
                    f"{program['name']} {role} stdout log:\n"
                    f"{program_stdout}"
                )
            else:
                logger.debug(f"Empty {program['name']} {role} stdout log :(")
            if len(program_stderr) > 0:
                logger.debug(
                    f"{program['name']} stderr log:\n" f"{program_stderr}"
                )
            else:
                logger.debug(f"Empty {program['name']} stderr log :(")
            if "client" in other_program["args"]:
                role = "client"
            else:
                role = "server"
            program_stdout, program_stderr = (
                HoststackUtil.get_hoststack_test_program_logs(
                    other_node, other_program
                )
            )
            if len(program_stdout) > 0:
                logger.debug(
                    f"{other_program['name']} {role} stdout log:\n"
                    f"{program_stdout}"
                )
            else:
                logger.debug(
                    f"Empty {other_program['name']} " f"{role} stdout log :("
                )
            if len(program_stderr) > 0:
                logger.debug(
                    f"{other_program['name']} {role} stderr log:\n"
                    f"{program_stderr}"
                )
            else:
                logger.debug(
                    f"Empty {other_program['name']} " f"{role} stderr log :("
                )
            raise
        # Wait a bit for stdout/stderr to be flushed to log files
        sleep(1)

    @staticmethod
    def analyze_hoststack_test_program_output(node, role, nsim_attr, program):
        """Gather HostStack test program output and check for errors.

        The [defer_fail] return bool is used instead of failing immediately
        to allow the analysis of both the client and server instances of
        the test program for debugging a test failure.  When [defer_fail]
        is true, then the string returned is debug output instead of
        JSON formatted test program results.

        :param node: DUT node.
        :param role: Role (client|server) of test program.
        :param nsim_attr: Network Simulation Attributes.
        :param program: Test program.
        :param program_args: List of test program args.
        :type node: dict
        :type role: str
        :type nsim_attr: dict
        :type program: dict
        :returns: tuple of [defer_fail] bool and either JSON formatted hoststack
            test program output or failure debug output.
        :rtype: bool, str
        :raises RuntimeError: If node subtype is not a DUT.
        """
        if node["type"] != "DUT":
            raise RuntimeError("Node type is not a DUT!")

        program_name = program["name"]
        program_stdout, program_stderr = (
            HoststackUtil.get_hoststack_test_program_logs(node, program)
        )

        env_vars = f"{program['env_vars']} " if "env_vars" in program else ""
        program_cmd = f"{env_vars}{program_name} {program['args']}"
        test_results = f"Test Results of '{program_cmd}':\n"

        if nsim_attr["output_nsim_enable"] or nsim_attr["xc_nsim_enable"]:
            if nsim_attr["output_nsim_enable"]:
                feature_name = "output"
            else:
                feature_name = "cross-connect"
            test_results += (
                f"NSIM({feature_name}): delay "
                f"{nsim_attr['delay_in_usec']} usecs, "
                f"avg-pkt-size {nsim_attr['average_packet_size']}, "
                f"bandwidth {nsim_attr['bw_in_bits_per_second']} "
                f"bits/sec, pkt-drop-rate {nsim_attr['packets_per_drop']} "
                f"pkts/drop\n"
            )

        if "error" in program_stderr.lower():
            test_results += f"ERROR DETECTED:\n{program_stderr}"
            return (True, test_results)
        if not program_stdout:
            test_results += f"\nNo {program} test data retrieved!\n"
            ls_stdout, _ = exec_cmd_no_error(
                node, "ls -l /tmp/*.log", sudo=True
            )
            test_results += f"{ls_stdout}\n"
            return (True, test_results)
        if program["name"] == "vpp_echo":
            if (
                "JSON stats" in program_stdout
                and '"has_failed": "0"' in program_stdout
            ):
                json_start = program_stdout.find("{")
                json_end = program_stdout.find(',\n  "closing"')
                json_results = f"{program_stdout[json_start:json_end]}\n}}"
                program_json = json.loads(json_results)
                export_hoststack_results(
                    bandwidth=program_json["rx_bits_per_second"],
                    duration=float(program_json["time"]),
                )
            else:
                test_results += "Invalid test data output!\n" + program_stdout
                return (True, test_results)
        elif program["name"] == "iperf3":
            test_results += program_stdout
            program_json = json.loads(program_stdout)["intervals"][0]["sum"]
            try:
                retransmits = program_json["retransmits"]
            except KeyError:
                retransmits = None
            export_hoststack_results(
                bandwidth=program_json["bits_per_second"],
                duration=program_json["seconds"],
                retransmits=retransmits,
            )
        else:
            test_results += "Unknown HostStack Test Program!\n" + program_stdout
            return (True, program_stdout)
        return (False, json.dumps(program_json))

    @staticmethod
    def hoststack_test_program_defer_fail(server_defer_fail, client_defer_fail):
        """Return True if either HostStack test program fail was deferred.

        :param server_defer_fail: server no results value.
        :param client_defer_fail: client no results value.
        :type server_defer_fail: bool
        :type client_defer_fail: bool
        :rtype: bool
        """
        return server_defer_fail and client_defer_fail
