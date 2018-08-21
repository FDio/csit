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
import time

from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.DMM.DMMConstants import DMMConstants as con
from resources.libraries.python.topology import Topology
from robot.api import logger

class SingleCliSer(object):
    """Test the DMM vs_epoll ping function."""

    @staticmethod
    def exec_the_base_vs_epoll_test(dut1_node, dut2_node,
                                    dut1_if_name, dut2_if_name):
        """Execute the vs_epoll on the dut1_node.

        :param dut1_node: Will execute the vs_epoll on this node.
        :param dut2_node: Will execute the vc_epoll on this node.
        :type dut1_node: dict
        :type dut2_node: dict
        """
        cmd = 'cd {0}/{1} && ./run_dmm.sh {2} {3} ' \
        .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS, 0, dut1_if_name)

        cmd += '2>&1 | tee log_run_dmm.txt &'
        exec_cmd_no_error(dut1_node, cmd)
        time.sleep(10)

        cmd = 'cd {0}/{1} && ./run_dmm.sh {2} {3} ' \
        .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS, 1, dut2_if_name)

        cmd += '2>&1 | tee log_run_dmm.txt'
        exec_cmd_no_error(dut2_node, cmd)

    @staticmethod
    def get_the_test_result(dut_node):
        """
        After executing exec_the_base_vs_epoll_test, use this
        to get the test result

        :param dut_node: will get the test result in this dut node
        :type dut_node: dict
        :returns: str.
        :rtype: str.
        """
        cmd = 'cat {0}/{1}/log_run_dmm.txt | grep "send 50000" | wc -l' \
        .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS)
        (stdout, stderr) = exec_cmd_no_error(dut_node, cmd)
        return stdout

    @staticmethod
    def echo_dmm_logs(dut_node):
        """
        :param dut_node:
        :type dut_node: dict
        """
        cmd = 'cat {0}/{1}/log_install_dmm.txt' \
        .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS)
        exec_cmd_no_error(dut_node, cmd)

    @staticmethod
    def exec_the_base_lwip_test(dut1_node, dut2_node,
                                dut1_if_name, dut2_if_name):
        """Test DMM with LWIP.

        :param dut1_node: Will execute the vs_epoll on this node.
        :param dut2_node: Will execute the vc_epoll on this node.
        :type dut1_node: dict
        :type dut2_node: dict
        """
        cmd = 'cd {0}/{1} && ./run_dmm_with_lwip.sh {2} {3} ' \
            .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS, 0, dut1_if_name)

        cmd += '2>&1 | tee log_run_dmm_with_lwip.txt &'
        exec_cmd_no_error(dut1_node, cmd)
        time.sleep(10)

        cmd = 'cd {0}/{1} && ./run_dmm_with_lwip.sh {2} {3} ' \
            .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS, 1, dut2_if_name)

        cmd += '2>&1 | tee log_run_dmm_with_lwip.txt'
        exec_cmd_no_error(dut2_node, cmd)

    @staticmethod
    def get_lwip_test_result(dut_node):
        """
        After executing exec_the_base_lwip_test, use this
        to get the test result

        :param dut_node: will get the test result in this dut node
        :type dut_node: dict
        :returns: str.
        :rtype: str.
        """
        cmd = 'cat {0}/{1}/log_run_dmm_with_lwip.txt | grep "send 50" | wc -l' \
        .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS)

        (stdout, stderr) = exec_cmd_no_error(dut_node, cmd)
        return stdout

    @staticmethod
    def echo_running_log (dut1_node, dut2_node):
        """
        :param dut1_node:
        :param dut2_node:
        :type dut1_node: dict
        :type dut2_node: dict
        """
        cmd = 'cat /var/log/nStack/running.log'
        exec_cmd_no_error(dut1_node, cmd)
        exec_cmd_no_error(dut2_node, cmd)

    @staticmethod
    def echo_dpdk_log (dut1_node, dut2_node):
        """
        :param dut1_node:
        :param dut2_node:
        :type dut1_node: dict
        :type dut2_node: dict
        """
        cmd = 'cat /var/log/nstack-dpdk/nstack_dpdk.log'
        exec_cmd_no_error(dut1_node, cmd)
        exec_cmd_no_error(dut2_node, cmd)

    @staticmethod
    def dmm_get_interface_name(dut_node, dut_interface):
        """
        :param dut_node:
        :param dut_interface:
        :type dut1_node: dict
        :type dut_interface: str
        :returns: interface name
        :rtype: str
        """
        mac = Topology.get_interface_mac(dut_node, dut_interface)
        cmd = 'ifconfig -a | grep {0}'.format(mac)
        (stdout, stderr) = exec_cmd_no_error(dut_node, cmd)
        interface_name = stdout.split(' ', 1)[0]
        return interface_name

    @staticmethod
    def set_dmm_interface_address(dut_node, ifname, ip_addr):
        """
        :param dut_node:
        :return:
        """
        cmd = 'sudo ifconfig {0} {1} netmask 255.255.255.0 up'\
            .format(ifname, ip_addr)
        exec_cmd_no_error(dut_node, cmd)
