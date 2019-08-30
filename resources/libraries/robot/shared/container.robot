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
| Documentation | Keywords related to linux containers
| ...
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.topology.Topology

*** Keywords ***
| Construct container on all DUTs
| | [Documentation] | Construct 1 CNF of specific technology on all DUT nodes.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chains: Total number of chains (Optional). Type: integer, default
| | ... | value: ${1}
| | ... | - nf_nodes: Total number of nodes per chain (Optional). Type: integer,
| | ... | default value: ${1}
| | ... | - nf_chain: Chain ID (Optional). Type: integer, default value: ${1}
| | ... | - nf_node: Node ID (Optional). Type: integer, default value: ${1}
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... |   network function as DUT, otherwise use single physical core for
| | ... |   every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... |   containers. Type: boolean, default value: ${False}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Construct container on all DUTs \| 1 \| 1 \| 1 \| 1 \| ${True} \|
| | ...
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${nf_chain}=${1}
| | ... | ${nf_node}=${1} | ${auto_scale}=${True} | ${pinning}=${True}
| | ...
| | ${nf_dtcr_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${nf_dtcr}
| | ${nf_dtcr}= | Run Keyword If | '${nf_dtcr_status}' == 'PASS'
| | ... | Set Variable | ${nf_dtcr} | ELSE | Set Variable | ${1}
| | ${nf_dtc}= | Run Keyword If | ${pinning}
| | ... | Set Variable If | ${auto_scale} | ${cpu_count_int}
| | ... | ${nf_dtc}
| | ${nf_id}= | Evaluate | (${nf_chain} - ${1}) * ${nf_nodes} + ${nf_node}
| | ${env}= | Create List | DEBIAN_FRONTEND=noninteractive
| | ${dut1_uuid_length} = | Get Length | ${dut1_uuid}
| | ${root}= | Run Keyword If | ${dut1_uuid_length}
| | ... | Get Docker Mergeddir | ${nodes['DUT1']} | ${dut1_uuid}
| | ... | ELSE | Set Variable | ${EMPTY}
| | ${node_arch}= | Get Node Arch | ${nodes['${dut}']}
| | ${name}= | Set Variable | ${dut}_${container_group}${nf_id}${dut1_uuid}
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
| | Run Keyword If | ${pinning}
| | ... | Set To Dictionary | ${cont_args} | cpuset_cpus=${nf_cpus}
| | Run Keyword | ${container_group}.Construct container | &{cont_args}
| | Add New Socket
| | ... | ${nodes['${dut}']} | PAPI | ${name}
| | ... | ${root}/tmp/vpp_sockets/${name}/api.sock

| Construct chain of containers
| | [Documentation] | Construct 1 chain of 1..N CNFs on selected/all DUT nodes.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chains: Total number of chains. Type: integer
| | ... | - nf_nodes: Total number of nodes per chain. Type: integer
| | ... | - nf_chain: Chain ID. Type: integer
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... |   network function as DUT, otherwise use single physical core for
| | ... |   every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... |   containers. Type: boolean, default value: ${False}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Construct chain of containers on all DUTs \| 1 \| 1 \| 1 \
| | ... | \| ${True} \|
| | ...
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${nf_chain}=${1}
| | ... | ${auto_scale}=${True} | ${pinning}=${True}
| | ...
| | :FOR | ${nf_node} | IN RANGE | 1 | ${nf_nodes}+1
| | | Construct container on all DUTs | nf_chains=${nf_chains}
| | | ... | nf_nodes=${nf_nodes} | nf_chain=${nf_chain} | nf_node=${nf_node}
| | | ... | auto_scale=${auto_scale} | pinning=${pinning}

| Construct chains of containers on all DUTs
| | [Documentation] | Construct 1..N chains of 1..N CNFs on all DUT nodes.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chains: Total number of chains (Optional). Type: integer, default
| | ... |   value: ${1}
| | ... | - nf_nodes: Total number of nodes per chain (Optional). Type: integer,
| | ... |   default value: ${1}
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... |   network function as DUT, otherwise use single physical core for
| | ... |   every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... |   containers. Type: boolean, default value: ${True}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Construct chains of containers on all DUTs \| 1 \| 1 \|
| | ...
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${auto_scale}=${True}
| | ... | ${pinning}=${True}
| | ...
| | :FOR | ${nf_chain} | IN RANGE | 1 | ${nf_chains}+1
| | | Construct chain of containers on all DUTs | nf_chains=${nf_chains}
| | | ... | nf_nodes=${nf_nodes} | nf_chain=${nf_chain}
| | | ... | auto_scale=${auto_scale} | pinning=${pinning}

| Acquire all '${group}' containers
| | [Documentation] | Acquire all container(s) in specific container group on
| | ... | all DUT nodes.
| | ...
| | Run Keyword | ${group}.Acquire all containers

| Create all '${group}' containers
| | [Documentation] | Create/deploy all container(s) in specific container group
| | ... | on all DUT nodes.
| | ...
| | Run Keyword | ${group}.Create all containers

| Start VPP in all '${group}' containers
| | [Documentation] | Start VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| | ...
| | Run Keyword | ${group}.Start VPP In All Containers

| Restart VPP in all '${group}' containers
| | [Documentation] | Restart VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| | ...
| | Run Keyword | ${group}.Restart VPP In All Containers

| Configure VPP in all '${group}' containers
| | [Documentation] | Configure VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| | ...
| | ${dut1_if2} = | Get Variable Value | \${dut1_if2} | ${None}
| | ${dut2_if2} = | Get Variable Value | \${dut2_if2} | ${None}
| | Run Keyword If | '${container_chain_topology}' == 'chain_ip4'
| | ... | ${group}.Configure VPP In All Containers | ${container_chain_topology}
| | ... | tg_if1_mac=${tg_if1_mac} | tg_if2_mac=${tg_if2_mac}
| | ... | nodes=${nf_nodes}
| | ... | ELSE IF | '${container_chain_topology}' == 'pipeline_ip4'
| | ... | ${group}.Configure VPP In All Containers | ${container_chain_topology}
| | ... | tg_if1_mac=${tg_if1_mac} | tg_if2_mac=${tg_if2_mac}
| | ... | nodes=${nf_nodes}
| | ... | ELSE IF | '${container_chain_topology}' == 'cross_horiz'
| | ... | ${group}.Configure VPP In All Containers | ${container_chain_topology}
| | ... | dut1_if=${dut1_if2} | dut2_if=${dut2_if2}
| | ... | ELSE
| | ... | ${group}.Configure VPP In All Containers | ${container_chain_topology}

| Stop all '${group}' containers
| | [Documentation] | Stop all container(s) in specific container group on all
| | ... | DUT nodes.
| | ...
| | Run Keyword | ${group}.Stop all containers

| Destroy all '${group}' containers
| | [Documentation] | Destroy all container(s) in specific container group on
| | ... | all DUT nodes.
| | ...
| | Run Keyword | ${group}.Destroy all containers

| Start containers for test
| | [Documentation]
| | ... | Start containers for test.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chains: Total number of chains. Type: integer
| | ... | - nf_nodes: Total number of nodes per chain. Type: integer
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... |   network function as DUT, otherwise use single physical core for
| | ... |   every network function. Type: boolean
| | ... | - pinning: Set True if CPU pinning should be done on starting
| | ... |   containers. Type: boolean, default value: ${False}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Start containers for test \| 1 \| 1 \|
| | ...
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${auto_scale}=${True}
| | ... | ${pinning}=${True}
| | ...
| | Set Test Variable | @{container_groups} | @{EMPTY}
| | Set Test Variable | ${container_group} | CNF
| | Set Test Variable | ${nf_nodes}
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=${container_engine} | WITH NAME | ${container_group}
| | Construct chains of containers on all DUTs | ${nf_chains} | ${nf_nodes}
| | ... | auto_scale=${auto_scale} | pinning=${pinning}
| | Acquire all '${container_group}' containers
| | Create all '${container_group}' containers
| | Configure VPP in all '${container_group}' containers
| | Start VPP in all '${container_group}' containers
| | Append To List | ${container_groups} | ${container_group}
| | Save VPP PIDs
