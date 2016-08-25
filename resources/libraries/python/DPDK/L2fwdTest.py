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


"""
This module exists to provide the l2fwd test for DPDK on topology nodes.
"""

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as con
from resources.libraries.python.topology import Topology

class L2fwdTest(object): # pylint: disable=too-few-public-methods
    """Test the DPDK l2fwd performance."""

    @staticmethod
    def start_the_l2fwd_test(dut_node, cpu_coremask, nb_cores, queue_nums,
                            jumbo_frames):
        """
        Execute the udpfwd on the dut_node.

        :param dut_node: will execute the udpfwd on this node
        :param dut_if: DUT interface name
        :param file_prefix: the test case config file prefix
        :param dest_ip: the UDP packet dest IP
        :param is_ipv4: execute the IPv4 or IPv6 test
        :type dut_node: dict
        :type dut_if: str
        :type file_prefix: str
        :type dest_ip: str
        :type is_ipv4: bool
        :return: none
        """
        ssh = SSH()
        ssh.connect(dut_node)

        cmd = 'cd {0}/dpdk-tests/dpdk_scripts/ && ./run_l2fwd.sh {1} {2} {3} {4}' \
              .format(con.REMOTE_FW_DIR, cpu_coremask,
              nb_cores, queue_nums, jumbo_frames)

        logger.console('Will Execute the cmd: {0}'.format(cmd))

        (ret_code, _, stderr) = ssh.exec_command(cmd, timeout=600)
        if 0 != ret_code:
            logger.error('Execute the l2fwd error: {0}'.format(stderr))
            raise Exception('Failed to execute l2fwd test at node {0}'
                            .format(dut_node['host']))

