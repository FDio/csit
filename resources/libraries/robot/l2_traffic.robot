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
| Documentation | Keywords to send and receive different types of traffic \
| ...           | through L2 network.
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficScriptExecutor

*** Keywords ***
| Send and receive ICMP Packet
| | [Documentation] | Send ICMPv4/ICMPv6 echo request from source interface to \
| | ...             | destination interface. Dot1q or Dot1ad tag(s) can be set.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address (Optional). Type: string
| | ... | - dst_ip - Destination IP address (Optional). Type: string
| | ... | - encaps - Encapsulation: Dot1q or Dot1ad (Optional). Type: string
| | ... | - vlan1 - VLAN (outer) tag (Optional). Type: integer
| | ... | - vlan2 - VLAN inner tag (Optional). Type: integer
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | _NOTE:_ Default IP is IPv4
| | ...
| | ... | \| Send and receive ICMP Packet \| ${nodes['TG']} \
| | ... | \| ${tg_to_dut_if1} \| ${tg_to_dut_if2} \|
| | ... | \| Send and receive ICMP Packet \| ${nodes['TG']} \| ${tg_to_dut1} \
| | ... | \| ${tg_to_dut2} \| encaps=Dot1q \| vlan1=100 \|
| | ... | \| Send and receive ICMP Packet \| ${nodes['TG']} \| ${tg_to_dut1} \
| | ... | \| ${tg_to_dut2} \| encaps=Dot1ad \| vlan1=110 \| vlan2=220 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_int} | ${dst_int} |
| | ... | ${src_ip}=192.168.100.1 | ${dst_ip}=192.168.100.2 | ${encaps}=${EMPTY}
| | ... | ${vlan1}=${EMPTY} | ${vlan2}=${EMPTY}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_int}
| | ${dst_mac}= | Get Interface Mac | ${tg_node} | ${dst_int}
| | ${src_int_name}= | Get interface name | ${tg_node} | ${src_int}
| | ${dst_int_name}= | Get interface name | ${tg_node} | ${dst_int}
| | ${args}= | Traffic Script Gen Arg | ${dst_int_name} | ${src_int_name}
| | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args1}= | Run Keyword Unless | '${encaps}' == '${EMPTY}' | Catenate
| | ... | --encaps ${encaps} | --vlan1 ${vlan1}
| | ${args2}= | Run Keyword Unless | '${vlan2}' == '${EMPTY}' | Set Variable
| | ... | --vlan2 ${vlan2}
| | ${args}= | Run Keyword If | '${args1}' == 'None' | Set Variable | ${args}
| | ... | ELSE IF | '${args2}' == 'None' | Catenate | ${args} | ${args1}
| | ... | ELSE | Catenate | ${args} | ${args1} | ${args2}
| | Run Traffic Script On Node | send_ip_icmp.py | ${tg_node} | ${args}

| Send and receive ICMP Packet should failed
| | [Documentation] | Send ICMPv4/ICMPv6 echo request from source interface to
| | ...             | destination interface and expect failure with
| | ...             | ICMP echo Rx timeout error message.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address (Optional). Type: string
| | ... | - dst_ip - Destination IP address (Optional). Type: string
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | _NOTE:_ Default IP is IPv4
| | ...
| | ... | \| Send and receive ICMP Packet \| ${nodes['TG']} \
| | ... | \| ${tg_to_dut_if1} \| ${tg_to_dut_if2} \|
| | ...
| | [Arguments] | ${tg_node} | ${src_int} | ${dst_int} |
| | ... | ${src_ip}=192.168.100.1 | ${dst_ip}=192.168.100.2
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_int}
| | ${dst_mac}= | Get Interface Mac | ${tg_node} | ${dst_int}
| | ${src_int_name}= | Get interface name | ${tg_node} | ${src_int}
| | ${dst_int_name}= | Get interface name | ${tg_node} | ${dst_int}
| | ${args}= | Traffic Script Gen Arg | ${dst_int_name} | ${src_int_name}
| | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Keyword And Expect Error | ICMP echo Rx timeout |
| | ... | Run Traffic Script On Node | send_ip_icmp.py | ${tg_node} | ${args}

| Send and receive ICMPv4 bidirectionally
| | [Documentation] | Send ICMPv4 echo request from both directions,
| | ...             | from interface1 to interface2 and
| | ...             | from interface2 to interface1.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address (Optional). Type: string
| | ... | - dst_ip - Destination IP address (Optional). Type: string
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send and receive ICMPv4 bidirectionally \| ${nodes['TG']} \
| | ... | \| ${tg_to_dut_if1} \| ${tg_to_dut_if2} \|
| | ...
| | [Arguments] | ${tg_node} | ${int1} | ${int2} | ${src_ip}=192.168.100.1 |
| | ... | ${dst_ip}=192.168.100.2
| | Send and receive ICMP Packet | ${tg_node} | ${int1} | ${int2} |
| | ... | ${src_ip} | ${dst_ip}
| | Send and receive ICMP Packet | ${tg_node} | ${int2} | ${int1} |
| | ... | ${dst_ip} | ${src_ip}

| Send and receive ICMPv6 bidirectionally
| | [Documentation] | Send ICMPv6 echo request from both directions,
| | ...             | from interface1 to interface2 and
| | ...             | from interface2 to interface1.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address (Optional). Type: string
| | ... | - dst_ip - Destination IP address (Optional). Type: string
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send and receive ICMPv6 bidirectionally \| ${nodes['TG']} \
| | ... | \| ${tg_to_dut_if1} \| ${tg_to_dut_if2} \|
| | ...
| | [Arguments] | ${tg_node} | ${int1} | ${int2} | ${src_ip}=3ffe:63::1 |
| | ... | ${dst_ip}=3ffe:63::2
| | Send and receive ICMP Packet | ${tg_node} | ${int1} | ${int2} |
| | ... | ${src_ip} | ${dst_ip}
| | Send and receive ICMP Packet | ${tg_node} | ${int2} | ${int1} |
| | ... | ${dst_ip} | ${src_ip}
