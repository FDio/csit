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
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/l2/tagging.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Library  | resources.libraries.python.Trace
| Library | resources.libraries.python.IPv6Util
| Force Tags | 3_NODE_DOUBLE_LINK_TOPO | VM_ENV | HW_ENV | VPP_VM_ENV
| ... | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *IPv4 with VLAN subinterfaces*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology
| ... | with double links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-IPv4-ICMPv4 on TG-DUT1-IF1,
| ... | Eth-dot1q-IPv4-ICMPv4 on TG-DUT1-IF2.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with 2 Vlan subinterfaces
| ... | on DUT1-IF2. The subinterfaces and DUT1-IF1 have IP addresses set and
| ... | corresponding IP neighbor entries are configured.
| ... | *[Ref] Applicable standard specifications:* IEEE 802.1q.

*** Variables ***

| ${ip4_net0_1}= | 192.168.0.1
| ${ip4_net0_2}= | 192.168.0.2
| ${ip4_net1_1}= | 192.168.100.1
| ${ip4_net1_2}= | 192.168.100.2
| ${ip4_net2_1}= | 192.168.200.1
| ${ip4_net2_2}= | 192.168.200.2
| ${ip4_prefix}= | 24
| ${tag_1}= | ${10}
| ${tag_2}= | ${20}

*** Test Cases ***
| TC01: Process untagged send tagged
| | Given Vlan Test Setup
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${ip4_net0_2} | ${ip4_net2_2} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | encaps_rx=Dot1q | vlan_rx=${tag_2}

| TC02: Process tagged send untagged
| | Given Vlan Test Setup
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${ip4_net2_2} | ${ip4_net0_2} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if1}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac}
| | ... | encaps_tx=Dot1q | vlan_tx=${tag_2}

| TC03: Process tagged send tagged
| | Given Vlan Test Setup
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${ip4_net1_2} | ${ip4_net2_2} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | encaps_tx=Dot1q | vlan_tx=${tag_1}
| | ... | encaps_rx=Dot1q | vlan_rx=${tag_2}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${ip4_net2_2} | ${ip4_net1_2} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | encaps_tx=Dot1q | vlan_tx=${tag_2}
| | ... | encaps_rx=Dot1q | vlan_rx=${tag_1}

*** Keywords ***
| Vlan Test Setup
| | Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Set interfaces in 2-node circular topology up
| |
| | ${vlan1_name} | ${vlan1_index}= | Create vlan sub-interface
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${tag_1}
| | ${vlan2_name} | ${vlan2_index}= | Create vlan sub-interface
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${tag_2}
| |
| | Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${ip4_net0_1} | ${ip4_prefix}
| | Set Interface Address | ${dut_node}
| | ... | ${vlan1_index} | ${ip4_net1_1} | ${ip4_prefix}
| | Set Interface Address | ${dut_node}
| | ... | ${vlan2_index} | ${ip4_net2_1} | ${ip4_prefix}
| |
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${ip4_net0_2}
| | ... | ${tg_to_dut_if1_mac}
| | Add IP Neighbor | ${dut_node} | ${vlan1_index} | ${ip4_net1_2}
| | ... | ${tg_to_dut_if2_mac}
| | Add IP Neighbor | ${dut_node} | ${vlan2_index} | ${ip4_net2_2}
| | ... | ${tg_to_dut_if2_mac}
