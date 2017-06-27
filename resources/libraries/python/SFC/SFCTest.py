# Copyright (c) 2017 Cisco and/or its affiliates.
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
This module implements functionality which configure and start
the NSH SFC functional test.
"""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as con
from resources.libraries.python.topology import Topology

class SFCTest(object):
    """Configure and Start the NSH SFC functional tests."""

    @staticmethod
    def config_and_start_SFC_test(dut_node, dut_if1, dut_if2, if1_adj_mac,
                                  if2_adj_mac, testtype):
        """
        Start the SFC functional on the dut_node.

        :param dut_node: Will execute the SFC on this node.
        :param dut_port: The ingress interface on the DUT.
        :param adj_mac: The adjacency interface MAC.
        :param testtype: The SFC functional test type.
                         (Classifier, Proxy Inbound, Proxy Outbound, SFF).
        :type dut_node: dict
        :type dut_port: str
        :type adj_mac: str
        :type testtype: str
        :returns: none
        :raises RuntimeError: If the script execute fails.
        """

        vpp_intf_name1 = Topology.get_interface_name(dut_node, dut_if1)
        vpp_intf_name2 = Topology.get_interface_name(dut_node, dut_if2)

        ssh = SSH()
        ssh.connect(dut_node)

        if testtype == "Classifier":
            exec_shell = "set_sfc_classifier.sh"
        elif testtype == "Proxy Inbound":
            exec_shell = "set_nsh_proxy_inbound.sh"
        elif testtype == "Proxy Outbound":
            exec_shell = "set_nsh_proxy_outbound.sh"
        else:
            exec_shell = "set_sfc_sff.sh"

        cmd = 'cd {0}/nsh_sfc_tests/sfc_scripts/ && sudo ./{1} {2} ' \
             '{3} {4} {5}'.format(con.REMOTE_FW_DIR, exec_shell, vpp_intf_name1,
                               vpp_intf_name2, if1_adj_mac, if2_adj_mac)

        (ret_code, _, _) = ssh.exec_command(cmd, timeout=600)
        if ret_code != 0:
            raise RuntimeError('Failed to execute SFC setup script ' \
                 '{0} at node {1}'.format(exec_shell, dut_node['host']))

    @staticmethod
    def start_the_tcpdump_on_the_node(from_node, from_port, filter_ip):
        """
        Start the tcpdump on the frome_node.

        :param from_node: Will execute the tcpdump on this node.
        :param from_port: Will capture the packets on this interface.
        :param filter_ip: filter the dest ip.
        :type from_node: dict
        :type from_port: str
        :type filter_ip: str
        :returns: none
        :raises RuntimeError: If the script "start_tcpdump.sh" fails.
        """

        interface_name = Topology.get_interface_name(from_node, from_port)

        ssh = SSH()
        ssh.connect(from_node)

        cmd = 'cd {0}/nsh_sfc_tests/sfc_scripts/ && sudo ./start_tcpdump.sh ' \
              '{1} {2}'.format(con.REMOTE_FW_DIR, interface_name, filter_ip)

        (ret_code, _, _) = ssh.exec_command(cmd, timeout=600)
        if ret_code != 0:
            raise RuntimeError('Failed to exec start_tcpdump.sh at node {0}'.
                               format(from_node['host']))
