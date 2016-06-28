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
| Documentation | *L2 cross-connect with QinQ test cases*
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
| ${outer_vlan_id}= | 100
| ${inner_vlan_id}= | 200
| ${type_subif}= | two_tags
| ${tag_rewrite_method}= | pop-2

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2XC and two VLAN push-pop switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1ad-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 cross-connect (L2XC), each with one interface to TG
| | ... | and one Ethernet interface towards the other DUT; each DUT
| | ... | pushes two VLAN tags on packets received from local TG, and
| | ... | popping two VLAN tags on packets transmitted to local TG. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref] 802dot1ad.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1_node} | ${subif_index_1} | ${dut2_node} | ${subif_index_2}
| | ... | ${tag_rewrite_method}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subif_index_1}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${subif_index_2}
| | Then Send and receive ICMP Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
