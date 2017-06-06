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
| Documentation | Keywords related to linux container (LXC)
| Library | resources.libraries.python.LXCUtils
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.topology.Topology

*** Keywords ***
| Create LXC container on DUT node
| | [Documentation] | Setup lxc container on DUT node.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lxc_name - Name of LXC container. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create LXC container on DUT node \| ${nodes['DUT1']} \
| | ... | \| DUT1_slave_1 \|
| | ...
| | [Arguments] | ${dut_node} | ${lxc_name}
| | ...
| | Import Library | resources.libraries.python.LXCUtils
| | ... | container_name=${lxc_name} | WITH NAME | ${lxc_name}
| | Run keyword | ${lxc_name}.Set node | ${dut_node}
| | Run keyword | ${lxc_name}.Create container | force_create=${TRUE}
| | Run keyword | ${lxc_name}.Mount host dir in container

| Create LXC container on DUT node with cpuset
| | [Documentation] | Create LXC container on DUT node with cpuset.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lxc_name - Name of LXC container. Type: dictionary
| | ... | - skip - number of cpus which will be skipped. Type: integer
| | ... | - count - number of cpus which will be allocated for lxc. Type:
| | ... | integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create LXC container on DUT node with cpuset \
| | ... | \| ${nodes['DUT1']} \| DUT1_slave_1 \| 6 \| 1 \|
| | ...
| | [Arguments] | ${dut_node} | ${lxc_name} | ${skip}=${6} | ${count}=${1}
| | ...
| | Import Library | resources.libraries.python.LXCUtils
| | ... | container_name=${lxc_name} | WITH NAME | ${lxc_name}
| | ${dut_numa}= | Get interfaces numa node | ${dut_node}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${lxc_cpus}= | CPU list per node str | ${dut_node} | ${dut_numa}
| | ... | skip_cnt=${skip} | cpu_cnt=${count} | smt_used=${False}
| | Run keyword | ${lxc_name}.Set node | ${dut_node}
| | Run keyword | ${lxc_name}.Create container | force_create=${TRUE}
| | Run keyword | ${lxc_name}.Mount host dir in container
| | Run keyword | ${lxc_name}.Container cpuset cpus | ${lxc_cpus}

| Create '${nr}' LXC containers on '${dut}' node
| | [Documentation] | Create and start multiple lxc containers on DUT node.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on DUT1 node \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | Create LXC container on DUT node | ${nodes['${dut}']}
| | | ... | ${dut}_${lxc_base_name}_${number}

| Create '${nr}' LXC containers on all DUT nodes
| | [Documentation] | Create and start multiple LXC containers on all DUT nodes.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on all DUT nodes \|
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Create '${nr}' LXC containers on '${dut}' node

| Create '${nr}' LXC containers on '${dut}' node with '${count}' cpus
| | [Documentation] | Create and start multiple LXC containers on DUT node.
| | ... | Set the cpuset.cpus cgroup profile for pin of cpus.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on DUT1 node with 2 cpus \|
| | ...
| | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
| | ${count_int}= | Convert To Integer | ${count}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${skip}= | Evaluate | ${skip_cpus} + (${nr} - 1) * ${count}
| | | Create LXC container on DUT node with cpuset | ${nodes['${dut}']}
| | | ... | ${dut}_${lxc_base_name}_${number} | ${skip} | ${count_int}

| Create '${nr}' LXC containers on all DUT nodes with '${count}' cpus
| | [Documentation] | Create and start multiple LXC containers on all DUT nodes.
| | ... | Set the cpuset.cpus cgroup profile for pin of cpus.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on all DUT nodes with 2 cpus \|
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Create '${nr}' LXC containers on '${dut}' node with '${count}' cpus

| Destroy LXC container on DUT node
| | [Documentation] | Stop and destroy LXC container on DUT node.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lxc_name - Name of LXC container. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Destroy LXC container on DUT node \| ${nodes['DUT1']} \
| | ... | \| DUT1_slave_1 \|
| | ...
| | [Arguments] | ${dut_node} | ${lxc_name}
| | ...
| | Import Library | resources.libraries.python.LXCUtils
| | ... | container_name=${lxc_name} | WITH NAME | ${lxc_name}
| | Run keyword | ${lxc_name}.Set node | ${dut_node}
| | Run keyword | ${lxc_name}.Destroy container

| Destroy '${nr}' LXC containers on '${dut}' node
| | [Documentation] | Stop and destroy multiple LXC containers on DUT node.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Destroy 5 LXC containers on DUT1 node \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | Destroy LXC container on DUT node | ${nodes['${dut}']}
| | | ... | ${dut}_${lxc_base_name}_${number}

| Destroy '${nr}' LXC containers on all DUT nodes
| | [Documentation] | Stop and destroy multiple LXC containers on all DUT nodes.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Destroy 5 LXC containers on all DUT nodes \|
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Destroy '${nr}' LXC containers on '${dut}' node

| Install VPP on LXC container on DUT node
| | [Documentation] | Install vpp on LXC container on DUT node.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lxc_name - Name of LXC container. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Install VPP on LXC container on DUT node \| ${nodes['DUT1']} \
| | ... | \| DUT1_slave_1 \|
| | ...
| | [Arguments] | ${dut_node} | ${lxc_name}
| | ...
| | Import Library | resources.libraries.python.LXCUtils
| | ... | container_name=${lxc_name} | WITH NAME | ${lxc_name}
| | Run keyword | ${lxc_name}.Set node | ${dut_node}
| | Run keyword | ${lxc_name}.Install VPP in container

| Install VPP on '${nr}' LXC containers on '${dut}' node
| | [Documentation] | Install VPP on multiple LXC containers on DUT node.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Install VPP on 5 LXC containers on DUT1 node \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | Install VPP on LXC container on DUT node | ${nodes['${dut}']}
| | | ... | ${dut}_${lxc_base_name}_${number}

| Install VPP on '${nr}' LXC containers on all DUT nodes
| | [Documentation] | Install VPP on multiple LXC containers on all DUT nodes.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Install VPP on 5 LXC containers on all DUT nodes \|
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Install VPP on '${nr}' LXC containers on '${dut}' node

| Create startup configuration of VPP on LXC container on DUT node
| | [Documentation] | Create base startup configuration of VPP on LXC container
| | ... | on DUT node.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lxc_name - Name of LXC container. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create startup configuration of VPP on LXC container on DUT node \
| | ... | \| ${nodes['DUT1']} \| DUT1_slave_1 \|
| | ...
| | [Arguments] | ${dut_node} | ${lxc_name}
| | ...
| | Import Library | resources.libraries.python.VppConfigGenerator
| | ... | WITH NAME | ${lxc_name}_conf
| | Run keyword | ${lxc_name}_conf.Set node | ${dut_node}
| | Run keyword | ${lxc_name}_conf.Add unix CLI listen
| | Run keyword | ${lxc_name}_conf.Add unix nodaemon
| | Run keyword | ${lxc_name}_conf.Add unix exec | "/tmp/running.exec"
| | Run keyword | ${lxc_name}_conf.Add plugin disable | "dpdk_plugin.so"
| | Run Keyword | ${lxc_name}_conf.Apply config LXC | ${lxc_name}

| Create startup configuration of VPP on '${nr}' LXC containers on '${dut}' node
| | [Documentation] | Create base startup configuration of VPP on multiple LXC
| | ... | container on DUT node.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create startup configuration of VPP on 1 LXC containers on DUT1 \
| | ... | node \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | Create startup configuration of VPP on LXC container on DUT node
| | | ... | ${nodes['${dut}']} | ${dut}_${lxc_base_name}_${number}

| Create startup configuration of VPP on '${nr}' LXC containers on all DUT nodes
| | [Documentation] | Create base startup configuration of VPP on multiple LXC
| | ... | container on all DUT nodes.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create startup configuration of VPP on 1 LXC containers on all \
| | ... | DUT nodes \|
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Create startup configuration of VPP on '${nr}' LXC containers on '${dut}' node
