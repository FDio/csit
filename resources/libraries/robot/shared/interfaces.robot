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
| Set single interfaces in path up
| | [Documentation]
| | ... | *Set UP state on single physical VPP interfaces in path on all DUT
| | ... | nodes and set maximal MTU.*
| |
| | ... | *Arguments:*
| | ... | - pf - NIC physical function (physical port).
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Set single interfaces in path \| 1 \|
| |
| | [Arguments] | ${pf}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set interfaces in path up on node on PF | ${dut} | ${pf}
| | END
| | All VPP Interfaces Ready Wait | ${nodes} | retries=${60}

| Set interfaces in path up
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on all DUT nodes and set
| | ... | maximal MTU.*
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set interfaces in path up on node | ${dut}
| | END
| | All VPP Interfaces Ready Wait | ${nodes} | retries=${60}

| Set interfaces in path up on node
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
| | ... | \| Set interfaces in path up on node \| DUT1 \|
| |
| | [Arguments] | ${dut}
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | Set interfaces in path up on node on PF | ${dut} | ${pf}
| | END

| Set interfaces in path up on node on PF
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on specified DUT node and
| | ... | set maximal MTU.*
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node on which to set the interfaces up.
| | ... | Type: string
| | ... | - pf - NIC physical function (physical port).
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Set interfaces in path up on node on PF \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | ${_chains} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | @{${dut}_${int}${pf}_1}
| | ${_id}= | Set Variable If | '${_chains}' == 'PASS' | _1 | ${EMPTY}
| | FOR | ${if} | IN | @{${dut}_${int}${pf}${_id}}
| | | Set Interface State | ${nodes['${dut}']} | ${if} | up
| | | VPP Set Interface MTU | ${nodes['${dut}']} | ${if}
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
| | | Run Keyword If | ${nic_rxq_size} > 0
| | | ... | ${dut}.Add DPDK Dev Default RXD | ${nic_rxq_size}
| | | Run Keyword If | ${nic_txq_size} > 0
| | | ... | ${dut}.Add DPDK Dev Default TXD | ${nic_txq_size}
| | | Run Keyword If | '${crypto_type}' != '${None}'
| | | ... | ${dut}.Add DPDK Cryptodev | ${thr_count_int}
| | END
| | ${_vlan_strip} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${vlan_strip_off}
| | Run keyword If | '${_vlan_strip}' == 'PASS' and ${duts_count} == 2
| | ... | Add DPDK VLAN strip offload switch off between DUTs

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
| | ... | Initialize driver based interfaces on all DUT. Interfaces are
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
| | | Initialize layer driver on node | ${dut} | ${driver}
| | END
| | Set Test Variable | ${int} | vf
| | Set interfaces in path up

| Initialize layer driver on node
| | [Documentation]
| | ... | Initialize driver based interfaces on DUT.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - driver - NIC driver used in test [vfio-pci|avf|rdma-core].
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer driver \| DUT1 \| vfio-pci \|
| |
| | [Arguments] | ${dut} | ${driver}
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | ${_vf}=
| | | ... | Copy List | ${${dut}_${int}${pf}}
| | | ${_ip4_addr}=
| | | ... | Copy List | ${${dut}_${int}${pf}_ip4_addr}
| | | ${_ip4_prefix}=
| | | ... | Copy List | ${${dut}_${int}${pf}_ip4_prefix}
| | | ${_mac}=
| | | ... | Copy List | ${${dut}_${int}${pf}_mac}
| | | ${_pci}=
| | | ... | Copy List | ${${dut}_${int}${pf}_pci}
| | | ${_vlan}=
| | | ... | Copy List | ${${dut}_${int}${pf}_vlan}
| | | Set Test Variable
| | | ... | ${${dut}_vf${pf}} | ${_vf}
| | | Set Test Variable
| | | ... | ${${dut}_vf${pf}_ip4_addr} | ${_ip4_addr}
| | | Set Suite Variable
| | | ... | ${${dut}_vf${pf}_ip4_prefix} | ${_ip4_prefix}
| | | Set Test Variable
| | | ... | ${${dut}_vf${pf}_mac} | ${_mac}
| | | Set Test Variable
| | | ... | ${${dut}_vf${pf}_pci} | ${_pci}
| | | Set Test Variable
| | | ... | ${${dut}_vf${pf}_vlan} | ${_vlan}
| | | Run Keyword | Initialize layer ${driver} on node | ${dut} | ${pf}
| | END

| Initialize layer vfio-pci on node
| | [Documentation]
| | ... | Initialize vfio-pci interfaces on DUT on NIC PF.
| | ... | Currently no operation.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - pf - NIC physical function (physical port). Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer vfio-pci on node \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | No operation

| Initialize layer avf on node
| | [Documentation]
| | ... | Initialize AVF (Intel) interfaces on DUT on NIC PF.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - pf - NIC physical function (physical port). Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer avf on node \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | FOR | ${vf} | IN RANGE | 0 | ${nic_vfs}
| | | ${_avf}= | VPP Create AVF Interface
| | | ... | ${nodes['${dut}']} | ${${dut}_vf${pf}}[${vf}]
| | | ... | num_rx_queues=${rxq_count_int}
| | | ... | rxq_size=${nic_rxq_size} | txq_size=${nic_txq_size}
| | | ${_ip4}=
| | | ... | Get Interface IP4 | ${nodes['${dut}']} | ${_avf}
| | | ${_ip4_prefix}=
| | | ... | Get Interface IP4 Prefix Length | ${nodes['${dut}']} | ${_avf}
| | | ${_mac}=
| | | ... | Get Interface MAC | ${nodes['${dut}']} | ${_avf}
| | | ${_pci}=
| | | ... | Get Interface PCI Addr | ${nodes['${dut}']} | ${_avf}
| | | ${_vlan}=
| | | ... | Get Interface VLAN | ${nodes['${dut}']} | ${_avf}
| | | Set List Value | ${${dut}_vf${pf}} | ${vf} | ${_avf}
| | | Set List Value | ${${dut}_vf${pf}_ip4_addr} | ${vf} | ${_ip4}
| | | Set List Value | ${${dut}_vf${pf}_ip4_prefix} | ${vf} | ${_ip4_prefix}
| | | Set List Value | ${${dut}_vf${pf}_mac} | ${vf} | ${_mac}
| | | Set List Value | ${${dut}_vf${pf}_pci} | ${vf} | ${_pci}
| | | Set List Value | ${${dut}_vf${pf}_vlan} | ${vf} | ${_vlan}
| | END

| Initialize layer rdma-core on node
| | [Documentation]
| | ... | Initialize rdma-core (Mellanox VPP) interfaces on DUT on NIC PF.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - pf - NIC physical function (physical port). Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer rdma-core on node \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | ${_rdma}= | VPP Create Rdma Interface
| | ... | ${nodes['${dut}']} | ${${dut}_vf${pf}}[0]
| | ... | num_rx_queues=${rxq_count_int}
| | ... | rxq_size=${nic_rxq_size} | txq_size=${nic_txq_size}
| | Set List Value | ${${dut}_vf${pf}} | 0 | ${_rdma}

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

| Initialize layer interface on node
| | [Documentation]
| | ... | Physical interfaces variables to be created on all DUTs.
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
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | Initialize layer interface on node on PF | ${dut} | ${pf} | count=${count}
| | END

| Initialize layer interface on node on PF
| | [Documentation]
| | ... | Baseline interfaces variables to be created.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - pf - NIC physical function (physical port). Type: integer
| | ... | - count - Number of baseline interface variables. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer interface on node on PF \| DUT1 \| 1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf} | ${count}=${1}
| |
| | FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | Set Test Variable
| | | ... | ${${dut}_${int}${pf}_${id}} | ${${dut}_${int}${pf}}
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
| | Set Test Variable | ${int} | bond

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
| | ${if_index}= | VPP Create Bond Interface
| | ... | ${nodes['${dut}']} | ${bond_mode} | load_balance=${lb_mode}
| | ... | mac=00:00:00:01:01:01
| | Set Interface State | ${nodes['${dut}']} | ${if_index} | up
| | VPP Enslave Physical Interface
| | ... | ${nodes['${dut}']} | ${${dut}_${int}1_1} | ${if_index}
| | VPP Enslave Physical Interface
| | ... | ${nodes['${dut}']} | ${${dut}_${int}2_1} | ${if_index}
| | FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | Set Test Variable | ${${dut}_bond1_${id}} | ${if_index}
| | | Set Test Variable | ${${dut}_bond2_${id}} | ${if_index}
| | END

| Initialize layer dot1q
| | [Documentation]
| | ... | Dot1q interfaces and variables to be created on all DUTs.
| |
| | ... | *Arguments:*
| | ... | - count - Number of chains.
| | ... | Type: integer
| | ... | - vlan_per_chain - Whether to create vlan subinterface for each chain.
| | ... | Type: boolean
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | \| Initialize layer dot1q \| 1 \| True \| 1 \|
| |
| | [Arguments] | ${count}=${1} | ${vlan_per_chain}=${True} | ${start}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize layer dot1q on node
| | | ... | ${dut} | count=${count} | vlan_per_chain=${vlan_per_chain}
| | | ... | start=${start}
| | END
| | Set Test Variable | ${int} | dot1q

| Initialize layer dot1q on node
| | [Documentation]
| | ... | Dot1q interfaces and variables to be created on all DUT's node.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - count - Number of chains.
| | ... | Type: integer
| | ... | - vlan_per_chain - Whether to create vlan subinterface for each chain.
| | ... | Type: boolean
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer dot1q on node \| DUT1 \| 1 \| True \| 1 \|
| |
| | [Arguments] | ${dut} | ${count}=${1} | ${vlan_per_chain}=${True}
| | ... | ${start}=${1}
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | Initialize layer dot1q on node on PF | ${dut} | pf=${pf} | count=${count}
| | | ... | vlan_per_chain=${vlan_per_chain} | start=${start}
| | END

| Initialize layer dot1q on node on PF
| | [Documentation]
| | ... | Dot1q interfaces and variables to be created on all DUT's node
| | ... | interfaces.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - pf - NIC physical function (physical port).
| | ... | Type: integer
| | ... | - count - Number of chains.
| | ... | Type: integer
| | ... | - vlan_per_chain - Whether to create vlan subinterface for each chain.
| | ... | Type: boolean
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer dot1q on node on PF \| DUT1 \| 3 \| True \| 2 \|
| |
| | [Arguments] | ${dut} | ${pf}=${1} | ${count}=${1}
| | ... | ${vlan_per_chain}=${True} | ${start}=${1}
| |
| | FOR | ${id} | IN RANGE | ${start} | ${count} + 1
| | | ${_dot1q} | Initialize layer dot1q on node on PF for chain
| | | ... | dut=${dut} | pf=${pf} | id=${id} | vlan_per_chain=${vlan_per_chain}
| | | # First id results in non-None indices, after that _1_ are defined.
| | | ${_dot1q}= | Set Variable If | '${_dot1q}' == '${NONE}'
| | | ... | ${${dut}_dot1q${pf}_1} | ${_dot1q}
| | | ${_dot1q}= | Create List | ${_dot1q}
| | | Set Test Variable | ${${dut}_dot1q${pf}_${id}} | ${_dot1q}
| | END

| Initialize layer dot1q on node on PF for chain
| | [Documentation]
| | ... | Optionally create tag popping subinterface per chain.
| | ... | Return interface indices for dot1q layer interfaces,
| | ... | or Nones if subinterfaces are not created.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - pf - NIC physical function (physical port).
| | ... | Type: integer
| | ... | - id - Positive index of the chain.
| | ... | Type: integer
| | ... | - vlan_per_chain - Whether to create vlan subinterface for each chain.
| | ... | Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer dot1q on node on PF for chain \| DUT1 \
| | ... | \| 1 \| 1 \| True \|
| |
| | [Arguments] | ${dut} | ${pf} | ${id} | ${vlan_per_chain}=${True}
| |
| | Return From Keyword If | ${id} != ${1} and not ${vlan_per_chain}
| | ... | ${NONE} | ${NONE}
| | ${_default}= | Evaluate | ${pf} * ${100} + ${id} - ${1}
| | ${_vlan}= | Get Variable Value | \${${dut}_pf${pf}_vlan}
| | ${_vlan}= | Set Variable If | '${_vlan}[0]' != '${NONE}'
| | ... | ${_vlan}[0] | ${_default}
| | ${_name} | ${_index}= | Create Vlan Subinterface
| | ... | ${nodes['${dut}']} | ${${dut}_${int}${pf}_${id}}[0] | ${_vlan}
| | Set Interface State | ${nodes['${dut}']} | ${_index} | up
| | Configure L2 tag rewrite method on interfaces
| | ... | ${nodes['${dut}']} | ${_index} | TAG_REWRITE_METHOD=pop-1
| | Return From Keyword | ${_index}

| Initialize layer ip4vxlan
| | [Documentation]
| | ... | VXLAN interfaces and variables to be created on all DUT's interfaces.
| |
| | ... | *Arguments:*
| | ... | - count - Number of vxlan interfaces.
| | ... | Type: integer
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | \| Initialize layer ip4vxlan \| 3 \| 2 \|
| |
| | [Arguments] | ${count}=${1} | ${start}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize layer ip4vxlan on node | ${dut} | count=${count}
| | | ... | start=${start}
| | END
| | Set Test Variable | ${int} | ip4vxlan

| Initialize layer ip4vxlan on node
| | [Documentation]
| | ... | Setup VXLANoIPv4 between TG and DUTs and DUT to DUT by connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | towards TG. VXLAN sub-interfaces has same IPv4 address as interfaces.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - count - Number of vxlan interfaces.
| | ... | Type: integer
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer ip4vxlan on node \| DUT1 \| 3 \| 2 \|
| |
| | [Arguments] | ${dut} | ${count}=${1} | ${start}=${1}
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | Initialize layer ip4vxlan on node on PF | ${dut} | pf=${pf}
| | | ... | count=${count} | start=${start}
| | END

| Initialize layer ip4vxlan on node on PF
| | [Documentation]
| | ... | Setup VXLANoIPv4 between TG and DUTs and DUT to DUT by connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | towards TG. VXLAN sub-interfaces has same IPv4 address as interfaces.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - pf - NIC physical function (physical port).
| | ... | Type: integer
| | ... | - count - Number of vxlan interfaces.
| | ... | Type: integer
| | ... | - start - Id of first chain, allows adding chains during test.
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer ip4vxlan on node on PF \| DUT1 \| 3 \| 2 \|
| |
| | [Arguments] | ${dut} | ${pf}=${1} | ${count}=${1} | ${start}=${1}
| |
| | Run Keyword If | "${start}" == "1" | VPP Interface Set IP Address
| | ... | ${nodes['${dut}']} | ${${dut}_${int}${pf}_1}[0]
| | ... | 172.${pf}6.0.1 | 24
| | FOR | ${id} | IN RANGE | ${start} | ${count} + 1
| | | ${_subnet}= | Evaluate | ${id} - 1
| | | ${_vni}= | Evaluate | ${id} - 1
| | | ${_ip4vxlan}= | Create VXLAN interface
| | | ... | ${nodes['${dut}']} | ${_vni}
| | | ... | 172.${pf}6.0.1 | 172.${pf}7.${_subnet}.2
| | | ${_prev_mac}= | Set Variable If | '${dut}' == 'DUT1'
| | | ... | ${tg_if1_mac} | ${dut1_if2_mac}
| | | ${_next_mac}= | Set Variable If | '${dut}' == 'DUT1' and ${duts_count} == 2
| | | ... | ${dut2_if1_mac} | ${tg_if2_mac}
| | | ${_even}= | Evaluate | ${pf} % 2
| | | ${_mac}= | Set Variable If | ${_even}
| | | ... | ${_prev_mac} | ${_next_mac}
| | | VPP Add IP Neighbor
| | | ... | ${nodes['${dut}']} | ${${dut}_${int}${pf}_${id}}[0]
| | | ... | 172.${pf}6.${_subnet}.2 | ${_mac}
| | | VPP Route Add
| | | ... | ${nodes['${dut}']} | 172.${pf}7.${_subnet}.0 | 24
| | | ... | gateway=172.${pf}6.${_subnet}.2
| | | ... | interface=${${dut}_${int}${pf}_${id}}[0]
| | | Set VXLAN Bypass
| | | ... | ${nodes['${dut}']} | ${${dut}_${int}${pf}_${id}}[0]
| | | ${_ip4vxlan}= | Create List | ${_ip4vxlan}
| | | Set Test Variable
| | | ... | ${${dut}_ip4vxlan${pf}_${id}} | ${_ip4vxlan}
| | END

| Configure vhost interfaces
| | [Documentation]
| | ... | Create two Vhost-User interfaces on defined VPP node.
| |
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node.
| | ... | Type: dictionary
| | ... | - ${sock1} - Socket path for first Vhost-User interface.
| | ... | Type: string
| | ... | - ${sock2} - Socket path for second Vhost-User interface.
| | ... | Type: string
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

| Get Vhost dump
| | [Documentation] | Get vhost-user dump.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node data.
| | ... | Type: dictionary
| |
| | [Arguments] | ${dut}
| |
| | ${vhost_dump}= | Vhost User Dump | ${dut}
| | Return From Keyword | ${vhost_dump}
