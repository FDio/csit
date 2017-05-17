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
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | VM_ENV | SKIP_VPP_PATCH
| Test Setup | Func Test Setup
| Test Teardown | Func Test Teardown
| Documentation | *L2XC with VLAN tag rewrite test cases - translate-1-1*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-dot1q-IPv4-ICMPv4 or
| ... | Eth-dot1q-IPv6-ICMPv6 on TG-DUT1 and DUT1-DUT2, Eth-IPv4-ICMPv4 or
| ... | Eth-IPv4-ICMPv4 on TG-DUT2 for L2 switching of IPv4/IPv6.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with L2 cross-connect
| ... | (L2XC) switching between VLAN sub-interface with VLAN tag rewrite
| ... | translate-1-1 method of interface towards TG and interface towards DUT2.
| ... | DUT2 is configured configured with L2 cross-connect (L2XC) switching
| ... | between VLAN sub-interface with VLAN tag rewrite pop-1 method
| ... | of interface towards DUT1 and interface towards TG.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are
| ... | sent from TG on link to DUT1 and received in TG on link form DUT2;
| ... | on receive TG verifies packets for correctness and their IPv4 src-addr,
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* IEEE 802.1q, IEEE 802.1ad.

*** Variables ***
| ${subid}= | 10

| ${outer_vlan_id1}= | 110
| ${outer_vlan_id2}= | 120
| ${outer_vlan_wrong}= | 150

| ${src_ip}= | 3ffe:63::1
| ${dst_ip}= | 3ffe:63::2

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2XC and VLAN translate-1-1 (DUT1) switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1q-IPv4-ICMPv4 on TG-DUT1 and \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | cross-connect (L2XC) with one interface to DUT2 and one VLAN
| | ... | sub-interface towards TG with VLAN tag rewrite translate-1-1 method;
| | ... | on DUT2 configure L2 cross-connect (L2XC) with one interface to TG
| | ... | and one VLAN sub-interface towards DUT1 with VLAN tag rewrite pop-1
| | ... | method. [Ver] Make TG send ICMPv4 Echo Req tagged with one Dot1q tag
| | ... | from one of its interfaces to another one via DUT1 and DUT2; verify
| | ... | that packet is received. [Ref] IEEE 802.1q
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Is Set On Interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-1-1 | tag1_id=${outer_vlan_id2}
| | And L2 Tag Rewrite Method Is Set On Interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-1
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Send and receive ICMP Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | encaps=Dot1q
| | ... | vlan1=${outer_vlan_id1}

| TC02: DUT1 and DUT2 with L2XC and VLAN translate-1-1 with wrong tag used (DUT1) switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1q-IPv4-ICMPv4 on TG-DUT1 and \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | cross-connect (L2XC) with one VLAN tagged sub-interface to DUT2 and
| | ... | one VLAN sub-interface towards TG with VLAN tag rewrite
| | ... | (translate-1-1) on sub-interface to DUT2; on DUT2 configure L2XC with
| | ... | one interface to TG and one VLAN sub-interface towards DUT1 with VLAN
| | ... | tag pop-1. [Ver] Make TG send ICMPv4 Echo Req tagged with one dot1q
| | ... | tag from one of its interfaces to another one via DUT1 and DUT2;
| | ... | verify that packet is not received. [Ref] IEEE 802.1q
| | [Tags] | SKIP_PATCH
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Is Set On Interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-1-1 | tag1_id=${outer_vlan_wrong}
| | And L2 Tag Rewrite Method Is Set On Interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-1
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send and receive ICMP Packet | ${tg_node} | ${tg_to_dut1}
| | ... | ${tg_to_dut2} | encaps=Dot1q | vlan1=${outer_vlan_id1}

| TC03: DUT1 and DUT2 with L2XC and VLAN translate-1-1 (DUT1) switch ICMPv6 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1q-IPv6-ICMPv6 on TG-DUT1 and \
| | ... | DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | cross-connect (L2XC) with one interface to DUT2 and one VLAN
| | ... | sub-interface towards TG with VLAN tag rewrite translate-1-1 method;
| | ... | on DUT2 configure L2 cross-connect (L2XC) with one interface to TG
| | ... | and one VLAN sub-interface towards DUT1 with VLAN tag rewrite pop-1
| | ... | method. [Ver] Make TG send ICMPv6 Echo Req tagegd with one Dot1q tag
| | ... | from one of its interfaces to another one via DUT1 and DUT2; verify
| | ... | that packet is received. [Ref] IEEE 802.1q
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Is Set On Interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-1-1 | tag1_id=${outer_vlan_id2}
| | And L2 Tag Rewrite Method Is Set On Interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-1
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Send and receive ICMP Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | src_ip=${src_ip}
| | ... | dst_ip=${dst_ip} | encaps=Dot1q | vlan1=${outer_vlan_id1}

| TC04: DUT1 and DUT2 with L2XC and VLAN translate-1-1 with wrong tag used (DUT1) switch ICMPv6 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1q-IPv6-ICMPv6 on TG-DUT1 and \
| | ... | DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUT2. [Cfg] On DUT1 configure L2
| | ... | cross-connect (L2XC) with one interface to DUT2 and one VLAN
| | ... | sub-interface towards TG with VLAN tag rewrite translate-1-1 method
| | ... | to set tag different from tag set on VLAN sub-interface of DUT2;
| | ... | on DUT2 configure L2 cross-connect (L2XC) with one interface to TG
| | ... | and one VLAN sub-interface towards DUT1 with VLAN tag rewrite pop-1
| | ... | method. [Ver] Make TG send ICMPv6 Echo Req tagegd with one Dot1q tag
| | ... | from one of its interfaces to another one via DUT1 and DUT2; verify
| | ... | that packet is not received. [Ref] IEEE 802.1q
| | [Tags] | SKIP_PATCH
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${vlan1_name} | ${vlan1_index}= | When Vlan Subinterface Created
| | ... | ${dut1_node} | ${dut1_to_tg} | ${outer_vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Is Set On Interface | ${dut1_node}
| | ... | ${vlan1_index} | translate-1-1 | tag1_id=${outer_vlan_wrong}
| | And L2 Tag Rewrite Method Is Set On Interface | ${dut2_node}
| | ... | ${vlan2_index} | pop-1
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${vlan1_index}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${vlan2_index}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send and receive ICMP Packet | ${tg_node} | ${tg_to_dut1}
| | ... | ${tg_to_dut2} | src_ip=${src_ip} | dst_ip=${dst_ip} | encaps=Dot1q
| | ... | vlan1=${outer_vlan_id1}
