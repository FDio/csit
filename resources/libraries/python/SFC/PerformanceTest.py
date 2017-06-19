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
This module implements functionality which configure and start
the NSH SFC performance test.
"""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as con
from resources.libraries.python.topology import Topology

class PerformanceTest(object):
    """Configure and Start the NSH SFC performance tests."""

    @staticmethod
    def Start_performance_test_on_DUT(dut_node, dut_if1, dut_if2,
        if1_adj_mac, if2_adj_mac, testtype, duttype):

        """
        Start the SFC performance test on the dut_node.

        :param dut_node: Will execute the SFC on this node.
        :param dut_if1: DUT topology link interface 1.
        :param dut_if2: DUT topology link interface 2.
        :param if1_adj_mac: DUT interface 1 adjacency interface MAC.
        :param if2_adj_mac: DUT interface 2 adjacency interface MAC.
        :param testtype: The SFC performance test type.
                         (Classifier, Proxy Inbound, Proxy Outbound, SFF).
        :param duttype: The DUT name. (DUT1, DUT2)
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :type if1_adj_mac: str
        :type if2_adj_mac: str
        :type testtype: str
        :type duttype: str
        :returns: none
        :raises RuntimeError: If the script execute fails.
        """

        vpp_intf1_name = Topology.get_interface_name(dut_node, dut_if1)
        vpp_intf2_name = Topology.get_interface_name(dut_node, dut_if2)

        ssh = SSH()
        ssh.connect(dut_node)

        if testtype == "Classifier":
            exec_shell = "set_sfc_classifier_perf.sh"
        elif testtype == "Proxy Inbound":
            exec_shell = "set_nsh_proxy_inbound_perf.sh"
        elif testtype == "Proxy Outbound":
            exec_shell = "set_nsh_proxy_outbound_perf.sh"
        else:
            exec_shell = "set_sfc_sff_perf.sh"

        cmd = 'cd {0}/nsh_sfc_tests/sfc_scripts/ && sudo ./{1} {2} ' \
              '{3} {4} {5} {6}'.format(con.REMOTE_FW_DIR, exec_shell, vpp_intf1_name,
                               vpp_intf2_name, if1_adj_mac, if2_adj_mac, duttype)

        (ret_code, _, _) = ssh.exec_command(cmd, timeout=600)
        if ret_code != 0:
            raise RuntimeError('Failed to execute SFC setup script ' \
                 '{0} at node {1}'.format(exec_shell, dut_node['host']))

