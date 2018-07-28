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
| Construct VNF containers on all DUTs
| | [Documentation] | Construct 1..N VNF container(s) of specific technology on
| | ... |  all DUT nodes.
| | ...
| | ${group}= | Set Variable | VNF
| | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=${container_engine} | WITH NAME | ${group}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${env}= | Create List | DEBIAN_FRONTEND=noninteractive
| | | ${mnt}= | Create List | /tmp:/mnt/host | /dev/vfio:/dev/vfio
| | | ... | /dev/bus:/dev/bus
| | | ${cpu_node}= | Get interfaces numa node | ${nodes['${dut}']}
| | | ... | ${dut1_if1} | ${dut1_if2}
| | | Run Keyword | ${group}.Construct containers
| | | ... | name=${dut}_${group} | node=${nodes['${dut}']} | mnt=${mnt}
| | | ... | image=${container_image} | cpu_count=${container_cpus}
| | | ... | cpu_skip=${skip_cpus} | cpuset_mems=${cpu_node}
| | | ... | cpu_shared=${False} | env=${env} | count=${container_count}
| | | ... | install_dkms=${container_install_dkms}
| | Append To List | ${container_groups} | ${group}

| Construct ETCD containers on all DUTs
| | [Documentation] | Construct Docker ETCD container on all DUTs.
| | ...
| | ${group}= | Set Variable | ETCD
| | ${command}= | Set Variable
| | ... | /usr/local/bin/etcd -advertise-client-urls http://0.0.0.0:2379 -listen-client-urls http://0.0.0.0:2379
| | ${image}= | Set Variable | quay.io/coreos/etcd:v3.2.5
| | ${publish}= | Create List | 2379:2379
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=Docker | WITH NAME | ${group}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${cpu_node}= | Get interfaces numa node | ${nodes['${dut}']}
| | | ... | ${dut1_if1} | ${dut1_if2}
| | | Run Keyword | ${group}.Construct container
| | | ... | name=${dut}_${group} | node=${nodes['${dut}']}
| | | ... | image=${container_image} | cpu_count=${1} | cpu_skip=${0}
| | | ... | cpuset_mems=${cpu_node} | cpu_shared=${True}
| | | ... | publish=${publish} | command=${command}
| | Append To List | ${container_groups} | ${group}

| Construct Kafka containers on all DUTs
| | [Documentation] | Construct Docker Kafka container on all DUTs.
| | ...
| | ${group}= | Set Variable | Kafka
| | ${image}= | Set Variable | spotify/kafka
| | ${publish}= | Create List | 2181:2181 | 9092:9092
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=Docker | WITH NAME | ${group}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${env}= | Create List | ADVERTISED_HOST=172.17.0.1 | ADVERTISED_PORT=9092
| | | ${cpu_node}= | Get interfaces numa node | ${nodes['${dut}']}
| | | ... | ${dut1_if1} | ${dut1_if2}
| | | Run Keyword | ${group}.Construct container
| | | ... | name=${dut}_${group} | node=${nodes['${dut}']} | image=${image}
| | | ... | cpu_count=${1} | cpu_skip=${0} | cpuset_mems=${cpu_node}
| | | ... | cpu_shared=${True} | publish=${publish} | env=${env}
| | Append To List | ${container_groups} | ${group}

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
| | Run Keyword | ${group}.Configure VPP In All Containers
| | ... | chain_topology=${container_chain_topology}
| | ... | dut1_if=${dut1_if2} | dut2_if=${dut2_if1}

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
