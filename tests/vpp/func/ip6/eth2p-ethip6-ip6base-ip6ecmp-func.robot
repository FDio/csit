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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Library | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *Ipv6 Multipath routing test cases*
| ...
| ... | *[Top] Network topologies:* TG=DUT 2-node topology with two links\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT configure interfaces IPv4 adresses,\
| ... | and multipath routing.
| ... | *[Ver] TG verification:* Test packets are sent from TG on the first\
| ... | link to DUT. Packet is received on TG on the second link from DUT1.

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
| TC01: IPv6 Equal-cost multipath routing
| | [Documentation]
| | ... | [Top] TG=DUT
| | ... | [Cfg] On DUT configure multipath routing wiht two equal-cost paths.
| | ... | [Ver] TG sends 100 IPv6 ICMP packets traffic on the first link to\
| | ... | DUT. On second link to TG verify if traffic is divided into two paths.
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And Vpp Set If Ipv6 Addr | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${ip_1} | ${prefix_length}
| | And Vpp Set If Ipv6 Addr | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${ip_2} | ${prefix_length}
| | And Add Ip Neighbor
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_1_ip} | ${neighbor_1_mac}
| | And Add Ip Neighbor
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_2_ip} | ${neighbor_2_mac}
| | And Suppress ICMPv6 router advertisement message | ${nodes}
| | When Vpp Route Add
| | ... | ${dut_node} | ${test_dst_ip} | ${prefix_length} | ${neighbor_1_ip}
| | ... | ${dut_to_tg_if1} | resolve_attempts=${NONE} | multipath=${TRUE}
| | And Vpp Route Add
| | ... | ${dut_node} | ${test_dst_ip} | ${prefix_length} | ${neighbor_2_ip}
| | ... | ${dut_to_tg_if1} | resolve_attempts=${NONE} | multipath=${TRUE}
| | Then Send packets and verify multipath routing | ${tg_node}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if1} | ${test_src_ip} | ${test_dst_ip}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${dut_to_tg_if1_mac}
| | ... | ${neighbor_1_mac} | ${neighbor_2_mac}
