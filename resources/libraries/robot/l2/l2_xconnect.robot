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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil

*** Keywords ***
| Configure L2XC
| | [Documentation] | Setup Bidirectional Cross Connect on DUTs
| | [Arguments] | ${node} | ${if1} | ${if2} |
| | Set Interface State | ${node} | ${if1} | up
| | Set Interface State | ${node} | ${if2} | up
| | Vpp Setup Bidirectional Cross Connect | ${node} | ${if1} | ${if2}

| Initialize L2 cross connect on node
| | [Documentation]
| | ... | Setup L2 cross connect topology by connecting RX/TX of two interfaces
| | ... | on each DUT. Interfaces are brought up.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of interfaces pairs to connect. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize L2 cross connect on node \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${count}=${1}
| |
| | FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | VPP Setup Bidirectional Cross Connect | ${nodes['${dut}']}
| | | ... | ${${dut_str}_${prev_layer}_${id}_1}
| | | ... | ${${dut_str}_${prev_layer}_${id}_2}
| | END

| Initialize L2 cross connect
| | [Documentation]
| | ... | Setup L2 cross connect topology by connecting RX/TX of two interfaces
| | ... | on each DUT. Interfaces are brought up.
| |
| | ... | *Arguments:*
| | ... | - count - Number of interfaces pairs to connect. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize L2 cross connect \| 1 \|
| |
| | [Arguments] | ${count}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize L2 cross connect on node | ${dut} | count=${count}
| | END

| Initialize L2 xconnect in 2-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology by cross connecting two interfaces on
| | ... | each DUT. Interfaces are brought up.
| |
| | Set interfaces in path up
| | VPP Setup Bidirectional Cross Connect | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Initialize L2 xconnect in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology by cross connecting two interfaces on
| | ... | each DUT. Interfaces are brought up.
| | ... |
| | Set interfaces in path up
| | VPP Setup Bidirectional Cross Connect | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | VPP Setup Bidirectional Cross Connect | ${dut2} | ${dut2_if1} | ${dut2_if2}

| Initialize L2 xconnect with VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology with VXLANoIPv4 by cross connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | between DUTs. VXLAN sub-interfaces has same IPv4 address as
| | ... | interfaces.
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if2} | 172.16.0.1 | 24
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if1} | 172.16.0.2 | 24
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 172.16.0.2 | ${dut2_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if1} | 172.16.0.1 | ${dut1_if2_mac}
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${dut2s_vxlan}

| Initialize L2 xconnect with Vhost-User on node
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on
| | ... | defined VPP node. Add each Vhost-User interface into L2 cross-connect
| | ... | with with physical inteface or Vhost-User interface of another VM.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - nf_nodes - VM count. Type: integer
| |
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /tmp/sock-\${VM_ID}-1
| | ... | - /tmp/sock-\${VM_ID}-2
| |
| | ... | *Example:*
| |
| | ... | \| Initialize L2 xconnect with Vhost-User on node \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${nf_nodes}=${1}
| |
| | FOR | ${number} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${sock1}= | Set Variable | /var/run/vpp/sock-${number}-1
| | | ${sock2}= | Set Variable | /var/run/vpp/sock-${number}-2
| | | ${prev_index}= | Evaluate | ${number}-1
| | | Configure vhost interfaces | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${dut}-vhost-${number}-if1
| | | ... | ${dut}-vhost-${number}-if2
| | | ${dut_xconnect_if1}= | Set Variable If | ${number}==1 | ${${dut}_if1}
| | | ... | ${${dut}-vhost-${prev_index}-if2}
| | | Configure L2XC | ${nodes['${dut}']} | ${dut_xconnect_if1}
| | | ... | ${${dut}-vhost-${number}-if1}
| | | Run Keyword If | ${number}==${nf_nodes} | Configure L2XC
| | | ... | ${nodes['${dut}']} | ${${dut}-vhost-${number}-if2} | ${${dut}_if2}
| | END

| Initialize L2 xconnect with Vhost-User
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on
| | ... | all VPP nodes. Add each Vhost-User interface into L2 cross-connect
| | ... | with with physical inteface or Vhost-User interface of another VM.
| |
| | ... | *Arguments:*
| | ... | - nf_nodes - VM count. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize L2 xconnect with Vhost-User \| 1 \|
| |
| | [Arguments] | ${nf_nodes}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize L2 xconnect with Vhost-User on node | ${dut}
| | | ... | nf_nodes=${nf_nodes}
| | END

| Initialize L2 xconnect with Vhost-User and VLAN in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Cross
| | ... | connect each Vhost interface with one physical interface.
| | ... | Setup VLAN between DUTs. All interfaces are brought up.
| |
| | ... | *Arguments:*
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| L2 xconnect with Vhost-User and VLAN initialized in a 3-node\
| | ... | circular topology \| 10 \| pop-1 \|
| |
| | [Arguments] | ${subid} | ${tag_rewrite}
| |
| | Set interfaces in path up
| | Initialize VLAN dot1q sub-interfaces in circular topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | Configure vhost interfaces
| | ... | ${dut1} | /var/run/vpp/sock-1-1 | /var/run/vpp/sock-1-2
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${vhost_if1}
| | Configure L2XC | ${dut1} | ${subif_index_1} | ${vhost_if2}
| | Configure vhost interfaces
| | ... | ${dut2} | /var/run/vpp/sock-1-1 | /var/run/vpp/sock-1-2
| | Configure L2XC | ${dut2} | ${subif_index_2} | ${vhost_if1}
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${vhost_if2}

| Initialize L2 xconnect with Vhost-User and VLAN with VPP link bonding in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Create one
| | ... | link bonding (BondEthernet) interface on both VPP nodes. Enslave one
| | ... | physical interface towards next DUT by BondEthernet interface. Setup
| | ... | VLAN on BondEthernet interfaces between DUTs. Cross connect one Vhost
| | ... | interface with physical interface towards TG and other Vhost interface
| | ... | with VLAN sub-interface. All interfaces are brought up.
| |
| | ... | *Arguments:*
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ... | - bond_mode - Link bonding mode. Type: string
| | ... | - lb_mode - Load balance mode. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize L2 xconnect with Vhost-User and VLAN with VPP link\
| | ... | bonding in 3-node circular topology \| 10 \| pop-1 \| xor \| l34 \|
| |
| | [Arguments] | ${subid} | ${tag_rewrite} | ${bond_mode} | ${lb_mode}
| |
| | Set interfaces in path up
| | ${dut1_eth_bond_if1}= | VPP Create Bond Interface | ${dut1} | ${bond_mode}
| | ... | ${lb_mode}
| | Set Interface State | ${dut1} | ${dut1_eth_bond_if1} | up
| | VPP Set interface MTU | ${dut1} | ${dut1_eth_bond_if1}
| | ${if2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut1_if2}
| | Run Keyword If | '${if2_status}' == 'PASS'
| | ... | VPP Enslave Physical Interface | ${dut1} | ${dut1_if2}
| | ... | ${dut1_eth_bond_if1}
| | ... | ELSE
| | ... | VPP Enslave Physical Interface | ${dut1} | ${dut1_if2_1}
| | ... | ${dut1_eth_bond_if1}
| | Run Keyword Unless | '${if2_status}' == 'PASS'
| | ... | VPP Enslave Physical Interface | ${dut1} | ${dut1_if2_2}
| | ... | ${dut1_eth_bond_if1}
| | ${dut2_eth_bond_if1}= | VPP Create Bond Interface | ${dut2} | ${bond_mode}
| | ... | ${lb_mode}
| | Set Interface State | ${dut2} | ${dut2_eth_bond_if1} | up
| | VPP Set interface MTU | ${dut1} | ${dut1_eth_bond_if1}
| | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2_if1}
| | Run Keyword If | '${if1_status}' == 'PASS'
| | ... | VPP Enslave Physical Interface | ${dut2} | ${dut2_if1}
| | ... | ${dut2_eth_bond_if1}
| | ... | ELSE
| | ... | VPP Enslave Physical Interface | ${dut2} | ${dut2_if1_1}
| | ... | ${dut2_eth_bond_if1}
| | Run Keyword Unless | '${if2_status}' == 'PASS'
| | ... | VPP Enslave Physical Interface | ${dut2} | ${dut2_if1_2}
| | ... | ${dut2_eth_bond_if1}
| | VPP Show Bond Data On All Nodes | ${nodes} | verbose=${TRUE}
| | Initialize VLAN dot1q sub-interfaces in circular topology
| | ... | ${dut1} | ${dut1_eth_bond_if1} | ${dut2} | ${dut2_eth_bond_if1}
| | ... | ${subid}
| | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | Configure vhost interfaces
| | ... | ${dut1} | /var/run/vpp/sock-1-1 | /var/run/vpp/sock-1-2
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${vhost_if1}
| | Configure L2XC | ${dut1} | ${subif_index_1} | ${vhost_if2}
| | Configure vhost interfaces
| | ... | ${dut2} | /var/run/vpp/sock-1-1 | /var/run/vpp/sock-1-2
| | Configure L2XC | ${dut2} | ${subif_index_2} | ${vhost_if1}
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${vhost_if2}

| Initialize L2 xconnect with memif pairs on DUT node
| | [Documentation]
| | ... | Create pairs of Memif interfaces on DUT node. Cross connect each Memif
| | ... | interface with one physical interface or virtual interface to create
| | ... | a chain accross DUT node.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: dictionary
| | ... | - count - Number of memif pairs (containers). Type: integer
| |
| | ... | *Note:*
| | ... | Socket paths for Memif are defined in following format:
| | ... | - /tmp/memif-\${dut}_CNF\${number}-\${sid}
| |
| | ... | KW uses test variable \${rxq_count_int} set by KW Add worker threads
| | ... | and rxqueues to all DUTs
| |
| | ... | *Example:*
| |
| | ... | \| Initialize L2 xconnect with memif pairs on DUT node \| ${dut} \
| | ... | \| ${1} \|
| |
| | [Arguments] | ${dut} | ${count}
| |
| | FOR | ${number} | IN RANGE | 1 | ${count}+1
| | | ${sock1}= | Set Variable | memif-${dut}_CNF
| | | ${sock2}= | Set Variable | memif-${dut}_CNF
| | | ${prev_index}= | Evaluate | ${number}-1
| | | Set up memif interfaces on DUT node | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${number} | ${dut}-memif-${number}-if1
| | | ... | ${dut}-memif-${number}-if2 | ${rxq_count_int} | ${rxq_count_int}
| | | ${xconnect_if1}= | Set Variable If | ${number}==1 | ${${dut}_if1}
| | | ... | ${${dut}-memif-${prev_index}-if2}
| | | Configure L2XC | ${nodes['${dut}']} | ${xconnect_if1}
| | | ... | ${${dut}-memif-${number}-if1}
| | | Run Keyword If | ${number}==${count} | Configure L2XC
| | | ... | ${nodes['${dut}']} | ${${dut}-memif-${number}-if2} | ${${dut}_if2}
| | END

| Initialize L2 xconnect with memif pairs
| | [Documentation]
| | ... | Create pairs of Memif interfaces on all defined VPP nodes. Cross
| | ... | connect each Memif interface with one physical interface or virtual
| | ... | interface to create a chain accross DUT node.
| |
| | ... | *Arguments:*
| | ... | - count - Number of memif pairs (containers). Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize L2 xconnect with memif pairs \| ${1} \|
| |
| | [Arguments] | ${count}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize L2 xconnect with memif pairs on DUT node | ${dut} | ${count}
| | END
| | Set interfaces in path up
| | Show Memif on all DUTs | ${nodes}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=memif

| Initialize L2 xconnect for single memif
| | [Documentation]
| | ... | Create single Memif interface on all defined VPP nodes. Cross
| | ... | connect Memif interface with one physical interface.
| |
| | ... | *Arguments:*
| | ... | - number - Memif ID. Type: integer
| |
| | ... | *Note:*
| | ... | Socket paths for Memif are defined in following format:
| | ... | - /tmp/memif-DUT1_CNF\${number}-\${sid}
| |
| | ... | KW uses test variable ${rxq_count_int} set by KW Add worker threads
| | ... | and rxqueues to all DUTs
| |
| | ... | *Example:*
| |
| | ... | \| Initialize L2 xconnect for single memif \| 1 \|
| |
| | [Arguments] | ${number}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | ${sock}= | Set Variable | memif-${dut}_CNF
| | | ${sid}= | Evaluate | (${number} * ${2}) - ${1}
| | | Set up single memif interface on DUT node | ${nodes['${dut}']} | ${sock}
| | | ... | mid=${number} | sid=${sid} | memif_if=${dut}-memif-${number}-if1
| | | ... | rxq=${rxq_count_int} | txq=${rxq_count_int}
| | | Configure L2XC | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ${${dut}-memif-${number}-if1}
| | END
| | Set single interfaces in path up
| | Show Memif on all DUTs | ${nodes}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=memif
