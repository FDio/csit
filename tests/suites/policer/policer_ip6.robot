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
| Force Tags | 3_NODE_DOUBLE_LINK_TOPO | VM_ENV | HW_ENV
| Resource | resources/libraries/robot/policer.robot
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Setup Topology for IPv6 policer testing
| Documentation | *IPv6 policer test cases*
| ...
| ... | *[Top] Network topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 configure interfaces IPv6 adresses,
| ... | and static neighbor record on the second interface.
| ... | *[Ver] TG verification:* Test packet is sent from TG on the first link
| ... | to DUT1. Packet is received on TG on the second link from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC2474, RFC2697, RFC2698.

*** Test Cases ***
| TC01: VPP policer marks packet
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Ref] RFC2474, RFC2698
| | ... | [Cfg] On DUT1 configure 2R3C color-aware policer on the first
| | ... | interface.
| | ... | [Ver] TG sends IPv6 TCP packet on the first link to DUT1, verify if
| | ... | DUT1 sends correct IPv6 TCP packet with correct DSCP on the second
| | ... | link to TG.
| | [Tags] | EXPECTED_FAILING
| | ${cir}= | Set Variable | ${100}
| | ${eir}= | Set Variable | ${100}
| | ${cb}= | Set Variable | ${100}
| | ${eb}= | Set Variable | ${100}
| | ${dscp}= | DSCP AF22
| | Given Policer Set Name | policer1
| | And Policer Set Node | ${dut_node}
| | And Policer Set CIR | ${cir}
| | And Policer Set EIR | ${eir}
| | And Policer Set CB | ${cb}
| | And Policer Set EB | ${eb}
| | And Policer Set Rate Type pps
| | And Policer Set Round Type Closest
| | And Policer Set Type 2R3C 2698
| | And Policer Set Conform Action Transmit
| | And Policer Set Exceed Action Mark and Transmit | ${dscp}
| | And Policer Set Violate Action Drop
| | And Policer Enable Color Aware
| | And Policer Classify Set Precolor Exceed
| | And Policer Classify Set Interface | ${dut_to_tg_if1}
| | And Policer Classify Set Match IP | ${tg_to_dut_if1_ip}
| | When Policer Set Configuration
| | Then Send Packet and Verify Marking | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if1_ip} | ${tg_to_dut_if2_ip} | ${dscp}
