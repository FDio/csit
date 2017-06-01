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
| Resource | resources/libraries/robot/interfaces.robot

*** Keywords ***
| Create GRE tunnel interface and set it up
| | [Documentation] | Create GRE tunnel interface and set it up on defined VPP node and put \
| | ... | the interface to UP state.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to create GRE tunnel. Type: dictionary
| | ... | - source_ip_address - GRE tunnel source IP address. Type: string
| | ... | - destination_ip_address - GRE tunnel destination IP address.
| | ... |   Type: string
| | ...
| | ... | *Return:*
| | ... | - name - Name of created GRE tunnel interface. Type: string
| | ... | - index - SW interface index of created GRE tunnel interface.
| | ... |   Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ${gre_name} \| ${gre_index}= \
| | ... | \| Create GRE tunnel interface and set it up \| ${dut} \
| | ... | \| 192.0.1.1 \| 192.0.1.2 \|
| | ...
| | [Arguments] | ${dut_node} | ${source_ip_address} | ${destination_ip_address}
| | ${name} | ${index}= | Create GRE tunnel interface
| | ... | ${dut_node} | ${source_ip_address} | ${destination_ip_address}
| | Set Interface State | ${dut_node} | ${index} | up
| | [Return] | ${name} | ${index}


| Send ICMPv4 and check received GRE header
| | [Documentation] | Send ICMPv4 packet and check if received packed contains \
| | ... | correct GRE, IP, MAC headers.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: dictionary
| | ... | - tx_if - Interface from where send ICPMv4 packet. Type: string
| | ... | - rx_if - Interface where to receive GRE packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of ICMP packet. Type: string
| | ... | - rx_dst_mac - Expected destination MAC address of GRE packet.
| | ... |   Type: string
| | ... | - inner_src_ip - Source IP address of ICMP packet. Type: string
| | ... | - inner_dst_ip - Destination IP address of ICMP packet.
| | ... |   Type: string
| | ... | - outer_src_ip - Source IP address of GRE packet. Type: string
| | ... | - outer_dst_ip - Destination IP address of GRE packet.
| | ... |   Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send ICMPv4 and check received GRE header \
| | ... | \| ${tg_node} \| ${tg_to_dut_if1} \| ${tg_to_dut_if2} \
| | ... | \| ${tx_dst_mac} \| ${rx_dst_mac} \| ${net1_host_address} \
| | ... | \| ${net2_host_address} \| ${dut1_ip_address} \| ${dut2_ip_address} \|
| | ...
| | [Arguments] | ${tg_node} | ${tx_if} | ${rx_if}
| | ... | ${tx_dst_mac} | ${rx_dst_mac}
| | ... | ${inner_src_ip} | ${inner_dst_ip}
| | ... | ${outer_src_ip} | ${outer_dst_ip}
| | ${tx_if_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_if_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate | --tx_if | ${tx_if_name} | --rx_if | ${rx_if_name}
| | ... | --tx_dst_mac | ${tx_dst_mac} | --rx_dst_mac | ${rx_dst_mac}
| | ... | --inner_src_ip | ${inner_src_ip} | --inner_dst_ip | ${inner_dst_ip}
| | ... | --outer_src_ip | ${outer_src_ip} | --outer_dst_ip | ${outer_dst_ip}
| | Run Traffic Script On Node
| | ... | send_icmp_check_gre_headers.py | ${tg_node} | ${args}


| Send GRE and check received ICMPv4 header
| | [Documentation] | Send IPv4 ICMPv4 packet encapsulated into GRE and \
| | ... | check IP, MAC headers on received packed.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: dictionary
| | ... | - tx_if - Interface from where send ICPMv4 packet. Type: string
| | ... | - rx_if - Interface where receive GRE packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of GRE packet. Type: string
| | ... | - rx_dst_mac - Expected destination MAC address of ICMP packet.
| | ... |   Type: string
| | ... | - inner_src_ip - Source IP address of ICMP packet. Type: string
| | ... | - inner_dst_ip - Destination IP address of ICMP packet.
| | ... |   Type: string
| | ... | - outer_src_ip - Source IP address of GRE packet. Type: string
| | ... | - outer_dst_ip - Destination IP address of  GRE packet.
| | ... |   Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send GRE and check received ICMPv4 header \| ${tg_node} \
| | ... | \| ${tg_to_dut_if2} \| ${tg_to_dut_if1} \| ${tx_dst_mac} \
| | ... | \| ${rx_dst_mac} \| ${net2_host_address} \| ${net1_host_address} \
| | ... | \| ${dut2_ip_address} \| ${dut1_ip_address} \|
| | ...
| | [Arguments] | ${tg_node} | ${tx_if} | ${rx_if}
| | ... | ${tx_dst_mac} | ${rx_dst_mac}
| | ... | ${inner_src_ip} | ${inner_dst_ip}
| | ... | ${outer_src_ip} | ${outer_dst_ip}
| | ${tx_if_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_if_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate | --tx_if | ${tx_if_name} | --rx_if | ${rx_if_name}
| | ... | --tx_dst_mac | ${tx_dst_mac} | --rx_dst_mac | ${rx_dst_mac}
| | ... | --inner_src_ip | ${inner_src_ip} | --inner_dst_ip | ${inner_dst_ip}
| | ... | --outer_src_ip | ${outer_src_ip} | --outer_dst_ip | ${outer_dst_ip}
| | Run Traffic Script On Node
| | ... | send_gre_check_icmp_headers.py | ${tg_node} | ${args}

| Send GRE and check received GRE header
| | [Documentation] | Send IPv4 UDP packet encapsulated into GRE and \
| | ... | check if received packed contains correct MAC GRE, IP, UDP headers.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: dictionary
| | ... | - tx_if - Interface from where send GRE packet. Type: string
| | ... | - rx_if - Interface where to receive GRE packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of transferred packet.
| | ... |   Type: string
| | ... | - tx_src_mac - Source MAC address of transferred packet. Type: string
| | ... | - tx_outer_dst_ip - Destination IP address of GRE packet. Type: string
| | ... | - tx_outer_src_ip - Source IP address of GRE packet. Type: string
| | ... | - tx_inner_dst_ip - Destination IP address of UDP packet. Type: string
| | ... | - tx_inner_src_ip - Source IP address of UDP packet. Type: string
| | ... | - rx_dst_mac - Expected destination MAC address. Type: string
| | ... | - rx_src_mac - Expected source MAC address. Type: string
| | ... | - rx_outer_dst_ip - Expected destination IP address of received GRE
| | ... |   packet. Type: string
| | ... | - rx_outer_src_ip - Expected source IP address of received GRE
| | ... |   packet. Type: string
| | ...
| | ... | __Note:__
| | ... | rx_inner_dst_ip and rx_inner_src_ip should be same as transferred
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Send GRE and check received GRE header \| ${tg_node} \
| | ... | \| port3 \| port3 \| 08:00:27:f3:be:f0 \| 08:00:27:46:2b:4c \
| | ... | \| 10.0.0.1 \| 10.0.0.2 \| 192.168.3.100 \| 192.168.2.100 \
| | ... | \| 08:00:27:46:2b:4c \| 08:00:27:f3:be:f0 \| 10.0.0.3 \| 10.0.0.1 \|
| | ...
| | [Arguments] | ${tg_node} | ${tx_if} | ${rx_if}
| | ... | ${tx_dst_mac} | ${tx_src_mac}
| | ... | ${tx_outer_dst_ip} | ${tx_outer_src_ip}
| | ... | ${tx_inner_dst_ip} | ${tx_inner_src_ip}
| | ... | ${rx_dst_mac} | ${rx_src_mac}
| | ... | ${rx_outer_dst_ip} | ${rx_outer_src_ip}
| | ${tx_if_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_if_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate | --tx_if | ${tx_if_name} | --rx_if | ${rx_if_name}
| | ... | --tx_dst_mac | ${tx_dst_mac} | --tx_src_mac | ${tx_src_mac}
| | ... | --tx_outer_dst_ip | ${tx_outer_dst_ip}
| | ... | --tx_outer_src_ip | ${tx_outer_src_ip}
| | ... | --tx_inner_dst_ip | ${tx_inner_dst_ip}
| | ... | --tx_inner_src_ip | ${tx_inner_src_ip}
| | ... | --rx_dst_mac | ${rx_dst_mac}
| | ... | --rx_src_mac | ${rx_src_mac}
| | ... | --rx_outer_dst_ip | ${rx_outer_dst_ip}
| | ... | --rx_outer_src_ip | ${rx_outer_src_ip}
| | Run Traffic Script On Node
| | ... | send_gre_check_gre_headers.py | ${tg_node} | ${args}
