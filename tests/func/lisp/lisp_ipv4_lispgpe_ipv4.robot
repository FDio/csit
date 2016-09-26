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
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/vrf.robot
| Resource | resources/libraries/robot/lisp/lispgpe.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/ipv4_lispgpe_ipv4/ipv4_lispgpe_ipv4.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | LISP
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
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2,\
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4\
| ... | routing and static routes. LISPoIPv4 tunnel is configured between\
| ... | DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in\
| ... | both directions by TG on links to DUT1 and DUT2; on receive\
| ... | TG verifies packets for correctness and their IPv4 src-addr, dst-addr\
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using physical interfaces
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - phy2lisp
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on\
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
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
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4}
| | ... | ${tg_to_dut2_mac}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4}
| | ... | ${tg_to_dut1_mac}
| | When Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC02: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using physical interfaces and VRF is enabled
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - vrf, phy2lisp
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on\
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Setup VRF on DUT | ${dut1_node} | ${dut1_fib_table} | ${dut1_to_dut2}
| | ... | ${dut2_to_dut1_ip4} | ${dut2_to_dut1_mac} | ${tg2_ip4} | ${dut1_to_tg}
| | ... | ${tg1_ip4} | ${tg_to_dut1_mac} | ${prefix4}
| | And Setup VRF on DUT | ${dut2_node} | ${dut2_fib_table} | ${dut2_to_dut1}
| | ... | ${dut1_to_dut2_ip4} | ${dut1_to_dut2_mac} | ${tg1_ip4} | ${dut2_to_tg}
| | ... | ${tg2_ip4} | ${tg_to_dut2_mac} | ${prefix4}
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4} | ${prefix4}
| | And Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC03: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using vhost interfaces
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - virt2lisp
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on\
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ... | AND | Show vpp trace dump on all DUTs
| | ... | AND | VPP Show Errors | ${nodes['DUT1']}
| | ... | AND | VPP Show Errors | ${nodes['DUT2']}
| | ... | AND | Stop and Clear QEMU | ${dut1_node} | ${vm_node}
| | ...
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4} | ${prefix4}
| | And Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4}
| | ... | ${tg_to_dut1_mac}
| | And Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4}
| | ... | ${tg_to_dut2_mac}
| | And Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4}
| | ... | ${dut2_to_dut1_mac}
| | And Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4}
| | ... | ${dut1_to_dut2_mac}
| | When Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | And Setup Qemu DUT1
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dst_vhost_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC04: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using vhost interfaces and VRF is enabled
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - vrf, virt2lisp \
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on\
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ... | AND | Show vpp trace dump on all DUTs
| | ... | AND | VPP Show Errors | ${nodes['DUT1']}
| | ... | AND | VPP Show Errors | ${nodes['DUT2']}
| | ... | AND | Stop and Clear QEMU | ${dut1_node} | ${vm_node}
| | ...
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Setup VRF on DUT | ${dut1_node} | ${dut1_fib_table} | ${dut1_to_dut2}
| | ... | ${dut2_to_dut1_ip4} | ${dut2_to_dut1_mac} | ${tg2_ip4} | ${dut1_to_tg}
| | ... | ${tg1_ip4} | ${tg_to_dut1_mac} | ${prefix4}
| | And Setup VRF on DUT | ${dut2_node} | ${dut2_fib_table} | ${dut2_to_dut1}
| | ... | ${dut1_to_dut2_ip4} | ${dut1_to_dut2_mac} | ${tg1_ip4} | ${dut2_to_tg}
| | ... | ${tg2_ip4} | ${tg_to_dut2_mac} | ${prefix4}
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4} | ${prefix4}
| | And Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | And Setup Qemu DUT1
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dst_vhost_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

*** Keywords ***
| Setup Qemu DUT1
| | [Documentation] | Setup Vhosts on DUT1 and setup IP to one of them. Setup\
| | ... | Qemu and bridge the vhosts.
| | ...
| | ${vhost1}= | And Vpp Create Vhost User Interface | ${dut1_node} | ${sock1}
| | ${vhost2}= | And Vpp Create Vhost User Interface | ${dut1_node} | ${sock2}
| | Set Interface State | ${dut1_node} | ${vhost1} | up
| | Set Interface State | ${dut1_node} | ${vhost2} | up
| | Bridge domain on DUT node is created | ${dut1_node} | ${bid} | learn=${TRUE}
| | Interface is added to bridge domain | ${dut1_node}
| | ... | ${dut1_to_tg} | ${bid} | 0
| | Interface is added to bridge domain | ${dut1_node}
| | ... | ${vhost1} | ${bid} | 0
| | ${vhost_mac}= | Get Vhost User Mac By SW Index | ${dut1_node} | ${vhost2}
| | Set test variable | ${dst_vhost_mac} | ${vhost_mac}
| | VM for Vhost L2BD forwarding is setup | ${dut1_node} | ${sock1} | ${sock2}
