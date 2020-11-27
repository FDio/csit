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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficScriptExecutor
| Documentation | Keywords to send and receive different types of traffic \
| ... | through L2 network.

*** Keywords ***
| Send IP packet and verify received packet
| | [Documentation] | Send IPv4/IPv6 packet from source interface to \
| | ... | destination interface. Packet can be set with Dot1q or
| | ... | Dot1ad tag(s) when required.
| |
| | ... | *Arguments:*
| |
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address (Optional). Type: string
| | ... | - dst_ip - Destination IP address (Optional). Type: string
| | ... | - encaps - Encapsulation: Dot1q or Dot1ad (Optional). Type: string
| | ... | - vlan1 - VLAN (outer) tag (Optional). Type: integer
| | ... | - vlan2 - VLAN inner tag (Optional). Type: integer
| | ... | - encaps_rx - Expected encapsulation on RX side: Dot1q or Dot1ad
| | ... | (Optional). Type: string
| | ... | - vlan1_rx - VLAN (outer) tag on RX side (Optional). Type: integer
| | ... | - vlan2_rx - VLAN inner tag on RX side (Optional). Type: integer
| |
| | ... | *Return:*
| |
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | _NOTE:_ Default IP is IPv4
| |
| | ... | \| Send IP packet and verify received packet \| \${nodes['TG']} \
| | ... | \| \${tg_to_dut_if1} \| \${tg_to_dut_if2} \|
| | ... | \| Send IP packet and verify received packet \| \${nodes['TG']} \
| | ... | \| \${tg_to_dut1} \| \${tg_to_dut2} \| encaps=Dot1q \| vlan1=100 \|
| | ... | \| Send IP packet and verify received packet \| \${nodes['TG']} \
| | ... | \| \${tg_to_dut1} \| \${tg_to_dut2} \| encaps=Dot1ad \| vlan1=110 \
| | ... | \| vlan2=220 \|
| | ... | \| Send IP packet and verify received packet \| \${nodes['TG']} \
| | ... | \| \${tg_to_dut1} \| \${tg_to_dut2} \| encaps=Dot1q \| vlan1=110 \
| | ... | \| encaps_rx=Dot1q \|
| | ... | \| Send IP packet and verify received packet \| \${nodes['TG']} \
| | ... | \| \${tg_to_dut1} \| \${tg_to_dut2} \| encaps=Dot1q \| vlan1=110 \
| | ... | \| encaps_rx=Dot1q \| vlan1_rx=120 \|
| |
| | [Arguments] | ${tg_node} | ${tx_src_port} | ${rx_dst_port}
| | ... | ${src_ip}=192.168.100.1 | ${dst_ip}=192.168.100.2
| | ... | ${encaps}=${EMPTY} | ${vlan1}=${EMPTY} | ${vlan2}=${EMPTY}
| | ... | ${encaps_rx}=${EMPTY} | ${vlan1_rx}=${EMPTY} | ${vlan2_rx}=${EMPTY}
| |
| | ${tx_src_mac}= | Get Interface Mac | ${tg_node} | ${tx_src_port}
| | ${rx_dst_mac}= | Get Interface Mac | ${tg_node} | ${rx_dst_port}
| | Then Send packet and verify headers
| | ... | ${tg} | 192.168.0.1 | 192.168.0.2
| | ... | ${tx_src_port} | ${tx_src_mac} | ${rx_dst_mac}
| | ... | ${rx_dst_port} | ${tx_src_mac} | ${rx_dst_mac}
| | ... | encaps_tx=${encaps} | vlan_tx=${vlan1} | vlan_outer_tx=${vlan2}
| | ... | encaps_rx=${encaps_rx} | vlan_rx=${vlan1_rx}
| | ... | vlan_outer_rx=${vlan2_rx}

| Send IPv4 bidirectionally and verify received packets
| | [Documentation] | Send IPv4 packets from both directions,
| | ... | from interface1 to interface2 and from interface2 to interface1.
| |
| | ... | *Arguments:*
| |
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address (Optional). Type: string
| | ... | - dst_ip - Destination IP address (Optional). Type: string
| |
| | ... | *Return:*
| |
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Send IPv4 bidirectionally and verify received packets \
| | ... | \| \${nodes['TG']} \| \${tg_to_dut_if1} \| \${tg_to_dut_if2} \|
| |
| | [Arguments] | ${tg_node} | ${int1} | ${int2} | ${src_ip}=192.168.100.1 |
| | ... | ${dst_ip}=192.168.100.2
| |
| | Send IP packet and verify received packet
| | ... | ${tg_node} | ${int1} | ${int2} | ${src_ip} | ${dst_ip}
| | Send IP packet and verify received packet
| | ... | ${tg_node} | ${int2} | ${int1} | ${dst_ip} | ${src_ip}

| Send IPv6 bidirectionally and verify received packets
| | [Documentation] | Send IPv6 packets from both directions,
| | ... | from interface1 to interface2 and from interface2 to interface1.
| |
| | ... | *Arguments:*
| |
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address (Optional). Type: string
| | ... | - dst_ip - Destination IP address (Optional). Type: string
| |
| | ... | *Return:*
| |
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Send IPv6 bidirectionally and verify received packets \
| | ... | \| ${nodes['TG']} \| ${tg_to_dut_if1} \| ${tg_to_dut_if2} \|
| |
| | [Arguments] | ${tg_node} | ${int1} | ${int2} | ${src_ip}=3ffe:63::1 |
| | ... | ${dst_ip}=3ffe:63::2
| |
| | Send IP packet and verify received packet
| | ... | ${tg_node} | ${int1} | ${int2} | ${src_ip} | ${dst_ip}
| | Send IP packet and verify received packet
| | ... | ${tg_node} | ${int2} | ${int1} | ${dst_ip} | ${src_ip}
