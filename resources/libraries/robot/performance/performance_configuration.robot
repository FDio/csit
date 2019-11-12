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
| Documentation | Performance suite keywords - configuration

*** Keywords ***
| Initialize LISP IPv4 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 addresses on all DUT nodes and TG \
| | ... | Don`t set route.
| |
| | ... | *Arguments:*
| | ... | - dut1_dut2_address - Ip address from DUT1 to DUT2. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_address - Ip address from DUT2 to DUT1. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - duts_prefix - ip prefix. Type: int
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| | ... | \| Initialize LISP IPv4 forwarding in 3-node circular topology \
| | ... | \| ${dut1_dut2_address} \| ${dut1_tg_address} \
| | ... | \| ${dut2_dut1_address} \| ${dut2_tg_address} \| ${duts_prefix} \|
| |
| | [Arguments] | ${dut1_dut2_address} | ${dut1_tg_address}
| | ... | ${dut2_dut1_address} | ${dut2_tg_address} | ${duts_prefix}
| |
| | Set interfaces in path up
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_address} | ${dut1_if2_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 20.20.20.2 | ${tg_if2_mac}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1}
| | ... | ${dut1_tg_address} | ${duts_prefix}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if2}
| | ... | ${dut1_dut2_address} | ${duts_prefix}
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if1}
| | ... | ${dut2_dut1_address} | ${duts_prefix}
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if2}
| | ... | ${dut2_tg_address} | ${duts_prefix}

| Initialize LISP GPE IPv4 over IPsec in 3-node circular topology
| | [Documentation] | Setup Lisp GPE IPv4 forwarding over IPsec.
| |
| | ... | *Arguments:*
| | ... | - encr_alg - Encryption algorithm. Type: string
| | ... | - auth_alg - Authentication algorithm. Type: string
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| | ... | \| Initialize LISP GPE IPv4 over IPsec in 3-node circular topology\
| | ... | \| ${encr_alg} \| ${auth_alg}
| |
| | [Arguments] | ${encr_alg} | ${auth_alg}
| |
| | Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | Initialize LISP IPv4 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ... | ${dut2_to_tg_ip4} | ${prefix4}
| | Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_ip4_static_adjacency} | ${dut2_ip4_static_adjacency}
| | Configure manual keyed connection for IPSec
| | ... | ${dut1} | ${dut1_if2} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip4} | ${dut2_to_dut1_ip4}
| | Configure manual keyed connection for IPSec
| | ... | ${dut2} | ${dut2_if1} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi}
| | ... | ${dut2_to_dut1_ip4} | ${dut1_to_dut2_ip4}

| Initialize LISP IPv6 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| |
| | ... | *Arguments:*
| | ... | - dut1_dut2_address - Ip address from DUT1 to DUT2. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_address - Ip address from DUT2 to DUT1. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - duts_prefix - ip prefix. Type: int
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| | ... | \| Initialize LISP IPv6 forwarding in 3-node circular topology \
| | ... | \| ${dut1_dut2_address} \| ${dut1_tg_address} \
| | ... | \| ${dut2_dut1_address} \| ${dut2_tg_address} \| ${duts_prefix} \|
| |
| | [Arguments] | ${dut1_dut2_address} | ${dut1_tg_address}
| | ... | ${dut2_dut1_address} | ${dut2_tg_address} | ${prefix}
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_tg_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_tg_address} | ${prefix}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_address} | ${dut1_if2_mac}

| Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 over IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| |
| | ... | *Arguments:*
| | ... | - dut1_dut2_ip6_address - IPv6 address from DUT1 to DUT2.
| | ... | Type: string
| | ... | - dut1_tg_ip4_address - IPv4 address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_ip6_address - IPv6 address from DUT2 to DUT1.
| | ... | Type: string
| | ... | - dut1_tg_ip4_address - IPv4 address from DUT1 to tg. Type: string
| | ... | - prefix4 - IPv4 prefix. Type: int
| | ... | - prefix6 - IPv6 prefix. Type: int
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| | ... | \| Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular \
| | ... | topology \| ${dut1_dut2_ip6_address} \| ${dut1_tg_ip4_address} \
| | ... | \| ${dut2_dut1_ip6_address} \| ${dut2_tg_ip4_address} \
| | ... | \| ${prefix4} \| ${prefix6} \|
| |
| | [Arguments] | ${dut1_dut2_ip6_address} | ${dut1_tg_ip4_address}
| | ... | ${dut2_dut1_ip6_address} | ${dut2_tg_ip4_address}
| | ... | ${prefix4} | ${prefix6}
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1}
| | ... | ${dut1_tg_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if2}
| | ... | ${dut2_tg_ip4_address} | ${prefix4}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 20.20.20.2 | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip6_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip6_address} | ${dut1_if2_mac}

| Initialize LISP IPv6 over IPv4 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 over IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| |
| | ... | *Arguments:*
| | ... | - dut1_dut2_ip4_address - IPv4 address from DUT1 to DUT2.
| | ... | Type: string
| | ... | - dut1_tg_ip6_address - IPv6 address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_ip4_address - IPv4 address from DUT2 to DUT1.
| | ... | Type: string
| | ... | - dut1_tg_ip6_address - IPv6 address from DUT1 to tg. Type: string
| | ... | - prefix4 - IPv4 prefix. Type: int
| | ... | - prefix6 - IPv6 prefix. Type: int
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| | ... | \| Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular \
| | ... | topology \| ${dut1_dut2_ip4_address} \| ${dut1_tg_ip6_address} \
| | ... | \| ${dut2_dut1_ip4_address} \| ${dut2_tg_ip6_address} \
| | ... | \| ${prefix6} \| ${prefix4} \|
| |
| | [Arguments] | ${dut1_dut2_ip4_address} | ${dut1_tg_ip6_address}
| | ... | ${dut2_dut1_ip4_address} | ${dut2_tg_ip6_address}
| | ... | ${prefix6} | ${prefix4}
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_tg_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_tg_ip6_address} | ${prefix6}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip4_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip4_address} | ${dut1_if2_mac}
