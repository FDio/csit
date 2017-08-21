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
| Create VNF containers on all DUTs
| | [Documentation] | Create 1..N VNF container(s) of specific technology on
| | ... |  all DUT nodes.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - technology - DUT node. Type: string
| | ... | - image - Name of LXC container. Type: string
| | ... | - count - Name of LXC container. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create VNF containers on all DUTs \| Docker \| ubuntu \| 5 \|
| | ... | \| Create VNF containers on all DUTs \| LXC \
| | ... | \| "-d ubuntu -r xenial -a amd64" \| 5 \|
| | ...
| | [Arguments] | ${technology} | ${image} | ${cpu_cnt}=${1} | ${count}=${1}
| | ...
| | ${group_name}= | Set Variable | VNF
| | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=${technology} | WITH NAME | ${group_name}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${dut_numa}= | Get interfaces numa node | ${dut}
| | | ... | ${dut1_if1} | ${dut1_if2}
| | | Run Keyword | ${group_name}.Construct container | node=${dut}
| | | ... | name=${dut}_csit_vpp | image=${image} | cpu_cnt=${cpu_cnt}
| | | ... | skip_cnt=${skip_cpus} | numa=${dut_numa} | smt_used=${False}
| | | ... | cpu_shared=${True} | count=${count}

| Start all '${group}' containers
| | [Documentation] | Start all container(s) on all DUT
| | ... | nodes.
| | ...
| | Run Keyword | ${group}.Start all containers

| Stop all '${group}' containers
| | [Documentation] | Stop all container(s) on all DUT
| | ... | nodes.
| | ...
| | Run Keyword | ${group}.Start all containers
