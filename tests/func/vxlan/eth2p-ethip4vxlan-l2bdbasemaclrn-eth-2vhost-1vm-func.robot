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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/vxlan.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Resource | resources/libraries/robot/qemu.robot
| Resource | resources/libraries/robot/double_qemu_setup.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV | VPP_VM_ENV
| Test Setup | Func Test Setup
| Test Teardown | Run Keywords | Func Test Teardown
| ... | AND | Run keyword | Qemu Teardown | ${dut1_node}
| ...                                     | ${${qemu1}} | ${qemu1}
| ... | AND | Run keyword | Qemu Teardown | ${dut2_node}
| ...                                     | ${${qemu2}} | ${qemu2}
| Documentation | *L2BD with VM combined with VXLAN test cases - IPv4*
| ...
| ... | *[Top] Network topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on
| ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for L2 switching of IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) switching combined with MAC learning enabled;
| ... | VXLAN tunnels are configured between L2BDs on DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent
| ... | in both directions by TG on links to DUT1 and DUT2; on receive TG
| ... | verifies packets for correctness and their IPv4 src-addr, dst-addr
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC7348.

*** Variables ***
| ${vni_1}= | 23

| ${bd_id1}= | 10
| ${bd_id2}= | 20

| ${ip4_addr1}= | 172.16.0.1
| ${ip4_addr2}= | 172.16.0.2
| ${ip4_prefix}= | 24

| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

| ${qemu1}= | qemu_instance_1
| ${qemu2}= | qemu_instance_2

| ${dut1_vhost1}= | dut1_vhost_if1
| ${dut1_vhost2}= | dut1_vhost_if2
| ${dut2_vhost1}= | dut2_vhost_if1
| ${dut2_vhost2}= | dut2_vhost_if2

*** Test Cases ***
| TC01:DUT1 and DUT2 with two L2BDs and VXLANoIPv4 tunnel switch ICMPv4 between TG links and VM links
| | [Documentation]
| | ... | [Top] TG-DUT1-VM-DUT1-DUT2-VM-DUT2-TG.
| | ... | [Enc] Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on DUT1-DUT2; Eth-IPv4-ICMPv4
| | ... | on TG-DUTn and DUTn=VM.
| | ... | [Cfg] On both DUTs configure two L2BDs (MAC learning enabled); first
| | ... | L2BD with untagged interface to TG and vhost-user interface to local
| | ... | VM, second one with vhost-user interface to local VM and VXLAN
| | ... | interface towards the other DUT. Configure linux bridge on both VMs
| | ... | to pass traffic between both vhost-user interfaces.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between two of its interfaces to
| | ... | be switched by DUT1 and DUT2; verify packets are switched between
| | ... | these TG interfaces.
| | ... | [Ref] RFC7348.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut1_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | ...                                                     | ${dut1_vhost1}
| | ...                                                     | ${dut1_vhost2}
| | And VPP Vhost interfaces for L2BD forwarding are setup | ${dut2_node}
| | ...                                                    | ${sock1}
| | ...                                                    | ${sock2}
| | ...                                                    | ${dut2_vhost1}
| | ...                                                    | ${dut2_vhost2}
| | And VM for Vhost L2BD forwarding is setup | ${dut1_node} | ${sock1}
| | ...                                       | ${sock2} | ${qemu1}
| | And VM for Vhost L2BD forwarding is setup | ${dut2_node} | ${sock1}
| | ...                                       | ${sock2} | ${qemu2}
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${ip4_addr1}
| | ...                       | ${ip4_prefix}
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${ip4_addr2}
| | ...                       | ${ip4_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip4_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip4_addr1}
| | ${dut1s_vxlan}= | And Create VXLAN interface | ${dut1_node} | ${vni_1}
| |                 | ...                        | ${ip4_addr1} | ${ip4_addr2}
| | ${dut2s_vxlan}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| |                 | ...                        | ${ip4_addr2} | ${ip4_addr1}
| | And Interfaces are added to BD | ${dut1_node} | ${bd_id1}
| | ...                            | ${dut1_to_tg} | ${${dut1_vhost1}}
| | And Interfaces are added to BD | ${dut1_node} | ${bd_id2}
| | ...                            | ${dut1s_vxlan} | ${${dut1_vhost2}}
| | And Interfaces are added to BD | ${dut2_node} | ${bd_id1}
| | ...                            | ${dut2_to_tg} | ${${dut2_vhost1}}
| | And Interfaces are added to BD | ${dut2_node} | ${bd_id2}
| | ...                            | ${dut2s_vxlan} | ${${dut2_vhost2}}
| | Then Send and receive ICMPv4 bidirectionally
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
