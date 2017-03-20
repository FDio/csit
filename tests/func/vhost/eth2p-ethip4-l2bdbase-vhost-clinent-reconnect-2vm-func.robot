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
| Force Tags | HW_ENV | VM_ENV | tmp
| Test Setup | Func Test Setup
| Test Teardown
| ... | Run Keywords | Log | none
| ... | AND | Log | none
| ... | AND | resources.libraries.python.QemuUtils.Qemu Kill All | ${dut_node}
| ... | AND | Func Test Teardown

| Documentation | *Vhost-User Interface Traffic Tests*
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-VXLAN-ETHICMPv4 for L2 switching of
| ... | IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG)
| ... | are set depending on test case; Namespaces (NM)
| ... | are set on DUT1 with attached linux-TAP.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets
| ... | are sent by TG on link to DUT1; On receipt TG verifies packets
| ... | for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*
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
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | ...
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Interfaces in 2-node path are up
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | ${dut_if1_ip} | ${prefix_length}
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${tg_if1_ip} | ${tg_to_dut_if1_mac}
| | ${vxlan1}= | Create VXLAN interface | ${dut_node} | ${101} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan2}= | Create VXLAN interface | ${dut_node} | ${102} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan3}= | Create VXLAN interface | ${dut_node} | ${103} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan4}= | Create VXLAN interface | ${dut_node} | ${104} | ${dut_if1_ip} | ${tg_if1_ip}
| | Set Interface State | ${dut_node} | ${vxlan1} | up
| | Set Interface State | ${dut_node} | ${vxlan2} | up
| | Set Interface State | ${dut_node} | ${vxlan3} | up
| | Set Interface State | ${dut_node} | ${vxlan4} | up
| | ${vhost_if1}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm1_1}
| | ${vhost_if2}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm1_2}
| | ${vhost_if3}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm2_1}
| | ${vhost_if4}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm2_2}
| | Set Interface State | ${dut_node} | ${vhost_if1} | up
| | Set Interface State | ${dut_node} | ${vhost_if2} | up
| | Set Interface State | ${dut_node} | ${vhost_if3} | up
| | Set Interface State | ${dut_node} | ${vhost_if4} | up
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${101} | ${vxlan1} | ${vhost_if1}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${102} | ${vxlan2} | ${vhost_if2}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${103} | ${vxlan3} | ${vhost_if3}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${104} | ${vxlan4} | ${vhost_if4}
| | Setup QEMU Vhost and Run | ${dut_node} | ${sock_vm1_1} | ${sock_vm1_2} | ${1}
| | Setup QEMU Vhost and Run | ${dut_node} | ${sock_vm2_1} | ${sock_vm2_2} | ${2}
| | Check traffic through VM
| | Run keyword | qemu-1.Qemu Kill
| | ${vm1}= | Run Keyword | qemu-1.Qemu Start
| | ${vhost_int_1}= | Get Vhost User If Name By Sock | ${vm1} | ${sock_vm1_1}
| | ${vhost_int_2}= | Get Vhost User If Name By Sock | ${vm1} | ${sock_vm1_2}
| | Linux Add Bridge | ${vm1} | br0 | ${vhost_int_1} | ${vhost_int_2}
| | Set Interface State | ${vm1} | ${vhost_int_1} | up | if_type=name
| | Set Interface State | ${vm1} | ${vhost_int_2} | up | if_type=name
| | Check traffic through VM


| Test reconnect when vpp restarts
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV | EXPECTED_FAILING
| | ...
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Interfaces in 2-node path are up
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | ${dut_if1_ip} | ${prefix_length}
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${tg_if1_ip} | ${tg_to_dut_if1_mac}
| | ${vxlan1}= | Create VXLAN interface | ${dut_node} | ${101} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan2}= | Create VXLAN interface | ${dut_node} | ${102} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan3}= | Create VXLAN interface | ${dut_node} | ${103} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan4}= | Create VXLAN interface | ${dut_node} | ${104} | ${dut_if1_ip} | ${tg_if1_ip}
| | Set Interface State | ${dut_node} | ${vxlan1} | up
| | Set Interface State | ${dut_node} | ${vxlan2} | up
| | Set Interface State | ${dut_node} | ${vxlan3} | up
| | Set Interface State | ${dut_node} | ${vxlan4} | up
| | ${vhost_if1}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm1_1}
| | ${vhost_if2}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm1_2}
| | ${vhost_if3}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm2_1}
| | ${vhost_if4}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm2_2}
| | Set Interface State | ${dut_node} | ${vhost_if1} | up
| | Set Interface State | ${dut_node} | ${vhost_if2} | up
| | Set Interface State | ${dut_node} | ${vhost_if3} | up
| | Set Interface State | ${dut_node} | ${vhost_if4} | up
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${101} | ${vxlan1} | ${vhost_if1}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${102} | ${vxlan2} | ${vhost_if2}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${103} | ${vxlan3} | ${vhost_if3}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${104} | ${vxlan4} | ${vhost_if4}
| | Setup QEMU Vhost and Run | ${dut_node} | ${sock_vm1_1} | ${sock_vm1_2} | ${1}
| | Setup QEMU Vhost and Run | ${dut_node} | ${sock_vm2_1} | ${sock_vm2_2} | ${2}
| | Check traffic through VM
| | ...
| | Setup All Duts ${nodes}
| | Save VPP PIDs
| | ...
| | Interfaces in 2-node path are up
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | ${dut_if1_ip} | ${prefix_length}
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${tg_if1_ip} | ${tg_to_dut_if1_mac}
| | ${vxlan1}= | Create VXLAN interface | ${dut_node} | ${101} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan2}= | Create VXLAN interface | ${dut_node} | ${102} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan3}= | Create VXLAN interface | ${dut_node} | ${103} | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan4}= | Create VXLAN interface | ${dut_node} | ${104} | ${dut_if1_ip} | ${tg_if1_ip}
| | Set Interface State | ${dut_node} | ${vxlan1} | up
| | Set Interface State | ${dut_node} | ${vxlan2} | up
| | Set Interface State | ${dut_node} | ${vxlan3} | up
| | Set Interface State | ${dut_node} | ${vxlan4} | up
| | ${vhost_if1}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm1_1}
| | ${vhost_if2}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm1_2}
| | ${vhost_if3}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm2_1}
| | ${vhost_if4}= | Vpp Create Vhost User Interface | ${dut_node} | ${sock_vm2_2}
| | Set Interface State | ${dut_node} | ${vhost_if1} | up
| | Set Interface State | ${dut_node} | ${vhost_if2} | up
| | Set Interface State | ${dut_node} | ${vhost_if3} | up
| | Set Interface State | ${dut_node} | ${vhost_if4} | up
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${101} | ${vxlan1} | ${vhost_if1}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${102} | ${vxlan2} | ${vhost_if2}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${103} | ${vxlan3} | ${vhost_if3}
| | Vpp Add L2 Bridge Domain | ${dut_node} | ${104} | ${vxlan4} | ${vhost_if4}
| | ...
| | Check traffic through VM


*** Keywords ***
| Setup QEMU Vhost and Run
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${qemu_id}
| | ...
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
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Test Variable | ${qemu-${qemu_id}} | ${vm}

| Check traffic through VM
| | ...
| | Send VXLAN receive VXLAN Packet | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_if1_ip} | ${dut_if1_ip} | ${101}
| | ... | ${dut_if1_ip} | ${tg_if1_ip} | ${102}
| | Send VXLAN receive VXLAN Packet | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_if1_ip} | ${dut_if1_ip} | ${103}
| | ... | ${dut_if1_ip} | ${tg_if1_ip} | ${104}

| Send VXLAN receive VXLAN Packet
| | ...
| | [Arguments] | ${tg_node} | ${tx_if} | ${rx_if} | ${tx_src_mac} | ${tx_dst_mac}
| | ... | ${tx_src_ip} | ${tx_dst_ip} | ${tx_vni}
| | ... | ${rx_src_ip} | ${rx_dst_ip} | ${rx_vni}
| | ${tx_if_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_if_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate
| | ... | --tx_if ${tx_if_name}
| | ... | --rx_if ${rx_if_name}
| | ... | --tx_src_mac ${tx_src_mac}
| | ... | --tx_dst_mac ${tx_dst_mac}
| | ... | --tx_src_ip ${tx_src_ip}
| | ... | --tx_dst_ip ${tx_dst_ip}
| | ... | --tx_vni ${tx_vni}
| | ... | --rx_src_ip ${rx_src_ip}
| | ... | --rx_dst_ip ${rx_dst_ip}
| | ... | --rx_vni ${rx_vni}
| | Run Traffic Script On Node | send_vxlan_check_vxlan.py | ${tg_node} | ${args}
