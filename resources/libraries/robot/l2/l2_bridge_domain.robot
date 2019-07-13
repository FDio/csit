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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.VhostUser
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot

*** Keywords ***
| Configure L2BD forwarding
| | [Documentation] | Setup BD between 2 interfaces on VPP node and if learning
| | ...             | is off set static L2FIB entry on second interface
| | [Arguments] | ${dut_node} | ${if1} | ${if2} | ${learn}=${TRUE}
| | ... | ${mac}=${EMPTY}
| | Set Interface State | ${dut_node} | ${if1} | up
| | Set Interface State | ${dut_node} | ${if2} | up
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${1} | ${if1} | ${if2} | ${learn}
| | Run Keyword If | ${learn} == ${FALSE}
| | ... | Vpp Add L2fib Entry | ${dut_node} | ${mac} | ${if2} | ${1}
| | Vpp Node Interfaces Ready Wait | ${dut_node}

| Initialize L2 bridge domain
| | [Documentation]
| | ... | Setup L2 DB topology by adding two interfaces on each DUT into BD
| | ... | that is created automatically with index 1. Learning is enabled.
| | ... | Interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id - Bridge domain ID. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domain \| 1 \|
| | ...
| | [Arguments] | ${bd_id}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_1} | ${bd_id}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_1} | ${bd_id}

| Configure path for 3-node BD-SHG test
| | [Documentation] | Compute path for bridge domain split-horizon group testing
| | ...             | on three given nodes with following interconnections
| | ...             | TG - (2 links) - DUT1 - (1 link) - DUT2 - (2 links) - TG
| | ...             | and set corresponding test case variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${tg_node} - TG node. Type: dictionary
| | ... | - ${dut1_node} - DUT1 node. Type: dictionary
| | ... | - ${dut2_node} - DUT2 node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${tg_node} - TG node.
| | ... | - ${tg_to_dut1_if1} - TG interface 1 towards DUT1.
| | ... | - ${tg_to_dut1_if2} - TG interface 2 towards DUT1.
| | ... | - ${tg_to_dut2_if1} - TG interface 1 towards DUT2.
| | ... | - ${tg_to_dut2_if2} - TG interface 2 towards DUT2.
| | ... | - ${dut1_node} - DUT1 node.
| | ... | - ${dut1_to_tg_if1} - DUT1 interface 1 towards TG.
| | ... | - ${dut1_to_tg_if2} - DUT1 interface 2 towards TG.
| | ... | - ${dut1_to_dut2} - DUT1 interface towards DUT2.
| | ... | - ${dut2_node} - DUT2 node.
| | ... | - ${dut2_to_tg_if1} - DUT2 interface 1 towards TG.
| | ... | - ${dut2_to_tg_if2} - DUT2 interface 2 towards TG.
| | ... | - ${dut2_to_dut1} - DUT2 interface towards DUT1.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Given Configure path for 3-node BD-SHG test \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['DUT2']} \|
| | [Arguments] | ${tg_node} | ${dut1_node} | ${dut2_node}
| | # Compute path TG - DUT1 with two links in between
| | Append Nodes | ${tg_node} | ${dut1_node} | ${tg_node}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_to_dut1_if1} | ${tmp}= | First Interface
| | ${tg_to_dut1_if2} | ${tmp}= | Last Interface
| | ${dut1_to_tg_if1} | ${tmp}= | First Ingress Interface
| | ${dut1_to_tg_if2} | ${tmp}= | Last Egress Interface
| | # Compute path TG - DUT2 with two links in between
| | Clear Path
| | Append Nodes | ${tg_node} | ${dut2_node} | ${tg_node}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_to_dut2_if1} | ${tmp}= | First Interface
| | ${tg_to_dut2_if2} | ${tmp}= | Last Interface
| | ${dut2_to_tg_if1} | ${tmp}= | First Ingress Interface
| | ${dut2_to_tg_if2} | ${tmp}= | Last Egress Interface
| | # Compute path DUT1 - DUT2 with one link in between
| | Clear Path
| | Append Nodes | ${dut1_node} | ${dut2_node}
| | Compute Path
| | ${dut1_to_dut2} | ${tmp}= | Next Interface
| | ${dut2_to_dut1} | ${tmp}= | Next Interface
| | # Set test variables
| | Set Test Variable | ${tg_to_dut1_if1}
| | Set Test Variable | ${tg_to_dut1_if2}
| | Set Test Variable | ${tg_to_dut2_if1}
| | Set Test Variable | ${tg_to_dut2_if2}
| | Set Test Variable | ${dut1_to_tg_if1}
| | Set Test Variable | ${dut1_to_tg_if2}
| | Set Test Variable | ${dut2_to_tg_if1}
| | Set Test Variable | ${dut2_to_tg_if2}
| | Set Test Variable | ${dut1_to_dut2}
| | Set Test Variable | ${dut2_to_dut1}
| | Set Test Variable | ${tg_node}
| | Set Test Variable | ${dut1_node}
| | Set Test Variable | ${dut2_node}

| Set interfaces in 3-node BD-SHG test up
| | [Documentation] | Set UP state on interfaces in 3-node path on nodes and
| | ...             | wait for all interfaces are ready.
| | ...
| | ... | *Arguments:*
| | ... | - No arguments.
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | _NOTE:_ This KW uses test variables sets in
| | ... |         "Configure path for 3-node BD-SHG test" KW.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure path for 3-node BD-SHG test \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['DUT2']} \|
| | ... | \| Set interfaces in 3-node BD-SHG test up \|
| | ...
| | Set Interface State | ${tg_node} | ${tg_to_dut1_if1} | up
| | Set Interface State | ${tg_node} | ${tg_to_dut1_if2} | up
| | Set Interface State | ${tg_node} | ${tg_to_dut2_if1} | up
| | Set Interface State | ${tg_node} | ${tg_to_dut2_if2} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_tg_if1} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_tg_if2} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_tg_if1} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_tg_if2} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_dut2} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_dut1} | up
| | Vpp Node Interfaces Ready Wait | ${dut1_node}
| | Vpp Node Interfaces Ready Wait | ${dut2_node}

| Create bridge domain
| | [Documentation] | Create bridge domain on given VPP node with defined
| | ...             | learning status.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${bd_id} - Bridge domain ID. Type: integer
| | ... | - ${learn} - Enable/disable MAC learn. Type: boolean, \
| | ... | default value: ${TRUE}
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create bridge domain \| ${nodes['DUT1']} \| 2 \|
| | ... | \| Create bridge domain \| ${nodes['DUT1']} \| 5 \
| | ... | \| learn=${FALSE} \|
| | [Arguments] | ${dut_node} | ${bd_id} | ${learn}=${TRUE}
| | ${learn} = | Set Variable If | ${learn} == ${TRUE} | ${1} | ${0}
| | Create L2 BD | ${dut_node} | ${bd_id} | learn=${learn}

| Add interface to bridge domain
| | [Documentation] | Set given interface admin state to up and add this
| | ...             | interface to required L2 bridge domain on defined
| | ...             | VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${dut_if} - DUT node interface name. Type: string
| | ... | - ${bd_id} - Bridge domain ID. Type: integer
| | ... | - ${shg} - Split-horizon group ID. Type: integer, default value: 0
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add interface to bridge domain \| ${nodes['DUT2']} \
| | ... | \| GigabitEthernet0/8/0 \| 3 \|
| | [Arguments] | ${dut_node} | ${dut_if} | ${bd_id} | ${shg}=0
| | Set Interface State | ${dut_node} | ${dut_if} | up
| | Add Interface To L2 BD | ${dut_node} | ${dut_if} | ${bd_id} | ${shg}

| Add destination port to L2FIB
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
| | ...
| | ... | \| Add destination port to L2FIB \| ${nodes['TG']} \
| | ... | \| eth1 \| ${nodes['DUT2']} \| GigabitEthernet0/8/0 \| 3 \|
| | [Arguments] | ${dest_node} | ${dest_node_if} | ${vpp_node}
| | ...         | ${vpp_node_if} | ${bd_id}
| | ${mac}= | Get Interface Mac | ${dest_node} | ${dest_node_if}
| | Vpp Add L2fib Entry | ${vpp_node} | ${mac} | ${vpp_node_if} | ${bd_id}

| Configure vhost interfaces for L2BD forwarding
| | [Documentation] | Create two Vhost-User interfaces on defined VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${sock1} - Socket path for first Vhost-User interface. Type: string
| | ... | - ${sock2} - Socket path for second Vhost-User interface. Type: string
| | ... | - ${vhost_if1} - Name of the first Vhost-User interface (Optional).
| | ... | Type: string
| | ... | - ${vhost_if2} - Name of the second Vhost-User interface (Optional).
| | ... | Type: string
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${${vhost_if1}} - First Vhost-User interface.
| | ... | - ${${vhost_if2}} - Second Vhost-User interface.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure vhost interfaces for L2BD forwarding \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \|
| | ... | \| Configure vhost interfaces for L2BD forwarding \
| | ... | \| ${nodes['DUT2']} \| /tmp/sock1 \| /tmp/sock2 \| dut2_vhost_if1 \
| | ... | \| dut2_vhost_if2 \|
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vhost_if1}=vhost_if1
| | ... | ${vhost_if2}=vhost_if2
| | ${vhost_1}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock1}
| | ${vhost_2}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock2}
| | Set Interface State | ${dut_node} | ${vhost_1} | up
| | Set Interface State | ${dut_node} | ${vhost_2} | up
| | Set Test Variable | ${${vhost_if1}} | ${vhost_1}
| | Set Test Variable | ${${vhost_if2}} | ${vhost_2}
