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

*** Keywords ***
| Configure VM for vhost L2BD forwarding
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
| | ... | \| Configure VM for vhost L2BD forwarding \| ${nodes['DUT1']} \
| | ... | \| /tmp/sock1 \| /tmp/sock2 \|
| | ... | \| Configure VM for vhost L2BD forwarding \| ${nodes['DUT2']} \
| | ... | \| /tmp/sock1 \| /tmp/sock2 \| qemu_instance_2 \|
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${qemu_name}=vm_node
| | Import Library | resources.libraries.python.QemuUtils | node=${dut_node} |
| | ... | WITH NAME | ${qemu_name}
| | Set Test Variable | ${${qemu_name}} | ${None}
| | Run Keyword  | ${qemu_name}.Qemu Add Vhost User If | ${sock1}
| | Run Keyword  | ${qemu_name}.Qemu Add Vhost User If | ${sock2}
| | ${vm}= | Run keyword | ${qemu_name}.Qemu Start
| | ${br}= | Set Variable | br0
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | ${br} | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Interface State | ${vm} | ${br} | up | if_type=name
| | Set Test Variable | ${${qemu_name}} | ${vm}
