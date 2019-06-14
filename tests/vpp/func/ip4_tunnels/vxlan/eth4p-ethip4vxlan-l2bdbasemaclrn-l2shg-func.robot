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
| Library  | resources.libraries.python.Trace
| ...
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Resource | resources/libraries/robot/overlay/vxlan.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/vm/qemu.robot
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| ...
| Test Setup | Set up functional test
| ...
| Test Teardown | Tear down functional test
| ...
| Documentation | *L2BD with SHG combined with VXLAN test cases - IPv4*
| ...
| ... | *[Top] Network topologies:* TG=DUT1=DUT2=TG 3-node circular topology
| ... | with double parallel links.
| ... | *[Enc] Packet encapsulations:* Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on
| ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for L2 switching of IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) switching combined with MAC learning enabled
| ... | and Split Horizon Groups (SHG); VXLAN tunnels are configured
| ... | between L2BDs on DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent
| ... | in both directions by TG on links to DUT1 and DUT2; on receive TG
| ... | verifies packets for correctness and their IPv4 src-addr, dst-addr
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC7348.

*** Variables ***
| ${vni_1}= | 23
| ${vni_2}= | 35

| ${bd_id1}= | 10
| ${bd_id2}= | 20
| ${bd_id3}= | 30
| ${shg1}= | 1
| ${shg2}= | 2

| ${ip4_addr1}= | 172.16.0.1
| ${ip4_addr2}= | 172.16.0.2
| ${ip4_prefix}= | 24

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2BD and VXLANoIPv4 tunnels in SHG switch ICMPv4 between TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG. [Enc] Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2; Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 configure L2
| | ... | bridge-domain (MAC learning enabled) with two untagged interfaces
| | ... | to TG and two VXLAN interfaces towards the DUT2 and put both VXLAN
| | ... | interfaces into the same Split-Horizon-Group (SHG). On DUT2 configure
| | ... | two L2 bridge-domain (MAC learning enabled), each with one untagged
| | ... | interface to TG and one VXLAN interface towards the DUT1. [Ver] Make
| | ... | TG send ICMPv4 Echo Reqs between all four of its interfaces to be
| | ... | switched by DUT1 and DUT2; verify packets are not switched between
| | ... | TG interfaces connected to DUT2 that are isolated by SHG on DUT1.
| | ... | [Ref] RFC7348.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Configure path for 3-node BD-SHG test | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['DUT2']}
| | And Set interfaces in 3-node BD-SHG test up
| | And VPP Interface Set IP Address | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${ip4_addr1} | ${ip4_prefix}
| | And VPP Interface Set IP Address | ${dut2_node} | ${dut2_to_dut1}
| | ... | ${ip4_addr2} | ${ip4_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip4_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip4_addr1}
| | ${dut1s_vxlan1}= | When Create VXLAN interface | ${dut1_node} | ${vni_1}
| | | ... | ${ip4_addr1} | ${ip4_addr2}
| | ${dut1s_vxlan2}= | And Create VXLAN interface | ${dut1_node} | ${vni_2}
| | | ... | ${ip4_addr1} | ${ip4_addr2}
| | ${dut2s_vxlan1}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| | | ... | ${ip4_addr2} | ${ip4_addr1}
| | ${dut2s_vxlan2}= | And Create VXLAN interface | ${dut2_node} | ${vni_2}
| | | ... | ${ip4_addr2} | ${ip4_addr1}
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan1} | up
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan2} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan1} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan2} | up
| | And Vpp Node Interfaces Ready Wait | ${dut1_node}
| | And Vpp Node Interfaces Ready Wait | ${dut2_node}
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_tg_if1}
| | ... | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_tg_if2}
| | ... | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1s_vxlan1}
| | ... | ${bd_id1} | ${shg1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1s_vxlan2}
| | ... | ${bd_id1} | ${shg1}
| | And Create bridge domain | ${dut2_node} | ${bd_id2}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg_if1}
| | ... | ${bd_id2}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2s_vxlan1}
| | ... | ${bd_id2}
| | And Create bridge domain | ${dut2_node} | ${bd_id3}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg_if2}
| | ... | ${bd_id3}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2s_vxlan2}
| | ... | ${bd_id3}
| | Then Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if1} | ${tg_to_dut2_if1}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if1} | ${tg_to_dut2_if2}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if2} | ${tg_to_dut2_if1}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if2} | ${tg_to_dut2_if2}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMPv4 bidirectionally and verify received packets
| | ... | ${tg_node} | ${tg_to_dut2_if1} | ${tg_to_dut2_if2}

| TC01: DUT1 and DUT2 with L2BD and VXLANoIPv4 tunnels in different SHGs switch ICMPv4 between TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG.[Enc] Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2; Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 configure L2
| | ... | bridge-domain (MAC learning enabled) with two untagged interfaces
| | ... | to TG and two VXLAN interfaces towards the DUT2 and put both VXLAN
| | ... | interfaces into the different Split-Horizon-Group (SHGs). On DUT2
| | ... | configure two L2 bridge-domain (MAC learning enabled), each with one
| | ... | untagged interface to TG and one VXLAN interface towards the DUT1.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between all four of its interfaces
| | ... | to be switched by DUT1 and DUT2; verify packets are switched between
| | ... | all TG interfaces. [Ref] RFC7348.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Configure path for 3-node BD-SHG test | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['DUT2']}
| | And Set interfaces in 3-node BD-SHG test up
| | And VPP Interface Set IP Address | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${ip4_addr1} | ${ip4_prefix}
| | And VPP Interface Set IP Address | ${dut2_node} | ${dut2_to_dut1}
| | ... | ${ip4_addr2} | ${ip4_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip4_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip4_addr1}
| | ${dut1s_vxlan1}= | When Create VXLAN interface | ${dut1_node} | ${vni_1}
| | | ... | ${ip4_addr1} | ${ip4_addr2}
| | ${dut1s_vxlan2}= | And Create VXLAN interface | ${dut1_node} | ${vni_2}
| | | ... | ${ip4_addr1} | ${ip4_addr2}
| | ${dut2s_vxlan1}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| | | ... | ${ip4_addr2} | ${ip4_addr1}
| | ${dut2s_vxlan2}= | And Create VXLAN interface | ${dut2_node} | ${vni_2}
| | | ... | ${ip4_addr2} | ${ip4_addr1}
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan1} | up
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan2} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan1} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan2} | up
| | And Vpp Node Interfaces Ready Wait | ${dut1_node}
| | And Vpp Node Interfaces Ready Wait | ${dut2_node}
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_tg_if1}
| | ... | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_tg_if2}
| | ... | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1s_vxlan1}
| | ... | ${bd_id1} | ${shg1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1s_vxlan2}
| | ... | ${bd_id1} | ${shg2}
| | And Create bridge domain | ${dut2_node} | ${bd_id2}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg_if1}
| | ... | ${bd_id2}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2s_vxlan1}
| | ... | ${bd_id2}
| | And Create bridge domain | ${dut2_node} | ${bd_id3}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg_if2}
| | ... | ${bd_id3}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2s_vxlan2}
| | ... | ${bd_id3}
| | Then Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if1} | ${tg_to_dut2_if1}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if1} | ${tg_to_dut2_if2}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if2} | ${tg_to_dut2_if1}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if2} | ${tg_to_dut2_if2}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut2_if1} | ${tg_to_dut2_if2}
