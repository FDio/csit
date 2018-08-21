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

class SingleCliSer(object):
    """Test the DMM vs_epoll ping function."""

    @staticmethod
    def exec_the_base_vs_epoll_test(dut1_node, dut2_node,
                                    dut1_if_name, dut2_if_name):
        """perform base vs_epoll test on DUT's

        :param dut1_node: Node to execute vs_epoll on
        :param dut2_node: Node to execute vc_common on
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

        :param dut_node: Node to get the test result on
        :type dut_node: dict
        :returns: str.
        :rtype: str.
        """
        cmd = 'cat {0}/{1}/log_run_dmm.txt | grep "send 50000" | wc -l' \
        .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS)
        (stdout, _) = exec_cmd_no_error(dut_node, cmd)
        return stdout

    @staticmethod
    def echo_dmm_logs(dut_node):
        """
        gets the prerequisites installation log from DUT

        :param dut_node: Node to get the installation log on
        :type dut_node: dict
        """
        cmd = 'cat {0}/{1}/log_install_prereq.txt' \
        .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS)
        exec_cmd_no_error(dut_node, cmd)

    @staticmethod
    def exec_the_base_lwip_test(dut1_node, dut2_node,
                                dut1_if_name, dut2_if_name):
        """Test DMM with LWIP.

        :param dut1_node: Node to execute vs_epoll on
        :param dut2_node: Node to execute vc_common on
        :param dut1_if_name: DUT1 to DUT2 interface name
        :param dut2_if_name: DUT2 to DUT1 interface name
        :type dut1_node: dict
        :type dut2_node: dict
        :type dut1_if_name: str
        :type dut2_if_name: str
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

        :param dut_node: Node to get the test result on
        :type dut_node: dict
        :returns: str.
        :rtype: str.
        """
        cmd = 'cat {0}/{1}/log_run_dmm_with_lwip.txt | grep "send 50" | wc -l' \
        .format(con.REMOTE_FW_DIR, con.DMM_SCRIPTS)

        (stdout, _) = exec_cmd_no_error(dut_node, cmd)
        return stdout

    @staticmethod
    def echo_running_log(dut1_node, dut2_node):
        """
        get the running log

        :param dut1_node: Node to get the running log on
        :param dut2_node: Node to get the running log on
        :type dut1_node: dict
        :type dut2_node: dict
        """
        cmd = 'cat /var/log/nStack/running.log'
        exec_cmd_no_error(dut1_node, cmd)
        exec_cmd_no_error(dut2_node, cmd)

    @staticmethod
    def echo_dpdk_log(dut1_node, dut2_node):
        """
        get the dpdk log

        :param dut1_node: Node to get the DPDK log on
        :param dut2_node: Node to get the DPDK log on
        :type dut1_node: dict
        :type dut2_node: dict
        """
        cmd = 'cat /var/log/nstack-dpdk/nstack_dpdk.log'
        exec_cmd_no_error(dut1_node, cmd)
        exec_cmd_no_error(dut2_node, cmd)

    @staticmethod
    def dmm_get_interface_name(dut_node, dut_interface):
        """
        get the interface name

        :param dut_node: Node to get the interface name on
        :param dut_interface: interface key
        :type dut_node: dict
        :type dut_interface: str
        :returns: interface name
        :rtype: str
        """
        mac = Topology.get_interface_mac(dut_node, dut_interface)
        cmd = 'ifconfig -a | grep {0}'.format(mac)
        (stdout, _) = exec_cmd_no_error(dut_node, cmd)
        interface_name = stdout.split(' ', 1)[0]
        return interface_name

    @staticmethod
    def set_dmm_interface_address(dut_node, ifname, ip_addr, ip4_prefix):
        """
        flush ip, set ip, set interface up

        :param dut_node: Node to set the interface address on
        :param ifname: Interface name
        :param ip_addr: IP address to configure
        :param ip4_prefix: Prefix length
        :type dut_node: dict
        :type ifname: str
        :type ip_addr: str
        :type ip4_prefix: int
        """
        cmd = 'sudo ip -4 addr flush dev {}'.format(ifname)
        exec_cmd_no_error(dut_node, cmd)
        cmd = 'sudo ip addr add {}/{} dev {}'\
            .format(ip_addr, ip4_prefix, ifname)
        exec_cmd_no_error(dut_node, cmd)
        cmd = 'sudo ip link set {0} up'.format(ifname)
        exec_cmd_no_error(dut_node, cmd)
