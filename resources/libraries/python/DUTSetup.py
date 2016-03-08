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

from robot.api import logger
from topology import NodeType
from ssh import SSH
from constants import Constants


class DUTSetup(object):

    def start_vpp_service_on_all_duts(self, nodes):
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

    def setup_all_duts(self, nodes):
        """Prepare all DUTs in given topology for test execution."""
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                self.setup_dut(node)

    def setup_dut(self, node):
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
