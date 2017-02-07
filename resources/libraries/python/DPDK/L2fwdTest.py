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

"""This module implements functionality which sets L2 forwarding for DPDK on
DUT nodes.
"""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as con


class L2fwdTest(object):
    """Setup the DPDK for l2fwd performance test."""

    @staticmethod
    def start_the_l2fwd_test(dut_node, cpu_cores, nb_cores, queue_nums,
                             jumbo_frames):
        """
        Execute the l2fwd on the dut_node.

        :param dut_node: Will execute the l2fwd on this node.
        :param cpu_cores: The DPDK run cores.
        :param nb_cores: The cores number for the forwarding.
        :param queue_nums: The queues number for the NIC.
        :param jumbo_frames: Are jumbo frames used or not.
        :type dut_node: dict
        :type cpu_cores: str
        :type nb_cores: str
        :type queue_nums: str
        :type jumbo_frames: str
        :returns: none
        :raises RuntimeError: If the script "run_l2fwd.sh" fails.
        """

        ssh = SSH()
        ssh.connect(dut_node)

        cmd = 'cd {0}/dpdk-tests/dpdk_scripts/ && sudo ./run_l2fwd.sh {1} ' \
              '{2} {3} {4}'.format(con.REMOTE_FW_DIR, cpu_cores, nb_cores,
                                   queue_nums, jumbo_frames)

        (ret_code, _, _) = ssh.exec_command(cmd, timeout=600)
        if ret_code != 0:
            raise RuntimeError('Failed to execute l2fwd test at node {0}'.
                               format(dut_node['host']))
