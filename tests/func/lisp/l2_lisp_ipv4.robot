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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.LispUtil
| Library | resources.libraries.python.L2Util
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/lisp/l2lisp.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/l2/l2_ipv4.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| ...
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| ...           | AND          | VPP Show Errors | ${nodes['DUT1']}
| ...           | AND          | VPP Show Errors | ${nodes['DUT2']}
| ...
| Documentation | *ip4-lispgpe-ip4 encapsulation test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* P4-Eth-ICMPv4-LISPGpe-IP4
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4
| ... | routing and static routes. LISPoIPv4 tunnel is configured between
| ... | DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in
| ... | both directions by TG on links to DUT1 and DUT2; on receive
| ... | TG verifies packets for correctness and their IPv4 src-addr, dst-addr
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: Route IPv4 packet through LISP with Bridge Domain setup.
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] IP4-Eth-ICMPv4-LISPGpe-IP4
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2. Also
| | ... | configure BD and assign it to LISP VNI.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both
| | ... | DUTs and LISP tunnel between them; verify IPv4, Ether headers on
| | ... | received packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4} | ${prefix4}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4}
| | ... | ${tg_to_dut2_mac}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4}
| | ... | ${tg_to_dut1_mac}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4}
| | ... | ${dut2_to_dut1_mac}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4}
| | ... | ${dut1_to_dut2_mac}
| | When Create L2 BD | ${dut1_node} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut1_node} | ${dut1_to_tg} | ${vpp_bd_id}
| | And Create L2 BD | ${dut2_node} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut2_node} | ${dut2_to_tg} | ${vpp_bd_id}
| | And Set up L2 Lisp on DUT | ${dut1_node}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${lisp_dut_settings}
| | And Set up L2 Lisp on DUT | ${dut2_node}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | ... | ${lisp_dut_settings}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_if1_mac} | ${tg_if2_mac}
| | ... | ${tg_to_dut2} | ${tg_if1_mac} | ${tg_if2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_if2_mac} | ${tg_if1_mac}
| | ... | ${tg_to_dut1} | ${tg_if2_mac} | ${tg_if1_mac}


