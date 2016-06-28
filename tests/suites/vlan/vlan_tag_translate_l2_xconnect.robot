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
| ${inner_vlan_id1}= | 220
| ${inner_vlan_wrong}= | 250

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2XC and two VLAN push-pop switch ICMPv4 between two TG links
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
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${outer_vlan_id1}
| | ${vlan21_name} | ${vlan21_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id1}
| | ${vlan22_name} | ${vlan22_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_tg} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${dut1_to_tg} | push-1 | ${outer_vlan_id1}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan21_index} | translate-1-1 | ${outer_vlan_id2}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_tg} | ${vlan1_index}
| | ... | ${dut2_node} | ${vlan21_index} | ${vlan22_index}
| | Then Send and receive ICMP Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}

| TC02: DUT1 and DUT2 with L2XC and VLAN translate-1-1 - negative
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
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${outer_vlan_id1}
| | ${vlan21_name} | ${vlan21_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${outer_vlan_id1}
| | ${vlan22_name} | ${vlan22_index}= | And Vlan Subinterface Created
| | ... | ${dut2_node} | ${dut2_to_tg} | ${outer_vlan_id2}
| | And L2 Tag Rewrite Method Set On Interface | ${dut1_node} | ${dut1_to_tg} | push-1 | ${outer_vlan_id1}
| | And L2 Tag Rewrite Method Set On Interface | ${dut2_node} | ${vlan21_index} | translate-1-1 | ${outer_vlan_wrong}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_tg} | ${vlan1_index}
| | ... | ${dut2_node} | ${vlan21_index} | ${vlan22_index}
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send and receive ICMP Packet| ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}

*** Keywords ***
| Vlan Subinterface Created
| | [Documentation] | Create VLAN subinterface on DUT
| | [Arguments] | ${dut_node} | ${interface} | ${vlan_id}
| | [Return] | ${vlan_name} | ${vlan_index}
| | ${interface_name}= | Get interface name | ${dut_node} | ${interface}
| | ${vlan_name} | ${vlan_index}= | Create Vlan Subinterface
| | ... | ${dut_node} | ${interface_name} | ${vlan_id}

| L2 Tag Rewrite Method Set On Interface
| | [Documentation] | Set L2 tag rewrite on (sub)interface on DUT
| | [Arguments] | ${dut_node} | ${interface} | ${tag_rewrite_method} | ${tag1_id}=${None} | ${tag2_id}=${None}
| | ${result}= | Evaluate | isinstance($interface, int)
| | ${interface_name}= | Run Keyword If | ${result} | Set Variable | ${interface}
| | ...                | ELSE | Get interface name | ${dut_node} | ${interface}
| | L2 Tag Rewrite | ${dut_node} | ${interface_name} | ${tag_rewrite_method} | ${tag1_id} | ${tag2_id}
