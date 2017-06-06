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
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create LXC container on DUT node \| ${nodes['DUT1']}
| | ...
| | [Arguments] | ${dut_node}
| | ...
| | Import Library | resources.libraries.python.LXCUtils
| | ... | container_name=${lxc_name} | WITH NAME | ${lxc_name}
| | Run keyword | ${lxc_name}.LXC Set Node | ${dut_node}
| | Run keyword | ${lxc_name}.LXC Is Created
| | Run keyword | ${lxc_name}.LXC Host Dir Is Mounted
| | Run keyword | ${lxc_name}.LXC Is Running

| Create LXC container on DUT node with cpuset
| | [Documentation] | Setup lxc container on DUT node with cpuset.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - skip - number of cpus which will be skipped. Type: int
| | ... | - count - number of cpus which will be allocated for lxc. Type: int
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create LXC container on DUT node with cpuset \
| | ... | \| ${nodes['DUT1']} \| 6 \| 1
| | ...
| | [Arguments] | ${dut_node} | ${skip}=${6} | ${count}=${1}
| | ...
| | Import Library | resources.libraries.python.LXCUtils
| | ... | container_name=${lxc_name} | WITH NAME | ${lxc_name}
| | ${dut_numa}= | Get interfaces numa node | ${dut_node}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${lxc_cpus}= | Cpu slice of list per node | ${dut_node} | ${dut_numa}
| | ... | skip_cnt=${skip} | cpu_cnt=${count} | smt_used=${False}
| | Run keyword | ${lxc_name}.LXC Set Node | ${dut_node}
| | Run keyword | ${lxc_name}.LXC Is Created
| | Run keyword | ${lxc_name}.LXC Host Dir Is Mounted
| | Run keyword | ${lxc_name}.LXC Is Running
| | Run keyword | ${lxc_name}.LXC Cpuset Cpus | ${lxc_cpus}

| Create '${nr}' LXC containers on '${dut}' node
| | [Documentation] | Create and start multiple lxc containers on DUT node.
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on DUT1 node
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | Create LXC container on DUT node | ${nodes['${dut}']}
| | | ... | ${dut}_${lxc_name}_${number}

| Create '${nr}' LXC containers on all DUT nodes
| | [Documentation] | Create and start multiple lxc containers on all DUT nodes.
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on all DUT nodes
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Create '${nr}' LXC container on '${dut}' node

| Create '${nr}' LXC containers on '${dut}' node with '${count}' cpus
| | [Documentation] | Create and start multiple lxc containers on DUT node.
| | ... | Set the cpuset.cpus cgroup profile for pin of cpus.
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on all DUT nodes with 2 cpus
| | ...
| | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${skip}= | Evaluate | ${skip_cpus} + (${nr} - 1) * ${count}
| | | Create LXC container on DUT node with cpuset | ${nodes['${dut}']}
| | | ... | ${dut}_${lxc_name}_${number} | ${skip} | ${count}


| Create '${nr}' LXC containers on all DUT nodes with '${count}' cpus
| | [Documentation] | Create and start multiple lxc containers on all DUT nodes.
| | ... | Set the cpuset.cpus cgroup profile for pin of cpus.
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on all DUT nodes with 2 cpus
| | ...
| | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Create '${nr}' LXC container on '${dut}' node with '${count}' cpus

| Destroy all LXC containers on '${dut}' node
| | [Documentation] | Stop and destroy all lxc containers on DUT node.
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Destroy all LXC containers on all DUT nodes
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${dut}_${lxc_name}_${number}.LXC Is Destroyed

| Destroy all LXC containers on all DUT nodes
| | [Documentation] | Stop and destroy all lxc containers on all DUT nodes.
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Destroy all LXC containers on all DUT nodes
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Destroy all LXC containers on '${dut}' node

| Install VPP on all LXC containers on '${dut}' node
| | [Documentation] | Install vpp on all lxc containers on DUT node.
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Install VPP on all LXC containers on all DUT nodes
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${dut}_${lxc_name}_${number}.LXC VPP Is Installed

| Install VPP on all LXC containers on all DUT nodes
| | [Documentation] | Install vpp on all lxc containers on all DUT nodes.
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Install VPP on all LXC containers on all DUT nodes
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Install VPP on all LXC containers on '${dut}' node
