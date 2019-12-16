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

"""Host Stack util library.
"""
from time import sleep
from robot.api import logger

from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.DUTSetup import DUTSetup
get_hoststack_app_pid = DUTSetup.get_app_pid

class HoststackUtil(object):
    """Utilities for Host Stack tests"""

    @staticmethod
    def get_vpp_echo_command (vpp_echo_attributes):
        """Construct the vpp_echo command using the specified attributes

        :param vpp_echo_attributes: vpp_echo application attributes
        :type vpp_echo_attributes: dict
        :returns vpp_echo command
        :rtype: list
        """
        proto = vpp_echo_attributes[u"uri_protocol"]
        addr = vpp_echo_attributes[u"uri_ip4_addr"]
        port = vpp_echo_attributes[u"uri_port"]
        vpp_echo_cmd = [u"vpp_echo", vpp_echo_attributes[u"role"],
            u"test-bytes", u"socket-name",
            vpp_echo_attributes[u"vpp_api_socket"],
            vpp_echo_attributes[u"json_output"],
            u"uri", f"{proto}://{addr}/{port}",
            u"nclients", vpp_echo_attributes[u"nclients"],
            u"quic-streams", vpp_echo_attributes[u"quic_streams"],
            u"time", vpp_echo_attributes[u"time"],
            u"fifo-size", vpp_echo_attributes[u"fifo_size"],
            f"TX={vpp_echo_attributes[u'tx_bytes']}",
            f"RX={vpp_echo_attributes[u'rx_bytes']}"]
        if vpp_echo_attributes[u"rx_results_diff"] == True:
            vpp_echo_cmd.append(u"rx-results-diff")
        if vpp_echo_attributes[u"tx_results_diff"] == True:
            vpp_echo_cmd.append(u"tx-results-diff")
        return vpp_echo_cmd

    @staticmethod
    def hoststack_session_enable(node):
        """Enable HostStack Sessions on node

        :param node: Node to enable/disable HostStack.
        :type node: dict
        """
        cmd = u"session_enable_disable"
        args = dict(is_enable = 1)
        err_msg = f"Failed to enable HostStack on {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def set_hoststack_quic_fifo_size(node, fifo_size):
        """Set the QUIC protocol fifo size

        :param node: Node to set the QUIC fifo size on
        :param fifo_size: fifo size, passed to the quic set fifo-size command
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
            logger.trace(cmd)
            try:
                PapiSocketExecutor.run_cli_cmd(node, cmd)
            except AssertionError:
                raise

    @staticmethod
    def get_hoststack_app_logs (node, app):
        """Get HostStack external application stdout log.

        :param node: DUT node
        :param app: External application name
        :type node: dict
        :type app: str
        """
        cmd = f"sh -c \'cat /tmp/{app}_stdout.log\'"
        stdout_log, _ = exec_cmd_no_error(node, cmd, sudo=True,
            message=f"Get {app} stdout log failed!")

        cmd = f"sh -c \'cat /tmp/{app}_stderr.log\'"
        stderr_log, _ = exec_cmd_no_error(node, cmd, sudo=True,
            message=f"Get {app} stderr log failed!")
        return stdout_log, stderr_log

    @staticmethod
    def start_hoststack_external_app(node, namespace, app, *args):
        """Startup sequence for HostStack external application.

        :param node: DUT node
        :param namespace: Net Namespace to run app in
        :param app: External application name
        :param args: List of application args
        :type node: dict
        :type namespace: str
        :type app: str
        :type args list
        :returns App Process ID
        :rtype: int
        :raises RuntimeError: If node subtype is not a DUT or startup failed.
        """
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")

        DUTSetup.kill_program(node, app, namespace)

        opts=u" ".join([str(x) for x in args])
        cmd = f"{shell_cmd} '{app} {opts} >/tmp/{app}_stdout.log" \
            f" 2>/tmp/{app}_stderr.log &'"
        try:
            exec_cmd_no_error(node, cmd, sudo=True)
            return get_hoststack_app_pid(node, app)[0]
        except RuntimeError:
            stdout_log, stderr_log = \
                HoststackUtil.get_hoststack_app_logs(node, app)
            raise RuntimeError(f"Start {app} failed!\nSTDERR:\n{stderr_log}" \
                               f"nSTDOUT:\n{stdout_log}")
        return None

    @staticmethod
    def stop_hoststack_external_app(node, app, pid):
        """Startup sequence for HostStack external application.

        :param node: DUT node
        :param app: External application name
        :param pid: Process ID of external application
        :type node: dict
        :type app: str
        :type pid: int
        """
        if app == u"nginx":
            cmd = u"nginx -s quit"
            errmsg = u"Quit nginx failed!"
        else:
            cmd = f'if [-n "$(ps {pid} | grep {app})" ] ; ' \
                f'then kill -s SIGTERM {pid}'
            errmsg = f"Kill {app} ({pid)} failed!"

        exec_cmd_no_error(node, cmd, message=errmsg, sudo=True)

    @staticmethod
    def hoststack_external_app_finished(node, app_pid):
        """Startup sequence for HostStack external application.

        :param node: DUT node
        :param app_pid: External application pid
        :type node: dict
        :type app_pid: str
        :raises RuntimeError: If node subtype is not a DUT.
        """
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")

        cmd = f"sh -c 'strace -qqe trace=none -p {app_pid}' || true"
        exec_cmd_no_error(node, cmd, sudo=True)
        sleep(1)

    @staticmethod
    def analyze_hoststack_external_app_output(node, role, nsim_attr,
                                              app, app_args):
        """Startup sequence for HostStack external application.

        :param node: DUT node
        :param role: Role (client|server) of application
        :param nsim_attr: Network Simulation Attributes
        :param app: External application name
        :param app_args: List of application args
        :type node: dict
        :type role: str
        :type nsim_attr: dict
        :type app: str
        :type app_args str
        :returns application results
        :rtype str
        :raises RuntimeError: If node subtype is not a DUT.
        """
        if node[u"type"] != u"DUT":
            raise RuntimeError(u"Node type is not a DUT!")

        app_stdout, app_stderr = \
            HoststackUtil.get_hoststack_app_logs(node, app)
        if len(app_stdout) == 0 and len(app_stderr) == 0:
            logger.trace(f"Retrying {app} log retrieval")
            app_stdout, app_stderr =
               HoststackUtil.get_hoststack_app_logs(node, app)

        logger.trace(f"app_stdout = |{app_stdout}|")
        logger.trace(f"app_stderr = |{app_stderr}|")

        no_results = False
        app_cmd = f"{app}"
        for x in app_args:
            app_cmd += f" {x}"
        test_results = f"Test Results of '{app_cmd}':\n"

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

        if u"error" in app_stderr.lower():
            test_results += u"ERROR DETECTED:\n"
            stderr_list = app_stderr.splitlines()
            for x in stderr_list:
                test_results += f"{x}\n"
            raise RuntimeError(test_results)
        elif len(app_stdout) == 0:
            no_results = True
            warning_msg=u"!!!!! DANGER, WILL ROBINSON, DANGER !!!!!"
            test_results += f"\n{warning_msg}\nNo {app} test data retrieved!\n"
            cmd=u"ls -l /tmp/*.log"
            ls_stdout, _ = exec_cmd_no_error(node, cmd, sudo=True)
            test_results += f"{ls_stdout}{warning_msg}\n"
        else:
            bad_test_results = False
            if app == u"vpp_echo" and not u"JSON stats" in app_stdout:
                test_results += u"Invalid test data output!\n"
                bad_test_results = True
            stdout_list = app_stdout.splitlines()
            for x in stdout_list:
                test_results += f"{x}\n"
            if bad_test_results == True:
                raise RuntimeError(test_results)

        #TODO: Incorporate show error stats into results analysis
        host = node[u"host"]
        show_errors = PapiSocketExecutor.run_cli_cmd(node, u"show error")
        test_results += f"\n{role} VPP 'show errors' on host {host}:\n" \
                        f"{show_errors}\n"

        # TODO: Restore no_results retval after vpp_echo app stops crashing
        no_results = False
        return no_results, test_results

    @staticmethod
    def no_hoststack_external_app_results(server_no_results, client_no_results):
        return server_no_results and client_no_results

    @staticmethod
    def get_hoststack_sessions (node, verbose=1):
        """Get HostStack session information.

        :param node: DUT node
        :param verbose: verbose level of show session output
        :type node: dict
        :type verbose: int
        :raises RuntimeError: if verbose argument is invalid
        """
        if not verbose == 1 or verbose == 2:
            raise RuntimeError(f"Invalid verbose level: {verbose!s}!")

        if verbose == 2:
            cmd = u"show session verbose 2"
        else:
            cmd = u"show session verbose"

        logger.trace(cmd)
        try:
            response = PapiSocketExecutor.run_cli_cmd(node, cmd)
        except AssertionError:
            raise

        return response[u"reply"]
