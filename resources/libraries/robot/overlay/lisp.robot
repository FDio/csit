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
| Library | String
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.IPv6Util
| ...
| Documentation | LISP keywords.

| Library | resources.libraries.python.topology.Topology
| Resource | resources/libraries/robot/overlay/lisp_api.robot
| Library  | resources.libraries.python.LispSetup.LispLocatorSet
| Library  | resources.libraries.python.LispSetup.LispLocator
| Library  | resources.libraries.python.LispSetup.LispLocalEid
| Library  | resources.libraries.python.LispSetup.LispAdjacency
| Library  | resources.libraries.python.LispSetup.LispRemoteMapping
| Library  | resources.libraries.python.LispSetup.LispEidTableMap

*** Keywords ***
| Configure path for LISP test
| | [Documentation] | Setup path for LISP testing TG<-->DUT1.
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - dut_if2 - DUT1<-->TG(if2) interface. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Configure path for LISP test \|
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Set Test Variable | ${dut1_if2}

| Configure topology for IPv4 LISP testing
| | [Documentation] | Setup topology for IPv4 LISP testing.
| | ...
| | ... | *Example:*
| | ... | \| Configure topology for IPv4 LISP testing \|
| | ...
| | Configure path for LISP test
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut_if1_ip4} | ${ip4_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut_if2_ip4} | ${ip4_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${src_ip4} | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dst_ip4} | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${tg2_ip4} | ${tg_if2_mac}

| Configure topology for IPv6 LISP testing
| | [Documentation] | Setup topology fo IPv6 LISP testing.
| | ...
| | ... | *Example:*
| | ... | \| Configure topology for IPv6 LISP testing \|
| | ...
| | Configure path for LISP test
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut_if1_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut_if2_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${src_ip6} | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dst_ip6} | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${tg2_ip6} | ${tg_if2_mac}

| Configure LISP in 2-node circular topology
| | [Documentation] | Configure LISP topology in 2-node circular topology.
| | ...
| | ... | *Arguments:*
| | ... | - dut1 - DUT1 node. Type: dictionary
| | ... | - dut1_if - DUT1 node interface. Type: string
| | ... | - dut1_int_index - DUT1 node interface index. Type: integer
| | ... | - locator_set - Locator set values. Type: dictionary
| | ... | - dut1_eid - DUT1 node eid address. Type: dictionary
| | ... | - dut1_static_adjacency - DUT1 static adjacency. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Configure LISP in 2-node circular topology \| ${dut1} \| ${interface_name} \
| | ... | \| None \| ${locator_set} \| ${dut1_eid} \
| | ... | \| ${dut1_static_adjacency} \|
| | ...
| | [Arguments]
| | ... | ${dut1} | ${dut1_if} | ${dut1_int_index}
| | ... | ${locator_set} | ${dut1_eid}
| | ... | ${dut1_static_adjacency}
| | ... | ${vni_table}=0 | ${vrf_table}=0
| | ...
# DUT1 settings:
| | ${dut1_int_index}= | Run Keyword If | ${dut1_int_index} is None
| | | ... | Get Interface Sw Index | ${dut1} | ${dut1_if}
| | | ... | ELSE | Set Variable | ${dut1_int_index}
| | Enable Lisp | ${dut1}
| | Vpp Add Lisp Locator Set | ${dut1} | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut1} | ${locator_set['locator_name'] }
| | ... | ${dut1_int_index} | ${locator_set['priority']}
| | ... | ${locator_set['weight']}
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

| Send packet and verify LISP encap
| | [Documentation] | Send ICMP packet to DUT out one interface and receive\
| | ... | a LISP encapsulated packet on the other interface.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ... | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_port - Interface of TG-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT1-if2. Type: string
| | ... | - rx_dst_mac - MAC address of TG-if2. Type: string
| | ... | - src_rloc - configured RLOC source address. Type: string
| | ... | - dst_rloc - configured RLOC destination address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send packet and verify LISP encap \| ${nodes['TG']} \| 10.0.0.1 \
| | ... | \| 32.0.0.1 \| eth2 \| 08:00:27:ee:fd:b3 \| 08:00:27:a2:52:5b \
| | ... | \| eth3 \| 08:00:27:4d:ca:7a \| 08:00:27:7d:fd:10 \| 10.0.1.1 \
| | ... | \| 10.0.1.2 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port}
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac}
| | ... | ${rx_dst_mac} | ${src_rloc} | ${dst_rloc}
| | ...
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip}
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | ... | --src_rloc | ${src_rloc} | --dst_rloc | ${dst_rloc}
| | Run Traffic Script On Node | lisp/lisp_check.py | ${tg_node}
| | ... | ${args}

| Configure topology for IPv6 LISPoIP4 testing
| | [Documentation] | Setup topology fo IPv6 LISPoIPV4 testing.
| | ...
| | ... | *Example:*
| | ... | \| Configure topology for IPv6 LISPoIP4 testing \|
| | ...
| | Configure path for IPv6 LISPoIP4 test
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut_if1_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut_if2_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${src_ip6} | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dst_ip6} | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${tg2_ip6} | ${tg_if2_mac}


