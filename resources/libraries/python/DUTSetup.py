# Copyright (c) 2016 Cisco and/or its affiliates.
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

from time import time

from robot.api import logger

from resources.libraries.python.topology import NodeType
from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.VatExecutor import VatExecutor


class DUTSetup(object):
    @staticmethod
    def start_vpp_service_on_all_duts(nodes):
        """Start up the VPP service on all nodes."""
        ssh = SSH()
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                ssh.connect(node)
                (ret_code, stdout, stderr) = \
                    ssh.exec_command_sudo('service vpp restart')
                if 0 != int(ret_code):
                    logger.debug('stdout: {0}'.format(stdout))
                    logger.debug('stderr: {0}'.format(stderr))
                    raise Exception('DUT {0} failed to start VPP service'.
                                    format(node['host']))

    @staticmethod
    def restart_vpp_on_dut_node(node):
        """Restart the VPP service on defined node.

        :param node: Node to restart VPP on.
        :type node: dict
        :return status: PASS or FAIL
        :return exec_time: Execution time [s] of vpp_restart command or None
        :rtype status: str
        :rtype exec_time: float
        """
        if node['type'] == NodeType.DUT:
            ssh = SSH()
            ssh.connect(node)
            start = time()
            (ret_code, stdout, stderr) = ssh.exec_command('sudo -S vpp_restart', timeout=20)
            exec_time = time() - start
            if 0 == int(ret_code):
                status = 'PASS'
                logger.debug('VPP successfully restarted on DUT node: {0}'.
                             format(node['host']))
                logger.debug('stdout: {0}'.format(stdout))
            else:
                status = 'FAIL'
                logger.debug('VPP failed to restart on DUT node: {0}'.
                             format(node['host']))
                logger.debug('stderr: {0}'.format(stderr))
        else:
            status = 'FAIL'
            exec_time = None
            logger.debug('Node is not DUT type: {0}'.format(node['host']))

        return status, exec_time

    @staticmethod
    def vpp_show_version_verbose(node):
        """Run "show version verbose" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_version_verbose.vat", node, json_out=False)

    @staticmethod
    def vpp_api_trace_save(node):
        """Run "api trace save" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("api_trace_save.vat", node, json_out=False)

    @staticmethod
    def vpp_api_trace_dump(node):
        """Run "api trace custom-dump" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("api_trace_dump.vat", node, json_out=False)

    @staticmethod
    def setup_all_duts(nodes):
        """Prepare all DUTs in given topology for test execution."""
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                DUTSetup.setup_dut(node)

    @staticmethod
    def setup_dut(node):
        ssh = SSH()
        ssh.connect(node)

        (ret_code, stdout, stderr) = \
            ssh.exec_command('sudo -Sn bash {0}/{1}/dut_setup.sh'.format(
                Constants.REMOTE_FW_DIR, Constants.RESOURCES_LIB_SH))
        logger.trace(stdout)
        logger.trace(stderr)
        if 0 != int(ret_code):
            logger.debug('DUT {0} setup script failed: "{1}"'.
                         format(node['host'], stdout + stderr))
            raise Exception('DUT test setup script failed at node {}'.
                            format(node['host']))
