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
| Library | resources.libraries.python.Policer
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPv4Util
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']}
| ...     | WITH NAME | dut1_v4
| Documentation | *Policer keywords*

*** Variables ***
| ${tg_to_dut_if1_ip4}= | 192.168.122.2
| ${tg_to_dut_if2_ip4}= | 192.168.123.2
| ${dut_to_tg_if1_ip4}= | 192.168.122.1
| ${dut_to_tg_if2_ip4}= | 192.168.123.1
| ${ip4_plen}= | ${24}
| ${tg_to_dut_if1_ip6}= | 3ffe:5f::2
| ${tg_to_dut_if2_ip6}= | 3ffe:60::2
| ${dut_to_tg_if1_ip6}= | 3ffe:5f::1
| ${dut_to_tg_if2_ip6}= | 3ffe:60::1
| ${ip6_plen}= | ${64}

*** Keywords ***
| Setup Topology for IPv4 policer testing
| | [Documentation] | Setup topology for IPv4 policer testing.
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${dut_to_tg_if1_ip} - DUT first interface IP address. Type: string
| | ... | - ${dut_to_tg_if2_ip} - DUT second interface IP address. Type: string
| | ... | - ${tg_to_dut_if1_ip} - TG first interface IP address. Type: string
| | ... | - ${tg_to_dut_if2_ip} - TG second interface IP address. Type: string
| | Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                            | ${nodes['TG']}
| | Interfaces in 2-node path are up
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1}
| | ...                   | ${dut_to_tg_if1_ip4} | ${ip4_plen}
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if2}
| | ...                   | ${dut_to_tg_if2_ip4} | ${ip4_plen}
| | dut1_v4.Set ARP | ${dut_to_tg_if2} | ${tg_to_dut_if2_ip4}
| | ...             | ${tg_to_dut_if2_mac}
| | Set Test Variable | ${dut_to_tg_if1_ip} | ${dut_to_tg_if1_ip4}
| | Set Test Variable | ${dut_to_tg_if2_ip} | ${dut_to_tg_if2_ip4}
| | Set Test Variable | ${tg_to_dut_if1_ip} | ${tg_to_dut_if1_ip4}
| | Set Test Variable | ${tg_to_dut_if2_ip} | ${tg_to_dut_if2_ip4}

| Setup Topology for IPv6 policer testing
| | [Documentation] | Setup topology for IPv6 policer testing.
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${dut_to_tg_if1_ip} - DUT first interface IP address. Type: string
| | ... | - ${dut_to_tg_if2_ip} - DUT second interface IP address. Type: string
| | ... | - ${tg_to_dut_if1_ip} - TG first interface IP address. Type: string
| | ... | - ${tg_to_dut_if2_ip} - TG second interface IP address. Type: string
| | Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                            | ${nodes['TG']}
| | Interfaces in 2-node path are up
| | Vpp Set If IPv6 Addr | ${dut_node} | ${dut_to_tg_if1}
| | ...                  | ${dut_to_tg_if1_ip6} | ${ip6_plen}
| | Vpp Set If IPv6 Addr | ${dut_node} | ${dut_to_tg_if2}
| | ...                  | ${dut_to_tg_if2_ip6} | ${ip6_plen}
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${tg_to_dut_if2_ip6}
| | ...             | ${tg_to_dut_if2_mac}
| | Vpp All RA Suppress Link Layer | ${nodes}
| | Set Test Variable | ${dut_to_tg_if1_ip} | ${dut_to_tg_if1_ip6}
| | Set Test Variable | ${dut_to_tg_if2_ip} | ${dut_to_tg_if2_ip6}
| | Set Test Variable | ${tg_to_dut_if1_ip} | ${tg_to_dut_if1_ip6}
| | Set Test Variable | ${tg_to_dut_if2_ip} | ${tg_to_dut_if2_ip6}

| Send Packet and Verify Marking
| | [Documentation] | Send packet and verify DSCP of the received packet.
| | ...
| | ... | *Arguments:*
| | ... | - ${node} - TG node. Type: dictionary
| | ... | - ${tx_if} - TG transmit interface. Type: string
| | ... | - ${rx_if} - TG receive interface. Type: string
| | ... | - ${src_mac} - Packet source MAC. Type: string
| | ... | - ${dst_mac} - Packet destination MAC. Type: string
| | ... | - ${src_ip} - Packet source IP address. Type: string
| | ... | - ${dst_ip} - Packet destination IP address. Type: string
| | ... | - ${dscp} - DSCP value to verify. Type: enum
| | ...
| | ... | *Example:*
| | ... | \| ${dscp}= \| DSCP AF22
| | ... | \| Send Packet and Verify Marking \| ${nodes['TG']} \| eth1 \| eth2 \
| | ... | \| 08:00:27:87:4d:f7 \| 52:54:00:d4:d8:22 \| 192.168.122.2 \
| | ... | \| 192.168.122.1 \| ${dscp}
| | [Arguments] | ${node} | ${tx_if} | ${rx_if} | ${src_mac} | ${dst_mac}
| | ...         | ${src_ip} | ${dst_ip} | ${dscp}
| | ${args}= | Traffic Script Gen Arg | ${rx_if} | ${tx_if} | ${src_mac}
| | ...      | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${dscp_num}= | Get DSCP Num Value | ${dscp}
| | ${args}= | Set Variable | ${args} --dscp ${dscp_num}
| | Run Traffic Script On Node | policer.py | ${node} | ${args}
