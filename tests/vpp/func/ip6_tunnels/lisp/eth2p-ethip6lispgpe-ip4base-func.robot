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
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Trace
| ...
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Resource | resources/libraries/robot/overlay/lisp_static_adjacency.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| ...
# import additional Lisp settings from resource file
| Variables | resources/test_data/lisp/static_adjacency/lisp_static_adjacency.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
| ... | VM_ENV | HW_ENV
| ...
| Test Setup | Set up functional test
| ...
| Test Teardown | Tear down functional test
| ...
| Documentation | *LISP static adjacency test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv6-LISP-IPv4-ICMPv4 on\
| ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv6\
| ... | tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4\
| ... | routing and static routes. LISPoIPv6 tunnel is configured\
| ... | between DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets\
| ... | are sent in both directions by TG on links to DUT1 and DUT2; on receive\
| ... | TG verifies packets for correctness and their IPv4 src-addr,\
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISPoIPv6 tunnel
| | [Tags] | EXPECTED_FAILING
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv6-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on\
| | ... | TG-DUTn.
| | ... | [Cfg] On DUT1 and DUT2 configure IPv6 LISP static adjacencies.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP tunnel between them; verify IPv4 headers on received\
| | ... | packets are correct.
| | ... | [Cfg2] Reconf LISP.
| | ... | [Ver2] Verify packets are received again via LISP tunnel.
| | ... | [Ref] RFC6830.
| | ...
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Configure IP addresses on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${dut1_to_dut2_ip4o6} | ${dut_prefix4o6}
| | ... | ${dut1_node} | ${dut1_to_tg}
| | ... | ${dut1_to_tg_ip4o6} | ${tg_prefix4o6}
| | ... | ${dut2_node} | ${dut2_to_dut1}
| | ... | ${dut2_to_dut1_ip4o6} | ${dut_prefix4o6}
| | ... | ${dut2_node} | ${dut2_to_tg}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4o6}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4o6}
| | VPP Add IP Neighbor
| | ... | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4o6} | ${tg_to_dut2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4o6} | ${tg_to_dut1_mac}
| | And Vpp All RA Suppress Link Layer | ${nodes}
| | When Configure LISP topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip4o6} | ${tg2_ip4o6}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip4o6} | ${tg1_ip4o6}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
| | When Change LISP Configuration | ${dut1_node} | ${dut2_node}
| | ... | ${dut1_to_dut2} | ${dut2_to_dut1} | ${dut1_to_dut2_mac}
| | ... | ${dut2_to_dut1_mac} | ${dut1_to_dut2_ip4o6}
| | ... | ${dut2_to_dut1_ip4o6_reconf} | ${dut_prefix4o6}
| | ... | ${dut1_ip4o6_static_adjacency}
| | ... | ${dut1_ip4o6_static_adjacency_reconf}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip4o6} | ${tg2_ip4o6}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip4o6} | ${tg1_ip4o6}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
