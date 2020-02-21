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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.VhostUser

*** Variables ***
| ${dpdk_no_tx_checksum_offload}= | ${True}

*** Keywords ***
| Set interfaces in path up
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on all DUT nodes and set
| | ... | maximal MTU.*
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set physical interfaces in path up on DUT | ${dut}
| | END
| | All VPP Interfaces Ready Wait | ${nodes} | retries=${300}

| Set physical interfaces in path up on DUT
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on specified DUT node and
| | ... | set maximal MTU.*
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node on which to set the interfaces up.
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Set physical interfaces in path up on DUT \| DUT1 \|
| |
| | [Arguments] | ${dut}
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | Set all interfaces in path up on DUT | ${dut} | ${pf}
| | END

| Set all interfaces in path up on DUT
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on specified DUT node and
| | ... | set maximal MTU.*
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node on which to set the interfaces up.
| | ... | Type: string
| | ... | - pf - NIC physical function (physical port).
| |
| | ... | *Example:*
| |
| | ... | \| Set all interfaces in path up on DUT \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | FOR | ${if} | IN | @{${dut}_${prev_layer}${pf}}
| | | Set Interface State | ${nodes['${dut}']} | ${if} | up
| | | VPP Set Interface MTU | ${nodes['${dut}']} | ${if}
| | END

| Set single interfaces in path up
| | [Documentation]
| | ... | *Set UP state on single VPP interfaces in path on all DUT nodes and
| | ... | set maximal MTU.*
| |
| | ... | *Arguments:*
| | ... | - pf - NIC physical function (physical port).
| |
| | ... | *Example:*
| |
| | ... | \| Set single interfaces in path \| 1 \|
| |
| | [Arguments] | ${pf}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set virtual interfaces in path up on DUT | ${dut} | ${pf}
| | END
| | All VPP Interfaces Ready Wait | ${nodes}

| Get Vhost dump
| | [Documentation] | Get vhost-user dump.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node data. Type: dictionary
| |
| | [Arguments] | ${dut_node}
| |
| | [Return] | ${vhost_dump}
| |
| | ${vhost_dump}= | Vhost User Dump | ${dut_node}

| Initialize layer interface on node
| | [Documentation]
| | ... | Baseline interfaces variables to be created.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of baseline interface variables. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer interface on node \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${count}=${1}
| |
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | Set Test Variable
| | | ... | ${${dut_str}_${prev_layer}1_${id}} | ${${dut_str}_${prev_layer}1}
| | | Set Test Variable
| | | ... | ${${dut_str}_${prev_layer}2_${id}} | ${${dut_str}_${prev_layer}2}
| | END

| Initialize layer interface
| | [Documentation]
| | ... | Physical interfaces variables to be created on all DUTs.
| |
| | ... | *Arguments:*
| | ... | - count - Number of untagged interfaces variables. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer interface \| 1 \|
| |
| | [Arguments] | ${count}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize layer interface on node | ${dut} | count=${count}
| | END

| Pre-initialize layer driver
| | [Documentation]
| | ... | Pre-initialize driver based interfaces on each DUT.
| |
| | ... | *Arguments:*
| | ... | - driver - NIC driver used in test [vfio-pci|avf|rdma-core].
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Pre-initialize layer driver \| vfio-pci \|
| |
| | [Arguments] | ${driver}
| |
| | Run Keyword | Pre-initialize layer ${driver} on all DUTs

| Pre-initialize layer vfio-pci on all DUTs
| | [Documentation]
| | ... | Pre-initialize vfio-pci driver by adding related sections to startup
| | ... | config on all DUTs.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK Dev | @{${dut}_pf_pci}
| | | Run Keyword If | ${dpdk_no_tx_checksum_offload}
| | | ... | ${dut}.Add DPDK No Tx Checksum Offload
| | | Run Keyword | ${dut}.Add DPDK Log Level | debug
| | | Run Keyword | ${dut}.Add DPDK Uio Driver | vfio-pci
| | | Run Keyword | ${dut}.Add DPDK Dev Default RXQ | ${rxq_count_int}
| | | Run Keyword If | not ${jumbo}
| | | ... | ${dut}.Add DPDK No Multi Seg
| | | Run Keyword If | ${rxd_count_int}
| | | ... | ${dut}.Add DPDK Dev Default RXD | ${rxd_count_int}
| | | Run Keyword If | ${txd_count_int}
| | | ... | ${dut}.Add DPDK Dev Default TXD | ${txd_count_int}
| | | Run Keyword If | '${crypto_type}' != '${None}'
| | | ... | ${dut}.Add DPDK Cryptodev | ${thr_count_int}
| | END

| Pre-initialize layer avf on all DUTs
| | [Documentation]
| | ... | Pre-initialize avf driver. Currently no operation.
| |
| | No operation

| Pre-initialize layer rdma-core on all DUTs
| | [Documentation]
| | ... | Pre-initialize rdma-core driver. Currently no operation.
| |
| | No operation

| Initialize layer driver
| | [Documentation]
| | ... | Initialize driver based interfaces on each DUT. Interfaces are
| | ... | brought up.
| |
| | ... | *Arguments:*
| | ... | - driver - NIC driver used in test [vfio-pci|avf|rdma-core].
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer driver \| vfio-pci \|
| |
| | [Arguments] | ${driver}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | Initialize layer ${driver} on node | ${dut}
| | END
| | Set interfaces in path up

| Initialize layer vfio-pci on node
| | [Documentation]
| | ... | Initialize vfio-pci interfaces on DUT. Currently no operation.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer vfio-pci on node \| DUT1 \|
| |
| | [Arguments] | ${dut}
| |
| | No operation

| Initialize layer avf on node
| | [Documentation]
| | ... | Initialize AVF interfaces on DUT.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer avf on node \| DUT1 \|
| |
| | [Arguments] | ${dut}
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | Initialize layer avf on node on PF | ${dut} | ${pf}
| | END

| Initialize layer avf on node on PF
| | [Documentation]
| | ... | Initialize AVF interfaces on DUT on NIC PF.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer avf (Intel) on node on PF \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | FOR | ${vf} | IN RANGE | 0 | ${nic_vfs}
| | | ${_vlan}= | Get Interface Vlan
| | | ... | ${nodes['${dut}']} | ${${dut}_${prev_layer}${pf}}[${vf}]
| | | ${_avf}= | VPP Create AVF Interface
| | | ... | ${nodes['${dut}']} | ${${dut}_${prev_layer}${pf}}[${vf}]
| | | ... | ${rxq_count_int}
| | | ${_mac}= | Get Interface MAC
| | | ... | ${nodes['${dut}']} | ${_avf}
| | | Set List Value | ${${dut}_${prev_layer}${pf}} | ${vf} | ${_avf}
| | | Insert Into List | ${${dut}_${prev_layer}${pf}_mac} | ${vf} | ${_mac}
| | | Insert Into List | ${${dut}_${prev_layer}${pf}_vlan} | ${vf} | ${_vlan}
| | END

| Initialize layer rdma-core on node
| | [Documentation]
| | ... | Initialize rdma-core interfaces on DUT.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer rdma-core on node \| DUT1 \|
| |
| | [Arguments] | ${dut}
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | Initialize layer rdma-core on node on PF | ${dut} | ${pf}
| | END

| Initialize layer rdma-core on node on PF
| | [Documentation]
| | ... | Initialize rdma-core (Mellanox VPP) interfaces on DUT on NIC PF.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer rdma-core on node on PF \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | FOR | ${vf} | IN RANGE | 0 | ${nic_vfs}
| | | ${_vlan}= | Get Interface Vlan
| | | ... | ${nodes['${dut}']} | ${${dut}_${prev_layer}${pf}}[${vf}]
| | | ${_avf}= | VPP Create Rdma Interface
| | | ... | ${nodes['${dut}']} | ${${dut}_${prev_layer}${pf}}[${vf}]
| | | ... | ${rxq_count_int}
| | | ${_mac}= | Get Interface MAC
| | | ... | ${nodes['${dut}']} | ${_avf}
| | | Set List Value | ${${dut}_${prev_layer}${pf}} | ${vf} | ${_avf}
| | | Insert Into List | ${${dut}_${prev_layer}${pf}_mac} | ${vf} | ${_mac}
| | | Insert Into List | ${${dut}_${prev_layer}${pf}_vlan} | ${vf} | ${_vlan}
| | END

| Initialize layer bonding on node
| | [Documentation]
| | ... | Bonded interface and variables to be created on across east and
| | ... | west DUT's node interfaces.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - bond_mode - Link bonding mode. Type: string
| | ... | - lb_mode - Load balance mode. Type: string
| | ... | - count - Number of bond interface variables. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer bonding on node \| DUT1 \| xor \| l34 \| 1 \|
| |
| | [Arguments] | ${dut} | ${bond_mode}=xor | ${lb_mode}=l34 | ${count}=${1}
| |
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | ${if_index}= | VPP Create Bond Interface
| | ... | ${nodes['${dut}']} | ${bond_mode} | load_balance=${lb_mode}
| | ... | mac=00:00:00:01:01:01
| | Set Interface State | ${nodes['${dut}']} | ${if_index} | up
| | VPP Enslave Physical Interface
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_1} | ${if_index}
| | VPP Enslave Physical Interface
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_2} | ${if_index}
| | FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | Set Test Variable | ${${dut_str}_bond_${id}_1} | ${if_index}
| | | Set Test Variable | ${${dut_str}_bond_${id}_2} | ${if_index}
| | END

| Initialize layer bonding
| | [Documentation]
| | ... | Bonded interfaces and variables to be created on all DUT's interfaces.
| |
| | ... | *Arguments:*
| | ... | - bond_mode - Link bonding mode. Type: string
| | ... | - lb_mode - Load balance mode. Type: string
| | ... | - count - Number of bond interface variables. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer bonding \| xor \| l34 \| 1 \|
| |
| | [Arguments] | ${bond_mode}=xor | ${lb_mode}=l34 | ${count}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize layer bonding on node
| | | ... | ${dut} | bond_mode=${bond_mode} | lb_mode=${lb_mode}
| | | ... | count=${count}
| | END
| | Set Test Variable | ${prev_layer} | bond

| Initialize layer dot1q on node for chain
| | [Documentation]
| | ... | Optionally create tag popping subinterface per chain.
| | ... | Return interface indices for dot1q layer interfaces,
| | ... | or Nones if subinterfaces are not created.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - id - Positive index of the chain. Type: integer
| | ... | - vlan_per_chain - Whether to create vlan subinterface for each chain.
| | ... | Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer dot1q on node for chain \| DUT1 \| 1 \| True \|
| |
| | [Arguments] | ${dut} | ${id} | ${vlan_per_chain}=${True}
| |
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | Return From Keyword If | ${id} != ${1} and not ${vlan_per_chain}
| | ... | ${NONE} | ${NONE}
| | # TODO: Is it worth creating Get Variable Value If Not None keyword?
| | ${default}= | Evaluate | ${100} + ${id} - ${1}
| | ${if1_vlan}= | Get Variable Value | \${${dut_str}_vlan1}
| | ${if1_vlan}= | Set Variable If | '${if1_vlan}' != '${NONE}'
| | ... | ${if1_vlan} | ${default}
| | ${default}= | Evaluate | ${200} + ${id} - ${1}
| | ${if2_vlan}= | Get Variable Value | \${${dut_str}_vlan2}
| | ${if2_vlan}= | Set Variable If | '${if2_vlan}' != '${NONE}'
| | ... | ${if2_vlan} | ${default}
| | ${if1_name} | ${if1_index}= | Create Vlan Subinterface
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_1}
| | ... | ${if1_vlan}
| | ${if2_name} | ${if2_index}= | Create Vlan Subinterface
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_2}
| | ... | ${if2_vlan}
| | Set Interface State | ${nodes['${dut}']} | ${if1_index} | up
| | Set Interface State | ${nodes['${dut}']} | ${if2_index} | up
| | Configure L2 tag rewrite method on interfaces
| | ... | ${nodes['${dut}']} | ${if1_index} | TAG_REWRITE_METHOD=pop-1
| | Configure L2 tag rewrite method on interfaces
| | ... | ${nodes['${dut}']} | ${if2_index} | TAG_REWRITE_METHOD=pop-1
| | Return From Keyword | ${if1_index} | ${if2_index}

| Initialize layer dot1q on node
| | [Documentation]
| | ... | Dot1q interfaces and variables to be created on all DUT's node
| | ... | interfaces.
| |
| | ... | TODO: Unify names for number of chains/pipelines/instances/interfaces.
| | ... | Chose names and descriptions that makes sense for both
| | ... | nf_density and older tests.
| | ... | Note that with vlan_per_chain=False it is not a number of interfaces.
| | ... | At least not number of real interfaces, just number of aliases.
| | ... | This TODO applies also to all keywords with nf_chains argument.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of chains. Type: integer
| | ... | - vlan_per_chain - Whether to create vlan subinterface for each chain.
| | ... | Type: boolean
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer dot1q on node \| DUT1 \| 3 \| True \| 2 \|
| |
| | [Arguments] | ${dut} | ${count}=${1} | ${vlan_per_chain}=${True}
| | ... | ${start}=${1}
| |
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | FOR | ${id} | IN RANGE | ${start} | ${count} + 1
| | | ${if1_index} | ${if2_index}= | Initialize layer dot1q on node for chain
| | | ... | dut=${dut} | id=${id} | vlan_per_chain=${vlan_per_chain}
| | | # First id results in non-None indices, after that _1_ are defined.
| | | ${if1_index}= | Set Variable If | '${if1_index}' == '${NONE}'
| | | ... | ${${dut_str}_dot1q_1_1} | ${if1_index}
| | | ${if2_index}= | Set Variable If | '${if2_index}' == '${NONE}'
| | | ... | ${${dut_str}_dot1q_1_2} | ${if2_index}
| | | Set Test Variable | ${${dut_str}_dot1q_${id}_1} | ${if1_index}
| | | Set Test Variable | ${${dut_str}_dot1q_${id}_2} | ${if2_index}
| | END

| Initialize layer dot1q
| | [Documentation]
| | ... | Dot1q interfaces and variables to be created on all DUT's interfaces.
| |
| | ... | *Arguments:*
| | ... | - count - Number of chains. Type: integer
| | ... | - vlan_per_chain - Whether to create vlan subinterface for each chain.
| | ... | Type: boolean
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | \| Initialize layer dot1q \| 3 \| True \| 2 \|
| |
| | [Arguments] | ${count}=${1} | ${vlan_per_chain}=${True} | ${start}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize layer dot1q on node | ${dut} | count=${count}
| | | ... | vlan_per_chain=${vlan_per_chain} | start=${start}
| | END
| | Set Test Variable | ${prev_layer} | dot1q

| Initialize layer ip4vxlan on node
| | [Documentation]
| | ... | Setup VXLANoIPv4 between TG and DUTs and DUT to DUT by connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | towards TG. VXLAN sub-interfaces has same IPv4 address as interfaces.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of vxlan interfaces. Type: integer
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer ip4vxlan on node \| DUT1 \| 3 \| 2 \|
| |
| | [Arguments] | ${dut} | ${count}=${1} | ${start}=${1}
| |
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | Run Keyword If | "${start}" == "1" | VPP Interface Set IP Address
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_1}
| | ... | 172.16.0.1 | 24
| | Run Keyword If | "${start}" == "1" | VPP Interface Set IP Address
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_2}
| | ... | 172.26.0.1 | 24
| | FOR | ${id} | IN RANGE | ${start} | ${count} + 1
| | | ${subnet}= | Evaluate | ${id} - 1
| | | ${vni}= | Evaluate | ${id} - 1
| | | ${ip4vxlan_1}= | Create VXLAN interface
| | | ... | ${nodes['${dut}']} | ${vni} | 172.16.0.1 | 172.17.${subnet}.2
| | | ${ip4vxlan_2}= | Create VXLAN interface
| | | ... | ${nodes['${dut}']} | ${vni} | 172.26.0.1 | 172.27.${subnet}.2
| | | ${prev_mac}= | Set Variable If | '${dut}' == 'DUT1'
| | | ... | ${tg_if1_mac} | ${dut1_if2_mac}
| | | ${next_mac}= | Set Variable If | '${dut}' == 'DUT1' and ${duts_count} == 2
| | | ... | ${dut2_if1_mac} | ${tg_if2_mac}
| | | VPP Add IP Neighbor
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_1}
| | | ... | 172.16.${subnet}.2 | ${prev_mac}
| | | VPP Add IP Neighbor
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_2}
| | | ... | 172.26.${subnet}.2 | ${next_mac}
| | | VPP Route Add
| | | ... | ${nodes['${dut}']} | 172.17.${subnet}.0 | 24
| | | ... | gateway=172.16.${subnet}.2
| | | ... | interface=${${dut_str}_${prev_layer}_${id}_1}
| | | VPP Route Add
| | | ... | ${nodes['${dut}']} | 172.27.${subnet}.0 | 24
| | | ... | gateway=172.26.${subnet}.2
| | | ... | interface=${${dut_str}_${prev_layer}_${id}_2}
| | | Set VXLAN Bypass
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_1}
| | | Set VXLAN Bypass
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_2}
| | | Set Test Variable
| | | ... | ${${dut_str}_ip4vxlan_${id}_1} | ${ip4vxlan_1}
| | | Set Test Variable
| | | ... | ${${dut_str}_ip4vxlan_${id}_2} | ${ip4vxlan_2}
| | END

| Initialize layer ip4vxlan
| | [Documentation]
| | ... | VXLAN interfaces and variables to be created on all DUT's interfaces.
| |
| | ... | *Arguments:*
| | ... | - count - Number of vxlan interfaces. Type: integer
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | \| Initialize layer ip4vxlan \| 3 \| 2 \|
| |
| | [Arguments] | ${count}=${1} | ${start}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize layer ip4vxlan on node | ${dut} | count=${count}
| | ... | start=${start}
| | END
| | Set Test Variable | ${prev_layer} | ip4vxlan

| Configure vhost interfaces
| | [Documentation]
| | ... | Create two Vhost-User interfaces on defined VPP node.
| |
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${sock1} - Socket path for first Vhost-User interface. Type: string
| | ... | - ${sock2} - Socket path for second Vhost-User interface. Type: string
| | ... | - ${vhost_if1} - Name of the first Vhost-User interface (Optional).
| | ... | Type: string
| | ... | - ${vhost_if2} - Name of the second Vhost-User interface (Optional).
| | ... | Type: string
| | ... | - ${is_server} - Server side of connection (Optional).
| | ... | Type: boolean
| | ... | - ${enable_gso} - Generic segmentation offloading (Optional).
| | ... | Type: boolean
| |
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${${vhost_if1}} - First Vhost-User interface.
| | ... | - ${${vhost_if2}} - Second Vhost-User interface.
| |
| | ... | *Example:*
| |
| | ... | \| Configure vhost interfaces \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \|
| | ... | \| Configure vhost interfaces \
| | ... | \| ${nodes['DUT2']} \| /tmp/sock1 \| /tmp/sock2 \| dut2_vhost_if1 \
| | ... | \| dut2_vhost_if2 \|
| |
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vhost_if1}=vhost_if1
| | ... | ${vhost_if2}=vhost_if2 | ${is_server}=${False}
| | ... | ${enable_gso}=${False}
| |
| | ${vhost_1}= | Vpp Create Vhost User Interface
| | ... | ${dut_node} | ${sock1} | is_server=${is_server}
| | ... | enable_gso=${enable_gso}
| | ${vhost_2}= | Vpp Create Vhost User Interface
| | ... | ${dut_node} | ${sock2} | is_server=${is_server}
| | ... | enable_gso=${enable_gso}
| | ${vhost_1_key}= | Get Interface By SW Index | ${dut_node} | ${vhost_1}
| | ${vhost_2_key}= | Get Interface By SW Index | ${dut_node} | ${vhost_2}
| | ${vhost_1_mac}= | Get Interface MAC | ${dut_node} | ${vhost_1_key}
| | ${vhost_2_mac}= | Get Interface MAC | ${dut_node} | ${vhost_2_key}
| | Set Interface State | ${dut_node} | ${vhost_1} | up
| | Set Interface State | ${dut_node} | ${vhost_2} | up
| | Set Test Variable | ${${vhost_if1}} | ${vhost_1}
| | Set Test Variable | ${${vhost_if2}} | ${vhost_2}
| | Set Test Variable | ${${vhost_if1}_mac} | ${vhost_1_mac}
| | Set Test Variable | ${${vhost_if2}_mac} | ${vhost_2_mac}
