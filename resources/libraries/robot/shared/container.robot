# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.topology.Topology

*** Keywords ***
| Construct container on all DUTs
| | [Documentation] | Construct 1 CNF of specific technology on all DUT nodes.
| | ...
| | ... | *Arguments:*
| | ... | - chains: Total number of chains. Type: integer
| | ... | - nodeness: Total number of nodes per chain. Type: integer
| | ... | - chain_id: Chain ID. Type: integer
| | ... | - node_id: Node ID. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Construct container on all DUTs \| 1 \| 1 \| 1 \| 1 \|
| | ...
| | [Arguments] | ${chains}=${1} | ${nodeness}=${1} | ${chain_id}=${1}
| | ... | ${node_id}=${1}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${nf_id}= | Evaluate | (${chain_id} - ${1}) * ${nodeness} + ${node_id}
| | | ${env}= | Create List | DEBIAN_FRONTEND=noninteractive
| | | ${mnt}= | Create List | /tmp:/mnt/host | /dev/vfio:/dev/vfio
| | | ${nf_cpus}= | Create network function CPU list | ${dut}
| | | ... | chains=${chains} | nodeness=${nodeness} | chain_id=${chain_id}
| | | ... | node_id=${node_id} | auto_scale=${True}
| | | Run Keyword | ${container_group}.Construct container
| | | ... | name=${dut}_${container_group}${nf_id}
| | | ... | node=${nodes['${dut}']} | mnt=${mnt} | env=${env}
| | | ... | cpuset_cpus=${nf_cpus}

| Construct chain of containers on all DUTs
| | [Documentation] | Construct 1 chain of 1..N CNFs on all DUT nodes.
| | ...
| | ... | *Arguments:*
| | ... | - chains: Total number of chains. Type: integer
| | ... | - nodeness: Total number of nodes per chain. Type: integer
| | ... | - chain_id: Chain ID. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Construct chain of containers on all DUTs \| 1 \| 1 \| 1 \|
| | ...
| | [Arguments] | ${chains} | ${nodeness} | ${chain_id}
| | ...
| | :FOR | ${node_id} | IN RANGE | 1 | ${nodeness}+1
| | | Construct container on all DUTs | chains=${chains} | nodeness=${nodeness}
| | | ... | chain_id=${chain_id} | node_id=${node_id}

| Construct chains of containers on all DUTs
| | [Documentation] | Construct 1..N chains of 1..N CNFs on all DUT nodes.
| | ...
| | ... | *Arguments:*
| | ... | - chains: Total number of chains. Type: integer
| | ... | - nodeness: Total number of nodes per chain. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Construct chains of containers on all DUTs \| 1 \| 1 \|
| | ...
| | [Arguments] | ${chains}=${1} | ${nodeness}=${1}
| | ...
| | :FOR | ${chain_id} | IN RANGE | 1 | ${chains}+1
| | | Construct chain of containers on all DUTs | chains=${chains}
| | | ... | nodeness=${nodeness} | chain_id=${chain_id}

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

| Install VPP in all '${group}' containers
| | [Documentation] | Install VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| | ...
| | Run Keyword | ${group}.Install VPP In All Containers

| Restart VPP in all '${group}' containers
| | [Documentation] | Restart VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| | ...
| | Run Keyword | ${group}.Restart VPP In All Containers

| Configure VPP in all '${group}' containers
| | [Documentation] | Configure VPP on all container(s) in specific container
| | ... | group on all DUT nodes.
| | ...
| | ${dut2_if2} = | Get Variable Value | \${dut2_if2} | ${EMPTY}
| | Run Keyword | ${group}.Configure VPP In All Containers
| | ... | chain_topology=${container_chain_topology}
| | ... | dut1_if=${dut1_if2} | dut2_if=${dut2_if2}

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
