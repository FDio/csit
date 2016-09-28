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


*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Show packet trace on all DUTs | ${nodes}
| ...           | AND          | Vpp Show Errors | ${nodes['DUT1']}
| ...           | AND          | Show vpp trace dump on all DUTs


*** Variables ***
| ${ip_1}= | 3ffe:61::1
| ${ip_2}= | 3ffe:62::1
| ${test_dst_ip}= | 3ffe:71::1
| ${test_src_ip}= | 3ffe:51::1
| ${prefix_length}= | 64
| ${neighbor_1_ip}= | 3ffe:62::2
| ${neighbor_1_mac}= | 02:00:00:00:00:02
| ${neighbor_2_ip}= | 3ffe:62::3
| ${neighbor_2_mac}= | 02:00:00:00:00:03

*** Test Cases ***
| TC01
| | [Documentation]
| | ... |
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are UP
| | And Vpp Set If Ipv6 Addr | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${ip_1} | ${prefix_length}
| | And Vpp Set If Ipv6 Addr | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${ip_2} | ${prefix_length}
| | And Add Ip Neighbor
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_1_ip} | ${neighbor_1_mac}
| | And Add Ip Neighbor
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_2_ip} | ${neighbor_2_mac}
| | And Vpp Route Add
| | ... | ${dut_node} | ${test_dst_ip} | ${prefix_length} | ${neighbor_1_ip}
| | ... | ${dut_to_tg_if1} | resolve-attempts= | ${NONE}
| | ... | multipath= ${TRUE}
| | And Vpp Route Add
| | ... | ${dut_node} | ${test_dst_ip} | ${prefix_length} | ${neighbor_2_ip}
| | ... | ${dut_to_tg_if1} | resolve-attempts= | ${NONE} |
| | ... | multipath= ${TRUE}
| | Then Send Packets And Check Multipath Routing | ${tg_node}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if1} | ${test_src_ip} | ${test_dst_ip}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${dut_to_tg_if1_mac}
| | ... | ${neighbor_1_mac} | ${neighbor_2_mac}
