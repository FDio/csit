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
| Resource | resources/libraries/robot/ipv4.robot
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
| ${ip_1}= | 192.168.1.1
| ${ip_2}= | 192.168.2.1
| ${test_dst_ip}= | 32.0.0.1
| ${test_src_ip}= | 16.0.0.1
| ${prefix_length}= | 32
| ${neighbor_1_ip}= | 192.168.2.10
| ${neighbor_1_mac}= | 02:00:00:00:00:02
| ${neighbor_2_ip}= | 192.168.2.20
| ${neighbor_2_mac}= | 02:00:00:00:00:03

*** Test Cases ***
| TC01
| | [Documentation]
| | ... |
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are UP
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${ip_1} | ${prefix_length}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${ip_2} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_1_ip} | ${neighbor_1_mac}
| | And Add Arp On Dut
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_2_ip} | ${neighbor_2_mac}
| | And Vpp Route Add
| | ... | ${dut_node} | ${test_dst_ip} | ${prefix_length} | ${neighbor_1_ip}
| | ... | ${dut_to_tg_if1} | resolve-attempts= | ${NONE}
| | ... | multipath= ${TRUE}
| | And Vpp Route Add
| | ... | ${dut_node} | ${test_dst_ip} | ${prefix_length} | ${neighbor_2_ip}
| | ... | ${dut_to_tg_if1} | resolve-attempts= | ${NONE} |
| | ... | multipath= ${TRUE}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if1}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac}

| TC02
| | [Documentation]
| | ... |
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are UP
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${ip_1} | ${prefix_length}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${ip_2} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_1_ip} | ${neighbor_1_mac}
| | And Add Arp On Dut
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_2_ip} | ${neighbor_2_mac}
| | And Vpp Route Add
| | ... | ${dut_node} | ${test_dst_ip} | ${prefix_length} | ${neighbor_1_ip}
| | ... | ${dut_to_tg_if1} | resolve-attempts= | ${NONE}
| | ... | multipath= ${TRUE} | weight= ${3}
| | And Vpp Route Add
| | ... | ${dut_node} | ${test_dst_ip} | ${prefix_length} | ${neighbor_2_ip}
| | ... | ${dut_to_tg_if1} | resolve-attempts= | ${NONE} |
| | ... | multipath= ${TRUE} | weight= ${1}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if1}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac}
