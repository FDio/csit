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
| Library | resources.libraries.python.QemuUtils
| Library | resources.libraries.python.ssh.SSH
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil

*** Keywords ***

| Exist QEMU Build List
| | [Documentation] | Return TRUE if variable QEMU_BUILD exist, otherwise FALSE
| | ${ret} | ${tmp}=  | Run Keyword And Ignore Error
| | ... | Variable Should Exist | @{QEMU_BUILD}
| | Return From Keyword If | "${ret}" == "PASS" | ${TRUE}
| | Return From Keyword | ${FALSE}

| Is QEMU Ready on Node
| | [Documentation] | Check if QEMU was built on the node before
| | [Arguments] | ${node}
| | ${ret}= | Exist QEMU Build List
| | Return From Keyword If | ${ret} == ${FALSE} | ${FALSE}
| | ${ret} | ${tmp}=  | Run Keyword And Ignore Error
| | ... | Should Contain | ${QEMU_BUILD} | ${node['host']}
| | Return From Keyword If | "${ret}" == "PASS" | ${TRUE}
| | Return From Keyword | ${FALSE}

| Add Node to QEMU Build List
| | [Documentation] | Add node to the list of nodes with builded QEMU (global
| | ...             | variable QEMU_BUILD)
| | [Arguments] | ${node}
| | ${ret}= | Exist QEMU Build List
| | Run Keyword If | ${ret} == ${TRUE}
| | ... | Append To List | ${QEMU_BUILD} | ${node['host']}
| | ... | ELSE | Set Global Variable | @{QEMU_BUILD} | ${node['host']}

| Build QEMU on Node
| | [Documentation] | Build QEMU from sources on the Node. Nodes with successful
| | ...             | QEMU build are stored in global variable list QEMU_BUILD
| | [Arguments] | ${node}
| | ${ready}= | Is QEMU Ready on Node | ${node}
| | Return From Keyword If | ${ready} == ${TRUE}
| | Build QEMU | ${node}
| | Add Node to QEMU Build List | ${node}

| Build QEMU on all DUTs
| | [Documentation] | Build QEMU from sources on all DUTs. Nodes with successful
| | ...             | QEMU build are stored in global variable list QEMU_BUILD
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Build QEMU on Node | ${nodes['${dut}']}

| Stop and Clear QEMU
| | [Documentation] | Stop QEMU, clear used sockets and close SSH connection
| | ...             | running on ${dut}, ${vm} is VM node info dictionary
| | ...             | returned by qemu_start or None.
| | [Arguments] | ${dut} | ${vm}
| | Qemu Set Node | ${dut}
| | Qemu Kill
| | Qemu Clear Socks
| | Run Keyword If | ${vm} is not None | Disconnect | ${vm}

| Kill Qemu on all DUTs
| | [Documentation] | Kill QEMU processes on all DUTs.
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Qemu Set Node | ${nodes['${dut}']}
| | | Qemu Kill

| VM for Vhost L2 forwarding is setup
| | [Documentation] | Setup QEMU and start VM with two vhost interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node to start VM on. Type: dictionary
| | ... | - ${sock1} - Socket path for first Vhost-User interface. Type: string
| | ... | - ${sock2} - Socket path for second Vhost-User interface. Type: string
| | ... | - ${qemu_name} - Qemu instance name by which the object will be
| | ... | accessed (Optional). Type: string
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${${qemu_name}} - VM node info. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VM for Vhost L2BD forwarding is setup \| ${nodes['DUT1']} \
| | ... | \| /tmp/sock1 \| /tmp/sock2 \|
| | ... | \| VM for Vhost L2BD forwarding is setup \| ${nodes['DUT2']} \
| | ... | \| /tmp/sock1 \| /tmp/sock2 \| qemu_instance_2 \|
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${qemu_name}=vm_node
| | Run Keyword Unless | "${qemu_name}" == "vm_node" | Import Library
| | ... | resources.libraries.python.QemuUtils | WITH NAME | ${qemu_name}
| | Set Test Variable | ${${qemu_name}} | ${None}
| | ${qemu_set_node}= | Run Keyword If | "${qemu_name}" == "vm_node"
| | | ...                              | Set Variable | Qemu Set Node
| | ... | ELSE | Replace Variables | ${qemu_name}.Qemu Set Node
| | Run keyword | ${qemu_set_node} | ${dut_node}
| | ${qemu_add_vhost}= | Run Keyword If | "${qemu_name}" == "vm_node"
| | | ...                               | Set Variable | Qemu Add Vhost User If
| | ... | ELSE | Replace Variables | ${qemu_name}.Qemu Add Vhost User If
| | Run keyword | ${qemu_add_vhost} | ${sock1}
| | Run keyword | ${qemu_add_vhost} | ${sock2}
| | ${qemu_start}= | Run Keyword If | "${qemu_name}" == "vm_node"
| | | ...                           | Set Variable | Qemu Start
| | ... | ELSE | Replace Variables | ${qemu_name}.Qemu Start
| | ${vm}= | Run keyword | ${qemu_start}
| | ${br}= | Set Variable | br0
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | ${br} | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Interface State | ${vm} | ${br} | up | if_type=name
| | Set Test Variable | ${${qemu_name}} | ${vm}

| VPP Vhost interfaces for L2 forwarding are setup
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
| | ... | \| VPP Vhost interfaces for L2BD forwarding are setup \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \|
| | ... | \| VPP Vhost interfaces for L2BD forwarding are setup \
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
