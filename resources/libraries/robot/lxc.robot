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
| | ... | - lxc_name - Container name. Type: string
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create LXC container on DUT node \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node} | ${lxc_name}
| | ...
| | Import Library | resources.libraries.python.LXCUtils
| | ... | container_name=${lxc_name} | WITH NAME | ${lxc_name}
| | Run keyword | ${lxc_name}.LXC Set Node | ${dut_node}
| | Run keyword | ${lxc_name}.LXC Is Created
| | Run keyword | ${lxc_name}.LXC Host Dir Is Mounted
| | Run keyword | ${lxc_name}.LXC Is Running

| Create '${nr}' LXC containers on all DUT nodes in a 2-node circular topology
| | [Documentation] | Create and start multiple lxc containers on all DUT nodes in
| | ... | in a 2-node circular topology.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - lxc_name - Container base name. Type: string
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC container on all DUT nodes \| slave \|
| | ...
| | [Arguments] | ${lxc_name}
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | Create LXC container on DUT node | ${dut1} | DUT1_${lxc_name}_${number}
| | | Set To Dictionary | ${dut1_lxc_refs} | DUT1_VM${number}

| Create '${nr}' LXC containers on all DUT nodes in a 3-node circular topology
| | [Documentation] | Create and start multiple lxc containers on all DUT nodes
| | ... | in a 3-node circular topology.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - lxc_name - Container base name. Type: string
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create 5 LXC containers on all DUT nodes in a 3-node circular \
| | ... | topology \| slave \|
| | ...
| | [Arguments] | ${lxc_name}
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | Create LXC container on DUT node | ${dut1} | DUT1_${lxc_name}_${number}
| | | Set To Dictionary | ${dut1_lxc_refs} | DUT1_${lxc_name}_${number}
| | | Create LXC container on DUT node | ${dut2} | DUT2_${lxc_name}_${number}
| | | Set To Dictionary | ${dut2_lxc_refs} | DUT2_${lxc_name}_${number}

