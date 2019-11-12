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
| Library  | resources.libraries.python.LispSetup.LispAdjacency
| Library  | resources.libraries.python.LispSetup.LispEidTableMap
| Library  | resources.libraries.python.LispSetup.LispLocalEid
| Library  | resources.libraries.python.LispSetup.LispLocator
| Library  | resources.libraries.python.LispSetup.LispLocatorSet
| Library  | resources.libraries.python.LispSetup.LispRemoteMapping
| Resource | resources/libraries/robot/shared/default.robot

*** Keywords ***
| Configure topology for IPv4 LISP testing
| | [Documentation] | Setup topology for IPv4 LISP testing.
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv4 LISP testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut_if1_ip4} | ${ip4_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut_if2_ip4} | ${ip4_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${src_ip4} | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dst_ip4} | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${tg_if2_ip4} | ${tg_if2_mac}

| Configure topology for IPv6 LISP testing
| | [Documentation] | Setup topology fo IPv6 LISP testing.
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv6 LISP testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut_if1_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut_if2_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${src_ip6} | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dst_ip6} | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${tg_if2_ip6} | ${tg_if2_mac}

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
| | ... | ${dut1} | ${dut1_if1} | ${dut_if1_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut_if2_ip4} | ${ip4_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${src_ip6} | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dst_ip6} | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${tg_if2_ip4} | ${tg_if2_mac}

| Configure topology for IPv4 LISPoIP6 testing
| | [Documentation] | Setup topology fo IPv4 LISPoIPV6 testing.
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv4 LISPoIP6 testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut_if1_ip4} | ${ip4_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut_if2_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${src_ip4} | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dst_ip4} | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${tg_if2_ip6} | ${tg_if2_mac}
