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
    def config_and_start_sfc_test(dut_node, dut_if1, dut_if2, if1_adj_mac,
                                  if2_adj_mac, testtype):
        """
        Start the SFC functional on the dut_node.

        :param dut_node: Will execute the SFC on this node.
        :param dut_if1: The first ingress interface on the DUT.
        :param dut_if2: The last egress interface on the DUT.
        :param if1_adj_mac: The interface 1 adjacency MAC.
        :param if2_adj_mac: The interface 2 adjacency MAC.
        :param testtype: The SFC functional test type.
                         (Classifier, Proxy Inbound, Proxy Outbound, SFF).
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :type if1_adj_mac: str
        :type if2_adj_mac: str
        :type testtype: str
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

        cmd = 'cd {0}/tests/nsh_sfc/sfc_scripts/ && sudo ./{1} {2} {3} {4} ' \
              '{5}'.format(con.REMOTE_FW_DIR, exec_shell, vpp_intf_name1,
                           vpp_intf_name2, if1_adj_mac, if2_adj_mac)

        (ret_code, _, _) = ssh.exec_command(cmd, timeout=600)
        if ret_code != 0:
            raise RuntimeError('Failed to execute SFC setup script ' \
                 '{0} at node {1}'.format(exec_shell, dut_node['host']))
