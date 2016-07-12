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
| | ${status} | ${value}= | Run Keyword And Ignore Error | Qemu System Status
| | Run Keyword If | "${status}" == "FAIL" | Qemu Kill
| | ... | ELSE IF | "${value}" == "running" | Qemu System Powerdown
| | ... | ELSE | Qemu Quit
| | Qemu Clear Socks
| | Run Keyword If | ${vm} is not None | Disconnect | ${vm}
