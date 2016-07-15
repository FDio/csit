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
| Library  | resources.libraries.python.Dhcp.DhcpClient
| Library  | resources.libraries.python.TrafficScriptExecutor
| Documentation | DHCP Client specific keywords.

*** Keywords ***
| Check DHCP DISCOVER header
| | [Documentation] | Check if DHCP DISCOVER message contains all required
| | ... | fields.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - interface - TG interface where listen for DHCP DISCOVER message.
| | ... |   Type: string
| | ... | - src_mac - DHCP client MAC address. Type: string
| | ... | - hostname - DHCP client hostname (Optional, Default="", if not
| | ... |   specified, the hostname is not checked). Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Check DHCP DISCOVER header \| ${nodes['TG']} \
| | ... | \| eth2 \| 08:00:27:66:b8:57 \|
| | ... | \| Check DHCP DISCOVER header \| ${nodes['TG']} \
| | ... | \| eth2 \| 08:00:27:66:b8:57 \| client-hostname \|
| | ...
| | [Arguments] | ${tg_node} | ${interface} | ${src_mac} | ${hostname}=${EMPTY}
| | ${interface_name}= | Get interface name | ${tg_node} | ${interface}
| | ${args}= | Catenate | --rx_if | ${interface_name} | --rx_src_mac | ${src_mac}
| | ${args}= | Run Keyword If | "${hostname}" == "" | Set Variable | ${args}
| | ...      | ELSE | Catenate | ${args} | --hostname | ${hostname}
| | Run Traffic Script On Node | dhcp/check_dhcp_discover.py
| | ... | ${tg_node} | ${args}


| Check DHCP REQUEST after OFFER
| | [Documentation] | Check if DHCP REQUEST message contains all required
| | ... | fields. DHCP REQUEST should be send by a client after DHCP OFFER
| | ... | message sent by a server.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - tg_interface - TG interface where listen for DHCP DISCOVER,
| | ... |   send DHCP OFFER and listen for DHCP REQUEST messages. Type: string
| | ... | - server_mac - DHCP server MAC address. Type: string
| | ... | - server_ip - DHCP server IP address. Type: string
| | ... | - client_mac - DHCP client MAC address. Type: string
| | ... | - client_ip - IP address that should be offered to client.
| | ... |   Type: string
| | ... | - client_mask - IP netmask that should be offered to client.
| | ... |   Type: string
| | ... | - hostname - DHCP client hostname (Optional, Default="", if not
| | ... |   specified, the hostname is not checked). Type: string
| | ... | - offer_xid - Transaction ID (Optional, Default="", if not specified
| | ... |   xid field in DHCP OFFER is same as in DHCP DISCOVER message).
| | ... |   Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Raises:*
| | ... | - DHCP REQUEST Rx timeout - if no DHCP REQUEST is received.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Check DHCP REQUEST after OFFER \| ${nodes['TG']} \
| | ... | \| eth2 \| 08:00:27:66:b8:57 \| 192.168.23.1 \
| | ... | \| 08:00:27:46:2b:4c \| 192.168.23.10 \| 255.255.255.0 \|
| | ...
| | ... | \| Run Keyword And Expect Error \| DHCP REQUEST Rx timeout \
| | ... | \| Check DHCP REQUEST after OFFER \
| | ... | \| ${nodes['TG']} \| eth2 \| 08:00:27:66:b8:57 \| 192.168.23.1 \
| | ... | \| 08:00:27:46:2b:4c \| 192.168.23.10 \| 255.255.255.0 \
| | ... | \| offer_xid=11113333 \|
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface} | ${server_mac} | ${server_ip}
| | ... | ${client_mac} | ${client_ip} | ${client_mask}
| | ... | ${hostname}=${EMPTY} | ${offer_xid}=${EMPTY}
| | ${tg_interface_name}= | Get interface name | ${tg_node} | ${tg_interface}
| | ${args}= | Catenate | --rx_if | ${tg_interface_name} | --server_mac
| | ... | ${server_mac} | --server_ip | ${server_ip} | --client_mac
| | ... | ${client_mac} | --client_ip | ${client_ip} | --client_mask
| | ... | ${client_mask}
| | ${args}= | Run Keyword If | "${hostname}" == "" | Set Variable | ${args}
| | ...      | ELSE | Catenate | ${args} | --hostname | ${hostname}
| | ${args}= | Run Keyword If | "${offer_xid}" == "" | Set Variable | ${args}
| | ...      | ELSE | Catenate | ${args} | --offer_xid | ${offer_xid}
| | Run Traffic Script On Node | dhcp/check_dhcp_request.py
| | ... | ${tg_node} | ${args}


| Send IP configuration to client via DHCP
| | [Documentation] | Run script that sends IP configuration to the DHCP client.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - tg_interface - TG interface where listen for DHCP DISCOVER,
| | ... |   send DHCP OFFER and DHCP ACK after DHCP REQUEST messages.
| | ... |   Type: string
| | ... | - server_mac - DHCP server MAC address. Type: string
| | ... | - server_ip - DHCP server IP address. Type: string
| | ... | - client_ip - IP address that is offered to client. Type: string
| | ... | - client_mask - IP netmask that is offered to client. Type: string
| | ... | - lease_time - IP lease time in seconds. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send IP configuration to client via DHCP \| ${nodes['TG']} \
| | ... | \| eth2 \| 08:00:27:66:b8:57 \| 192.168.23.1 \
| | ... | \| 192.168.23.10 \| 255.255.255.0 \| 86400 \|
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface}
| | ... | ${server_mac} | ${server_ip} | ${client_ip} | ${client_mask}
| | ... | ${lease_time}
| | ${tg_interface_name}= | Get interface name | ${tg_node} | ${tg_interface}
| | ${args}= | Catenate | --rx_if | ${tg_interface_name}
| | ... | --server_mac | ${server_mac} | --server_ip | ${server_ip}
| | ... | --client_ip | ${client_ip} | --client_mask | ${client_mask}
| | ... | --lease_time | ${lease_time}
| | Run Traffic Script On Node | dhcp/check_dhcp_request_ack.py
| | ... | ${tg_node} | ${args}

| Send DHCP Messages
| | [Documentation] | Send and receive DHCP messages between client
| | ...             | and server through DHCP proxy.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - tg_interface1 - TG interface. Type: string
| | ... | - tg_interface2 - TG interface. Type: string
| | ... | - server_ip - DHCP server IP address. Type: string
| | ... | - client_ip - Client IP address. Type: string
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
| | Run Traffic Script On Node | dhcp/send_dhcp_messages.py
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
| | ... | \| eth3 \| eth4 \| 0.0.0.0 \| 255.255.255.255 \
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface1} | ${tg_interface2}
| | ... | ${tx_src_ip} | ${tx_dst_ip} |
| | ${tg_interface_name1}= | Get interface name | ${tg_node} | ${tg_interface1}
| | ${tg_interface_name2}= | Get interface name | ${tg_node} | ${tg_interface2}
| | ${args}= | Catenate | --tx_if | ${tg_interface_name1}
| | ...                 | --rx_if | ${tg_interface_name2}
| | ...                 | --tx_src_ip | ${tx_src_ip}
| | ...                 | --tx_dst_ip | ${tx_dst_ip}
| | Run Traffic Script On Node | dhcp/send_dhcp_discover.py
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
| | ... | \| eth3 \| eth4 \| 0.0.0.0 \| 255.255.255.255 \
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface1} | ${tg_interface2}
| | ... | ${tx_src_ip} | ${tx_dst_ip} |
| | ${tg_interface_name1}= | Get interface name | ${tg_node} | ${tg_interface1}
| | ${tg_interface_name2}= | Get interface name | ${tg_node} | ${tg_interface2}
| | ${args}= | Catenate | --tx_if | ${tg_interface_name1}
| | ...                 | --rx_if | ${tg_interface_name2}
| | ...                 | --tx_src_ip | ${tx_src_ip}
| | ...                 | --tx_dst_ip | ${tx_dst_ip}
| | Run Keyword And Expect Error | DHCP DISCOVER timeout
| | ... | Run Traffic Script On Node | dhcp/send_dhcp_discover.py
| | ... | ${tg_node} | ${args}
