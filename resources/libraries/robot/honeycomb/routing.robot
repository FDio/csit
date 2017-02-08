# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.honeycomb.Routing.RoutingKeywords

*** Keywords ***
| Honeycomb configures routing table
| | [Documentation] | Uses Honeycomb API to configure a routing table.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - name - name for the new routing table. Type: string
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type:string
| | ... | - data - Settings for the new routing table. Type: dictionary
| | ... | - vrf - vrf-id the new table will belong to. Type: integer
| | ... | - special - Does the table contain special rules. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures routing table \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| ipv4 \| ${data} \|
| | [Arguments] | ${node} | ${name} | ${ip_version} | ${data} | ${vrf}=${1}
| | ... | ${special}=${EMPTY}
| | Configure routing table | ${node} | ${name} | ${ip_version} | ${data}
| | ... | ${vrf} | ${special}

| Routing data from Honeycomb should contain
| | [Documentation] | Uses Honeycomb API to retrieve operational data about\
| | ... | a routing table, and compares with the data provided.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - name - name of the routing table. Type: string
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type:string
| | ... | - expected_data - Data to compare against. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Routing data from Honeycomb should contain \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| ipv4 \| ${data} \|
| | [Arguments] | ${node} | ${name} | ${ip_version} | ${expected_data}
| | ${data}= | Get Routing Table Oper | ${node} | ${name} | ${ip_version}
| | Should Contain | ${data} | ${expected_data}

| Log routing configuration from VAT
| | [Documentation] | Uses test API to read routing configuration from VPP\
| | ... | and prints received response into robot log.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Log routing configuration from VAT \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Log routing configuration | ${node}

| Honeycomb removes routing configuration
| | [Documentation] | Uses Honeycomb API to remove Honeycomb-created\
| | ... | routing configuration from the node. Entries configured automatically\
| | ... | by VPP will not be removed.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - name - name of the routing table to remove. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes routing configuration \| ${nodes['DUT1']} \
| | ... | \| table1 \|
| | [Arguments] | ${node} | ${name}
| | Delete routing table | ${node} | ${name}

| Verify Route IPv4
| | [Documentation] | Send an ICMP packet from one TG interface and receive\
| | ... | it on the other TG interface.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: integer
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: integer
| | ... | - tx_port - Source interface (TG-if1). Type: string
| | ... | - tx_mac - MAC address of source interface (TG-if1). Type: string
| | ... | - rx_port - Destionation interface (TG-if2). Type: string
| | ... | - rx_mac - MAC address of DUT interface (DUT-if1). Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Verify Route IPv4 \| ${nodes['TG']} \
| | ... | \| 16.0.0.1 \| 32.0.0.1 \| eth1 \| 08:00:27:cc:4f:54 \
| | ... | \| eth2 \| 08:00:27:c9:6a:d5 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_port}
| | ... | ${tx_mac} | ${rx_port} | ${rx_mac}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --src_mac | ${tx_mac}
| | ...                 | --dst_mac | ${rx_mac}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --dst_ip | ${dst_ip}
| | ...                 | --tx_if | ${tx_port_name}
| | ...                 | --rx_if | ${rx_port_name}
| | Run Traffic Script On Node | send_ip_icmp.py | ${tg_node} | ${args}

| Verify Route IPv6
| | [Documentation] | Send an ICMPv6 packet from one TG interface and receive\
| | ... | it on the other TG interface.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: integer
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: integer
| | ... | - tx_port - Source interface (TG-if1). Type: string
| | ... | - tx_mac - MAC address of source interface (TG-if1). Type: string
| | ... | - rx_port - Destionation interface (TG-if2). Type: string
| | ... | - rx_mac - MAC address of DUT interface (DUT-if1). Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Verify Route IPv6 \| ${nodes['TG']} \
| | ... | \| 10::1 \| 11::1 \| eth2 \| 08:00:27:cc:4f:54 \
| | ... | \| eth4 \| 08:00:27:c9:6a:d5 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_port}
| | ... | ${tx_mac} | ${rx_port} | ${rx_mac}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --src_mac | ${tx_mac}
| | ...                 | --dst_mac | ${rx_mac}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --dst_ip | ${dst_ip}
| | ...                 | --tx_if | ${tx_port_name}
| | ...                 | --rx_if | ${rx_port_name}
| | Run Traffic Script On Node | send_ip_icmp.py | ${tg_node} | ${args}

| Verify multipath route
| | [Documentation] | Send 100 ICMP or ICMPv6 packets from one TG interface\
| | ... | and receive them on the other TG interface. Verify destination MAC\
| | ... | addresses of the packets so that exactly 50 of them use the first\
| | ... | address and the other 50 use the second address.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: integer
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: integer
| | ... | - tx_port - Source interface (TG-if1). Type: string
| | ... | - tx_src_mac - MAC address of source interface (TG-if1). Type: string
| | ... | - rx_port - Destionation interface (TG-if2). Type: string
| | ... | - tx_dst_mac - MAC address of DUT ingress interface (DUT-if1).\
| | ... | Type: string
| | ... | - rx_src_mac - MAC address of DUT egress interface (DUT-if2).\
| | ... | Type: string
| | ... | - rx_dst_mac1 - MAC address of first next-hop option. Type: string
| | ... | - rx_dst_mac2 - MAC address of second next-hop option. Type: string
| | ... |
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ___ \| ${nodes['TG']} \
| | ... | \| 16.0.0.1 \| 32.0.0.1 \| eth2 \| 08:00:27:cc:4f:54 \
| | ... | \| eth4 \| 08:00:27:c9:6a:d5 \| ${1} \| ${1} \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_port}
| | ... | ${tx_src_mac} | ${rx_port} | ${tx_dst_mac} | ${rx_src_mac}
| | ... | ${rx_dst_mac1} | ${rx_dst_mac2}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_if1_mac | ${tx_src_mac}
| | ...                 | --dut_if1_mac | ${tx_dst_mac}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --dst_ip | ${dst_ip}
| | ...                 | --tx_if | ${tx_port_name}
| | ...                 | --rx_if | ${rx_port_name}
| | ...                 | --dut_if2_mac | ${rx_src_mac}
| | ...                 | --path_1_mac | ${rx_dst_mac_1}
| | ...                 | --path_2_mac | ${rx_dst_mac_2}
| | Run Traffic Script On Node | send_icmp_check_multipath.py | ${tg_node}
| | ... | ${args}