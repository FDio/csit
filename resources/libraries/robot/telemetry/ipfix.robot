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

"""IPFIX keywords"""

*** Settings ***
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.InterfaceUtil
| Resource | resources/libraries/robot/default.robot
| Documentation | Traffic keywords

*** Keywords ***
| Send packets and verify IPFIX
| | [Documentation] | Send simple TCP or UDP packets from source interface\
| | ... | to destination interface. Listen for IPFIX flow report on source\
| | ... | interface and verify received report against number of packets sent.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - dst_node - Destination node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address. Type: string
| | ... | - dst_ip - Destination IP address. Type: string
| | ... | - protocol - TCP or UDP (Optional, default is TCP). Type: string
| | ... | - port - Source and destination ports to use
| | ... | (Optional, default is port 20). Type: integer
| | ... | - count - Number of packets to send
| | ... | (Optional, default is one packet). Type: integer
| | ... | - timeout - Timeout value in seconds (Optional, default is 10 sec).
| | ... | Should be at least twice the configured IPFIX flow report interval.
| | ... | Type: integer
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send packets and verify IPFIX \| ${nodes['TG']} | ${nodes['DUT1']}\
| | ... | \| eth1 \| GigabitEthernet0/8/0 \| 16.0.0.1 \| 192.168.0.2 \| UDP \
| | ... | \| ${20} \| ${5} \| ${10} \|
| | ... |
| | [Arguments] | ${tg_node} | ${dst_node} | ${src_int} | ${dst_int} |
| | ... | ${src_ip} | ${dst_ip} | ${protocol}=tcp | ${port}=20 | ${count}=1
| | ... | ${timeout}=${10}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_int}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_int}
| | ${src_int_name}= | Get interface name | ${tg_node} | ${src_int}
| | ${dst_int_name}= | Get interface name | ${dst_node} | ${dst_int}
| | ${args}= | Traffic Script Gen Arg | ${dst_int_name} | ${src_int_name}
| | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Set Variable
| | ... | ${args} --protocol ${protocol} --port ${port} --count ${count}
| | Run Traffic Script On Node | ipfix_check.py | ${tg_node} | ${args}
| | ... | ${timeout}

| Send session sweep and verify IPFIX
| | [Documentation] | Send simple TCP or UDP packets from source interface\
| | ... | to destination interface using a range of source addresses. Listen\
| | ... | for IPFIX flow report on source interface and verify received report\
| | ... | against number of packets sent from each source address.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - dst_node - Destination node. Type: dictionary
| | ... | - src_int - Source interface. Type: string
| | ... | - dst_int - Destination interface. Type: string
| | ... | - src_ip - Source IP address. Type: string
| | ... | - dst_ip - Destination IP address. Type: string
| | ... | - ip_range - Number of sequential source addresses. Type:integer
| | ... | - protocol - TCP or UDP (Optional, defaults to TCP). Type: string
| | ... | - port - Source and destination ports to use (Optional). Type: integer
| | ... | - count - Number of packets to send (Optional). Type: integer
| | ... | - timeout - Timeout value in seconds (optional). Type:integer
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send packets and verify IPFIX \| ${nodes['TG']} | ${nodes['DUT1']}\
| | ... | \| eth1 \| GigabitEthernet0/8/0 \| 16.0.0.1 \| 192.168.0.2 \| 20 \|
| | ... | UDP \| ${20} \| ${5} \| ${10} \|
| | ... |
| | [Arguments] | ${tg_node} | ${dst_node} | ${src_int} | ${dst_int} |
| | ... | ${src_ip} | ${dst_ip} | ${ip_range} | ${protocol}=tcp | ${port}=20
| | ... | ${count}=${1} | ${timeout}=${10}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_int}
| | ${dst_mac}= | Set Variable | ${dut1_to_tg_mac}
| | ${src_int_name}= | Get interface name | ${tg_node} | ${src_int}
| | ${dst_int_name}= | Get interface name | ${dst_node} | ${dst_int}
| | ${args}= | Traffic Script Gen Arg | ${dst_int_name} | ${src_int_name}
| | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Set Variable | ${args} --protocol ${protocol} --port ${port}
| | ${args}= | Set Variable | ${args} --count ${count} --sessions ${ip_range}
| | Run Traffic Script On Node | ipfix_sessions.py | ${tg_node} | ${args}
| | ... | ${timeout}