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

from resources.libraries.python.ssh import SSH
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.DMM.DMMConstants import DMMConstants as con
from resources.libraries.python.topology import Topology

class SingleCliSer(object):
    """Test DMM with single client-server topology."""

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
    def setup_dmm_dut(dut1_node, dut2_node, dut1_if_name, dut2_if_name,
                      script_name, dut1_ip, dut2_ip, prefix_len):
        """
        Setup DMM on DUT nodes.

        :param dut1_node: Node to setup DMM on.
        :param dut2_node: Node to setup DMM on.
        :param dut1_if_name: DUT1 to DUT2 interface name.
        :param dut2_if_name: DUT2 to DUT1 interface name.
        :param script_name: Name of the script to run.
        :param dut1_ip: IP address to configure on DUT1.
        :param dut2_ip: IP address to configure on DUT2.
        :param prefix_len: Prefix length.
        :type dut1_node: dict
        :type dut2_node: dict
        :type dut1_if_name: str
        :type dut2_if_name: str
        :type script_name: str
        :type dut1_ip: str
        :type dut2_ip: str
        :type prefix_len: int
        """
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

    @staticmethod
    def execute_test(dut1_node, dut2_node, dut1_if_name, dut2_if_name,
                     script_name, dut1_ip, dut2_ip):
        """
        Run the given test case.

        :param dut1_node: Node to run an app with DMM on.
        :param dut2_node: Node to run an app with DMM on.
        :param dut1_if_name: DUT1 to DUT2 interface name.
        :param dut2_if_name: DUT2 to DUT1 interface name.
        :param script_name: Name of the script to run.
        :param dut1_ip: DUT1 IP address.
        :param dut2_ip: DUT2 IP address.
        :type dut1_node: dict
        :type dut2_node: dict
        :type dut1_if_name: str
        :type dut2_if_name: str
        :type script_name: str
        :type dut1_ip: str
        :type dut2_ip: str
        """
        cmd = 'cd {0}/{1} && ./{2} run 0 {3} {4} {5} ' \
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name,
                    dut1_if_name, dut1_ip, dut2_ip)
        cmd += '2>&1 | tee log_{0}.txt &'.format(script_name)
        exec_cmd(dut1_node, cmd)
        time.sleep(10)

        cmd = 'cd {0}/{1} && ./{2} run 1 {3} {4} {5} ' \
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name,
                    dut2_if_name, dut1_ip, dut2_ip)
        cmd += '2>&1 | tee log_{0}.txt'.format(script_name)
        exec_cmd(dut2_node, cmd)

    @staticmethod
    def verify_test_result(dut1_node, dut2_node, script_name):
        """
        Verify the test and return result.

        :param dut1_node: Node to verify test result on.
        :param dut2_node: Node to verify test result on.
        :param script_name: Name of the script to run.
        :type dut1_node: dict
        :type dut2_node: dict
        :type script_name: str
        :returns: test result PASS/FAIL.
        :rtype: str
        """
        cmd = 'cd {0}/{1} && ./{2} verify 0' \
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name)
        (_, stdout_ser, _) = exec_cmd(dut1_node, cmd)

        cmd = 'cd {0}/{1} && ./{2} verify 1' \
            .format(con.REMOTE_FW_DIR, con.DMM_RUN_SCRIPTS, script_name)
        (_, stdout_cli, _) = exec_cmd(dut2_node, cmd)

        if stdout_ser.find('DMM_CSIT_TEST_PASSED') != -1 \
                and stdout_cli.find('DMM_CSIT_TEST_PASSED') != -1:
            return "PASS"
        else:
            return "FAIL"

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
        cmd = 'mv /var/log/nStack/running.log /var/log/nStack/{0}_ser.log'\
            .format(script_name)
        exec_cmd(dut1_node, cmd, sudo=True)
        cmd = 'mv /var/log/nStack/running.log /var/log/nStack/{0}_cli.log'\
            .format(script_name)
        exec_cmd(dut2_node, cmd, sudo=True)

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
        time.sleep(5)

    @staticmethod
    def run_dmm_func_test_cases(dut1_node, dut2_node, dut1_if_name,
                                dut2_if_name, dut1_ip, dut2_ip, prefix_len):
        """
        Execute all the functional test cases and return result.

        :param dut1_node: Node to run an app with DMM on.
        :param dut2_node: Node to run an app with DMM on.
        :param dut1_if_name: DUT1 to DUT2 interface name.
        :param dut2_if_name: DUT2 to DUT1 interface name.
        :param dut1_ip: IP address to configure on DUT1.
        :param dut2_ip: IP address to configure on DUT2.
        :param prefix_len: Prefix length.
        :type dut1_node: dict
        :type dut2_node: dict
        :type dut1_if_name: str
        :type dut2_if_name: str
        :type dut1_ip: str
        :type dut2_ip: str
        :type prefix_len: int
        :returns: Total testcase count, Passed testcase count.
        :rtype: tuple(int, int)
        """
        passed = 0
        total = 0
        failed = 0
        path = '{0}/*'.format(con.DMM_RUN_SCRIPTS)
        files = [os.path.basename(x) for x in glob.glob(path)]
        print "list of files : {0}".format(files)

        for name in files:
            print("file name : {}").format(name)
            total += 1
            SingleCliSer.setup_dmm_dut(dut1_node, dut2_node, dut1_if_name,
                                       dut2_if_name, name, dut1_ip, dut2_ip,
                                       prefix_len)
            SingleCliSer.execute_test(dut1_node, dut2_node, dut1_if_name,
                                      dut2_if_name, name, dut1_ip, dut2_ip)
            result = SingleCliSer.verify_test_result(dut1_node, dut2_node,
                                                     '{0}'.format(name))
            if result == "PASS":
                passed += 1
            elif result == "FAIL":
                failed += 1

            SingleCliSer.print_dmm_log(dut1_node, dut2_node, name)
            SingleCliSer.cleanup_dmm_dut(dut1_node, dut2_node, name)
            print("TOTAL :{} PASSED : {} FAILED: {}").format\
                (total, passed, failed)

        return total, passed

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

    @staticmethod
    def get_logs_from_node(dut_node):
        """
        Get logs from node to the test executor machine.

        :param dut_node: Node to artifact the logs of.
        :type dut_node: dict
        """
        ssh = SSH()
        ssh.connect(dut_node)
        ssh.scp(".", '/var/log/nStack/*.log',
                get=True, timeout=60, wildcard=True)

        (ret, _, _) = exec_cmd(dut_node, 'ls -l /var/log/app*.log')
        if ret == 0:
            ssh.scp(".", '/var/log/app*.log',
                    get=True, timeout=60, wildcard=True)

        exec_cmd(dut_node, 'rm -rf /var/log/nStack/*.log', sudo=True)
        exec_cmd(dut_node, 'rm -rf /var/log/app*.log', sudo=True)

    @staticmethod
    def archive_dmm_logs(dut1_node, dut2_node):
        """
        Get logs from both DUT's to the test executor machine.

        :param dut1_node: DUT1 node.
        :param dut2_node: DUT2 node.
        :type dut1_node: dict
        :type dut2_node: dict
        """
        SingleCliSer.get_logs_from_node(dut1_node)
        SingleCliSer.get_logs_from_node(dut2_node)
