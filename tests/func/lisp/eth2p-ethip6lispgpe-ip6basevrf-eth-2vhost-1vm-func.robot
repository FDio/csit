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
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.VPPUtil
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/qemu.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/vrf.robot
| Resource | resources/libraries/robot/lisp/lispgpe.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/ipv6_lispgpe_ipv6/ipv6_lispgpe_ipv6.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | LISP
| ...
| Test Setup | Run Keywords | Set up functional test
| ... | AND | Vpp All Ra Suppress Link Layer | ${nodes}
| ...
| Test Teardown | Tear down LISP functional test with QEMU | ${vm_node}
| ...
| Documentation | *ip6-lispgpe-ip6 encapsulation test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv6-LISP-IPv6-ICMPv6 on DUT1-DUT2,\
| ... | Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv6 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv6\
| ... | routing and static routes. LISPoIPv6 tunnel is configured between\
| ... | DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv6 Echo Request packets are sent in\
| ... | both directions by TG on links to DUT1 and DUT2; on receive\
| ... | TG verifies packets for correctness and their IPv6 src-addr, dst-addr\
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using vhost interfaces and VRF is enabled
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv6-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on\
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Case: ip6-lispgpe-ip6 - vrf, virt2lisp
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv6 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | ...
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Assign Interface To Fib Table | ${dut1_node}
| | ... | ${dut1_to_tg} | ${fib_table_1} | ipv6=${TRUE}
| | And Assign Interface To Fib Table | ${dut2_node}
| | ... | ${dut2_to_tg} | ${fib_table_1} | ipv6=${TRUE}
| | And Vpp Set If IPv6 Addr
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip6} | ${prefix6}
| | And Vpp Set If IPv6 Addr
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip6} | ${prefix6}
| | And Vpp Set If IPv6 Addr
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip6} | ${prefix6}
| | And Vpp Set If IPv6 Addr
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip6} | ${prefix6}
| | And Add IP Neighbors
| | And Vpp All RA Suppress Link Layer | ${nodes}
| | When Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ... | ${dut1_to_dut2_ip6_static_adjacency}
| | ... | ${dut2_to_dut1_ip6_static_adjacency}
| | ... | ${dut1_dut2_vni} | ${fib_table_1}
| | And Setup Qemu DUT1 | ${fib_table_1}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip6} | ${tg2_ip6}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dst_vhost_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip6} | ${tg1_ip6}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

*** Keywords ***
| Setup Qemu DUT1
| | [Documentation] | Setup Vhosts on DUT1 and setup IP on one of them. Setup\
| | ... | Qemu and bridge the vhosts. Optionally, you can set fib table ID\
| | ... | where the vhost2 interface should be assigned to.
| | ...
| | [Arguments] | ${fib_table}=0
| | ...
| | ${vhost1}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock1}
| | ${vhost2}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock2}
| | Assign Interface To Fib Table | ${dut1_node}
| | ... | ${vhost2} | ${fib_table} | ipv6=${TRUE}
| | Vpp Set If IPv6 Addr | ${dut1_node} | ${vhost2} | ${vhost_ip}
| | ... | ${prefix6}
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

| Add IP Neighbors
| | [Documentation]
| | ... | Add IP neighbors to physical interfaces on DUTs.
| | ...
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip6}
| | ... | ${tg_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip6}
| | ... | ${tg_to_dut2_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip6}
| | ... | ${dut2_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip6}
| | ... | ${dut1_to_dut2_mac}
