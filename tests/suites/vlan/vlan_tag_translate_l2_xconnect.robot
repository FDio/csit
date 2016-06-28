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
| Resource | resources/libraries/robot/tagging.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | VM_ENV
| Test Setup | Setup all DUTs before test
| Suite Setup | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *L2 cross-connect with VLAN tag rewrite  test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology with
| ... | single links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-dot1ad-IPv4-ICMPv4 on DUT1-DUT2,
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for L2 switching of IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | cross-connect (L2XC) switching with 802.1ad QinQ VLAN tag push and pop.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are
| ... | sent in both directions by TG on links to DUT1 and DUT2; on receive TG
| ... | verifies packets for correctness and their IPv4 src-addr, dst-addr and
| ... | MAC addresses.
| ... | *[Ref] Applicable standard specifications:* IEEE 802.1ad.

*** Variables ***
| ${subid}= | 10
| ${outer_vlan_id1}= | 110
| ${outer_vlan_id2}= | 120
| ${outer_vlan_wrong}= | 150
| ${inner_vlan_id1}= | 210
| ${inner_vlan_id2}= | 220
| ${inner_vlan_wrong}= | 250

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2XC and VLAN translate-1-1 switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 cross-connect (L2XC), each with one interface to TG
| | ... | and one VLAN sub-interface towards the other DUT; each DUT
| | ... | pushes two VLAN tags on packets received from local TG, and
| | ... | popping two VLAN tags on packets transmitted to local TG. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref] 802dot1q.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${vlan1_index} | translate-1-1 | tag1_id=${outer_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan2_index} | pop-1
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Send and receive ICMP Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1q | vlan1=${outer_vlan_id1}

| TC02: DUT1 and DUT2 with L2XC and VLAN translate-1-1 - wrong tag used
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 cross-connect (L2XC), each with one interface to TG
| | ... | and one VLAN sub-interface towards the other DUT; each DUT
| | ... | pushes two VLAN tags on packets received from local TG, and
| | ... | popping two VLAN tags on packets transmitted to local TG. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref] 802dot1q.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${vlan1_index} | translate-1-1 | tag1_id=${outer_vlan_wrong}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan2_index} | pop-1
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send and receive ICMP Packet | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1q | vlan1=${outer_vlan_id1}

| TC03: DUT1 and DUT2 with L2XC and VLAN translate-1-2 switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 cross-connect (L2XC), each with one interface to TG
| | ... | and one VLAN sub-interface towards the other DUT; each DUT
| | ... | pushes two VLAN tags on packets received from local TG, and
| | ... | popping two VLAN tags on packets transmitted to local TG. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref] 802dot1q.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Tagged Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid} | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2} | type_subif=two_tags dot1ad
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${vlan1_index} | translate-1-2 | push_dot1q=Disabled | tag1_id=${outer_vlan_id2} | tag2_id=${inner_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan2_index} | pop-2
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Send and receive ICMP Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1q | vlan1=${outer_vlan_id1}

| TC04: DUT1 and DUT2 with L2XC and VLAN translate-1-2 switch ICMPv4 between two TG links - wrong inner tag used
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 cross-connect (L2XC), each with one interface to TG
| | ... | and one VLAN sub-interface towards the other DUT; each DUT
| | ... | pushes two VLAN tags on packets received from local TG, and
| | ... | popping two VLAN tags on packets transmitted to local TG. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref] 802dot1q.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Tagged Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid} | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2} | type_subif=two_tags dot1ad
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${vlan1_index} | translate-1-2 | push_dot1q=Disabled | tag1_id=${outer_vlan_id2} | tag2_id=${inner_vlan_wrong}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan2_index} | pop-2
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send and receive ICMP Packet | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1q | vlan1=${outer_vlan_id1}

| TC05: DUT1 and DUT2 with L2XC and VLAN translate-1-2 switch ICMPv4 between two TG links - wrong outer tag used
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 cross-connect (L2XC), each with one interface to TG
| | ... | and one VLAN sub-interface towards the other DUT; each DUT
| | ... | pushes two VLAN tags on packets received from local TG, and
| | ... | popping two VLAN tags on packets transmitted to local TG. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref] 802dot1q.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Tagged Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid} | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2} | type_subif=two_tags dot1ad
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${vlan1_index} | translate-1-2 | push_dot1q=Disabled | tag1_id=${outer_vlan_wrong} | tag2_id=${inner_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan2_index} | pop-2
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send and receive ICMP Packet | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1q | vlan1=${outer_vlan_id1}

| TC06: DUT1 and DUT2 with L2XC and VLAN translate-1-2 switch ICMPv4 between two TG links - wrong outer and inner tags used
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 cross-connect (L2XC), each with one interface to TG
| | ... | and one VLAN sub-interface towards the other DUT; each DUT
| | ... | pushes two VLAN tags on packets received from local TG, and
| | ... | popping two VLAN tags on packets transmitted to local TG. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref] 802dot1q.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Tagged Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${subid} | outer_vlan_id=${outer_vlan_id2} | inner_vlan_id=${inner_vlan_id2} | type_subif=two_tags dot1ad
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${vlan1_index} | translate-1-2 | push_dot1q=Disabled | tag1_id=${outer_vlan_wrong} | tag2_id=${inner_vlan_wrong}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan2_index} | pop-2
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send and receive ICMP Packet | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1q | vlan1=${outer_vlan_id1}

| TC07: DUT1 and DUT2 with L2XC and VLAN translate-2-1 switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 cross-connect (L2XC), each with one interface to TG
| | ... | and one VLAN sub-interface towards the other DUT; each DUT
| | ... | pushes two VLAN tags on packets received from local TG, and
| | ... | popping two VLAN tags on packets transmitted to local TG. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref] 802dot1q.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Tagged Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subid} | outer_vlan_id=${outer_vlan_id1} | inner_vlan_id=${inner_vlan_id1} | type_subif=two_tags dot1ad
| | ${vlan2_name} | ${vlan2_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${vlan1_index} | translate-2-1 | tag1_id=${outer_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan2_index} | pop-1
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Send and receive ICMP Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1ad | vlan1=${outer_vlan_id1} | vlan2=${outer_vlan_id2}
