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
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/overlay/lisp_static_adjacency.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Trace
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
| Documentation | *IP AFI independent functional tests.*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2,\
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4\
| ... | routing and static routes. LISPoIPv4 tunnel is\
| ... | configured between DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets\
| ... | are sent in both directions by TG on links to DUT1 and DUT2; on receive\
| ... | TG verifies packets for correctness and their IPv4 src-addr,\
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv4 over LISPoIPv4 tunnel after disable-enable
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on\
| | ... | TG-DUTn.
| | ... | [Cfg1] On DUT1 and DUT2 configure IPv4 LISP static adjacencies.
| | ... | [Ver1] Make TG send ICMPv4 Echo Req between its interfaces across\
| | ... | both DUTs and LISP tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Cfg2] Disable LISP.
| | ... | [Ver2] Verify packets are not received via LISP tunnel.
| | ... | [Cfg3] Re-enable LISP.
| | ... | [Ver3] Verify packets are received again via LISP tunnel.
| | ... | [Ref] RFC6830.
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Configure IP addresses on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${dut1_to_dut2_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg}
| | ... | ${dut1_to_tg_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_dut1}
| | ... | ${dut2_to_dut1_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_tg}
| | ... | ${dut2_to_tg_ip4} | ${prefix4}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4}
| | And VPP Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4}
| | ... | ${tg_to_dut2_mac}
| | And VPP Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4}
| | ... | ${tg_to_dut1_mac}
| | When Configure LISP topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
| | When Disable Lisp | ${dut1_node}
| | Then Packet transmission from port to port should fail
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Packet transmission from port to port should fail
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
| | When Enable Lisp | ${dut1_node}
| | And Vpp Add Lisp Adjacency | ${dut1_node}
| | ... | ${dut1_to_dut2_ip4_static_adjacency['vni']}
| | ... | ${dut1_to_dut2_ip4_static_adjacency['deid']}
| | ... | ${dut1_to_dut2_ip4_static_adjacency['prefix']}
| | ... | ${dut1_to_dut2_ip4_static_adjacency['seid']}
| | ... | ${dut1_to_dut2_ip4_static_adjacency['prefix']}
| | And Vpp Add Lisp Adjacency | ${dut2_node}
| | ... | ${dut2_to_dut1_ip4_static_adjacency['vni']}
| | ... | ${dut2_to_dut1_ip4_static_adjacency['deid']}
| | ... | ${dut2_to_dut1_ip4_static_adjacency['prefix']}
| | ... | ${dut2_to_dut1_ip4_static_adjacency['seid']}
| | ... | ${dut2_to_dut1_ip4_static_adjacency['prefix']}
| | Then Wait Until Keyword Succeeds | 2x | 5s | Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Wait Until Keyword Succeeds | 2x | 5s | Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
