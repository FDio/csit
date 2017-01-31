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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/tagging.robot
| Resource | resources/libraries/robot/traffic.robot
| Library  | resources.libraries.python.Trace
| Library | resources.libraries.python.IPv6Util
| Force Tags | 3_NODE_DOUBLE_LINK_TOPO | VM_ENV | HW_ENV | VPP_VM_ENV
| Test Setup | Func Test Setup
| Test Teardown | Func Test Teardown
| Documentation | *IPv4 with VLAN subinterfaces*
| ...

*** Variables ***

| ${ip4_net0_1}= | 192.168.0.1
| ${ip4_net0_2}= | 192.168.0.2
| ${ip4_net1_1}= | 192.168.100.1
| ${ip4_net1_2}= | 192.168.100.2
| ${ip4_net2_1}= | 192.168.200.1
| ${ip4_net2_2}= | 192.168.200.2
| ${ip4_prefix}= | 24

*** Test Cases ***
| TC01: Process untagged send tagged
| | [Tags] |
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up

| | ${vlan1_name} | ${vlan1_index}= | Vlan Subinterface Created
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${10}
| | ${vlan2_name} | ${vlan2_index}= | Vlan Subinterface Created
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${20}

| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${ip4_net0_1} | ${ip4_prefix}
| | And Set Interface Address | ${dut_node}
| | ... | ${vlan2_index} | ${ip4_net1_1} | ${ip4_prefix}
| | And Set Interface Address | ${dut_node}
| | ... | ${vlan2_index} | ${ip4_net2_1} | ${ip4_prefix}

| | And Add IP Neighbor | ${dut_node} | ${vlan2_index} | ${ip4_net0_2}
| | ... | ${tg_to_dut_if1_mac}
| | And Add IP Neighbor | ${dut_node} | ${vlan2_index} | ${ip4_net1_2}
| | ... | ${tg_to_dut_if2_mac}
| | And Add IP Neighbor | ${dut_node} | ${vlan2_index} | ${ip4_net2_2}
| | ... | ${tg_to_dut_if2_mac}

| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${ip4_net0_2} | ${ip4_net2_2} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | encaps_rx=Dot1q | vlan_rx=${20}

| TC02: Process untagged send tagged
| | [Tags] | tmp
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up

| | ${vlan1_name} | ${vlan1_index}= | Vlan Subinterface Created
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${10}
| | ${vlan2_name} | ${vlan2_index}= | Vlan Subinterface Created
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${20}

| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${ip4_net0_1} | ${ip4_prefix}
| | And Set Interface Address | ${dut_node}
| | ... | ${vlan2_index} | ${ip4_net1_1} | ${ip4_prefix}
| | And Set Interface Address | ${dut_node}
| | ... | ${vlan2_index} | ${ip4_net2_1} | ${ip4_prefix}

| | And Add IP Neighbor | ${dut_node} | ${vlan2_index} | ${ip4_net0_2}
| | ... | ${tg_to_dut_if1_mac}
| | And Add IP Neighbor | ${dut_node} | ${vlan2_index} | ${ip4_net1_2}
| | ... | ${tg_to_dut_if2_mac}
| | And Add IP Neighbor | ${dut_node} | ${vlan2_index} | ${ip4_net2_2}
| | ... | ${tg_to_dut_if2_mac}

| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${ip4_net1_2} | ${ip4_net2_2} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | encaps_tx=Dot1q | vlan_tx=${10}
| | ... | encaps_rx=Dot1q | vlan_rx=${20}
