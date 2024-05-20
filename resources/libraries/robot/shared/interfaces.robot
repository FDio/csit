# Copyright (c) 2024 Cisco and/or its affiliates.
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
| | ... | nodes.*
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
| | ... | *Set UP state on VPP interfaces in path on all DUT nodes.*
| |
| | ... | *Arguments:*
| | ... | - validate - Validate interfaces are up.
| | ... | Type: boolean
| |
| | [Arguments] | ${validate}=${True}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set interfaces in path up on node | ${dut}
| | END
| | Run Keyword If | ${validate}
| | ... | All VPP Interfaces Ready Wait | ${nodes} | retries=${60}

| Set interfaces in path up on node
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on specified DUT node.*
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
| | ... | *Set UP state on VPP interfaces in path on specified DUT node.*
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

| Pre-initialize layer tap on all DUTs
| | [Documentation]
| | ... | Pre-initialize tap driver. Currently no operation.
| |
| | No operation

| Pre-initialize layer vhost on all DUTs
| | [Documentation]
| | ... | Pre-initialize vhost driver. Currently no operation.
| |
| | No operation

| Pre-initialize layer vfio-pci on all DUTs
| | [Documentation]
| | ... | Pre-initialize vfio-pci driver by adding related sections to startup
| | ... | config on all DUTs.
| |
| | ${index}= | Get Index From List | ${TEST TAGS} | DPDK
| | Run Keyword If | ${index} >= 0 | Return From Keyword
| | FOR | ${dut} | IN | @{duts}
| | | Stop VPP Service | ${nodes['${dut}']}
| | | Unbind PCI Devices From Other Driver | ${nodes['${dut}']} | vfio-pci |
| | | ... | @{${dut}_pf_pci}
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
| | | ... | ${dut}.Add DPDK Cryptodev | ${dp_count_int}
| | | Run Keyword | ${dut}.Add DPDK Max Simd Bitwidth | ${GRAPH_NODE_VARIANT}
| | END

| Pre-initialize layer avf on all DUTs
| | [Documentation]
| | ... | Pre-initialize avf driver. Currently no operation.
| |
| | No operation

| Pre-initialize layer af_xdp on all DUTs
| | [Documentation]
| | ... | Pre-initialize af_xdp driver.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set Interface State PCI
| | | ... | ${nodes['${dut}']} | ${${dut}_pf_pci} | state=up
| | | Set Interface XDP off
| | | ... | ${nodes['${dut}']} | ${${dut}_pf_pci}
| | | Set Interface Channels
| | | ... | ${nodes['${dut}']} | ${${dut}_pf_pci} | num_queues=${rxq_count_int}
| | | ... | channel=combined
| | END

| Pre-initialize layer rdma-core on all DUTs
| | [Documentation]
| | ... | Pre-initialize rdma-core driver.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set Interface MTU | ${nodes['${dut}']} | ${${dut}_pf_pci}
| | | ... | mtu=${recommended_mtu}
| | | Set Interface Flow Control
| | | ... | ${nodes['${dut}']} | ${${dut}_pf_pci} | rxf="off" | txf="off"
| | END

| Pre-initialize layer mlx5_core on all DUTs
| | [Documentation]
| | ... | Pre-initialize mlx5_core driver.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set Interface Flow Control
| | | ... | ${nodes['${dut}']} | ${${dut}_pf_pci} | rxf="off" | txf="off"
| | END
| | ${index}= | Get Index From List | ${TEST TAGS} | DPDK
| | Run Keyword If | ${index} >= 0 | Return From Keyword
| | FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK Dev | @{${dut}_pf_pci}
| | | Run Keyword If | ${dpdk_no_tx_checksum_offload}
| | | ... | ${dut}.Add DPDK No Tx Checksum Offload
| | | Run Keyword | ${dut}.Add DPDK Log Level | debug
| | | Run Keyword | ${dut}.Add DPDK Dev Default RXQ | ${rxq_count_int}
| | | Run Keyword If | not ${jumbo}
| | | ... | ${dut}.Add DPDK No Multi Seg
| | | Run Keyword If | ${nic_rxq_size} > 0
| | | ... | ${dut}.Add DPDK Dev Default RXD | ${nic_rxq_size}
| | | Run Keyword If | ${nic_txq_size} > 0
| | | ... | ${dut}.Add DPDK Dev Default TXD | ${nic_txq_size}
| | | Run Keyword If | '${crypto_type}' != '${None}'
| | | ... | ${dut}.Add DPDK Cryptodev | ${dp_count_int}
| | | Run Keyword | ${dut}.Add DPDK Max Simd Bitwidth | ${GRAPH_NODE_VARIANT}
| | END

| Initialize layer driver
| | [Documentation]
| | ... | Initialize driver based interfaces on all DUT. Interfaces are
| | ... | brought up.
| |
| | ... | *Arguments:*
| | ... | - driver - NIC driver used in test [vfio-pci|avf|rdma-core].
| | ... | Type: string
| | ... | - validate - Validate interfaces are up.
| | ... | Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer driver \| vfio-pci \|
| |
| | [Arguments] | ${driver} | ${validate}=${True}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize layer driver on node | ${dut} | ${driver}
| | END
| | Set Test Variable | ${int} | vf
| | Set interfaces in path up | validate=${validate}

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

| Initialize layer tap on node
| | [Documentation]
| | ... | Initialize tap interfaces on DUT.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - pf - TAP ID (logical port).
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer tap on node \| DUT1 \| 0 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | Create Namespace
| | ... | ${nodes['${dut}']} | tap${${pf}-1}_namespace
| | ${tap_feature_mask}= | Create Tap feature mask | gso=${enable_gso}
| | ${_tap}=
| | ... | And Add Tap Interface | ${nodes['${dut}']} | tap${${pf}-1}
| | ... | host_namespace=tap${${pf}-1}_namespace
| | ... | num_rx_queues=${rxq_count_int}
| | ... | rxq_size=${nic_rxq_size} | txq_size=${nic_txq_size}
| | ... | tap_feature_mask=${tap_feature_mask}
| | ${_mac}=
| | ... | Get Interface MAC | ${nodes['${dut}']} | tap${pf}
| | ${_tap}= | Create List | ${_tap}
| | ${_mac}= | Create List | ${_mac}
| | Vhost User Affinity
| | ... | ${nodes['${dut}']} | ${${dut}_pf${pf}}[0]
| | ... | skip_cnt=${${CPU_CNT_MAIN}+${CPU_CNT_SYSTEM}+${cpu_count_int}}
| | Set Test Variable
| | ... | ${${dut}_vf${pf}} | ${_tap}
| | Set Test Variable
| | ... | ${${dut}_vf${pf}_mac} | ${_mac}

| Initialize layer vhost on node
| | [Documentation]
| | ... | Initialize vhost interfaces on DUT.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - pf - VHOST ID (logical port).
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer vhost on node \| DUT1 \| 0 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | ${virtio_feature_mask}= | Create Virtio feature mask | gso=${enable_gso}
| | ${vhost}= | Vpp Create Vhost User Interface
| | ... | ${nodes['${dut}']} | /var/run/vpp/sock-${pf}-1
| | ... | is_server=${True} | virtio_feature_mask=${virtio_feature_mask}
| | ${_mac}=
| | ... | Get Interface MAC | ${nodes['${dut}']} | vhost${pf}
| | ${_vhost}= | Create List | ${_vhost}
| | ${_mac}= | Create List | ${_mac}
| | Set Test Variable
| | ... | ${${dut}_vf${pf}} | ${_vhost}
| | Set Test Variable
| | ... | ${${dut}_vf${pf}_mac} | ${_mac}

| Initialize layer vfio-pci on node
| | [Documentation]
| | ... | Initialize vfio-pci interfaces on DUT on NIC PF.
| | ... | Currently just set MTU to the recommended value.
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
| | Set Interface State | ${nodes['${dut}']} | ${${dut}_pf${pf}}[0] | down
| | VPP Set Interface MTU
| | ... | ${nodes['${dut}']} | ${${dut}_pf${pf}}[0] | mtu=${recommended_mtu}

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
| | | VPP Set Interface MTU
| | | ... | ${nodes['${dut}']} | ${${dut}_vf${pf}}[${vf}] | mtu=${recommended_mtu}
| | END

| Initialize layer af_xdp on node
| | [Documentation]
| | ... | Initialize AF_XDP (eBPF) interfaces on DUT on NIC PF.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - pf - NIC physical function (physical port). Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize layer af_xdp on node \| DUT1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${pf}
| |
| | ${_af_xdp}= | VPP Create AF XDP Interface
| | ... | ${nodes['${dut}']} | ${${dut}_vf${pf}}[0]
| | ... | num_rx_queues=${65535}
| | ... | rxq_size=${nic_rxq_size} | txq_size=${nic_txq_size}
| | ${cpu_skip_cnt}= | Evaluate | ${CPU_CNT_SYSTEM}+${CPU_CNT_MAIN}
| | ${cpu_skip_cnt}= | Evaluate | ${cpu_skip_cnt}+${cpu_count_int}
| | ${cpu_skip_cnt}= | Evaluate | ${cpu_skip_cnt}+(${pf}-${1})*${rxq_count_int}
| | Set Interface IRQs Affinity
| | ... | ${nodes['${dut}']} | ${_af_xdp}
| | ... | cpu_skip_cnt=${cpu_skip_cnt} | cpu_cnt=${rxq_count_int}
| | Set List Value | ${${dut}_vf${pf}} | 0 | ${_af_xdp}

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

| Initialize layer mlx5_core on node
| | [Documentation]
| | ... | Initialize mlx5_core interfaces on DUT on NIC PF.
| | ... | Currently just set MTU to the recommended value.
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
| | Set Interface State | ${nodes['${dut}']} | ${${dut}_pf${pf}}[0] | down
| | VPP Set Interface MTU
| | ... | ${nodes['${dut}']} | ${${dut}_pf${pf}}[0] | mtu=${recommended_mtu}

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
| | VPP Add Bond Member
| | ... | ${nodes['${dut}']} | ${${dut}_${int}1_1} | ${if_index}
| | VPP Add Bond Member
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
| | | ${_dot1q}= | Initialize layer dot1q on node on PF for chain
| | | ... | dut=${dut} | pf=${pf} | id=${id} | vlan_per_chain=${vlan_per_chain}
| | | # First id results in non-None indices, after that _1_ are defined.
| | | ${_dot1q}= | Set Variable If | '${_dot1q}' == '${NONE}'
| | | ... | ${${dut}_dot1q${pf}_1}[0] | ${_dot1q}
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
| | ... | ${NONE}
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
| | | ${_prev_mac}=
| | | ... | Set Variable If | '${dut}' == 'DUT1'
| | | ... | ${TG_pf1_mac}[0] | ${DUT1_pf2_mac}[0]
| | | ${_next_mac}=
| | | ... | Set Variable If | '${dut}' == 'DUT1' and ${duts_count} == 2
| | | ... | ${DUT2_pf1_mac}[0] | ${TG_pf2_mac}[0]
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
| | ... | - ${virtio_feature_mask} - Enabled Virtio feature flags (Optional).
| | ... | Type: integer
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
| | ... | ${virtio_feature_mask}=${None}
| |
| | ${vhost_1}= | Vpp Create Vhost User Interface
| | ... | ${dut_node} | ${sock1} | is_server=${is_server}
| | ... | virtio_feature_mask=${virtio_feature_mask}
| | ${vhost_2}= | Vpp Create Vhost User Interface
| | ... | ${dut_node} | ${sock2} | is_server=${is_server}
| | ... | virtio_feature_mask=${virtio_feature_mask}
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

| Lower DUT1-DUT2 MTU For Fragmentation
| | [Documentation] | Set lower MTU on both ends of DUT1-DUT2 link.
| |
| | ... | This should force VPP to fragment (and reassembly) packets.
| | ... | Should be called after Initialize Layer Interface.
| | ... | Suite variables such as \${dut2_if1} should be defined by then.
| |
| | ... | As VPP (at least dpdk plugin) require interface to be down
| | ... | before MTU can be changed, interfaces are temporarily downed.
| |
| | # TODO: ip_reassembly_set to increase max_reassembly_length so jumbo passes.
| | Set Interface State | ${nodes['DUT1']} | ${dut1_if2} | down
| | Set Interface State | ${nodes['DUT2']} | ${dut2_if1} | down
| | VPP Set Interface MTU
| | ... | ${nodes['DUT1']} | ${dut1_if2} | ${MTU_FOR_FRAGMENTATION}
| | VPP Set Interface MTU
| | ... | ${nodes['DUT2']} | ${dut2_if1} | ${MTU_FOR_FRAGMENTATION}
| | Set Interface State | ${nodes['DUT1']} | ${dut1_if2} | up
| | Set Interface State | ${nodes['DUT2']} | ${dut2_if1} | up
