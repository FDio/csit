# Copyright (c) 2018 Huawei Technologies Co.,Ltd.
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
This module exists to provide the vs_epoll ping test for DMM on topology nodes.
"""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.DMM.DMMConstants import DMMConstants as con
from resources.libraries.python.topology import Topology

import time

class SingleCliSer(object):
    """Test the DMM vs_epoll ping function."""

    @staticmethod
    def exec_the_base_vs_epoll_test(dut1_node, dut2_node):
        """Execute the vs_epoll on the dut1_node.

        :param dut1_node: Will execute the vs_epoll on this node.
        :param dut2_node: Will execute the vc_epoll on this node.
        :type dut1_node: dict
        :type dut2_node: dict
        :returns: positive value if packets are sent and received
        :raises RuntimeError:If failed to execute vs_epoll test on  dut1_node.
        """
        dut1_ip = Topology.get_node_hostname(dut1_node)
        dut2_ip = Topology.get_node_hostname(dut2_node)

        ssh = SSH()
        ssh.connect(dut1_node)

	cmd = 'cd {0}/{1} && ./run_dmm.sh {2} {3} {4} 2>&1 | tee log_run_dmm.txt &' \
	.format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS, dut1_ip, dut2_ip, 0)

        (ret_code, stdout_ser, _) = ssh.exec_command(cmd, timeout=6000)
        if ret_code != 0:
            raise RuntimeError('Failed to execute vs_epoll test at node {0}'
                               .format(dut1_node['host']))
	
	time.sleep(10)

        ssh = SSH()
        ssh.connect(dut2_node)

	cmd = 'cd {0}/{1} && ./run_dmm.sh {2} {3} {4} 2>&1 | tee log_run_dmm.txt' \
	.format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS, dut1_ip, dut2_ip, 1)
        
	(ret_code, stdout_cli, _) = ssh.exec_command(cmd, timeout=6000)
        if ret_code != 0:
            raise RuntimeError('Failed to execute vs_epoll test at node {0}'
                               .format(dut1_node['host']))

	return (stdout_cli.find("send 50000"))
