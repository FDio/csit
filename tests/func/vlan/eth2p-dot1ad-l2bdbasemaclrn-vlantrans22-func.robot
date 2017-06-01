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
| Resource | resources/libraries/robot/tagging.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | VM_ENV | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *L2BD with VLAN tag rewrite test cases - translate-2-2*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-dot1ad-IPv4-ICMPv4 or
| ... | Eth-dot1ad-IPv6-ICMPv6 on TG-DUT1 and DUT1-DUT2, Eth-IPv4-ICMPv4 or
| ... | Eth-IPv6-ICMPv6 on TG-DUT2 for L2 switching of IPv4/IPv6.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with bridge domain (L2BD)
| ... | switching combined with MAC learning enabled and added VLAN
| ... | sub-interface with VLAN tag rewrite translate-2-2 method of interface
| ... | towards TG and interface towards DUT2. DUT2 is configured with L2
| ... | bridge domain (L2BD) switching between VLAN sub-interface with VLAN tag
| ... | rewrite pop-2 method of interface towards DUT1 and interface towards TG.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are
| ... | sent from TG on link to DUT1 and received in TG on link form DUT2;
| ... | on receive TG verifies packets for correctness and their IPv4 src-addr,
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* IEEE 802.1q, IEEE 802.1ad.

*** Variables ***
| ${bd_id1}= | 1

| ${subid}= | 10

| ${outer_vlan_id1}= | 110
| ${outer_vlan_id2}= | 120
| ${outer_vlan_wrong}= | 150

| ${inner_vlan_id1}= | 210
| ${inner_vlan_id2}= | 220
| ${inner_vlan_wrong}= | 250

| ${src_ip6}= | 3ffe:63::1
| ${dst_ip6}= | 3ffe:63::2

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2BD and VLAN translate-2-2 switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on TG-DUT1 and \
| | ... | on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | bridge domain (L2BD) with one interface to DUT2 and one Dot1ad
| | ... | sub-interface towards TG with VLAN tag rewrite translate-2-2 method;
| | ... | on DUT2 configure L2 bridge domain (L2BD) with one interface to TG and
| | ... | one Dot1ad sub-interface towards DUT1 with VLAN tag rewrite pop-2
| | ... | tagged with Dot1ad tags from one of its interfaces to another one
| | ... | method. [Ver] Make TG send ICMPv4 Echo Req via DUT1 and DUT2; verify
| | ... | that packet is received. [Ref] IEEE 802.1ad
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create tagged sub-interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1}
| | ... | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Create tagged sub-interface
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2}
| | ... | type_subif=two_tags dot1ad
| | And Configure L2 tag rewrite method on interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-2-2 | push_dot1q=${False}
| | ... | tag1_id=${outer_vlan_id2} | tag2_id=${inner_vlan_id2}
| | And Configure L2 tag rewrite method on interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-2
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${vlan2_index}
| | ...                                     | ${bd_id1}
| | Then Send ICMP packet and verify received packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1ad
| | ... | vlan1=${outer_vlan_id1} | vlan2=${inner_vlan_id1}

| TC02: DUT1 and DUT2 with L2BD and VLAN translate-2-2 with wrong inner tag used (DUT1) switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on TG-DUT1 and \
| | ... | on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | bridge domain (L2BD) with one interface to DUT2 and one Dot1ad
| | ... | sub-interface towards TG with VLAN tag rewrite translate-2-2 method to
| | ... | set inner tag different from inner tag set on Dot1ad sub-interface of
| | ... | DUT2; on DUT2 configure L2 bridge domain (L2BD) with one interface to
| | ... | TG and one Dot1ad sub-interface towards DUT1 with VLAN tag rewrite
| | ... | pop-2 tagged with Dot1ad tags from one of its interfaces to another
| | ... | one method. [Ver] Make TG send ICMPv4 Echo Req via DUT1 and DUT2;
| | ... | verify that packet is not received. [Ref] IEEE 802.1ad
| | [Tags] | SKIP_PATCH
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create tagged sub-interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1}
| | ... | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Create tagged sub-interface
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2}
| | ... | type_subif=two_tags dot1ad
| | And Configure L2 tag rewrite method on interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-2-2 | push_dot1q=${False}
| | ... | tag1_id=${outer_vlan_id2} | tag2_id=${inner_vlan_wrong}
| | And Configure L2 tag rewrite method on interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-2
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${vlan2_index}
| | ...                                     | ${bd_id1}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP packet and verify received packet | ${tg_node} | ${tg_to_dut1}
| | ... | ${tg_to_dut2} | encaps=Dot1ad | vlan1=${outer_vlan_id1}
| | ... | vlan2=${inner_vlan_id1}

| TC03: DUT1 and DUT2 with L2BD and VLAN translate-2-2 with wrong outer tag used (DUT1) switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on TG-DUT1 and \
| | ... | on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | bridge domain (L2BD) with one interface to DUT2 and one Dot1ad
| | ... | sub-interface towards TG with VLAN tag rewrite translate-2-2 method to
| | ... | set outer tag different from outer tag set on Dot1ad sub-interface of
| | ... | DUT2; on DUT2 configure L2 bridge domain (L2BD) with one interface to
| | ... | TG and one Dot1ad sub-interface towards DUT1 with VLAN tag rewrite
| | ... | pop-2 tagged with Dot1ad tags from one of its interfaces to another
| | ... | one method. [Ver] Make TG send ICMPv4 Echo Req via DUT1 and DUT2;
| | ... | verify that packet is not received. [Ref] IEEE 802.1ad
| | [Tags] | SKIP_PATCH
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create tagged sub-interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1}
| | ... | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Create tagged sub-interface
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2}
| | ... | type_subif=two_tags dot1ad
| | And Configure L2 tag rewrite method on interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-2-2 | push_dot1q=${False}
| | ... | tag1_id=${outer_vlan_wrong} | tag2_id=${inner_vlan_id2}
| | And Configure L2 tag rewrite method on interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-2
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${vlan2_index}
| | ...                                     | ${bd_id1}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP packet and verify received packet | ${tg_node} | ${tg_to_dut1}
| | ... | ${tg_to_dut2} | encaps=Dot1ad | vlan1=${outer_vlan_id1}
| | ... | vlan2=${inner_vlan_id1}

| TC04: DUT1 and DUT2 with L2BD and VLAN translate-2-2 with wrong outer and inner tags used (DUT1) switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on TG-DUT1 and \
| | ... | on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | bridge domain (L2BD) with one interface to DUT2 and one Dot1ad
| | ... | sub-interface towards TG with VLAN tag rewrite translate-2-2 method to
| | ... | set tags different from tags set on Dot1ad sub-interface of DUT2;
| | ... | on DUT2 configure L2 bridge domain (L2BD) with one interface to TG
| | ... | and one Dot1ad sub-interface towards DUT1 with VLAN tag rewrite pop-2
| | ... | tagged with Dot1ad tags from one of its interfaces to another one
| | ... | method. [Ver] Make TG send ICMPv4 Echo Req via DUT1 and DUT2; verify
| | ... | that packet is not received. [Ref] IEEE 802.1ad
| | [Tags] | SKIP_PATCH
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create tagged sub-interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1}
| | ... | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Create tagged sub-interface
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2}
| | ... | type_subif=two_tags dot1ad
| | And Configure L2 tag rewrite method on interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-2-2 | push_dot1q=${False}
| | ... | tag1_id=${outer_vlan_wrong} | tag2_id=${inner_vlan_wrong}
| | And Configure L2 tag rewrite method on interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-2
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${vlan2_index}
| | ...                                     | ${bd_id1}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP packet and verify received packet | ${tg_node} | ${tg_to_dut1}
| | ... | ${tg_to_dut2} | encaps=Dot1ad | vlan1=${outer_vlan_id1}
| | ... | vlan2=${inner_vlan_id1}

| TC05: DUT1 and DUT2 with L2BD and VLAN translate-2-2 switch ICMPv6 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv6-ICMPv6 on TG-DUT1 and \
| | ... | on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | bridge domain (L2BD) with one interface to DUT2 and one Dot1ad
| | ... | sub-interface towards TG with VLAN tag rewrite translate-2-2 method;
| | ... | on DUT2 configure L2 bridge domain (L2BD) with one interface to TG and
| | ... | one Dot1ad sub-interface towards DUT1 with VLAN tag rewrite pop-1
| | ... | tagged with Dot1ad tags from one of its interfaces to another one
| | ... | method. [Ver] Make TG send ICMPv6 Echo Req via DUT1 and DUT2; verify
| | ... | that packet is received. [Ref] IEEE 802.1ad
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create tagged sub-interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1}
| | ... | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Create tagged sub-interface
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2}
| | ... | type_subif=two_tags dot1ad
| | And Configure L2 tag rewrite method on interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-2-2 | push_dot1q=${False}
| | ... | tag1_id=${outer_vlan_id2} | tag2_id=${inner_vlan_id2}
| | And Configure L2 tag rewrite method on interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-2
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${vlan2_index}
| | ...                                     | ${bd_id1}
| | Then Send ICMP packet and verify received packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | src_ip=${src_ip6}
| | ... | dst_ip=${dst_ip6} | encaps=Dot1ad | vlan1=${outer_vlan_id1}
| | ... | vlan2=${inner_vlan_id1}

| TC06: DUT1 and DUT2 with L2BD and VLAN translate-2-2 with wrong inner tag used (DUT1) switch ICMPv6 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv6-ICMPv6 on TG-DUT1 and \
| | ... | on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | bridge domain (L2BD) with one interface to DUT2 and one Dot1ad
| | ... | sub-interface towards TG with VLAN tag rewrite translate-2-2 method to
| | ... | set inner tag different from inner tag set on Dot1ad sub-interface of
| | ... | DUT2; on DUT2 configure L2 bridge domain (L2BD) with one interface to
| | ... | TG and one Dot1ad sub-interface towards DUT1 with VLAN tag rewrite
| | ... | pop-1 tagged with Dot1ad tags from one of its interfaces to another
| | ... | one method. [Ver] Make TG send ICMPv6 Echo Req via DUT1 and DUT2;
| | ... | verify that packet is not received. [Ref] IEEE 802.1ad
| | [Tags] | SKIP_PATCH
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create tagged sub-interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1}
| | ... | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Create tagged sub-interface
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2}
| | ... | type_subif=two_tags dot1ad
| | And Configure L2 tag rewrite method on interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-2-2 | push_dot1q=${False}
| | ... | tag1_id=${outer_vlan_id2} | tag2_id=${inner_vlan_wrong}
| | And Configure L2 tag rewrite method on interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-2
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${vlan2_index}
| | ...                                     | ${bd_id1}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP packet and verify received packet | ${tg_node} | ${tg_to_dut1}
| | ... | ${tg_to_dut2} | src_ip=${src_ip6} | dst_ip=${dst_ip6} | encaps=Dot1ad
| | ... | vlan1=${outer_vlan_id1} | vlan2=${inner_vlan_id1}

| TC07: DUT1 and DUT2 with L2BD and VLAN translate-2-2 with wrong outer tag used (DUT1) switch ICMPv6 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv6-ICMPv6 on TG-DUT1 and \
| | ... | on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | bridge domain (L2BD) with one interface to DUT2 and one Dot1ad
| | ... | sub-interface towards TG with VLAN tag rewrite translate-2-2 method to
| | ... | set outer tag different from outer tag set on Dot1ad sub-interface of
| | ... | DUT2; on DUT2 configure L2 bridge domain (L2BD) with one interface to
| | ... | TG and one Dot1ad sub-interface towards DUT1 with VLAN tag rewrite
| | ... | pop-1 tagged with Dot1ad tags from one of its interfaces to another
| | ... | one method. [Ver] Make TG send ICMPv6 Echo Req via DUT1 and DUT2;
| | ... | verify that packet is not received. [Ref] IEEE 802.1ad
| | [Tags] | SKIP_PATCH
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create tagged sub-interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1}
| | ... | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Create tagged sub-interface
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2}
| | ... | type_subif=two_tags dot1ad
| | And Configure L2 tag rewrite method on interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-2-2 | push_dot1q=${False}
| | ... | tag1_id=${outer_vlan_wrong} | tag2_id=${inner_vlan_id2}
| | And Configure L2 tag rewrite method on interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-2
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${vlan2_index}
| | ...                                     | ${bd_id1}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP packet and verify received packet | ${tg_node} | ${tg_to_dut1}
| | ... | ${tg_to_dut2} | src_ip=${src_ip6} | dst_ip=${dst_ip6} | encaps=Dot1ad
| | ... | vlan1=${outer_vlan_id1} | vlan2=${inner_vlan_id1}

| TC08: DUT1 and DUT2 with L2BD and VLAN translate-2-2 with wrong outer and inner tags used (DUT1) switch ICMPv6 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv6-ICMPv6 on TG-DUT1 and \
| | ... | on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | bridge domain (L2BD) with one interface to DUT2 and one Dot1ad
| | ... | sub-interface towards TG with VLAN tag rewrite translate-2-2 method to
| | ... | set tags different from tags set on Dot1ad sub-interface of DUT2;
| | ... | on DUT2 configure L2 bridge domain (L2BD) with one interface to TG
| | ... | and one Dot1ad sub-interface towards DUT1 with VLAN tag rewrite pop-1
| | ... | tagged with Dot1ad tags from one of its interfaces to another one
| | ... | method. [Ver] Make TG send ICMPv6 Echo Req via DUT1 and DUT2; verify
| | ... | that packet is not received. [Ref] IEEE 802.1ad
| | [Tags] | SKIP_PATCH
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create tagged sub-interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1}
| | ... | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Create tagged sub-interface
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2}
| | ... | type_subif=two_tags dot1ad
| | And Configure L2 tag rewrite method on interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-2-2 | push_dot1q=${False}
| | ... | tag1_id=${outer_vlan_wrong} | tag2_id=${inner_vlan_wrong}
| | And Configure L2 tag rewrite method on interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-2
| | And Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut2_node} | ${vlan2_index}
| | ...                                     | ${bd_id1}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP packet and verify received packet | ${tg_node} | ${tg_to_dut1}
| | ... | ${tg_to_dut2} | src_ip=${src_ip6} | dst_ip=${dst_ip6} | encaps=Dot1ad
| | ... | vlan1=${outer_vlan_id1} | vlan2=${inner_vlan_id1}
