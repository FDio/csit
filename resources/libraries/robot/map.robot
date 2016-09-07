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
| Variables | resources/libraries/python/topology.py
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.TGSetup
| Library | resources.libraries.python.Map
| Documentation | Keywords for MAP feature in VPP.

*** Keywords ***
| Send IPv4 UDP and check headers for lightweight 4over6
| | [Documentation]
| | ... | Send empty UDP to given IPv4 dst and UDP port and check received \
| | ... | packets headers (Ethernet, IPv6, IPv4, UDP).
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: string
| | ... | - tx_if - Interface from where to send ICPMv4 packet. Type: string
| | ... | - rx_if - Interface where to receive IPinIP packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of IPv4 packet. Type: string
| | ... | - tx_dst_ipv4 - Destination IPv4 address. Type: string
| | ... | - tx_src_ipv4 - Source IPv4 address. Type: string
| | ... | - tx_dst_udp_port - Destination UDP port. Type: integer
| | ... | - rx_dst_mac - Expected destination MAC address. Type: string
| | ... | - rx_src_mac - Expected source MAC address. Type: string
| | ... | - dst_ipv6 - Expected destination IPv6 address. Type: string
| | ... | - src_ipv6 - Expected source IPv6 address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send IPv4 UDP and check headers for lightweight 4over6 \
| | ... | \| ${tg_node} \| eth3 \| eth2 \| 08:00:27:66:b8:57 \| 20.0.0.1 \
| | ... | \| 20.0.0.2 \| 1232 \| 08:00:27:46:2b:4c \| 08:00:27:f3:be:f0 \
| | ... | \| 2001:1::2 \| 2001:1::1 \|
| | ...
| | [Arguments]
| | ... | ${tg_node} | ${tx_if} | ${rx_if} | ${tx_dst_mac} | ${tx_dst_ipv4}
| | ... | ${tx_src_ipv4} | ${tx_dst_udp_port} | ${rx_dst_mac} | ${rx_src_mac}
| | ... | ${dst_ipv6} | ${src_ipv6}
| | ...
| | ${tx_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate
| | ... | --tx_if | ${tx_name} | --rx_if | ${rx_name}
| | ... | --tx_dst_mac | ${tx_dst_mac} | --tx_src_ipv4 | ${tx_src_ipv4}
| | ... | --tx_dst_ipv4 | ${tx_dst_ipv4}
| | ... | --tx_dst_udp_port | ${tx_dst_udp_port}
| | ... | --rx_dst_mac | ${rx_dst_mac} | --rx_src_mac | ${rx_src_mac}
| | ... | --src_ipv6 | ${src_ipv6} | --dst_ipv6 | ${dst_ipv6}
| | ...
| | Run Traffic Script On Node
| | ... | send_ipv4_udp_check_lw_4o6.py | ${tg_node} | ${args}

| Send IPv4 ICMP and check headers for lightweight 4over6
| | [Documentation]
| | ... | Send ICMP request with ID to given IPv4 destination and \
| | ... | check received packets headers (Ethernet, IPv6, IPv4, ICMP).
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: string
| | ... | - tx_if - Interface from where to send ICPMv4 packet. Type: string
| | ... | - rx_if - Interface where to receive IPinIP packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of IPv4 packet. Type: string
| | ... | - tx_dst_ipv4 - Destination IPv4 address. Type: string
| | ... | - tx_src_ipv4 - Source IPv4 address. Type: string
| | ... | - tx_icmp_id - ICMP ID. Type: integer
| | ... | - rx_dst_mac - Expected destination MAC address. Type: string
| | ... | - rx_src_mac - Expected source MAC address. Type: string
| | ... | - dst_ipv6 - Expected destination IPv6 address. Type: string
| | ... | - src_ipv6 - Expected source IPv6 address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send IPv4 ICMP and check headers for lightweight 4over6 \
| | ... | \| ${tg_node} \| eth3 \| eth2 \| 08:00:27:66:b8:57 \| 20.0.0.1 \
| | ... | \| 20.0.0.2 \| 1232 \| 08:00:27:46:2b:4c \| 08:00:27:f3:be:f0 \
| | ... | \| 2001:1::2 \| 2001:1::1 \|
| | ...
| | [Arguments]
| | ... | ${tg_node} | ${tx_if} | ${rx_if} | ${tx_dst_mac} | ${tx_dst_ipv4}
| | ... | ${tx_src_ipv4} | ${tx_icmp_id} | ${rx_dst_mac} | ${rx_src_mac}
| | ... | ${dst_ipv6} | ${src_ipv6}
| | ...
| | ${tx_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate
| | ... | --tx_if | ${tx_name} | --rx_if | ${rx_name}
| | ... | --tx_dst_mac | ${tx_dst_mac} | --tx_src_ipv4 | ${tx_src_ipv4}
| | ... | --tx_dst_ipv4 | ${tx_dst_ipv4} | --tx_icmp_id | ${tx_icmp_id}
| | ... | --rx_dst_mac | ${rx_dst_mac} | --rx_src_mac | ${rx_src_mac}
| | ... | --src_ipv6 | ${src_ipv6} | --dst_ipv6 | ${dst_ipv6}
| | ...
| | Run Traffic Script On Node
| | ... | send_ipv4_icmp_check_lw_4o6.py | ${tg_node} | ${args}

| Send IPv4 UDP in IPv6 and check headers for lightweight 4over6
| | [Documentation]
| | ... | Send empty UDP in IPv4 in IPv6 and check if IPv4 packet is correctly \
| | ... | decapsulated from IPv6.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: string
| | ... | - tx_if - Interface from where to send ICPMv4 packet. Type: string
| | ... | - rx_if - Interface where to receive IPinIP packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of IPv4 packet. Type: string
| | ... | - tx_src_mac - Source MAC address of IPv4 packet. Type: string
| | ... | - tx_dst_ipv6 - Destination IPv6 address. Type: string
| | ... | - tx_src_ipv6 - Source IPv6 address. Type: string
| | ... | - tx_dst_ipv4 - Destination IPv4 address. Type: string
| | ... | - tx_src_ipv4 - Source IPv4 address. Type: string
| | ... | - tx_src_udp_port - Source UDP port. Type: integer
| | ... | - rx_dst_mac - Expected destination MAC address. Type: string
| | ... | - rx_src_mac - Expected source MAC address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send IPv4 UDP in IPv6 and check headers for lightweight 4over6 \
| | ... | \| ${tg_node} \| eth3 \| eth2 \
| | ... | \| 08:00:27:66:b8:57 \| 08:00:27:33:54:21 \
| | ... | \| 2001:1::2 \| 2001:1::1 \| 20.0.0.1 \| 20.0.0.2 \
| | ... | \| 1232 \| 08:00:27:46:2b:4c \| 08:00:27:f3:be:f0 \|
| | ...
| | [Arguments]
| | ... | ${tg_node} | ${tx_if} | ${rx_if} | ${tx_dst_mac} | ${tx_src_mac}
| | ... | ${tx_dst_ipv6} | ${tx_src_ipv6} | ${tx_dst_ipv4} | ${tx_src_ipv4}
| | ... | ${tx_src_udp_port} | ${rx_dst_mac} | ${rx_src_mac}
| | ...
| | ${tx_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate
| | ... | --tx_if | ${tx_name} | --rx_if | ${rx_name}
| | ... | --tx_dst_mac | ${tx_dst_mac} | --tx_src_mac | ${tx_src_mac}
| | ... | --tx_dst_ipv6 | ${tx_dst_ipv6} | --tx_src_ipv6 | ${tx_src_ipv6}
| | ... | --tx_dst_ipv4 | ${tx_dst_ipv4} | --tx_src_ipv4 | ${tx_src_ipv4}
| | ... | --tx_src_udp_port | ${tx_src_udp_port}
| | ... | --rx_dst_mac | ${rx_dst_mac} | --rx_src_mac | ${rx_src_mac}
| | ...
| | Run Traffic Script On Node
| | ... | send_lw_4o6_check_ipv4_udp.py | ${tg_node} | ${args}

| Send IPv4 UDP in IPv6 and check headers for lightweight hairpinning
| | [Documentation]
| | ... | Send empty UDP in IPv4 in IPv6 and check if IPv4 packet is correctly \
| | ... | decapsulated and re-encapsulated to another lwB4.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: string
| | ... | - tx_if - Interface from where to send ICPMv4 packet. Type: string
| | ... | - rx_if - Interface where to receive IPinIP packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of send IPv6 packet. \
| | ... |   Type: string
| | ... | - tx_dst_ipv6 - Destination IPv6 address (lwAFTR). Type: string
| | ... | - tx_src_ipv6 - Source IPv6 address (lwB4_1). Type: string
| | ... | - tx_dst_ipv4 - Destination IPv4 address. Type: string
| | ... | - tx_src_ipv4 - Source IPv4 address. Type: string
| | ... | - tx_dst_udp_port - Destination UDP port (PSID_2 related). \
| | ... |   Type: integer
| | ... | - tx_src_udp_port - Source UDP port (PSID_1 related). Type: integer
| | ... | - rx_dst_mac - Expected destination MAC address. Type: string
| | ... | - rx_src_mac - Expected source MAC address. Type: string
| | ... | - rx_dst_ipv6 - Expected destination IPv6 address (lwB4_2). \
| | ... |   Type: string
| | ... | - rx_src_ipv6 - Expected source IPv6 address (lwAFTR). Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send IPv4 UDP in IPv6 and check headers for lightweight hairpinning \
| | ... | \| ${tg_node} \| port3 \| port3 \| 08:00:27:f3:be:f0 \| 2001:1::1 \
| | ... | \| 2001:1::2 \| 20.0.0.1 \| 20.0.0.1 \| ${6232} \| ${1232} \
| | ... | \| 08:00:27:46:2b:4c \| 08:00:27:f3:be:f0 \| 2001:1::3 \| 2001:1::1 \|
| | ...
| | [Arguments]
| | ... | ${tg_node} | ${tx_if} | ${rx_if}
| | ... | ${tx_dst_mac}
| | ... | ${tx_dst_ipv6} | ${tx_src_ipv6}
| | ... | ${tx_dst_ipv4} | ${tx_src_ipv4}
| | ... | ${tx_dst_udp_port} | ${tx_src_udp_port}
| | ... | ${rx_dst_mac} | ${rx_src_mac}
| | ... | ${rx_dst_ipv6} | ${rx_src_ipv6}
| | ...
| | ${tx_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate
| | ... | --tx_if | ${tx_name} | --rx_if | ${rx_name}
| | ... | --tx_dst_mac | ${tx_dst_mac}
| | ... | --tx_dst_ipv6 | ${tx_dst_ipv6} | --tx_src_ipv6 | ${tx_src_ipv6}
| | ... | --tx_dst_ipv4 | ${tx_dst_ipv4} | --tx_src_ipv4 | ${tx_src_ipv4}
| | ... | --tx_dst_udp_port | ${tx_dst_udp_port}
| | ... | --tx_src_udp_port | ${tx_src_udp_port}
| | ... | --rx_dst_mac | ${rx_dst_mac} | --rx_src_mac | ${rx_src_mac}
| | ... | --rx_dst_ipv6 | ${rx_dst_ipv6} | --rx_src_ipv6 | ${rx_src_ipv6}
| | ...
| | Run Traffic Script On Node
| | ... | send_lw_4o6_check_hairpinning_udp.py | ${tg_node} | ${args}

| Send IPv4 UDP and check IPv6 headers for MAP-T
| | [Documentation]
| | ... | Send a UDP in IPv4 and check if IPv4 source and destination \
| | ... | addresses are correctly translated into IPv6 addresses.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: string
| | ... | - tx_if - Interface from where to send IPv4 UDP packet. Type: string
| | ... | - rx_if - Interface where to receive IPv6 UDP packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of IPv4 packet. Type: string
| | ... | - tx_dst_ipv4 - Destination IPv4 address. Type: string
| | ... | - tx_src_ipv4 - Source IPv4 address. Type: string
| | ... | - tx_dst_udp_port - Destination UDP port. Type: integer
| | ... | - rx_dst_mac - Expected destination MAC address. Type: string
| | ... | - rx_src_mac - Expected source MAC address. Type: string
| | ... | - dst_ipv6 - Expected destination IPv6 address. Type: string
| | ... | - src_ipv6 - Expected source IPv6 address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send IPv4 UDP and check IPv6 headers for MAP-T \
| | ... | \| ${tg_node} \| port3 \| port3 \| 08:00:27:66:b8:57 \
| | ... | \| 20.169.201.219 \| 100.0.0.1 \| ${1232} \| 08:00:27:46:2b:4c \
| | ... | \| 08:00:27:f3:be:f0 \| 2001:db8::14a9:c9db:0 \
| | ... | \| 2001:db8:ffff::6400:1 \|
| | ...
| | [Arguments]
| | ... | ${tg_node} | ${tx_if} | ${rx_if}
| | ... | ${tx_dst_mac} | ${tx_dst_ipv4} | ${tx_src_ipv4} | ${tx_dst_udp_port}
| | ... | ${rx_dst_mac} | ${rx_src_mac} | ${dst_ipv6} | ${src_ipv6}
| | ...
| | ${tx_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate
| | ... | --tx_if | ${tx_name} | --rx_if | ${rx_name}
| | ... | --tx_dst_mac | ${tx_dst_mac}
| | ... | --tx_src_ipv4 | ${tx_src_ipv4} | --tx_dst_ipv4 | ${tx_dst_ipv4}
| | ... | --tx_dst_udp_port | ${tx_dst_udp_port}
| | ... | --rx_dst_mac | ${rx_dst_mac} | --rx_src_mac | ${rx_src_mac}
| | ... | --rx_src_ipv6 | ${src_ipv6} | --rx_dst_ipv6 | ${dst_ipv6}
| | ...
| | Run Traffic Script On Node
| | ... | send_ipv4_udp_check_map_t.py | ${tg_node} | ${args}

| Send IPv6 UDP and check IPv4 headers for MAP-T
| | [Documentation]
| | ... | Send a UDP in IPv6 and check if IPv6 source and destination \
| | ... | addresses are correctly translated into IPv4 addresses.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: string
| | ... | - tx_if - Interface from where to send IPv4 UDP packet. Type: string
| | ... | - rx_if - Interface where to receive IPv6 UDP packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of IPv4 packet. Type: string
| | ... | - tx_src_mac - Source MAC address of IPv4 packet. Type: string
| | ... | - tx_dst_ipv6 - Destination IPv6 address. Type: string
| | ... | - tx_src_ipv6 - Source IPv6 address. Type: string
| | ... | - tx_src_udp_port - Source UDP port. Type: integer
| | ... | - rx_dst_mac - Expected destination MAC address. Type: string
| | ... | - rx_src_mac - Expected source MAC address. Type: string
| | ... | - dst_ipv4 - Expected destination IPv4 address. Type: string
| | ... | - src_ipv4 - Expected source IPv4 address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send IPv6 UDP and check IPv4 headers for MAP-T \
| | ... | \| port3 \| port4 \| 08:00:27:f3:be:f0 \| 2001:db8:ffff::6400:1 \
| | ... | \| 2001:db8::14a9:c9db:0 \| ${1232} \| 08:00:27:58:71:eb \
| | ... | \| 08:00:27:66:b8:57 \| 100.0.0.1 \| 20.169.201.219 \|
| | ...
| | [Arguments]
| | ... | ${tg_node} | ${tx_if} | ${rx_if} | ${tx_dst_mac} | ${tx_src_mac}
| | ... | ${tx_dst_ipv6} | ${tx_src_ipv6} | ${tx_src_udp_port}
| | ... | ${rx_dst_mac} | ${rx_src_mac} | ${dst_ipv4} | ${src_ipv4}
| | ...
| | ${tx_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate
| | ... | --tx_if | ${tx_name} | --rx_if | ${rx_name}
| | ... | --tx_dst_mac | ${tx_dst_mac} | --tx_src_mac | ${tx_src_mac}
| | ... | --tx_src_ipv6 | ${tx_src_ipv6} | --tx_dst_ipv6 | ${tx_dst_ipv6}
| | ... | --tx_src_udp_port | ${tx_src_udp_port}
| | ... | --rx_dst_mac | ${rx_dst_mac} | --rx_src_mac | ${rx_src_mac}
| | ... | --rx_src_ipv4 | ${src_ipv4} | --rx_dst_ipv4 | ${dst_ipv4}
| | ...
| | Run Traffic Script On Node
| | ... | send_ipv6_udp_check_map_t.py | ${tg_node} | ${args}
