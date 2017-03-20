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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/qemu.robot
| Resource | resources/libraries/robot/vxlan.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Func Test Setup
| Test Teardown
| ... | Run Keywords | Log | none
| ... | AND | Log | none
#| ... | AND | resources.libraries.python.QemuUtils.Qemu Kill All | ${dut_node}
| ... | AND | Func Test Teardown

| Documentation | *tbd.*
| ...
| ... | tbd
| ... | tbd
| ... | tbd
| ... | tbd

*** Variables ***
| ${tg_if1_ip}= | 192.168.0.1
| ${dut_if1_ip}= | 192.168.0.2
| ${prefix_length}= | ${24}

| ${sock_vm1_1}= | /tmp/sock1
| ${sock_vm1_2}= | /tmp/sock2
| ${sock_vm2_1}= | /tmp/sock3
| ${sock_vm2_2}= | /tmp/sock4

*** Test Cases ***
| Test reconnect when qemu restarts
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV | tmp
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | And Set Interface Address
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_if1_ip} | ${prefix_length}
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | ${dut_if1_ip} | ${prefix_length}
| | ${vhost_if1}= | And Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm1_1}
| | ${vhost_if2}= | And Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm1_2}
| | ${vhost_if3}= | And Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm2_1}
| | ${vhost_if4}= | And Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm2_2}
| | ${vxlan1}= | Create VXLAN interface | ${dut_node} | ${101} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan2}= | Create VXLAN interface | ${dut_node} | ${102} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan3}= | Create VXLAN interface | ${dut_node} | ${103} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan4}= | Create VXLAN interface | ${dut_node} | ${104} | ${dut_if1_ip} | ${tg_if1_ip}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${101} | ${vxlan1} | ${vhost_if1}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${102} | ${vxlan2} | ${vhost_if2}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${103} | ${vxlan3} | ${vhost_if3}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${104} | ${vxlan4} | ${vhost_if4}
# set interfaces up: vhost, vm int
# add neibhor to tg
# after recreate create br
###########

| | Setup QEMU Vhost and Run | ${dut_node} | ${sock_vm1_1} | ${sock_vm1_2} | ${1}
| | Setup QEMU Vhost and Run | ${dut_node} | ${sock_vm2_1} | ${sock_vm2_2} | ${2}
| | Check traffic through VM
| | Run keyword | qemu-1.Qemu Kill
| | Run Keyword | qemu-1.Qemu Start
| | Check traffic through VM


*** Keywords ***
| Setup QEMU Vhost and Run
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${qemu_id}
| | Import Library | resources.libraries.python.QemuUtils | qemu_id=${qemu_id} | WITH NAME | qemu-${qemu_id}
| | ${qemu_add_vhost}= | Replace Variables | qemu-${qemu_id}.Qemu Add Vhost User If
| | ${qemu_set_node}= | Replace Variables | qemu-${qemu_id}.Qemu Set Node
| | ${qemu_start}= | Replace Variables | qemu-${qemu_id}.Qemu Start
| | Run keyword | ${qemu_set_node} | ${dut_node}
| | Run keyword | ${qemu_add_vhost} | ${sock1}
| | Run keyword | ${qemu_add_vhost} | ${sock2}
| | ${vm}= | Run keyword | ${qemu_start}
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | br0 | ${vhost1} | ${vhost2}
| | Set Test Variable | ${qemu-${qemu_id}} | ${vm}

| Check traffic through VM
| | ...
| | Log | tbd