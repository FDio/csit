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
| | [Documentation] | Compute path for testing on two given nodes in circular
| | ...             | topology and set corresponding test case variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${tg_node} - TG node. Type: dictionary
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${tg2_node} - Node where the path ends. Must be the same as TG node
| | ... |   parameter in circular topology. Type: dictionary
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
| | ... | - ${tg_to_dut_if1_mac}
| | ... | - ${tg_to_dut_if2_mac}
| | ... | - ${dut_to_tg_if1_mac}
| | ... | - ${dut_to_tg_if2_mac}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Given Path for 2-node testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['TG']} \|
| | ...
| | [Arguments] | ${tg_node} | ${dut_node} | ${tg2_node}
| | Should Be Equal | ${tg_node} | ${tg2_node}
| | Append Nodes | ${tg_node} | ${dut_node} | ${tg_node}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_to_dut_if1} | ${tmp}= | First Interface
| | ${tg_to_dut_if2} | ${tmp}= | Last Interface
| | ${dut_to_tg_if1} | ${tmp}= | First Ingress Interface
| | ${dut_to_tg_if2} | ${tmp}= | Last Egress Interface
| | ${tg_to_dut_if1_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut_if1}
| | ${tg_to_dut_if2_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut_if2}
| | ${dut_to_tg_if1_mac}= | Get interface mac | ${dut_node} | ${dut_to_tg_if1}
| | ${dut_to_tg_if2_mac}= | Get interface mac | ${dut_node} | ${dut_to_tg_if2}
| | Set Test Variable | ${tg_to_dut_if1}
| | Set Test Variable | ${tg_to_dut_if2}
| | Set Test Variable | ${dut_to_tg_if1}
| | Set Test Variable | ${dut_to_tg_if2}
| | Set Test Variable | ${tg_to_dut_if1_mac}
| | Set Test Variable | ${tg_to_dut_if2_mac}
| | Set Test Variable | ${dut_to_tg_if1_mac}
| | Set Test Variable | ${dut_to_tg_if2_mac}
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
| | ... | _NOTE:_ This KW uses test variables sets in
| | ... |         "Path for 2-node testing is set" KW.
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
| | [Documentation] | Compute path for testing on three given nodes in circular
| | ...             | topology and set corresponding test case variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${tg_node} - TG node. Type: dictionary
| | ... | - ${dut1_node} - DUT1 node. Type: dictionary
| | ... | - ${dut2_node} - DUT2 node. Type: dictionary
| | ... | - ${tg2_node} - Node where the path ends. Must be the same as TG node
| | ... |   parameter in circular topology. Type: dictionary
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
| | ... | - ${tg_to_dut1_mac}
| | ... | - ${tg_to_dut2_mac}
| | ... | - ${dut1_to_tg_mac}
| | ... | - ${dut1_to_dut2_mac}
| | ... | - ${dut2_to_tg_mac}
| | ... | - ${dut2_to_dut1_mac}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Given Path for 3-node testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['DUT2']} \| ${nodes['TG']} \|
| | ...
| | [Arguments] | ${tg_node} | ${dut1_node} | ${dut2_node} | ${tg2_node}
| | Should Be Equal | ${tg_node} | ${tg2_node}
| | Append Nodes | ${tg_node} | ${dut1_node} | ${dut2_node} | ${tg_node}
| | Compute Path
| | ${tg_to_dut1} | ${tmp}= | Next Interface
| | ${dut1_to_tg} | ${tmp}= | Next Interface
| | ${dut1_to_dut2} | ${tmp}= | Next Interface
| | ${dut2_to_dut1} | ${tmp}= | Next Interface
| | ${dut2_to_tg} | ${tmp}= | Next Interface
| | ${tg_to_dut2} | ${tmp}= | Next Interface
| | ${tg_to_dut1_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut1}
| | ${tg_to_dut2_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut2}
| | ${dut1_to_tg_mac}= | Get interface mac | ${dut1_node} | ${dut1_to_tg}
| | ${dut1_to_dut2_mac}= | Get interface mac | ${dut1_node} | ${dut1_to_dut2}
| | ${dut2_to_tg_mac}= | Get interface mac | ${dut2_node} | ${dut2_to_tg}
| | ${dut2_to_dut1_mac}= | Get interface mac | ${dut2_node} | ${dut2_to_dut1}
| | Set Test Variable | ${tg_to_dut1}
| | Set Test Variable | ${dut1_to_tg}
| | Set Test Variable | ${tg_to_dut2}
| | Set Test Variable | ${dut2_to_tg}
| | Set Test Variable | ${dut1_to_dut2}
| | Set Test Variable | ${dut2_to_dut1}
| | Set Test Variable | ${tg_to_dut1_mac}
| | Set Test Variable | ${tg_to_dut2_mac}
| | Set Test Variable | ${dut1_to_tg_mac}
| | Set Test Variable | ${dut1_to_dut2_mac}
| | Set Test Variable | ${dut2_to_tg_mac}
| | Set Test Variable | ${dut2_to_dut1_mac}
| | Set Test Variable | ${tg_node}
| | Set Test Variable | ${dut1_node}
| | Set Test Variable | ${dut2_node}

| Interfaces in 3-node path are up
| | [Documentation]
| | ... | Set UP state on interfaces in 3-node path on nodes and \
| | ... | wait until all interfaces are ready.
| | ...
| | ... | *Arguments:*
| | ... | - No arguments.
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | _NOTE:_ This KW uses test variables sets in
| | ... |         "Path for 3-node testing is set" KW.
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

| Path for Double-Link 3-node testing is set
| | [Documentation]
| | ... | Compute path for testing on three given nodes in circular \
| | ... | topology with double link and set corresponding \
| | ... | test case variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${tg_node} - TG node. Type: dictionary
| | ... | - ${dut1_node} - DUT1 node. Type: dictionary
| | ... | - ${dut2_node} - DUT2 node. Type: dictionary
| | ... | - ${tg2_node} - Node where the path ends. Must be the same as TG node
| | ... |   parameter in circular topology. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ... |
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${tg_node} - TG node.
| | ... | - ${tg_to_dut1_if1} - TG interface towards DUT1 interface 1.
| | ... | - ${tg_to_dut1_if2} - TG interface towards DUT1 interface 2.
| | ... | - ${tg_to_dut1_mac_if1} - TG towards DUT1 MAC address interface 1.
| | ... | - ${tg_to_dut1_mac_if2} - TG towards DUT1 MAC address interface 2.
| | ... | - ${tg_to_dut2_if1} - TG interface towards DUT2 interface 1.
| | ... | - ${tg_to_dut2_if2} - TG interface towards DUT2 interface 2.
| | ... | - ${tg_to_dut2_mac_if1} - TG towards DUT2 MAC address interface 1.
| | ... | - ${tg_to_dut2_mac_if2} - TG towards DUT2 MAC address interface 2.
| | ... | - ${dut1_node} - DUT1 node.
| | ... | - ${dut1_to_tg_if1} - DUT1 interface towards TG interface 1.
| | ... | - ${dut1_to_tg_if2} - DUT1 interface towards TG interface 2.
| | ... | - ${dut1_to_tg_mac_if1} - DUT1 towards TG MAC address interface 1.
| | ... | - ${dut1_to_tg_mac_if2} - DUT1 towards TG MAC address interface 2.
| | ... | - ${dut1_to_dut2_if1} - DUT1 interface towards DUT2 interface 1.
| | ... | - ${dut1_to_dut2_if2} - DUT1 interface towards DUT2 interface 2.
| | ... | - ${dut1_to_dut2_mac_if1} - DUT1 towards DUT2 MAC address interface 1.
| | ... | - ${dut1_to_dut2_mac_if2} - DUT1 towards DUT2 MAC address interface 2.
| | ... | - ${dut2_node} - DUT2 node.
| | ... | - ${dut2_to_tg_if1} - DUT2 interface towards TG interface 1.
| | ... | - ${dut2_to_tg_if2} - DUT2 interface towards TG interface 2.
| | ... | - ${dut2_to_tg_mac_if1} - DUT2 towards TG MAC address interface 1.
| | ... | - ${dut2_to_tg_mac_if2} - DUT2 towards TG MAC address interface 2.
| | ... | - ${dut2_to_dut1_if1} - DUT2 interface towards DUT1 interface 1.
| | ... | - ${dut2_to_dut1_if2} - DUT2 interface towards DUT1 interface 2.
| | ... | - ${dut2_to_dut1_mac_if1} - DUT2 towards DUT1 MAC address interface 1.
| | ... | - ${dut2_to_dut1_mac_if2} - DUT2 towards DUT1 MAC address interface 2.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Path for Double-Link 3-node testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['DUT2']} \| ${nodes['TG']} \|
| | ...
| | [Arguments] | ${tg_node} | ${dut1_node} | ${dut2_node} | ${tg2_node}
| | Should Be Equal | ${tg_node} | ${tg2_node}
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
| | Append Nodes | ${dut1_node} | ${dut2_node} | ${dut1_node}
| | Compute Path | always_same_link=${FALSE}
| | ${dut1_to_dut2_if1} | ${tmp}= | First Interface
| | ${dut1_to_dut2_if2} | ${tmp}= | Last Interface
| | ${dut2_to_dut1_if1} | ${tmp}= | First Ingress Interface
| | ${dut2_to_dut1_if2} | ${tmp}= | Last Egress Interface
| | # Set test variables
| | Set Test Variable | ${tg_to_dut1_if1}
| | Set Test Variable | ${tg_to_dut1_if2}
| | Set Test Variable | ${tg_to_dut2_if1}
| | Set Test Variable | ${tg_to_dut2_if2}
| | Set Test Variable | ${dut1_to_tg_if1}
| | Set Test Variable | ${dut1_to_tg_if2}
| | Set Test Variable | ${dut2_to_tg_if1}
| | Set Test Variable | ${dut2_to_tg_if2}
| | Set Test Variable | ${dut1_to_dut2_if1}
| | Set Test Variable | ${dut1_to_dut2_if2}
| | Set Test Variable | ${dut2_to_dut1_if1}
| | Set Test Variable | ${dut2_to_dut1_if2}
| | Set Test Variable | ${tg_node}
| | Set Test Variable | ${dut1_node}
| | Set Test Variable | ${dut2_node}
| | # Set Mac Addresses
| | ${tg_to_dut1_if1_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut1_if1}
| | ${tg_to_dut1_if2_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut1_if2}
| | ${tg_to_dut2_if1_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut2_if1}
| | ${tg_to_dut2_if2_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut2_if2}
| | ${dut1_to_tg_if1_mac}= | Get interface mac | ${dut1_node}
| | ... | ${dut1_to_tg_if1}
| | ${dut1_to_tg_if2_mac}= | Get interface mac | ${dut1_node}
| | ... | ${dut1_to_tg_if2}
| | ${dut1_to_dut2_if1_mac}= | Get interface mac | ${dut1_node}
| | ... | ${dut1_to_dut2_if1}
| | ${dut1_to_dut2_if2_mac}= | Get interface mac | ${dut1_node}
| | ... | ${dut1_to_dut2_if2}
| | ${dut2_to_tg_if1_mac}= | Get interface mac | ${dut2_node}
| | ... | ${dut2_to_tg_if1}
| | ${dut2_to_tg_if2_mac}= | Get interface mac | ${dut2_node}
| | ... | ${dut2_to_tg_if2}
| | ${dut2_to_dut1_if1_mac}= | Get interface mac | ${dut2_node}
| | ... | ${dut2_to_dut1_if1}
| | ${dut2_to_dut1_if2_mac}= | Get interface mac | ${dut2_node}
| | ... | ${dut2_to_dut1_if2}
| | Set Test Variable | ${tg_to_dut1_if1_mac}
| | Set Test Variable | ${tg_to_dut1_if2_mac}
| | Set Test Variable | ${tg_to_dut2_if1_mac}
| | Set Test Variable | ${tg_to_dut2_if2_mac}
| | Set Test Variable | ${dut1_to_tg_if1_mac}
| | Set Test Variable | ${dut1_to_tg_if2_mac}
| | Set Test Variable | ${dut1_to_dut2_if1_mac}
| | Set Test Variable | ${dut1_to_dut2_if2_mac}
| | Set Test Variable | ${dut2_to_tg_if1_mac}
| | Set Test Variable | ${dut2_to_tg_if2_mac}
| | Set Test Variable | ${dut2_to_dut1_if1_mac}
| | Set Test Variable | ${dut2_to_dut1_if2_mac}

| Interfaces in Double-Link 3-node path are UP
| | [Documentation]
| | ... | Set UP state on interfaces in 3-node double link path \
| | ... | wait until all interfaces are ready.
| | ...
| | ... | *Arguments:*
| | ... | - No arguments.
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | _NOTE:_ This KW uses test variables sets in
| | ... |         "Path for Double-Link 3-node testing is set" KW.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Path for Double-Link 3-node testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['TG']} \|
| | ... | \| Interfaces in Double-Link 3-node testing are UP \|
| | ...
| | Set Interface State | ${tg_node} | ${tg_to_dut1_if1} | up
| | Set Interface State | ${tg_node} | ${tg_to_dut1_if2} | up
| | Set Interface State | ${tg_node} | ${tg_to_dut2_if1} | up
| | Set Interface State | ${tg_node} | ${tg_to_dut2_if2} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_tg_if1} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_tg_if2} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_tg_if1} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_tg_if2} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_dut2_if1} | up
| | Set Interface State | ${dut1_node} | ${dut1_to_dut2_if2} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_dut1_if1} | up
| | Set Interface State | ${dut2_node} | ${dut2_to_dut1_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1_node}
| | Vpp Node Interfaces Ready Wait | ${dut2_node}