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
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.topology.Topology
| Documentation | SPAN traffic keywords

*** Keywords ***
| Send Packet And Check Received Copies
| | [Documentation] | Sends an ARP or ICMP packet from TG to DUT using one\
| | ... | link, then receive a copy of both the sent packet and the DUT's reply\
| | ... | on the second link.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - tx_src_port - First interface on TG. Type: string
| | ... | - tx_src_mac - MAC address of the first interface on TG. Type: string
| | ... | - tx_dst_mac - MAC address of the first interface on DUT. Type: string
| | ... | - rx_port - Second interface on TG. Type: string
| | ... | - src_ip - Packet source IP address. Type: string
| | ... | - dst_ip - Packet destination IP address. Type: string
| | ... | - ptype - Type of payload, ARP, ICMP or ICMPv6. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send Packet And Check Received Copies \| ${nodes['TG']} \| eth1 \
| | ... | \| 8:00:27:ee:fd:b3 \| 08:00:27:a2:52:5b \
| | ... | \| eth3 \| 192.168.0.2 \| 192.168.0.3 \| ARP \|
| | ...
| | [Arguments] | ${tg_node} | ${tx_src_port}
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port}
| | ... | ${src_ip} | ${dst_ip} | ${ptype}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate
| | ... | --tg_src_mac ${tx_src_mac} --dut_if1_mac ${tx_dst_mac}
| | ... | --src_ip ${src_ip} --dst_ip ${dst_ip}
| | ... | --tx_if ${tx_port_name} --rx_if | ${rx_port_name}
| | ... | --ptype ${ptype}
| | Run Traffic Script On Node | span_check.py | ${tg_node} |
| | ... | ${args}
