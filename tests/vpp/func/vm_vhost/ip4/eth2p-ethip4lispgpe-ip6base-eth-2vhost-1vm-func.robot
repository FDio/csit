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
| Resource | resources/libraries/robot/overlay/lispgpe.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/vm/qemu.robot
| Library  | resources.libraries.python.IPUtil
| Library | resources.libraries.python.VhostUser
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.VPPUtil
# import additional Lisp settings from resource file
| Variables | resources/test_data/lisp/static_adjacency/lisp_static_adjacency.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
| ... | VM_ENV | HW_ENV
| ...
| Test Setup | Set up functional test
| ...
| Test Teardown | Tear down LISP functional test with QEMU | ${vm_node}
| ...
| Documentation | *LISP static adjacency test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv6-ICMPv6 on DUT1-DUT2,\
| ... | Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv6\
| ... | routing and static routes. LISPoIPv4 tunnel is configured\
| ... | between DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv6 Echo Request packets\
| ... | are sent in both directions by TG on links to DUT1 and DUT2; on receive\
| ... | TG verifies packets for correctness and their IPv6 src-addr,\
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using vhost interfaces
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on\
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Case: ip6-lispgpe-ip4 - main fib, virt2lisp
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv6 headers on\
| | ... | received packets are correct.
| | ...
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Configure IP addresses on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip6o4}
| | ... | ${dut_prefix6o4}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip6o4} | ${tg_prefix6o4}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip6o4}
| | ... | ${dut_prefix6o4}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip6o4}
| | ... | ${tg_to_dut1_mac}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip6o4}
| | ... | ${tg_to_dut2_mac}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip6o4}
| | ... | ${dut2_to_dut1_mac}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip6o4}
| | ... | ${dut1_to_dut2_mac}
| | And Vpp All RA Suppress Link Layer | ${nodes}
| | When Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ... | ${dut1_ip6o4_static_adjacency}
| | ... | ${dut2_ip6o4_static_adjacency}
| | And Setup Qemu DUT1
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip6o4} | ${tg2_ip6o4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dst_vhost_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip6o4} | ${tg1_ip6o4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

*** Keywords ***
| Setup Qemu DUT1
| | [Documentation] | Setup Vhosts on DUT1 and setup IP on one of them. Setup\
| | ... | Qemu and bridge the vhosts.
| | ...
| | ${vhost1}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock1}
| | ${vhost2}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock2}
| | Set Interface Address | ${dut1_node} | ${vhost2} | ${vhost_ip} | ${prefix6}
| | Set Interface State | ${dut1_node} | ${vhost1} | up
| | Set Interface State | ${dut1_node} | ${vhost2} | up
| | Create bridge domain | ${dut1_node} | ${bid} | learn=${TRUE}
| | Add interface to bridge domain | ${dut1_node}
| | ... | ${dut1_to_tg} | ${bid} | 0
| | Add interface to bridge domain | ${dut1_node}
| | ... | ${vhost1} | ${bid} | 0
| | ${vhost_mac}= | Get Vhost User Mac By SW Index | ${dut1_node} | ${vhost2}
| | Set test variable | ${dst_vhost_mac} | ${vhost_mac}
| | Configure VM for vhost L2BD forwarding | ${dut1_node} | ${sock1} | ${sock2}
