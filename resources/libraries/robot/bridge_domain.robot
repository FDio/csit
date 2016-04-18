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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/l2_traffic.robot

*** Keywords ***
| Path for 2-node BD testing is set
| | [Documentation] | Compute path for bridge domain testing on two given nodes
| | ...             | and set corresponding test case variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${TG} - TG node. Type: dictionary
| | ... | - ${DUT} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ... |
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${TG} - TG node.
| | ... | - ${tg_to_dut_if1} - 1st TG interface towards DUT.
| | ... | - ${tg_to_dut_if2} - 2nd TG interface towards DUT.
| | ... | - ${DUT} - DUT node.
| | ... | - ${dut_to_tg_if1} - 1st DUT interface towards TG.
| | ... | - ${dut_to_tg_if2} - 2nd DUT interface towards TG.
| | ...
| | ... | *Example:*
| | ... | Given Path for 2-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']} |
| | ...
| | [Arguments] | ${TG} | ${DUT}
| | Append Nodes | ${TG} | ${DUT} | ${TG}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_to_dut_if1} | ${tmp}= | First Interface
| | ${tg_to_dut_if2} | ${tmp}= | Last Interface
| | ${dut_to_tg_if1} | ${tmp}= | First Ingress Interface
| | ${dut_to_tg_if2} | ${tmp}= | Last Egress Interface
| | Set Test Variable | ${tg_to_dut_if1}
| | Set Test Variable | ${tg_to_dut_if2}
| | Set Test Variable | ${dut_to_tg_if1}
| | Set Test Variable | ${dut_to_tg_if2}
| | Set Test Variable | ${TG}
| | Set Test Variable | ${DUT}

| Path for 3-node BD testing is set
| | [Documentation] | Compute path for bridge domain testing on three given nodes
| | ...             | and set corresponding test case variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${TG} - TG node. Type: dictionary
| | ... | - ${DUT1} - DUT1 node. Type: dictionary
| | ... | - ${DUT2} - DUT2 node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ... |
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${TG} - TG node.
| | ... | - ${tg_to_dut1} - TG interface towards DUT1.
| | ... | - ${tg_to_dut2} - TG interface towards DUT2.
| | ... | - ${DUT1} - DUT1 node.
| | ... | - ${dut1_to_tg} - DUT1 interface towards TG.
| | ... | - ${dut1_to_dut2} - DUT1 interface towards DUT2.
| | ... | - ${DUT2} - DUT2 node.
| | ... | - ${dut2_to_tg} - DUT2 interface towards TG.
| | ... | - ${dut2_to_dut1} - DUT2 interface towards DUT1.
| | ...
| | ... | *Example:*
| | ... | Given Path for 3-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} |
| | ...
| | [Arguments] | ${TG} | ${DUT1} | ${DUT2}
| | Append Nodes | ${TG} | ${DUT1} | ${DUT2} | ${TG}
| | Compute Path
| | ${tg_to_dut1} | ${tg}= | Next Interface
| | ${dut1_to_tg} | ${dut1}= | Next Interface
| | ${dut1_to_dut2} | ${dut1}= | Next Interface
| | ${dut2_to_dut1} | ${dut2}= | Next Interface
| | ${dut2_to_tg} | ${dut2}= | Next Interface
| | ${tg_to_dut2} | ${tg}= | Next Interface
| | Set Test Variable | ${tg_to_dut1}
| | Set Test Variable | ${dut1_to_tg}
| | Set Test Variable | ${tg_to_dut2}
| | Set Test Variable | ${dut2_to_tg}
| | Set Test Variable | ${dut1_to_dut2}
| | Set Test Variable | ${dut2_to_dut1}
| | Set Test Variable | ${tg}
| | Set Test Variable | ${dut1}
| | Set Test Variable | ${dut2}

| Bridge domain on DUT node is created
| | [Documentation] | Create bridge domain on given VPP node with defined
| | ...             | learning status.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${bd_id} - Bridge domain ID. Type: integer
| | ... | - ${learn} - Enable/disable MAC learn. Type: boolean Default value: ${TRUE}
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | Bridge domain on DUT node is created | ${nodes['DUT1']} | 2 |
| | ... | Bridge domain on DUT node is created | ${nodes['DUT1']} | 5 | learn=${FALSE} |
| | ...
| | [Arguments] | ${dut_node} | ${bd_id} | ${learn}=${TRUE}
| | ${learn} = | Set Variable If | ${learn} == ${TRUE} | ${1} | ${0}
| | Create L2 BD | ${dut_node} | ${bd_id} | learn=${learn}

| Interface is added to bridge domain
| | [Documentation] | Set given interface admin state to up and add this
| | ...             | interface to required L2 bridge domain on defined VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${dut_if} - DUT node interface name. Type: string
| | ... | - ${bd_id} - Bridge domain ID. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | Interface is added to bridge domain | ${nodes['DUT2']} | GigabitEthernet0/8/0 | 3 |
| | ...
| | [Arguments] | ${dut_node} | ${dut_if} | ${bd_id}
| | Set Interface State | ${dut_node} | ${dut_if} | u
| | Add Interface To L2 BD | ${dut_node} | ${dut_if} | ${bd_id}

| Destination port is added to L2FIB on DUT node
| | [Documentation] | Create a static L2FIB entry for required destination port
| | ...             | on defined interface and bridge domain ID
| | ...             | of the given VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dest_node} - Destination node. Type: dictionary
| | ... | - ${dest_node_if} - Destination node interface name. Type: string
| | ... | - ${vpp_node} - DUT node to add L2FIB entry on. Type: dictionary
| | ... | - ${vpp_node_if} - DUT node interface name. Type: string
| | ... | - ${bd_id} - Bridge domain ID. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | Destination port is added to L2FIB on DUT node | ${nodes['TG']} | eth1 | ${nodes['DUT2']} | GigabitEthernet0/8/0 | 3 |
| | ...
| | [Arguments] | ${dest_node} | ${dest_node_if} | ${vpp_node} | ${vpp_node_if} | ${bd_id}
| | ${mac}= | Get Interface Mac | ${dest_node} | ${dest_node_if}
| | Vpp Add L2fib Entry | ${vpp_node} | ${mac} | ${vpp_node_if} | ${bd_id}

Interfaces on all VPP nodes in the path are up
| | [Documentation] | Wait until all interfaces of the given VPP node
| | ...             | with admin-up state are in link-up state.
| | ...
| | ... | *Arguments:*
| | ... | - @{nodes} - DUT nodes. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | Interfaces on all VPP nodes in the path are up | ${nodes['DUT1']} | ${nodes['DUT2']} |
| | ...
| | [Arguments] | @{nodes}
| | :FOR | ${node} | IN | @{nodes}
| |      | VPP Node Interfaces Ready Wait | ${node}
