# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.Policer
| Library | resources.libraries.python.TrafficScriptExecutor
| ...
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| ...
| Documentation | Policer keywords

*** Keywords ***
| Configure topology for IPv4 policer test
| | [Documentation] | Setup topology for IPv4 policer testing.
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - dut_to_tg_if1_ip - DUT first interface IP address. Type: string
| | ... | - dut_to_tg_if2_ip - DUT second interface IP address. Type: string
| | ... | - tg_to_dut_if1_ip - TG first interface IP address. Type: string
| | ... | - tg_to_dut_if2_ip - TG second interface IP address. Type: string
| | Configure path in 2-node circular topology | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['TG']}
| | Set interfaces in 2-node circular topology up
| | VPP Interface Set IP Address | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${dut_to_tg_if1_ip4} | ${ip4_plen}
| | VPP Interface Set IP Address | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${dut_to_tg_if2_ip4} | ${ip4_plen}
| | VPP Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${tg_to_dut_if2_ip4}
| | ... | ${tg_to_dut_if2_mac}
| | Set Test Variable | ${dut_to_tg_if1_ip} | ${dut_to_tg_if1_ip4}
| | Set Test Variable | ${dut_to_tg_if2_ip} | ${dut_to_tg_if2_ip4}
| | Set Test Variable | ${tg_to_dut_if1_ip} | ${tg_to_dut_if1_ip4}
| | Set Test Variable | ${tg_to_dut_if2_ip} | ${tg_to_dut_if2_ip4}

| Configure topology for IPv6 policer test
| | [Documentation] | Setup topology for IPv6 policer testing.
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - dut_to_tg_if1_ip - DUT first interface IP address. Type: string
| | ... | - dut_to_tg_if2_ip - DUT second interface IP address. Type: string
| | ... | - tg_to_dut_if1_ip - TG first interface IP address. Type: string
| | ... | - tg_to_dut_if2_ip - TG second interface IP address. Type: string
| | Configure path in 2-node circular topology | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['TG']}
| | Set interfaces in 2-node circular topology up
| | VPP Interface Set IP Address
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${tg_to_dut_if2_ip6}
| | ... | ${tg_to_dut_if2_mac}
| | Vpp All RA Suppress Link Layer | ${nodes}
| | Set Test Variable | ${dut_to_tg_if1_ip} | ${dut_to_tg_if1_ip6}
| | Set Test Variable | ${dut_to_tg_if2_ip} | ${dut_to_tg_if2_ip6}
| | Set Test Variable | ${tg_to_dut_if1_ip} | ${tg_to_dut_if1_ip6}
| | Set Test Variable | ${tg_to_dut_if2_ip} | ${tg_to_dut_if2_ip6}

| Send packet and verify marking
| | [Documentation] | Send packet and verify DSCP of the received packet.
| | ...
| | ... | *Arguments:*
| | ... | - node - TG node. Type: dictionary
| | ... | - tx_if - TG transmit interface. Type: string
| | ... | - rx_if - TG receive interface. Type: string
| | ... | - src_mac - Packet source MAC. Type: string
| | ... | - dst_mac - Packet destination MAC. Type: string
| | ... | - src_ip - Packet source IP address. Type: string
| | ... | - dst_ip - Packet destination IP address. Type: string
| | ... | - dscp - DSCP value to verify. Type: enum
| | ...
| | ... | *Example:*
| | ... | \| ${dscp}= \| DSCP AF22 \|
| | ... | \| Send packet and verify marking \| ${nodes['TG']} \| eth1 \| eth2 \
| | ... | \| 08:00:27:87:4d:f7 \| 52:54:00:d4:d8:22 \| 192.168.122.2 \
| | ... | \| 192.168.122.1 \| ${dscp} \|
| | [Arguments] | ${node} | ${tx_if} | ${rx_if} | ${src_mac} | ${dst_mac}
| | ... | ${src_ip} | ${dst_ip} | ${dscp}
| | ${tx_if_name}= | Get Interface Name | ${node} | ${tx_if}
| | ${rx_if_name}= | Get Interface Name | ${node} | ${rx_if}
| | ${args}= | Traffic Script Gen Arg | ${rx_if_name} | ${tx_if_name}
| | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${dscp_num}= | Get DSCP Num Value | ${dscp}
| | ${args}= | Set Variable | ${args} --dscp ${dscp_num}
| | Run Traffic Script On Node | policer.py | ${node} | ${args}
