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
This module exists to provide single client-server test for DMM
on topology nodes.
"""
import time
import os
import glob

from resources.libraries.python.ssh import exec_cmd
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.DMM.DMMConstants import DMMConstants as con
from resources.libraries.python.topology import Topology

class SingleCliSer(object):
    """Test DMM with single client-server topology."""
    PASSED = 0
    TOTAL = 0
    FAILED = 0

    @staticmethod
    def set_dmm_interface_address(dut_node, ifname, ip_addr, ip4_prefix):
        """
        Flush ip, set ip, set interface up.

        :param dut_node: Node to set the interface address on.
        :param ifname: Interface name.
        :param ip_addr: IP address to configure.
        :param ip4_prefix: Prefix length.
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

    @staticmethod
    def setup_dmm_dut(dut1_node, dut2_node,
                      dut1_if_name, dut2_if_name, script_name):
        """
        Setup DMM on DUT nodes.

        :param dut1_node: Node to setup DMM on.
        :param dut2_node: Node to setup DMM on.
        :param dut1_if_name: DUT1 to DUT2 interface name.
        :param dut2_if_name: DUT2 to DUT1 interface name.
        :param script_name: Name of the script to run.
        :type dut1_node: dict
        :type dut2_node: dict
        :type dut1_if_name: str
        :type dut2_if_name: str
        :type script_name: str
        :return: DUT1 ip , DUT2 ip.
        :rtype: tuple(str, str)
        """
        dut1_ip = '172.28.128.3'
        dut2_ip = '172.28.128.4'
        prefix_len = 24
        SingleCliSer.set_dmm_interface_address(dut1_node, dut1_if_name,
                                               dut1_ip, prefix_len)
        SingleCliSer.set_dmm_interface_address(dut2_node, dut2_if_name,
                                               dut2_ip, prefix_len)
        cmd = 'cd {0}/{1} && ./{2} setup 0 {3} {4} {5}'\
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name,
                    dut1_if_name, dut1_ip, dut2_ip)
        exec_cmd(dut1_node, cmd)

        cmd = 'cd {0}/{1} && ./{2} setup 1 {3} {4} {5}'\
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name,
                    dut2_if_name, dut1_ip, dut2_ip)
        exec_cmd(dut2_node, cmd)

        return dut1_ip, dut2_ip

    @staticmethod
    def print_dmm_log(dut1_node, dut2_node, script_name):
        """
        Print DMM logs.

        :param dut1_node: Node to print DMM logs of.
        :param dut2_node: Node to print DMM logs of.
        :param script_name: Name of the script to run.
        :type dut1_node: dict
        :type dut2_node: dict
        :type script_name: str
        """
        cmd = 'cd {0}/{1} && ./{2} log 0'\
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name)
        exec_cmd(dut1_node, cmd)

        cmd = 'cd {0}/{1} && ./{2} log 1'\
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name)
        exec_cmd(dut2_node, cmd)

    @staticmethod
    def cleanup_dmm_dut(dut1_node, dut2_node, script_name):
        """
        Cleanup DMM DUT node.

        :param dut1_node: DMM node to be cleaned up.
        :param dut2_node: DMM node to be cleaned up.
        :param script_name: Name of the script to run.
        :type dut1_node: dict
        :type dut2_node: dict
        :type script_name: str
        """
        cmd = 'cd {0}/{1} && ./{2} cleanup 0'\
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name)
        exec_cmd(dut1_node, cmd)
        exec_cmd(dut2_node, cmd)

    @staticmethod
    def verify_n_cleanup_dmm_dut(dut1_node, dut2_node, script_name):
        """
        Verify the test result and perform cleanup on DUTs.

        :param dut1_node: Node to verify test result on.
        :param dut2_node: Node to verify test result on.
        :param script_name: Name of the script to run.
        :type dut1_node: dict
        :type dut2_node: dict
        :type script_name: str
        """
        SingleCliSer.TOTAL += 1

        cmd = 'cd {0}/{1} && ./{2} verify 0' \
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name)
        (_, stdout_ser, _) = exec_cmd(dut1_node, cmd)

        cmd = 'cd {0}/{1} && ./{2} verify 1' \
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name)
        (_, stdout_cli, _) = exec_cmd(dut2_node, cmd)

        if (stdout_ser.find('DMM_CSIT_TEST_PASSED') != -1
            and stdout_cli.find('DMM_CSIT_TEST_PASSED') != -1):
            SingleCliSer.PASSED += 1
        else:
            SingleCliSer.FAILED += 1

        print("TOTAL :{} PASSED : {} FAILED: {}").format(SingleCliSer.TOTAL,
                                                         SingleCliSer.PASSED,
                                                         SingleCliSer.FAILED)
        SingleCliSer.print_dmm_log(dut1_node, dut2_node, script_name)
        SingleCliSer.cleanup_dmm_dut(dut1_node, dut2_node, script_name)

    @staticmethod
    def run_dmm_func_test_cases(dut1_node, dut2_node,
                                dut1_if_name, dut2_if_name):
        """
        Perform base vs_epoll test on DUT's.

        :param dut1_node: Node to run an app with DMM on.
        :param dut2_node: Node to run an app with DMM on.
        :param dut1_if_name: DUT1 to DUT2 interface name.
        :param dut2_if_name: DUT2 to DUT1 interface name.
        :type dut1_node: dict
        :type dut2_node: dict
        :type dut1_if_name: str
        :type dut2_if_name: str
        """
        path = '{0}/*'.format(con.DMM_RUN_SCRIPTS)
        files = [os.path.basename(x) for x in glob.glob(path)]
        print "list of files : {0}".format(files)

        for name in files:
            (dut1_if_ip, dut2_if_ip) = \
                SingleCliSer.setup_dmm_dut(dut1_node, dut2_node,
                                           dut1_if_name, dut2_if_name, name)

            print("file name : {}").format(name)
            cmd = 'cd {0}/{1} && ./{2} run 0 {3} {4} {5} '\
                .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, name,
                        dut1_if_name, dut1_if_ip, dut2_if_ip)
            cmd += '2>&1 | tee log_{0}.txt &'.format(name)
            exec_cmd(dut1_node, cmd)
            time.sleep(10)

            cmd = 'cd {0}/{1} && ./{2} run 1 {3} {4} {5} '\
                .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, name,
                        dut2_if_name, dut1_if_ip, dut2_if_ip)
            cmd += '2>&1 | tee log_{0}.txt'.format(name)
            exec_cmd(dut2_node, cmd)

            SingleCliSer.verify_n_cleanup_dmm_dut(dut1_node, dut2_node,
                                                  '{0}'.format(name))
            time.sleep(5)

    @staticmethod
    def get_result():
        """
        Get the result stored as env variables.

        :return: Total testcase count, Passed testcase count.
        :rtype: tuple(str, str)
        """
        return SingleCliSer.TOTAL, SingleCliSer.PASSED

    @staticmethod
    def dmm_get_interface_name(dut_node, dut_interface):
        """
        Get the interface name.

        :param dut_node: Node to get the interface name on.
        :param dut_interface: Interface key.
        :type dut_node: dict
        :type dut_interface: str
        :returns: Interface name.
        :rtype: str
        """
        mac = Topology.get_interface_mac(dut_node, dut_interface)
        cmd = 'ifconfig -a | grep {0}'.format(mac)
        (stdout, _) = exec_cmd_no_error(dut_node, cmd)
        interface_name = stdout.split(' ', 1)[0]
        return interface_name
