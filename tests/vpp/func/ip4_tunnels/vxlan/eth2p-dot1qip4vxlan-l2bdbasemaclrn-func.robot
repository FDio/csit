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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/overlay/vxlan.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *RFC7348 VXLAN: Bridge-domain with VXLAN over VLAN test cases*
| ...
| ... | *[Top] Network topologies:* TG-DUT1-DUT2-TG 3-node circular topology with
| ... | single links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-dot1q-IPv4-VXLAN-Eth-IPv4-ICMPv4 on
| ... | DUT1-DUT2, Eth-dot1q-IPv4-ICMPv4 on TG-DUTn for L2 switching of IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) switching combined with static MACs, MAC learning
| ... | enabled and Split Horizon Groups (SHG) depending on test case; VXLAN
| ... | tunnels are configured between L2BDs on DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are
| ... | sent in both directions by TG on links to DUT1 and DUT2; on receive TG
| ... | verifies packets for correctness and their IPv4 src-addr, dst-addr and
| ... | MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC7348.

*** Variables ***
| ${VNI}= | 23
| ${BID}= | 23
| ${VLAN}= | 10

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2BD and VXLANoIPv4oVLAN tunnels switch ICMPv4 between TG links
| | [Tags] | EXPECTED_FAILING
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-dot1q-IPv4-VXLAN-Eth-IPv4-ICMPv4 on\
| | ... | DUT1-DUT2; Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 bridge-domain (MAC learning enabled), each with one
| | ... | interface to TG and one VXLAN tunnel interface towards the other DUT
| | ... | over VLAN sub-interface. [Ver] Make TG send ICMPv4 Echo Req between
| | ... | two of its interfaces, verify all packets are received. [Ref] RFC7348.
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Create vlan interfaces for VXLAN | ${VLAN}
| | ... | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${dut2_node} | ${dut2_to_dut1}
| | And Configure IP addresses and neighbors on interfaces
| | ... | ${dut1_node} | ${dut1s_vlan_name} | ${dut1s_vlan_index}
| | ... | ${dut2_node} | ${dut2s_vlan_name} | ${dut2s_vlan_index}
| | ${dut1s_vxlan}= | When Create VXLAN interface | ${dut1_node} | ${VNI}
| | | ... | ${dut1s_ip_address} | ${dut2s_ip_address}
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan} | up
| | And Add interfaces to L2BD | ${dut1_node} | ${BID}
| | ... | ${dut1_to_tg} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | And Create VXLAN interface | ${dut2_node} | ${VNI}
| | | ... | ${dut2s_ip_address} | ${dut1s_ip_address}
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan} | up
| | And Add interfaces to L2BD | ${dut2_node} | ${BID}
| | ... | ${dut2_to_tg} | ${dut2s_vxlan}
| | Then Send ICMPv4 bidirectionally and verify received packets
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
