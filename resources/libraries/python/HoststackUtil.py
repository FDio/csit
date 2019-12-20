# Copyright (c) 2020 Cisco and/or its affiliates.
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
from time import sleep
from robot.api import logger

from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.DUTSetup import DUTSetup

class HoststackUtil(object):
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
        # TODO: Use a python class instead of dictionary for the return type
        proto = vpp_echo_attributes[u"uri_protocol"]
        addr = vpp_echo_attributes[u"uri_ip4_addr"]
        port = vpp_echo_attributes[u"uri_port"]
        vpp_echo_cmd = {}
        vpp_echo_cmd[u"name"] = u"vpp_echo"
        vpp_echo_cmd[u"args"] = f"{vpp_echo_attributes[u'role']} " \
            f"socket-name {vpp_echo_attributes[u'vpp_api_socket']} " \
            f"{vpp_echo_attributes[u'json_output']} " \
            f"uri {proto}://{addr}/{port} " \
            f"nclients {vpp_echo_attributes[u'nclients']} " \
            f"quic-streams {vpp_echo_attributes[u'quic_streams']} " \
            f"time {vpp_echo_attributes[u'time']} " \
            f"fifo-size {vpp_echo_attributes[u'fifo_size']} " \
            f"TX={vpp_echo_attributes[u'tx_bytes']} " \
            f"RX={vpp_echo_attributes[u'rx_bytes']}"
        if vpp_echo_attributes[u"rx_results_diff"] == True:
            vpp_echo_cmd[u"args"] += u" rx-results-diff"
        if vpp_echo_attributes[u"tx_results_diff"] == True:
            vpp_echo_cmd[u"args"] += u" tx-results-diff"
        return vpp_echo_cmd

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
    def set_hoststack_quic_crypto_engine(node, quic_crypto_engine):
        """Set the Hoststack QUIC crypto engine on node

        :param node: Node to enable/disable HostStack.
        :param quic_crypto_engine: type of crypto engine
        :type node: dict
        :type quic_crypto_engine: str
        """
        vpp_crypto_engines = {u"openssl", u"ia32", u"ipsecmb"}
        if quic_crypto_engine == u"nocrypto":
            logger.trace(u"No QUIC crypto engine.")
            return

        if quic_crypto_engine in vpp_crypto_engines:
            cmds = [ u"quic set crypto api vpp",
                     f"set crypto handler aes-128-gcm {quic_crypto_engine}",
                     f"set crypto handler aes-256-gcm {quic_crypto_engine}" ]
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
    def get_hoststack_test_program_logs (node, program):
        """Get HostStack test program stdout log.

        :param node: DUT node.
        :param program: test program.
        :type node: dict
        :type program: dict
        """
        program_name = program[u"name"]
        cmd = f"sh -c \'cat /tmp/{program_name}_stdout.log\'"
        stdout_log, _ = exec_cmd_no_error(node, cmd, sudo=True,
            message=f"Get {program_name} stdout log failed!")

        cmd = f"sh -c \'cat /tmp/{program_name}_stderr.log\'"
        stderr_log, _ = exec_cmd_no_error(node, cmd, sudo=True,
            message=f"Get {program_name} stderr log failed!")
        return stdout_log, stderr_log

    @staticmethod
    def start_hoststack_test_program(node, namespace, program):
        """Start the specified HostStack test program.

        :param node: DUT node.
        :param namespace: Net Namespace to run program in.
        :param program: Test program.
        :type node: dict
        :type namespace: str
        :type program: dict
        :returns: Process ID
        :rtype: int
        :raises RuntimeError: If node subtype is not a DUT or startup failed.
        """
        # TODO: Pin test program to core(s) on same numa node as VPP.
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")

        DUTSetup.kill_program(node, program[u"name"], namespace)

        if namespace == u"default":
            shell_cmd=u"sh -c"
        else:
            shell_cmd=f"ip netns exec {namespace} sh -c"

        env_vars = f"{program[u'env_vars']} " if u"env_vars" in program else u""
        program_name = program[u"name"]
        args = program[u"args"]
        cmd = f"nohup {shell_cmd} \'{env_vars}{program_name} {args} " \
            f">/tmp/{program_name}_stdout.log " \
            f"2>/tmp/{program_name}_stderr.log &\'"
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
    def hoststack_test_program_finished(node, program_pid):
        """Wait for the specified HostStack test program process to complete.

        :param node: DUT node.
        :param program_pid: test program pid.
        :type node: dict
        :type program_pid: str
        :raises RuntimeError: If node subtype is not a DUT.
        """
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")

        cmd = f"sh -c 'strace -qqe trace=none -p {program_pid}'"
        exec_cmd(node, cmd, sudo=True)
        # Wait a bit for stdout/stderr to be flushed to log files
        # TODO: see if sub-second sleep works e.g. sleep(0.1)
        sleep(1)

    @staticmethod
    def analyze_hoststack_test_program_output(node, role, nsim_attr,
                                              program):
        """Gather HostStack test program output and check for errors.

        :param node: DUT node.
        :param role: Role (client|server) of test program.
        :param nsim_attr: Network Simulation Attributes.
        :param program: Test program.
        :param program_args: List of test program args.
        :type node: dict
        :type role: str
        :type nsim_attr: dict
        :type program: dict
        :returns: tuple of no results bool and test program results.
        :rtype: bool, str
        :raises RuntimeError: If node subtype is not a DUT.
        """
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")

        program_name = program[u"name"]
        program_stdout, program_stderr = \
            HoststackUtil.get_hoststack_test_program_logs(node, program)
        if len(program_stdout) == 0 and len(program_stderr) == 0:
            logger.trace(f"Retrying {program_name} log retrieval")
            program_stdout, program_stderr = \
               HoststackUtil.get_hoststack_test_program_logs(node, program)

        no_results = False
        env_vars = f"program[u'env_vars'] " if u"env_vars" in program else u""
        program_cmd = f"{env_vars}{program_name} {program[u'args']}"
        test_results = f"Test Results of '{program_cmd}':\n"

        if nsim_attr[u"output_feature_enable"] == True or \
            nsim_attr[u"cross_connect_feature_enable"] == True:
            if nsim_attr[u"output_feature_enable"] == True:
                feature_name = u"output"
            else:
                feature_name = u"cross-connect"
            delay = nsim_attr[u"delay_in_usec"],
            pkt_sz = nsim_attr[u"average_packet_size"],
            bw = nsim_attr[u"bandwidth_in_bits_per_second"],
            drop_rate = nsim_attr[u"packets_per_drop"]
            test_results += f"NSIM({feature_name}): delay {delay} usecs, " \
                f"avg-pkt-size {pkt_sz}, bandwidth {bw} bits/sec, " \
                f"pkt-drop-rate {drop_rate} pkts/drop\n"

        if u"error" in program_stderr.lower():
            test_results += f"ERROR DETECTED:\n{program_stderr}"
            raise RuntimeError(test_results)
        elif len(program_stdout) == 0:
            no_results = True
            test_results += f"\nNo {program} test data retrieved!\n"
            cmd=u"ls -l /tmp/*.log"
            ls_stdout, _ = exec_cmd_no_error(node, cmd, sudo=True)
            test_results += f"{ls_stdout}\n"
        else:
            bad_test_results = False
            if program == u"vpp_echo" and not u"JSON stats" in program_stdout:
                test_results += u"Invalid test data output!\n"
                bad_test_results = True
            test_results += program_stdout
            if bad_test_results == True:
                raise RuntimeError(test_results)

        # TODO: Incorporate show error stats into results analysis
        host = node[u"host"]
        show_errors = PapiSocketExecutor.run_cli_cmd(node, u"show error")
        test_results += f"\n{role} VPP 'show errors' on host {host}:\n" \
                        f"{show_errors}\n"

        return no_results, test_results

    @staticmethod
    def no_hoststack_test_program_results(server_no_results, client_no_results):
        """Return True if no HostStack test program output was gathered.

        :param server_no_results: server no results value.
        :param client_no_results: client no results value.
        :type server_no_results: bool
        :type client_no_results: bool
        :rtype: bool
        """
        return server_no_results and client_no_results
