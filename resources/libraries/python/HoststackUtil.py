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

"""Host Stack util library."""
import json
from time import sleep
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.model.ExportResult import (
    export_hoststack_results
)
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error

class HoststackUtil():
    """Utilities for Host Stack tests."""

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
        proto = vpp_echo_attributes[u"uri_protocol"]
        addr = vpp_echo_attributes[u"uri_ip4_addr"]
        port = vpp_echo_attributes[u"uri_port"]
        vpp_echo_cmd = {}
        vpp_echo_cmd[u"name"] = u"vpp_echo"
        vpp_echo_cmd[u"args"] = f"{vpp_echo_attributes[u'role']} " \
            f"socket-name {vpp_echo_attributes[u'app_api_socket']} " \
            f"{vpp_echo_attributes[u'json_output']} " \
            f"uri {proto}://{addr}/{port} " \
            f"nthreads {vpp_echo_attributes[u'nthreads']} " \
            f"mq-size {vpp_echo_attributes[u'mq_size']} " \
            f"nclients {vpp_echo_attributes[u'nclients']} " \
            f"quic-streams {vpp_echo_attributes[u'quic_streams']} " \
            f"time {vpp_echo_attributes[u'time']} " \
            f"fifo-size {vpp_echo_attributes[u'fifo_size']} " \
            f"TX={vpp_echo_attributes[u'tx_bytes']} " \
            f"RX={vpp_echo_attributes[u'rx_bytes']}"
        if vpp_echo_attributes[u"rx_results_diff"]:
            vpp_echo_cmd[u"args"] += u" rx-results-diff"
        if vpp_echo_attributes[u"tx_results_diff"]:
            vpp_echo_cmd[u"args"] += u" tx-results-diff"
        if vpp_echo_attributes[u"use_app_socket_api"]:
            vpp_echo_cmd[u"args"] += u" use-app-socket-api"
        return vpp_echo_cmd

    @staticmethod
    def get_iperf3_command(iperf3_attributes):
        """Construct the iperf3 command using the specified attributes.

        :param iperf3_attributes: iperf3 test program attributes.
        :type iperf3_attributes: dict
        :returns: Command line components of the iperf3 command
            'env_vars' - environment variables
            'name' - program name
            'args' - command arguments.
        :rtype: dict
        """
        iperf3_cmd = {}
        iperf3_cmd[u"env_vars"] = f"VCL_CONFIG={Constants.REMOTE_FW_DIR}/" \
            f"{Constants.RESOURCES_TPL_VCL}/" \
            f"{iperf3_attributes[u'vcl_config']}"
        if iperf3_attributes[u"ld_preload"]:
            iperf3_cmd[u"env_vars"] += \
                f" LD_PRELOAD={Constants.VCL_LDPRELOAD_LIBRARY}"
        if iperf3_attributes[u'transparent_tls']:
            iperf3_cmd[u"env_vars"] += u" LDP_ENV_TLS_TRANS=1"

        json_results = u" --json" if iperf3_attributes[u'json'] else u""
        ip_address = f" {iperf3_attributes[u'ip_address']}" if u"ip_address" \
                     in iperf3_attributes else u""
        iperf3_cmd[u"name"] = u"iperf3"
        iperf3_cmd[u"args"] = f"--{iperf3_attributes[u'role']}{ip_address} " \
                              f"--interval 0{json_results} " \
                              f"--version{iperf3_attributes[u'ip_version']}"

        if iperf3_attributes[u"role"] == u"server":
            iperf3_cmd[u"args"] += u" --one-off"
        else:
            iperf3_cmd[u"args"] += u" --get-server-output"
            if u"parallel" in iperf3_attributes:
                iperf3_cmd[u"args"] += \
                    f" --parallel {iperf3_attributes[u'parallel']}"
            if u"time" in iperf3_attributes:
                iperf3_cmd[u"args"] += \
                    f" --time {iperf3_attributes[u'time']}"
            if iperf3_attributes[u"udp"]:
                iperf3_cmd[u"args"] += u" --udp"
                iperf3_cmd[u"args"] += \
                    f" --bandwidth {iperf3_attributes[u'bandwidth']}"
            if iperf3_attributes[u"length"] > 0:
                iperf3_cmd[u"args"] += \
                    f" --length {iperf3_attributes[u'length']}"
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
    def set_hoststack_quic_crypto_engine(node, quic_crypto_engine,
                                         fail_on_error=False):
        """Set the Hoststack QUIC crypto engine on node

        :param node: Node to enable/disable HostStack.
        :param quic_crypto_engine: type of crypto engine
        :type node: dict
        :type quic_crypto_engine: str
        """
        vpp_crypto_engines = {u"openssl", u"native", u"ipsecmb"}
        if quic_crypto_engine == u"nocrypto":
            logger.trace(u"No QUIC crypto engine.")
            return

        if quic_crypto_engine in vpp_crypto_engines:
            cmds = [u"quic set crypto api vpp",
                    f"set crypto handler aes-128-gcm {quic_crypto_engine}",
                    f"set crypto handler aes-256-gcm {quic_crypto_engine}"]
        elif quic_crypto_engine == u"picotls":
            cmds = [u"quic set crypto api picotls"]
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
        cmd = f"sh -c \'cat /tmp/{program_name}_stdout.log\'"
        stdout_log, _ = exec_cmd_no_error(node, cmd, sudo=True, \
            message=f"Get {program_name} stdout log failed!")

        cmd = f"sh -c \'cat /tmp/{program_name}_stderr.log\'"
        stderr_log, _ = exec_cmd_no_error(node, cmd, sudo=True, \
            message=f"Get {program_name} stderr log failed!")

        return stdout_log, stderr_log

    @staticmethod
    def get_hoststack_test_program_logs(node, program):
        """Get HostStack test program stdout log.

        :param node: DUT node.
        :param program: test program.
        :type node: dict
        :type program: dict
        """
        program_name = program[u"name"]
        program_stdout_log, program_stderr_log = \
            HoststackUtil._get_hoststack_test_program_logs(node,
                                                           program_name)
        if len(program_stdout_log) == 0 and len(program_stderr_log) == 0:
            logger.trace(f"Retrying {program_name} log retrieval")
            program_stdout_log, program_stderr_log = \
               HoststackUtil._get_hoststack_test_program_logs(node,
                                                              program_name)
        return program_stdout_log, program_stderr_log

    @staticmethod
    def get_nginx_command(nginx_attributes, nginx_version, nginx_ins_dir):
        """Construct the NGINX command using the specified attributes.

        :param nginx_attributes: NGINX test program attributes.
        :param nginx_version: NGINX version.
        :param nginx_ins_dir: NGINX install dir.
        :type nginx_attributes: dict
        :type nginx_version: str
        :type nginx_ins_dir: str
        :returns: Command line components of the NGINX command
            'env_vars' - environment variables
            'name' - program name
            'args' - command arguments.
            'path' - program path.
        :rtype: dict
        """
        nginx_cmd = dict()
        nginx_cmd[u"env_vars"] = f"VCL_CONFIG={Constants.REMOTE_FW_DIR}/" \
                                 f"{Constants.RESOURCES_TPL_VCL}/" \
                                 f"{nginx_attributes[u'vcl_config']}"
        if nginx_attributes[u"ld_preload"]:
            nginx_cmd[u"env_vars"] += \
                f" LD_PRELOAD={Constants.VCL_LDPRELOAD_LIBRARY}"
        if nginx_attributes[u'transparent_tls']:
            nginx_cmd[u"env_vars"] += u" LDP_ENV_TLS_TRANS=1"

        nginx_cmd[u"name"] = u"nginx"
        nginx_cmd[u"path"] = f"{nginx_ins_dir}nginx-{nginx_version}/sbin/"
        nginx_cmd[u"args"] = f"-c {nginx_ins_dir}/" \
                             f"nginx-{nginx_version}/conf/nginx.conf"
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
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")

        program_name = program[u"name"]
        DUTSetup.kill_program(node, program_name, namespace)

        if namespace == u"default":
            shell_cmd = u"sh -c"
        else:
            shell_cmd = f"ip netns exec {namespace} sh -c"

        env_vars = f"{program[u'env_vars']} " if u"env_vars" in program else u""
        args = program[u"args"]
        program_path = program.get(u"path", u"")
        # NGINX used `worker_cpu_affinity` in configuration file
        taskset_cmd = u"" if program_name == u"nginx" else \
                                             f"taskset --cpu-list {core_list}"
        cmd = f"nohup {shell_cmd} \'{env_vars}{taskset_cmd} " \
              f"{program_path}{program_name} {args} >/tmp/{program_name}_" \
              f"stdout.log 2>/tmp/{program_name}_stderr.log &\'"
        try:
            exec_cmd_no_error(node, cmd, sudo=True)
            return DUTSetup.get_pid(node, program_name)[0]
        except RuntimeError:
            stdout_log, stderr_log = \
                HoststackUtil.get_hoststack_test_program_logs(node,
                                                              program)
            raise RuntimeError(f"Start {program_name} failed!\nSTDERR:\n" \
                               f"{stderr_log}\nSTDOUT:\n{stdout_log}")
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
        program_name = program[u"name"]
        if program_name == u"nginx":
            cmd = u"nginx -s quit"
            errmsg = u"Quit nginx failed!"
        else:
            cmd = f'if [ -n "$(ps {pid} | grep {program_name})" ] ; ' \
                f'then kill -s SIGTERM {pid}; fi'
            errmsg = f"Kill {program_name} ({pid}) failed!"

        exec_cmd_no_error(node, cmd, message=errmsg, sudo=True)

    @staticmethod
    def hoststack_test_program_finished(node, program_pid, program,
                                        other_node, other_program):
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
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")
        if other_node[u"type"] != u"DUT":
            raise RuntimeError(u"Other node type is not a DUT!")

        cmd = f"sh -c 'strace -qqe trace=none -p {program_pid}'"
        try:
            exec_cmd(node, cmd, sudo=True)
        except:
            sleep(180)
            if u"client" in program[u"args"]:
                role = u"client"
            else:
                role = u"server"
            program_stdout, program_stderr = \
                HoststackUtil.get_hoststack_test_program_logs(node, program)
            if len(program_stdout) > 0:
                logger.debug(f"{program[u'name']} {role} stdout log:\n"
                             f"{program_stdout}")
            else:
                logger.debug(f"Empty {program[u'name']} {role} stdout log :(")
            if len(program_stderr) > 0:
                logger.debug(f"{program[u'name']} stderr log:\n"
                             f"{program_stderr}")
            else:
                logger.debug(f"Empty {program[u'name']} stderr log :(")
            if u"client" in other_program[u"args"]:
                role = u"client"
            else:
                role = u"server"
            program_stdout, program_stderr = \
                HoststackUtil.get_hoststack_test_program_logs(other_node,
                                                              other_program)
            if len(program_stdout) > 0:
                logger.debug(f"{other_program[u'name']} {role} stdout log:\n"
                             f"{program_stdout}")
            else:
                logger.debug(f"Empty {other_program[u'name']} "
                             f"{role} stdout log :(")
            if len(program_stderr) > 0:
                logger.debug(f"{other_program[u'name']} {role} stderr log:\n"
                             f"{program_stderr}")
            else:
                logger.debug(f"Empty {other_program[u'name']} "
                             f"{role} stderr log :(")
            raise
        # Wait a bit for stdout/stderr to be flushed to log files
        sleep(1)

    @staticmethod
    def analyze_hoststack_test_program_output(
            node, role, nsim_attr, program):
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
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")

        program_name = program[u"name"]
        program_stdout, program_stderr = \
            HoststackUtil.get_hoststack_test_program_logs(node, program)

        env_vars = f"{program[u'env_vars']} " if u"env_vars" in program else u""
        program_cmd = f"{env_vars}{program_name} {program[u'args']}"
        test_results = f"Test Results of '{program_cmd}':\n"

        if nsim_attr[u"output_nsim_enable"] or \
            nsim_attr[u"xc_nsim_enable"]:
            if nsim_attr[u"output_nsim_enable"]:
                feature_name = u"output"
            else:
                feature_name = u"cross-connect"
            test_results += \
                f"NSIM({feature_name}): delay " \
                f"{nsim_attr[u'delay_in_usec']} usecs, " \
                f"avg-pkt-size {nsim_attr[u'average_packet_size']}, " \
                f"bandwidth {nsim_attr[u'bw_in_bits_per_second']} " \
                f"bits/sec, pkt-drop-rate {nsim_attr[u'packets_per_drop']} " \
                f"pkts/drop\n"

        if u"error" in program_stderr.lower():
            test_results += f"ERROR DETECTED:\n{program_stderr}"
            return (True, test_results)
        if not program_stdout:
            test_results += f"\nNo {program} test data retrieved!\n"
            ls_stdout, _ = exec_cmd_no_error(node, u"ls -l /tmp/*.log",
                                             sudo=True)
            test_results += f"{ls_stdout}\n"
            return (True, test_results)
        if program[u"name"] == u"vpp_echo":
            if u"JSON stats" in program_stdout and \
                    u'"has_failed": "0"' in program_stdout:
                json_start = program_stdout.find(u"{")
                json_end = program_stdout.find(u',\n  "closing"')
                json_results = f"{program_stdout[json_start:json_end]}\n}}"
                program_json = json.loads(json_results)
                export_hoststack_results(
                    bandwidth=program_json["rx_bits_per_second"],
                    duration=float(program_json["time"])
                )
            else:
                test_results += u"Invalid test data output!\n" + program_stdout
                return (True, test_results)
        elif program[u"name"] == u"iperf3":
            test_results += program_stdout
            program_json = json.loads(program_stdout)[u"intervals"][0][u"sum"]
            try:
                retransmits = program_json["retransmits"]
            except KeyError:
                retransmits = None
            export_hoststack_results(
                bandwidth=program_json["bits_per_second"],
                duration=program_json["seconds"],
                retransmits=retransmits
            )
        else:
            test_results += u"Unknown HostStack Test Program!\n" + \
                            program_stdout
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
