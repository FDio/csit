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
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| Test Setup | Set up functional test
| Test Teardown | Run Keywords
| ... | resources.libraries.python.QemuUtils.Qemu Kill All | ${dut_node} | AND
| ... | Tear down functional test
| Documentation | *Vhost-User Interface Traffic Tests*
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-VXLAN-ETH-IP on TG-DUT link.
| ... | ETH-IP on VirtualEthernet-VM interface.
| ... | *[Cfg] DUT configuration:* On DUT is running 2 VM with 2 vhost-user
| ... | interface on each VM. DUT is configured with VXLAN and vhost-user
| ... | interfaces in bridge-domain (L2BD).
| ... | *[Cfg] VM configuration:* VM has both vhost-user interfaces added into
| ... | Linux Bridge.
| ... | *[Ver] TG verification:*
| ... | VXLAN packet is send to DUT where is decapsulated and send bridged to
| ... | vhost-user inteface. VM forwards frame to its second interface and VPP
| ... | encapsulates it to another VXLAN tunnel. Packets
| ... | are sent and received by TG on link to DUT.

*** Variables ***
| ${tg_if1_ip}= | 192.168.0.1
| ${dut_if1_ip}= | 192.168.0.2
| ${prefix_length}= | ${24}

| ${sock_vm1_1}= | /tmp/sock1
| ${sock_vm1_2}= | /tmp/sock2
| ${sock_vm2_1}= | /tmp/sock3
| ${sock_vm2_2}= | /tmp/sock4

*** Test Cases ***
| TC01:  Qemu reconnects to VPPs vhost-user when Qemu is killed and restarted
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | ${dut_if1_ip}
| | ... | ${prefix_length}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${tg_if1_ip}
| | ... | ${tg_to_dut_if1_mac}
| | ${vxlan1}= | And Create VXLAN interface | ${dut_node} | ${101}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan2}= | And Create VXLAN interface | ${dut_node} | ${102}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan3}= | And Create VXLAN interface | ${dut_node} | ${103}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan4}= | And Create VXLAN interface | ${dut_node} | ${104}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | And Set Interface State | ${dut_node} | ${vxlan1} | up
| | And Set Interface State | ${dut_node} | ${vxlan2} | up
| | And Set Interface State | ${dut_node} | ${vxlan3} | up
| | And Set Interface State | ${dut_node} | ${vxlan4} | up
| | ${vhost_if1}= | And Vpp Create Vhost User Interface
| | ... | ${dut_node} | ${sock_vm1_1}
| | ${vhost_if2}= | And Vpp Create Vhost User Interface
| | ... | ${dut_node} | ${sock_vm1_2}
| | ${vhost_if3}= | And Vpp Create Vhost User Interface
| | ... | ${dut_node} | ${sock_vm2_1}
| | ${vhost_if4}= | And Vpp Create Vhost User Interface
| | ... | ${dut_node} | ${sock_vm2_2}
| | And Set Interface State | ${dut_node} | ${vhost_if1} | up
| | And Set Interface State | ${dut_node} | ${vhost_if2} | up
| | And Set Interface State | ${dut_node} | ${vhost_if3} | up
| | And Set Interface State | ${dut_node} | ${vhost_if4} | up
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${101} | ${vxlan1}
| | ... | ${vhost_if1}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${102} | ${vxlan2}
| | ... | ${vhost_if2}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${103} | ${vxlan3}
| | ... | ${vhost_if3}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${104} | ${vxlan4}
| | ... | ${vhost_if4}
| | And Configure QEMU vhost and run it VM | ${dut_node} | ${sock_vm1_1} | ${sock_vm1_2}
| | ... | ${1}
| | And Configure QEMU vhost and run it VM | ${dut_node} | ${sock_vm2_1} | ${sock_vm2_2}
| | ... | ${2}
| | And Check traffic through VM
| | When Run keyword | qemu-1.Qemu Kill
| | ${vm1}= | And Run Keyword | qemu-1.Qemu Start
| | ${vhost_int_1}= | And Get Vhost User If Name By Sock | ${vm1}
| | ... | ${sock_vm1_1}
| | ${vhost_int_2}= | And Get Vhost User If Name By Sock | ${vm1}
| | ... | ${sock_vm1_2}
| | And Linux Add Bridge | ${vm1} | br0 | ${vhost_int_1} | ${vhost_int_2}
| | And Set Interface State | ${vm1} | ${vhost_int_1} | up | if_type=name
| | And Set Interface State | ${vm1} | ${vhost_int_2} | up | if_type=name
| | Then Check traffic through VM


| TC02: VPP reconnects to Qemu vhost-user when Restart VPP and reconfigured
| | [Tags] | EXPECTED_FAILING
| | [Documentation]
| | ... | *Failing:* Qemu doesn't support reconnect prior to version 2.7.
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | ${dut_if1_ip}
| | ... | ${prefix_length}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${tg_if1_ip}
| | ... | ${tg_to_dut_if1_mac}
| | ${vxlan1}= | And Create VXLAN interface | ${dut_node} | ${101}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan2}= | And Create VXLAN interface | ${dut_node} | ${102}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan3}= | And Create VXLAN interface | ${dut_node} | ${103}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan4}= | And Create VXLAN interface | ${dut_node} | ${104}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | And Set Interface State | ${dut_node} | ${vxlan1} | up
| | And Set Interface State | ${dut_node} | ${vxlan2} | up
| | And Set Interface State | ${dut_node} | ${vxlan3} | up
| | And Set Interface State | ${dut_node} | ${vxlan4} | up
| | ${vhost_if1}= | And Vpp Create Vhost User Interface | ${dut_node}
| | ... | ${sock_vm1_1}
| | ${vhost_if2}= | And Vpp Create Vhost User Interface | ${dut_node}
| | ... | ${sock_vm1_2}
| | ${vhost_if3}= | And Vpp Create Vhost User Interface | ${dut_node}
| | ... | ${sock_vm2_1}
| | ${vhost_if4}= | And Vpp Create Vhost User Interface | ${dut_node}
| | ... | ${sock_vm2_2}
| | And Set Interface State | ${dut_node} | ${vhost_if1} | up
| | And Set Interface State | ${dut_node} | ${vhost_if2} | up
| | And Set Interface State | ${dut_node} | ${vhost_if3} | up
| | And Set Interface State | ${dut_node} | ${vhost_if4} | up
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${101} | ${vxlan1}
| | ... | ${vhost_if1}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${102} | ${vxlan2}
| | ... | ${vhost_if2}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${103} | ${vxlan3}
| | ... | ${vhost_if3}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${104} | ${vxlan4}
| | ... | ${vhost_if4}
| | And Configure QEMU vhost and run it VM | ${dut_node} | ${sock_vm1_1} | ${sock_vm1_2}
| | ... | ${1}
| | And Configure QEMU vhost and run it VM | ${dut_node} | ${sock_vm2_1} | ${sock_vm2_2}
| | ... | ${2}
| | And Check traffic through VM
| | And Verify VPP PID in Teardown
| | When Setup All Duts ${nodes}
| | And Save VPP PIDs
| | And Set interfaces in 2-node circular topology up
| | And Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | ${dut_if1_ip}
| | ... | ${prefix_length}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${tg_if1_ip}
| | ... | ${tg_to_dut_if1_mac}
| | ${vxlan1}= | And Create VXLAN interface | ${dut_node} | ${101}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan2}= | And Create VXLAN interface | ${dut_node} | ${102}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan3}= | And Create VXLAN interface | ${dut_node} | ${103}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | ${vxlan4}= | And Create VXLAN interface | ${dut_node} | ${104}
| | ... | ${dut_if1_ip} | ${tg_if1_ip}
| | And Set Interface State | ${dut_node} | ${vxlan1} | up
| | And Set Interface State | ${dut_node} | ${vxlan2} | up
| | And Set Interface State | ${dut_node} | ${vxlan3} | up
| | And Set Interface State | ${dut_node} | ${vxlan4} | up
| | ${vhost_if1}= | And Vpp Create Vhost User Interface | ${dut_node}
| | ... | ${sock_vm1_1}
| | ${vhost_if2}= | And Vpp Create Vhost User Interface | ${dut_node}
| | ... | ${sock_vm1_2}
| | ${vhost_if3}= | And Vpp Create Vhost User Interface | ${dut_node}
| | ... | ${sock_vm2_1}
| | ${vhost_if4}= | And Vpp Create Vhost User Interface | ${dut_node}
| | ... | ${sock_vm2_2}
| | And Set Interface State | ${dut_node} | ${vhost_if1} | up
| | And Set Interface State | ${dut_node} | ${vhost_if2} | up
| | And Set Interface State | ${dut_node} | ${vhost_if3} | up
| | And Set Interface State | ${dut_node} | ${vhost_if4} | up
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${101} | ${vxlan1}
| | ... | ${vhost_if1}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${102} | ${vxlan2}
| | ... | ${vhost_if2}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${103} | ${vxlan3}
| | ... | ${vhost_if3}
| | And Vpp Add L2 Bridge Domain | ${dut_node} | ${104} | ${vxlan4}
| | ... | ${vhost_if4}
| | Then Check traffic through VM


*** Keywords ***
| Configure QEMU vhost and run it VM
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${qemu_id}
| | Import Library | resources.libraries.python.QemuUtils | qemu_id=${qemu_id}
| | ... | WITH NAME | qemu-${qemu_id}
| | ${q_add_vhost}= | Replace Variables | qemu-${qemu_id}.Qemu Add Vhost User If
| | ${q_set_node}= | Replace Variables | qemu-${qemu_id}.Qemu Set Node
| | ${q_start}= | Replace Variables | qemu-${qemu_id}.Qemu Start
| | Run keyword | ${q_set_node} | ${dut_node}
| | Run keyword | ${q_add_vhost} | ${sock1}
| | Run keyword | ${q_add_vhost} | ${sock2}
| | ${vm}= | Run keyword | ${q_start}
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | br0 | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Test Variable | ${qemu-${qemu_id}} | ${vm}

| Check traffic through VM
| | [Documentation] | Send VXLAN traffic through both configured VMs.
| | Send VXLAN encapsulated packet and verify received packet | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_if1_ip} | ${dut_if1_ip} | ${101}
| | ... | ${dut_if1_ip} | ${tg_if1_ip} | ${102}
| | Send VXLAN encapsulated packet and verify received packet | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_if1_ip} | ${dut_if1_ip} | ${103}
| | ... | ${dut_if1_ip} | ${tg_if1_ip} | ${104}
