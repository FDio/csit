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
| Library  | Collections
| Resource | resources/libraries/robot/default.robot
| Library  | resources.libraries.python.Dhcp.DhcpProxy
| Library  | resources.libraries.python.TrafficScriptExecutor
| Documentation | DHCP Proxy specific keywords.

*** Keywords ***
| Send DHCP Messages
| | [Documentation] | Send and receive DHCP messages between client
| | ...             | and server through DHCP proxy.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - tg_interface1 - TG interface. Type: string
| | ... | - tg_interface2 - TG interface. Type: string
| | ... | - server_ip - DHCP server IP address. Type: string
| | ... | - server_mac - DHCP server MAC address. Type: string
| | ... | - client_ip - Client IP address. Type: string
| | ... | - client_mac - Client MAC address. Type: string
| | ... | - proxy_ip - DHCP proxy IP address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send DHCP Messages \| ${nodes['TG']} \
| | ... | \| eth3 \| eth4 \| 192.168.0.100 \| 08:00:27:cc:4f:54 \
| | ... | \| 172.16.0.2 \| 08:00:27:64:18:d2 \| 172.16.0.1 \|
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface1} | ${tg_interface2}
| | ... | ${server_ip} | ${server_mac} | ${client_ip} | ${client_mac}
| | ... | ${proxy_ip} |
| | ${tg_interface_name1}= | Get interface name | ${tg_node} | ${tg_interface1}
| | ${tg_interface_name2}= | Get interface name | ${tg_node} | ${tg_interface2}
| | ${args}= | Catenate | --tx_if | ${tg_interface_name1}
| | ...                 | --rx_if | ${tg_interface_name2}
| | ...                 | --server_ip | ${server_ip}
| | ...                 | --server_mac | ${server_mac}
| | ...                 | --client_ip | ${client_ip}
| | ...                 | --client_mac | ${client_mac}
| | ...                 | --proxy_ip | ${proxy_ip}
| | Run Traffic Script On Node | dhcp/send_and_check_proxy_messages.py
| | ... | ${tg_node} | ${args}

| Send DHCP DISCOVER
| | [Documentation] | Send and receive DHCP DISCOVER.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - tg_interface1 - TG interface. Type: string
| | ... | - tg_interface2 - TG interface. Type: string
| | ... | - tx_src_ip - Source address of DHCP DISCOVER packet. Type: string
| | ... | - tx_dst_ip - Destination address of DHCP DISCOVER packet. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send DHCP DISCOVER \| ${nodes['TG']} \
| | ... | \| eth3 \| eth4 \| 0.0.0.0 \| 255.255.255.255 \|
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface1} | ${tg_interface2}
| | ... | ${tx_src_ip} | ${tx_dst_ip} |
| | ${tg_interface_name1}= | Get interface name | ${tg_node} | ${tg_interface1}
| | ${tg_interface_name2}= | Get interface name | ${tg_node} | ${tg_interface2}
| | ${args}= | Catenate | --tx_if | ${tg_interface_name1}
| | ...                 | --rx_if | ${tg_interface_name2}
| | ...                 | --tx_src_ip | ${tx_src_ip}
| | ...                 | --tx_dst_ip | ${tx_dst_ip}
| | Run Traffic Script On Node | dhcp/send_and_check_proxy_discover.py
| | ... | ${tg_node} | ${args}

| Send DHCP DISCOVER should fail
| | [Documentation] | Send and receive DHCP DISCOVER should fail.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - tg_interface1 - TG interface. Type: string
| | ... | - tg_interface2 - TG interface. Type: string
| | ... | - tx_src_ip - Source address of DHCP DISCOVER packet. Type: string
| | ... | - tx_dst_ip - Destination address of DHCP DISCOVER packet. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send DHCP DISCOVER should fail \| ${nodes['TG']} \
| | ... | \| eth3 \| eth4 \| 0.0.0.0 \| 255.255.255.1 \|
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface1} | ${tg_interface2}
| | ... | ${tx_src_ip} | ${tx_dst_ip} |
| | ${tg_interface_name1}= | Get interface name | ${tg_node} | ${tg_interface1}
| | ${tg_interface_name2}= | Get interface name | ${tg_node} | ${tg_interface2}
| | ${args}= | Catenate | --tx_if | ${tg_interface_name1}
| | ...                 | --rx_if | ${tg_interface_name2}
| | ...                 | --tx_src_ip | ${tx_src_ip}
| | ...                 | --tx_dst_ip | ${tx_dst_ip}
| | Run Keyword And Expect Error | DHCP DISCOVER Rx timeout
| | ... | Run Traffic Script On Node | dhcp/send_and_check_proxy_discover.py
| | ... | ${tg_node} | ${args}