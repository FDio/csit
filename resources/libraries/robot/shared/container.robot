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
| Documentation | Keywords related to linux containers
|
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.topology.Topology
| Variables | resources/libraries/python/Constants.py

*** Keywords ***
| Construct container on all DUTs
| | [Documentation] | Construct 1 CNF of specific technology on all DUT nodes.
| |
| | ... | *Arguments:*
| | ... | - nf_chains: Total number of chains (Optional). Type: integer, default
| | ... | value: ${1}
| | ... | - nf_nodes: Total number of nodes per chain (Optional). Type: integer,
| | ... | default value: ${1}
| | ... | - nf_chain: Chain ID (Optional). Type: integer, default value: ${1}
| | ... | - nf_node: Node ID (Optional). Type: integer, default value: ${1}
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... | network function as DUT, otherwise use single physical core for
| | ... | every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... | containers. Type: boolean, default value: ${False}
| |
| | ... | *Example:*
| |
| | ... | \| Construct container on all DUTs \| 1 \| 1 \| 1 \| 1 \| ${True} \|
| |
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${nf_chain}=${1}
| | ... | ${nf_node}=${1} | ${auto_scale}=${True} | ${pinning}=${True}
| |
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | Construct container on DUT | ${dut}
| | | ... | ${nf_chains} | ${nf_nodes} | ${nf_chain}
| | | ... | ${nf_node} | ${auto_scale} | ${pinning}
| | END

| Construct container on DUT
| | [Documentation] | Construct 1 CNF of specific technology on specific DUT.
| |
| | ... | *Arguments:*
| | ... | - dut: DUT node to construct the CNF on. Type: string
| | ... | - nf_chains: Total number of chains (Optional). Type: integer, default
| | ... | value: ${1}
| | ... | - nf_nodes: Total number of nodes per chain (Optional). Type: integer,
| | ... | default value: ${1}
| | ... | - nf_chain: Chain ID (Optional). Type: integer, default value: ${1}
| | ... | - nf_node: Node ID (Optional). Type: integer, default value: ${1}
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... | network function as DUT, otherwise use single physical core for
| | ... | every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... | containers. Type: boolean, default value: ${False}
| |
| | ... | *Example:*
| |
| | ... | \| Construct container on DUT \| DUT1 \| 1 \| 1 \| 1 \| 1 \|
| | ... | \| ${True} \|
| |
| | [Arguments] | ${dut}
| | ... | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${nf_chain}=${1}
| | ... | ${nf_node}=${1} | ${auto_scale}=${True} | ${pinning}=${True}
| |
| | ${nf_dtcr_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${nf_dtcr}
| | ${nf_dtcr}= | Run Keyword If | '${nf_dtcr_status}' == 'PASS'
| | ... | Set Variable | ${nf_dtcr} | ELSE | Set Variable | ${1}
| | ${nf_dtc}= | Run Keyword If | ${pinning}
| | ... | Set Variable If | ${auto_scale} | ${cpu_count_int}
| | ... | ${nf_dtc}
| | ${nf_id}= | Evaluate | (${nf_chain} - ${1}) * ${nf_nodes} + ${nf_node}
| | ${env}= | Create List | DEBIAN_FRONTEND=noninteractive
| | ${in_container}= | Running in Container | ${nodes['${dut}']}
| | ${root}= | Run Keyword If | ${in_container}
| | ... | Get Docker Mergeddir | ${nodes['${dut}']}
| | ... | ELSE | Set Variable | ${EMPTY}
| | ${node_arch}= | Get Node Arch | ${nodes['${dut}']}
| | ${name}= | Set Variable | ${dut}_${container_group}${nf_id}${DUT1_UUID}
| | ${mnt}= | Create List
| | ... | ${root}/tmp/:/mnt/host/
| | ... | ${root}/tmp/vpp_sockets/${name}/:/run/vpp/
| | ... | ${root}/dev/vfio/:/dev/vfio/
| | ... | ${root}/usr/bin/vpp:/usr/bin/vpp
| | ... | ${root}/usr/bin/vppctl:/usr/bin/vppctl
| | ... | ${root}/usr/lib/${node_arch}-linux-gnu/:/usr/lib/${node_arch}-linux-gnu/
| | ... | ${root}/usr/share/vpp/:/usr/share/vpp/
| | ${nf_cpus}= | Set Variable | ${None}
| | ${nf_cpus}= | Run Keyword If | ${pinning}
| | ... | Get Affinity NF | ${nodes} | ${dut}
| | ... | nf_chains=${nf_chains} | nf_nodes=${nf_nodes}
| | ... | nf_chain=${nf_chain} | nf_node=${nf_node}
| | ... | vs_dtc=${cpu_count_int} | nf_dtc=${nf_dtc} | nf_dtcr=${nf_dtcr}
| | &{cont_args}= | Create Dictionary
| | ... | name=${name} | node=${nodes['${dut}']} | mnt=${mnt} | env=${env}
| | ... | root=${root} | page_size=${page_size}
| | Run Keyword If | ${pinning}
| | ... | Set To Dictionary | ${cont_args} | cpuset_cpus=${nf_cpus}
| | Run Keyword | ${container_group}.Construct container | &{cont_args}

| Construct chain of containers
| | [Documentation] | Construct 1 chain of 1..N CNFs on selected/all DUT nodes.
| |
| | ... | *Arguments:*
| | ... | - dut: DUT node to start the containers on. Run on all nodes if None.
| | ... | Type: string or None
| | ... | - nf_chains: Total number of chains. Type: integer
| | ... | - nf_nodes: Total number of nodes per chain. Type: integer
| | ... | - nf_chain: Chain ID. Type: integer
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... | network function as DUT, otherwise use single physical core for
| | ... | every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... | containers. Type: boolean, default value: ${False}
| |
| | ... | *Example:*
| |
| | ... | \| Construct chain of containers \| 1 \| 1 \| 1 \| ${True} \|
| |
| | [Arguments] | ${dut}=${None} | ${nf_chains}=${1} | ${nf_nodes}=${1}
| | ... | ${nf_chain}=${1} | ${auto_scale}=${True} | ${pinning}=${True}
| |
| | FOR | ${nf_node} | IN RANGE | 1 | ${nf_nodes}+1
| | | Run Keyword If | '${dut}' == '${None}'
| | | ... | Construct container on all DUTs
| | | ... | nf_chains=${nf_chains} | nf_nodes=${nf_nodes} | nf_chain=${nf_chain}
| | | ... | nf_node=${nf_node} | auto_scale=${auto_scale} | pinning=${pinning}
| | | ... | ELSE
| | | ... | Construct container on DUT | ${dut}
| | | ... | nf_chains=${nf_chains} | nf_nodes=${nf_nodes} | nf_chain=${nf_chain}
| | | ... | nf_node=${nf_node} | auto_scale=${auto_scale} | pinning=${pinning}
| | END

| Construct chains of containers
| | [Documentation] | Construct 1..N chains of 1..N CNFs on selected/all DUT
| | ... | nodes.
| |
| | ... | *Arguments:*
| | ... | - dut: DUT node to start the containers on. Run on all nodes if None.
| | ... | Type: string or None
| | ... | - nf_chains: Total number of chains (Optional). Type: integer, default
| | ... | value: ${1}
| | ... | - nf_nodes: Total number of nodes per chain (Optional). Type: integer,
| | ... | default value: ${1}
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... | network function as DUT, otherwise use single physical core for
| | ... | every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... | containers. Type: boolean, default value: ${True}
| |
| | ... | *Example:*
| |
| | ... | \| Construct chains of containers \| 1 \| 1 \|
| |
| | [Arguments] | ${dut}=${None} | ${nf_chains}=${1} | ${nf_nodes}=${1}
| | ... | ${auto_scale}=${True} | ${pinning}=${True}
| |
| | FOR | ${nf_chain} | IN RANGE | 1 | ${nf_chains}+1
| | | Construct chain of containers
| | | ... | dut=${dut} | nf_chains=${nf_chains} | nf_nodes=${nf_nodes}
| | | ... | nf_chain=${nf_chain} | auto_scale=${auto_scale} | pinning=${pinning}
| | END

| Acquire all '${group}' containers
| | [Documentation] | Acquire all container(s) in specific container group on
| | ... | all DUT nodes.
| |
| | Run Keyword | ${group}.Acquire all containers

| Create all '${group}' containers
| | [Documentation] | Create/deploy all container(s) in specific container group
| | ... | on all DUT nodes.
| |
| | Run Keyword | ${group}.Create all containers

| Start VPP in all '${group}' containers
| | [Documentation] | Start VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| |
| | Run Keyword | ${group}.Start VPP In All Containers

| Restart VPP in all '${group}' containers
| | [Documentation] | Restart VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| |
| | Run Keyword | ${group}.Restart VPP In All Containers

| Configure VPP in all '${group}' containers
| | [Documentation] | Configure VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - container_chain_topology - Topology type used for configuring CNF
| | ... | (VPP) in container. Type: string
| |
| | ${dut1_if2} = | Get Variable Value | \${dut1_if2} | ${None}
| | ${dut2_if2} = | Get Variable Value | \${dut2_if2} | ${None}
| | Run Keyword If | '${container_chain_topology}' == 'chain_ip4'
| | ... | ${group}.Configure VPP In All Containers
| | ... | ${container_chain_topology}
| | ... | tg_pf1_mac=${TG_pf1_mac}[0]
| | ... | tg_pf2_mac=${TG_pf2_mac}[0]
| | ... | nodes=${nf_nodes}
| | ... | ELSE IF | '${container_chain_topology}' == 'chain_ipsec'
| | ... | ${group}.Configure VPP In All Containers
| | ... | ${container_chain_topology}
| | ... | tg_pf1_ip4=${tg_if1_ip4}
| | ... | tg_pf1_mac=${TG_pf1_mac}[0]
| | ... | tg_pf2_ip4=${tg_if2_ip4}
| | ... | tg_pf2_mac=${TG_pf2_mac}[0]
| | ... | dut1_if1_ip4=${dut1_if1_ip4}
| | ... | dut1_if2_ip4=${dut1_if2_ip4}
| | ... | dut2_if1_ip4=${dut2_if1_ip4}
| | ... | dut2_if2_ip4=${dut2_if2_ip4}
| | ... | raddr_ip4=${raddr_ip4}
| | ... | laddr_ip4=${laddr_ip4}
| | ... | nodes=${nodes}
| | ... | nf_nodes=${nf_nodes}
| | ... | ELSE IF | '${container_chain_topology}' == 'pipeline_ip4'
| | ... | ${group}.Configure VPP In All Containers
| | ... | ${container_chain_topology}
| | ... | tg_pf1_mac=${TG_pf1_mac}[0]
| | ... | tg_pf2_mac=${TG_pf2_mac}[0]
| | ... | nodes=${nf_nodes}
| | ... | ELSE IF | '${container_chain_topology}' == 'cross_horiz'
| | ... | ${group}.Configure VPP In All Containers
| | ... | ${container_chain_topology}
| | ... | dut1_if=${DUT1_${int}2}[0]
| | ... | dut2_if=${DUT2_${int}2}[0]
| | ... | ELSE IF | '${container_chain_topology}' == 'chain_dma'
| | ... | ${group}.Configure VPP In All Containers
| | ... | ${container_chain_topology}
| | ... | dma_wqs=${DUT1_dma_wqs}
| | ... | ELSE
| | ... | ${group}.Configure VPP In All Containers
| | ... | ${container_chain_topology}

| Stop all '${group}' containers
| | [Documentation] | Stop all container(s) in specific container group on all
| | ... | DUT nodes.
| |
| | Run Keyword | ${group}.Stop all containers

| Destroy all '${group}' containers
| | [Documentation] | Destroy all container(s) in specific container group on
| | ... | all DUT nodes.
| |
| | Run Keyword | ${group}.Destroy all containers

| Verify VPP in all '${group}' containers
| | [Documentation] | Verify that VPP is running inside containers in specific
| | ... | container group on all DUT nodes. Does 120 retries with one second
| | ... | between retries.
| |
| | Run Keyword | ${group}.Verify VPP in all containers

| Start containers for test
| | [Documentation]
| | ... | Start containers for test.
| |
| | ... | *Arguments:*
| | ... | - dut: DUT node to start the containers on. Run on all nodes if None.
| | ... | Type: string or None
| | ... | - nf_chains: Total number of chains. Type: integer
| | ... | - nf_nodes: Total number of nodes per chain. Type: integer
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... | network function as DUT, otherwise use single physical core for
| | ... | every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... | containers. Type: boolean, default value: ${False}
| |
| | ... | *Example:*
| |
| | ... | \| Start containers for test \| 1 \| 1 \|
| |
| | [Arguments] | ${dut}=${None} | ${nf_chains}=${1} | ${nf_nodes}=${1}
| | ... | ${auto_scale}=${True} | ${pinning}=${True}
| |
| | Set Test Variable | @{container_groups} | @{EMPTY}
| | Set Test Variable | ${container_group} | CNF
| | Set Test Variable | ${nf_nodes}
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=${container_engine} | WITH NAME | ${container_group}
| | Construct chains of containers
| | ... | dut=${dut} | nf_chains=${nf_chains} | nf_nodes=${nf_nodes}
| | ... | auto_scale=${auto_scale} | pinning=${pinning}
| | Acquire all '${container_group}' containers
| | Create all '${container_group}' containers
| | Configure VPP in all '${container_group}' containers
| | Start VPP in all '${container_group}' containers
| | Append To List | ${container_groups} | ${container_group}
| | Save VPP PIDs

# TODO: Remove the vswitch startup.conf and read the host configuration instead.
| Start vswitch in container on DUT
| | [Documentation]
| | ... | Configure and start vswitch in container.
| |
| | ... | *Arguments:*
| | ... | - dut: DUT node on which to install vswitch. Type: string
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues: Number of RX queues. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Start vswitch in container on DUT \| DUT1 \| 1 \| 1 \|
| |
| | [Arguments] | ${dut} | ${phy_cores} | ${rx_queues}=${None}
| |
| | Set Test Variable | ${container_group} | VSWITCH
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=${container_engine} | WITH NAME | VSWITCH
| | Construct container on DUT | ${dut}
| | ... | nf_chains=${1} | nf_nodes=${1} | nf_chain=${1}
| | ... | nf_node=${1} | auto_scale=${False} | pinning=${False}
| | Acquire all '${container_group}' containers
| | Create all '${container_group}' containers
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_count_int} | Convert to Integer | ${phy_cores}
| | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | ${dp_count_int}= | Run keyword if | ${smt_used}
| | ... | Evaluate | int(${cpu_count_int}*2)
| | ... | ELSE | Set variable | ${dp_count_int}
| | ${rxq_ratio} = | Get Variable Value | \${rxq_ratio} | ${1}
| | ${rxq_count_int}= | Run Keyword If | ${rx_queues}
| | ... | Set variable | ${rx_queues}
| | ... | ELSE | Evaluate | int(${dp_count_int}/${rxq_ratio})
| | ${rxq_count_int}= | Run keyword if | ${rxq_count_int} == 0
| | ... | Set variable | ${1}
| | ... | ELSE | Set variable | ${rxq_count_int}
| | VSWITCH.Configure VPP in all containers | chain_vswitch
| | ... | rxq=${rxq_count_int} | n_instances=${n_instances} | node=${dut}
| | ... | dut1_if1=${DUT1_${int}1}[0] | dut1_if2=${DUT1_${int}2}[0]
| | ... | dut2_if1=${DUT2_${int}1}[0] | dut2_if2=${DUT2_${int}2}[0]
| | ... | dut2_if2_ip4=${dut2_if2_ip4}
| | ... | tg_pf1_ip4=${tg_if1_ip4} | tg_pf1_mac=${TG_pf1_mac}[0]
| | ... | tg_pf2_ip4=${tgi_f2_ip4} | tg_pf2_mac=${TG_pf2_mac}[0]
| | ... | nodes=${nodes}
| | Start VPP in all '${container_group}' containers

| Start vswitch in container
| | [Documentation]
| | ... | Configure and start vswitch in container on all DUTs.
| |
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues: Number of RX queues. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Start vswitch in container \| 1 \| 1 \|
| |
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | Start vswitch in container on DUT
| | | ... | ${dut} | ${phy_cores} | ${rx_queues}
| | END
| | Append To List | ${container_groups} | ${container_group}
| | Save VPP PIDs

| Start vswitch containers
| | [Documentation]
| | ... | Configure and start multiple vswitch in container on all DUTs.
| |
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues: Number of RX queues. Type: integer
| |
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None}
| |
| | Set Test Variable | @{container_groups} | @{EMPTY}
| | Set Test Variable | ${container_group} | VSWITCH
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=${container_engine} | WITH NAME | VSWITCH
| | Stop VPP service on all DUTs | ${nodes}
| | FOR | ${dut} | IN | @{duts}
| | | FOR | ${i} | IN RANGE | 1 | ${${nic_pfs}//${2}+1}
| | | | Construct container on DUT | ${dut}
| | | | ... | nf_chains=${1} | nf_nodes=${${nic_pfs}//${2}}
| | | | ... | nf_chain=${1} | nf_node=${i}
| | | | ... | auto_scale=${False} | pinning=${False}
| | | END
| | END
| | Run Keyword | VSWITCH.Acquire all containers
| | Run Keyword | VSWITCH.Create all containers
| | Run Keyword | VSWITCH.Configure vpp in all containers
| | ... | vswitch_ip4scale | nodes=${nodes} | rts_per_flow=${rts_per_flow}
| | Run Keyword | VSWITCH.Start VPP In All Containers
| | Append To List | ${container_groups} | VSWITCH
| | Save VPP PIDs
