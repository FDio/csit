# Copyright (c) 2016 Cisco and/or its affiliates.
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

*** Keywords ***
| Path for 2-node testing is set
| | [Documentation] | Compute path for bridge domain testing on two given nodes
| | ...             | and set corresponding test case variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${tg_node} - TG node. Type: dictionary
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${tg_node} - TG node again for better readability of a testcase.
| | ... |   Must be the same as a first parameter. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${tg_node} - TG node.
| | ... | - ${tg_to_dut_if1} - 1st TG interface towards DUT.
| | ... | - ${tg_to_dut_if2} - 2nd TG interface towards DUT.
| | ... | - ${dut_node} - DUT node.
| | ... | - ${dut_to_tg_if1} - 1st DUT interface towards TG.
| | ... | - ${dut_to_tg_if2} - 2nd DUT interface towards TG.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Given Path for 2-node testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['TG']} \|
| | ...
| | [Arguments] | ${tg_node} | ${dut_node} | ${tg_node}
| | Append Nodes | ${tg_node} | ${dut_node} | ${tg_node}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_to_dut_if1} | ${tmp}= | First Interface
| | ${tg_to_dut_if2} | ${tmp}= | Last Interface
| | ${dut_to_tg_if1} | ${tmp}= | First Ingress Interface
| | ${dut_to_tg_if2} | ${tmp}= | Last Egress Interface
| | Set Test Variable | ${tg_to_dut_if1}
| | Set Test Variable | ${tg_to_dut_if2}
| | Set Test Variable | ${dut_to_tg_if1}
| | Set Test Variable | ${dut_to_tg_if2}
| | Set Test Variable | ${tg_node}
| | Set Test Variable | ${dut_node}

| Interfaces in 2-node path are up
| | [Documentation] | Set UP state on interfaces in 2-node path on nodes and
| | ...             | wait for all interfaces are ready. Requires more than
| | ...             | one link between nodes.
| | ...
| | ... | *Arguments:*
| | ... | - No arguments.
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Given Path for 2-node testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['TG']} \|
| | ... | \| And Interfaces in 2-node path are up \|
| | ...
| | Set Interface State | ${tg_node} | ${tg_to_dut_if1} | up
| | Set Interface State | ${tg_node} | ${tg_to_dut_if2} | up
| | Set Interface State | ${dut_node} | ${dut_to_tg_if1} | up
| | Set Interface State | ${dut_node} | ${dut_to_tg_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut_node}

| Path for 3-node testing is set
| | [Documentation] | Compute path for bridge domain testing on three given
| | ...             | nodes and set corresponding test case variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${tg_node} - TG node. Type: dictionary
| | ... | - ${dut1_node} - DUT1 node. Type: dictionary
| | ... | - ${dut2_node} - DUT2 node. Type: dictionary
| | ... | - ${tg_node} - TG node again for better readability of a testcase.
| | ... |   Must be the same as a first parameter. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ... |
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${tg_node} - TG node.
| | ... | - ${tg_to_dut1} - TG interface towards DUT1.
| | ... | - ${tg_to_dut2} - TG interface towards DUT2.
| | ... | - ${dut1_node} - DUT1 node.
| | ... | - ${dut1_to_tg} - DUT1 interface towards TG.
| | ... | - ${dut1_to_dut2} - DUT1 interface towards DUT2.
| | ... | - ${dut2_node} - DUT2 node.
| | ... | - ${dut2_to_tg} - DUT2 interface towards TG.
| | ... | - ${dut2_to_dut1} - DUT2 interface towards DUT1.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Given Path for 3-node BD testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['DUT2']} \| ${nodes['TG']} \|
| | ...
| | [Arguments] | ${tg_node} | ${dut1_node} | ${dut2_node} | ${tg_node}
| | Append Nodes | ${tg_node} | ${dut1_node} | ${dut2_node} | ${tg_node}
| | Compute Path
| | ${tg_to_dut1} | ${tmp}= | Next Interface
| | ${dut1_to_tg} | ${tmp}= | Next Interface
| | ${dut1_to_dut2} | ${tmp}= | Next Interface
| | ${dut2_to_dut1} | ${tmp}= | Next Interface
| | ${dut2_to_tg} | ${tmp}= | Next Interface
| | ${tg_to_dut2} | ${tmp}= | Next Interface
| | Set Test Variable | ${tg_to_dut1}
| | Set Test Variable | ${dut1_to_tg}
| | Set Test Variable | ${tg_to_dut2}
| | Set Test Variable | ${dut2_to_tg}
| | Set Test Variable | ${dut1_to_dut2}
| | Set Test Variable | ${dut2_to_dut1}
| | Set Test Variable | ${tg_node}
| | Set Test Variable | ${dut1_node}
| | Set Test Variable | ${dut2_node}

| Interfaces in 3-node path are up
| | [Documentation] | Set UP state on interfaces in 3-node path on nodes and
| | ...             | wait for all interfaces are ready.
| | ...
| | ... | *Arguments:*
| | ... | - No arguments.
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Given Path for 3-node testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['TG']} \|
| | ... | \| And Interfaces in 3-node path are up \|
| | ...
| | Set Interface State | ${tg_node} | ${tg_to_dut1} | up
| | Set Interface State | ${tg_node} | ${tg_to_dut2} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_tg} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_dut2} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_tg} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_dut1} | up
| | Vpp Node Interfaces Ready Wait | ${dut1_node}
| | Vpp Node Interfaces Ready Wait | ${dut2_node}
