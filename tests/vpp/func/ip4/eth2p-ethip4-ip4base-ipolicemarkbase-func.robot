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
| Resource | resources/libraries/robot/features/policer.robot
| Library | resources.libraries.python.Trace
| Test Setup | Run Keywords | Set up functional test
| ...        | AND          | Configure topology for IPv4 policer test
| Test Teardown | Tear down functional test
| Documentation | *IPv4 policer test cases*
| ...
| ... | *[Top] Network topologies:* TG=DUT1 2-node topology with two links\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 configure interfaces IPv4 adresses,\
| ... | and static ARP record on the second interface.
| ... | *[Ver] TG verification:* Test packet is sent from TG on the first link\
| ... | to DUT1. Packet is received on TG on the second link from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC2474, RFC2697, RFC2698.

*** Variables ***
| ${tg_to_dut_if1_ip4}= | 192.168.122.2
| ${tg_to_dut_if2_ip4}= | 192.168.123.2
| ${dut_to_tg_if1_ip4}= | 192.168.122.1
| ${dut_to_tg_if2_ip4}= | 192.168.123.1
| ${ip4_plen}= | ${24}

| ${cir}= | ${100}
| ${eir}= | ${150}
| ${cb}= | ${200}
| ${eb}= | ${300}

*** Test Cases ***
| TC01: VPP policer 2R3C Color-aware marks packet
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Ref] RFC2474, RFC2698.
| | ... | [Cfg] On DUT1 configure 2R3C color-aware policer on the first\
| | ... | interface.
| | ... | [Ver] TG sends IPv4 TCP packet on the first link to DUT1.\
| | ... | On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends\
| | ... | correct IPv4 TCP packet with correct DSCP on the second link to TG.
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
| | Then Send packet and verify marking | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if1_ip} | ${tg_to_dut_if2_ip} | ${dscp}

| TC02: VPP policer 2R3C Color-blind marks packet
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Ref] RFC2474, RFC2698.
| | ... | [Cfg] On DUT1 configure 2R3C color-blind policer on the first\
| | ... | interface.
| | ... | [Ver] TG sends IPv4 TCP packet on the first link to DUT1.\
| | ... | On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends\
| | ... | correct IPv4 TCP packet with correct DSCP on the second link to TG.
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
| | And Policer Set Conform Action Mark and Transmit | ${dscp}
| | And Policer Set Exceed Action Transmit
| | And Policer Set Violate Action Drop
| | And Policer Classify Set Precolor Conform
| | And Policer Classify Set Interface | ${dut_to_tg_if1}
| | And Policer Classify Set Match IP | ${tg_to_dut_if1_ip}
| | When Policer Set Configuration
| | Then Send packet and verify marking | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if1_ip} | ${tg_to_dut_if2_ip} | ${dscp}

| TC03: VPP policer 1R3C Color-aware marks packet
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Ref] RFC2474, RFC2697.
| | ... | [Cfg] On DUT1 configure 1R3C color-aware policer on the first\
| | ... | interface.
| | ... | [Ver] TG sends IPv4 TCP packet on the first link to DUT1.\
| | ... | On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends\
| | ... | correct IPv4 TCP packet with correct DSCP on the second link to TG.
| | ${dscp}= | DSCP AF22
| | Given Policer Set Name | policer1
| | And Policer Set Node | ${dut_node}
| | And Policer Set CIR | ${1}
| | And Policer Set CB | ${2}
| | And Policer Set EB | ${eb}
| | And Policer Set Rate Type pps
| | And Policer Set Round Type Closest
| | And Policer Set Type 1R3C
| | And Policer Set Conform Action Transmit
| | And Policer Set Exceed Action Mark and Transmit | ${dscp}
| | And Policer Set Violate Action Drop
| | And Policer Enable Color Aware
| | And Policer Classify Set Precolor Exceed
| | And Policer Classify Set Interface | ${dut_to_tg_if1}
| | And Policer Classify Set Match IP | ${tg_to_dut_if1_ip}
| | When Policer Set Configuration
| | Then Send packet and verify marking | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if1_ip} | ${tg_to_dut_if2_ip} | ${dscp}

| TC04: VPP policer 1R3C Color-blind marks packet
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Ref] RFC2474, RFC2697.
| | ... | [Cfg] On DUT1 configure 1R3C color-blind policer on the first\
| | ... | interface.
| | ... | [Ver] TG sends IPv4 TCP packet on the first link to DUT1.\
| | ... | On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends\
| | ... | correct IPv4 TCP packet with correct DSCP on the second link to TG.
| | ${dscp}= | DSCP AF22
| | Given Policer Set Name | policer1
| | And Policer Set Node | ${dut_node}
| | And Policer Set CIR | ${cir}
| | And Policer Set CB | ${cb}
| | And Policer Set EB | ${eb}
| | And Policer Set Rate Type pps
| | And Policer Set Round Type Closest
| | And Policer Set Type 1R3C
| | And Policer Set Conform Action Mark and Transmit | ${dscp}
| | And Policer Set Exceed Action Transmit
| | And Policer Set Violate Action Drop
| | And Policer Classify Set Precolor Conform
| | And Policer Classify Set Interface | ${dut_to_tg_if1}
| | And Policer Classify Set Match IP | ${tg_to_dut_if1_ip}
| | When Policer Set Configuration
| | Then Send packet and verify marking | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if1_ip} | ${tg_to_dut_if2_ip} | ${dscp}