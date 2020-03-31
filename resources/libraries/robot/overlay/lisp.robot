# Copyright (c) 2020 Cisco and/or its affiliates.
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
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.LispSetup.LispAdjacency
| Library  | resources.libraries.python.LispSetup.LispEidTableMap
| Library  | resources.libraries.python.LispSetup.LispLocator
| Library  | resources.libraries.python.LispSetup.LispLocalEid
| Library  | resources.libraries.python.LispSetup.LispLocatorSet
| Library  | resources.libraries.python.LispSetup.LispRemoteMapping
|
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/overlay/lisp_api.robot

*** Keywords ***
| Configure topology for IPv4 LISP testing
| | [Documentation] | Setup topology for IPv4 LISP testing.
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv4 LISP testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut_if1_ip4} | ${ip4_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut_if2_ip4} | ${ip4_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${src_ip4} | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dst_ip4} | ${TG_pf2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tg_if2_ip4} | ${TG_pf2_mac}[0]

| Configure topology for IPv6 LISP testing
| | [Documentation] | Setup topology fo IPv6 LISP testing.
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv6 LISP testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut_if1_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut_if2_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${src_ip6} | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dst_ip6} | ${TG_pf2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tg_if2_ip6} | ${TG_pf2_mac}[0]

| Configure LISP topology in 3-node circular topology
| | [Documentation] | Set up Lisp static adjacency topology.
| |
| | ... | *Arguments:*
| | ... | - dut1_node - DUT1 node. Type: dictionary
| | ... | - dut1_int_name - DUT1 node interface name. Type: string
| | ... | - dut1_int_index - DUT1 node interface index. Type: integer
| | ... | - dut2_node - DUT2 node. Type: dictionary
| | ... | - dut2_int_name - DUT2 node interface name. Type: string
| | ... | - dut2_int_index - DUT2 node interface index. Type: integer
| | ... | - locator_set - Locator set values. Type: dictionary
| | ... | - dut1_eid - Dut1 node eid address. Type: dictionary
| | ... | - dut2_eid - Dut2 node eid address. Type: dictionary
| | ... | - dut1_static_adjacency - Dut1 static adjacency. Type: dictionary
| | ... | - dut2_static_adjacency - Dut2 static address. Type: dictionary
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| | ... | \| Configure LISP topology in 3-node circular topology \
| | ... | \| ${dut1_node} \| ${interface_name} \| None \
| | ... | \| ${dut2_node} \| ${interface_name} \| None \
| | ... | \| ${locator_set} \| ${dut1_eid} \| ${dut2_eid} \
| | ... | \| ${dut1_static_adjacency} \| ${dut2_static_adjacency} \|
| |
| | [Arguments] | ${dut1_node} | ${dut1_int_name} | ${dut1_int_index}
| | ... | ${dut2_node} | ${dut2_int_name} | ${dut2_int_index}
| | ... | ${locator_set} | ${dut1_eid} | ${dut2_eid}
| | ... | ${dut1_static_adjacency} | ${dut2_static_adjacency}
| | ${dut1_int_index}= | Run Keyword If | ${dut1_int_index} is None
| | ... | Get Interface Sw Index | ${dut1_node} | ${dut1_int_name}
| | ... | ELSE | Set Variable | ${dut1_int_index}
| | ${dut2_int_index}= | Run Keyword If | ${dut2_int_index} is None
| | ... | Get Interface Sw Index | ${dut2_node} | ${dut2_int_name}
| | ... | ELSE | Set Variable | ${dut2_int_index}
| | Enable Lisp | ${dut1_node}
| | Vpp Add Lisp Locator Set | ${dut1_node} | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut1_node} | ${locator_set['locator_name']}
| | ... | ${dut1_int_index} | ${locator_set['priority']}
| | ... | ${locator_set['weight']}
| | Vpp Add Lisp Local Eid | ${dut1_node} | ${dut1_eid['locator_name']}
| | ... | ${dut1_eid['vni']} | ${dut1_eid['eid']} | ${dut1_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut1_node} | ${dut1_static_adjacency['vni']}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut1_node} | ${dut1_static_adjacency['vni']}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | Enable Lisp | ${dut2_node}
| | Vpp Add Lisp Locator Set | ${dut2_node} | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut2_node} | ${locator_set['locator_name']}
| | ... | ${dut2_int_index} | ${locator_set['priority']}
| | ... | ${locator_set['weight']}
| | Vpp Add Lisp Local Eid | ${dut2_node} | ${dut2_eid['locator_name']}
| | ... | ${dut2_eid['vni']} | ${dut2_eid['eid']} | ${dut2_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut2_node} | ${dut2_static_adjacency['vni']}
| | ... | ${dut2_static_adjacency['deid']}
| | ... | ${dut2_static_adjacency['prefix']}
| | ... | ${dut2_static_adjacency['seid']}
| | ... | ${dut2_static_adjacency['prefix']}
| | ... | ${dut2_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut2_node} | ${dut2_static_adjacency['vni']}
| | ... | ${dut2_static_adjacency['deid']}
| | ... | ${dut2_static_adjacency['prefix']}
| | ... | ${dut2_static_adjacency['seid']}
| | ... | ${dut2_static_adjacency['prefix']}

| Configure LISP in 2-node circular topology
| | [Documentation] | Configure LISP topology in 2-node circular topology.
| |
| | ... | *Arguments:*
| | ... | - dut1 - DUT1 node. Type: dictionary
| | ... | - dut1_if - DUT1 node interface. Type: string
| | ... | - dut1_int_index - DUT1 node interface index. Type: integer
| | ... | - locator_set - Locator set values. Type: dictionary
| | ... | - dut1_eid - DUT1 node eid address. Type: dictionary
| | ... | - dut1_static_adjacency - DUT1 static adjacency. Type: dictionary
| | ... | - is_gpe - To enable GPE. Other than zero to enable Type: integer
| | ... | - vni_table - vni table Eid Table Mapping Type: integer
| | ... | - vrf_table - vrf table Eid Table Mapping Type: integer
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| | ... | \| Configure LISP in 2-node circular topology \
| | ... | \| ${dut1} \| ${interface_name} \
| | ... | \| None \| ${locator_set} \| ${dut1_eid} \
| | ... | \| ${dut1_static_adjacency} \|
| |
| | [Arguments]
| | ... | ${dut1} | ${dut1_if} | ${dut1_int_index}
| | ... | ${locator_set} | ${dut1_eid}
| | ... | ${dut1_static_adjacency}
| | ... | ${is_gpe}=0
| | ... | ${vni_table}=0 | ${vrf_table}=0
| |
| | # DUT1 settings:
| | ${dut1_int_index}= | Run Keyword If | ${dut1_int_index} is None
| | ... | Get Interface Sw Index | ${dut1} | ${dut1_if}
| | ... | ELSE | Set Variable | ${dut1_int_index}
| | Enable Lisp | ${dut1}
| | Run keyword if | ${is_gpe} != 0
| | ... | Enable Lisp GPE | ${dut1}
| | Vpp Add Lisp Locator Set | ${dut1} | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut1} | ${locator_set['locator_name']}
| | ... | ${dut1_int_index} | ${locator_set['priority']}
| | ... | ${locator_set['weight']}
| | Run keyword if | ${is_gpe} != 0
| | ... | Vpp Lisp Eid Table Mapping | ${dut1}
| | ... | ${vni_table}
| | ... | vrf=${vrf_table}
| | Vpp Add Lisp Local Eid | ${dut1} | ${dut1_eid['locator_name']}
| | ... | ${dut1_eid['vni']} | ${dut1_eid['eid']} | ${dut1_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut1} | ${dut1_static_adjacency['vni']}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut1} | ${dut1_static_adjacency['vni']}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}

| Configure topology for IPv6 LISPoIP4 testing
| | [Documentation] | Setup topology fo IPv6 LISPoIPV4 testing.
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv6 LISPoIP4 testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut_if1_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut_if2_ip4} | ${ip4_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${src_ip6} | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dst_ip6} | ${TG_pf2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tg_if2_ip4} | ${TG_pf2_mac}[0]

| Configure topology for IPv4 LISPoIP6 testing
| | [Documentation] | Setup topology fo IPv4 LISPoIPV6 testing.
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv4 LISPoIP6 testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut_if1_ip4} | ${ip4_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut_if2_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${src_ip4} | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dst_ip4} | ${TG_pf2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tg_if2_ip6} | ${TG_pf2_mac}[0]

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
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 10.10.10.2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut2_dut1_address}
| | ... | ${DUT2_${int}1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut1_dut2_address}
| | ... | ${DUT1_${int}2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}2}[0] | 20.20.20.2 | ${TG_pf2_mac}[0]
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_tg_address} | ${duts_prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut1_dut2_address} | ${duts_prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut2_dut1_address} | ${duts_prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${dut2_tg_address} | ${duts_prefix}

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
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${NONE}
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_ip4_static_adjacency} | ${dut2_ip4_static_adjacency}
| | Configure manual keyed connection for IPSec
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip4} | ${dut2_to_dut1_ip4}
| | Configure manual keyed connection for IPSec
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${encr_alg} | ${encr_key}
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
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_tg_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut1_dut2_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut2_dut1_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${dut2_tg_address} | ${prefix}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 2001:1::2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 2001:2::2 | ${TG_pf2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut2_dut1_address}
| | ... | ${DUT2_${int}1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut1_dut2_address}
| | ... | ${DUT1_${int}2_mac}[0]

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
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_tg_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut1_dut2_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut2_dut1_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${dut2_tg_ip4_address} | ${prefix4}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 10.10.10.2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}2}[0] | 20.20.20.2 | ${TG_pf2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut2_dut1_ip6_address}
| | ... | ${DUT2_${int}1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut1_dut2_ip6_address}
| | ... | ${DUT1_${int}2_mac}[0]

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
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_tg_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut1_dut2_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut2_dut1_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${dut2_tg_ip6_address} | ${prefix6}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 2001:1::2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}2}[0] | 2001:2::2 | ${TG_pf2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut2_dut1_ip4_address}
| | ... | ${DUT2_${int}1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut1_dut2_ip4_address}
| | ... | ${DUT1_${int}2_mac}[0]
