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
| Library | resources.libraries.python.VPPUtil
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.VhostUser
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/vrf.robot
| Resource | resources/libraries/robot/qemu.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/lisp/lispgpe.robot
| Resource | resources/libraries/robot/lisp/l2lisp.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/rtr/rtr_ipv4_lispgpe_ipv4.py
| ...
| Force Tags | 3_NODE_DOUBLE_LINK_TOPO | VM_ENV | LISP | POKUS
| ...
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| ...           | AND          | Show VPP Settings | ${nodes['DUT1']} | lisp eid |
| ...           | AND          | Show VPP Settings | ${nodes['DUT2']} | lisp eid |
| ...
| Documentation | *RTR encapsulation test cases*
| ...
| ... | *[Top] Network Topologies:* TG=DUT1=DUT2=TG 3-node circular topology\
| ... | with double links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2,\
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4\
| ... | ARP entries and DUT2 is configured with one route. LISPoIPv4 tunnel \
| ... | is configured between DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in\
| ... | one direction by TG on link to DUT1 and DUT2; on receive\
| ... | TG verifies packets for correctness and their IPv4 src-addr, dst-addr\
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: Re-encapsulating router (RTR) IPv4 - IPv4
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG.
| | ... | [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2,\
| | ... | Eth-IPv4-ICMPv4 on TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2. Add\
| | ... | route from vrf0 to vrf1 on DUT2 and encap with different VNI
| | ... | [Ver] Case: ip4-lispgpe-ip4 - main fib, vrf, rtr\
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across\
| | ... | both DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830.
| | Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Interfaces in Double-Link 3-node path are UP
| | Assign Interface To Fib Table | ${dut1_node}
| | ... | ${dut1_to_tg_if2} | ${fib_table_2}
| | Assign Interface To Fib Table | ${dut2_node}
| | ... | ${dut2_to_tg_if2} | ${fib_table_2}
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_tg_if1} | ${dut1_to_tg_if1_ip} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg_if2} | ${dut1_to_tg_if2_ip} | ${prefix4}
| | ... | ${dut1_node}
| | ... | ${dut1_to_dut2_if1} | ${dut1_to_dut2_if1_ip4} | ${prefix4}
| | ... | ${dut1_node}
| | ... | ${dut1_to_dut2_if2} | ${dut1_to_dut2_if2_ip4} | ${prefix4}
| | ... | ${dut2_node}
| | ... | ${dut2_to_dut1_if1} | ${dut2_to_dut1_if1_ip4} | ${prefix4}
| | ... | ${dut2_node}
| | ... | ${dut2_to_dut1_if2} | ${dut2_to_dut1_if2_ip4} | ${prefix4}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_tg_if2} | ${tg2_ip4}
| | ... | ${tg_to_dut1_if2_mac} | ${fib_table_2}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2_if1}
| | ... | ${dut2_to_dut1_if1_ip4} | ${dut2_to_dut1_if1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1_if2}
| | ... | ${dut1_to_dut2_if2_ip4} | ${dut1_to_dut2_if2_mac}
| | Setup RTR Lisp
| | Vpp Route Add | ${dut2_node}
| | ... | ${dst_ip_range} | ${prefix4} | ${dut1_to_dut2_if2_ip4}
| | ... | ${dut2_to_dut1_if1} | lookup_vrf=${fib_table_2}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1_if1} | ${tg_to_dut1_if1_mac} | ${dut1_to_tg_if1_mac}
| | ... | ${tg_to_dut1_if2} | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}


*** Keywords ***
| Setup RTR Lisp
| | ${dut1_int_index}= | Get Interface Sw Index
| | ... | ${dut1_node} | ${dut1_to_dut2_if1}
| | ${dut1_int2_index}= | Get Interface Sw Index
| | ... | ${dut1_node} | ${dut1_to_dut2_if2}
| | ${dut2_int_index}= | Get Interface Sw Index
| | ... | ${dut2_node} | ${dut2_to_dut1_if2}
#
| | Enable Lisp | ${dut1_node}
| | Enable Lisp | ${dut2_node}
| | Enable Lisp GPE | ${dut1_node}
| | Enable Lisp GPE | ${dut2_node}
#Lisp DUT1 vni0
| | Vpp Add Lisp Locator Set | ${dut1_node}
| | ... | ${locator1}
| | Vpp Add Lisp Locator | ${dut1_node}
| | ... | ${locator1}
| | ... | ${dut1_int_index}
| | ... | ${duts_locator_set['priority']}
| | ... | ${duts_locator_set['weight']}
| | Vpp Add Lisp Local Eid | ${dut1_node}
| | ... | ${locator1}
| | ... | ${vni_dut1_1}
| | ... | ${src_ip_range}
| | ... | ${prefix4}
| | Vpp Add Lisp Remote Mapping | ${dut1_node}
| | ... | ${vni_dut1_1}
| | ... | ${dst_ip_range}
| | ... | ${prefix4}
| | ... | ${EMPTY}
| | ... | ${EMPTY}
| | ... | ${dut2_to_dut1_if1_ip4}
| | Vpp Add Lisp Adjacency | ${dut1_node}
| | ... | ${vni_dut1_1}
| | ... | ${dst_ip_range}
| | ... | ${prefix4}
| | ... | ${src_ip_range}
| | ... | ${prefix4}
#Lisp DUT1 vni1
| | Vpp Add Lisp Locator Set | ${dut1_node}
| | ... | ${locator2}
| | Vpp Add Lisp Locator | ${dut1_node}
| | ... | ${locator2}
| | ... | ${dut1_int2_index}
| | ... | ${duts_locator_set['priority']}
| | ... | ${duts_locator_set['weight']}
| | Vpp Lisp Eid Table Mapping | ${dut1_node}
| | ... | ${vni_dut1_2}
| | ... | vrf=${fib_table_2}
#Lisp DUT2
| | Vpp Add Lisp Locator Set | ${dut2_node}
| | ... | ${locator2}
| | Vpp Add Lisp Locator | ${dut2_node}
| | ... | ${locator2}
| | ... | ${dut2_int_index}
| | ... | ${duts_locator_set['priority']}
| | ... | ${duts_locator_set['weight']}
| | Vpp Lisp Eid Table Mapping | ${dut2_node}
| | ... | ${vni_dut2}
| | ... | vrf=${fib_table_2}
| | Vpp Add Lisp Local Eid | ${dut2_node}
| | ... | ${locator2}
| | ... | ${vni_dut2}
| | ... | ${src_ip_range}
| | ... | ${prefix4}
| | Vpp Add Lisp Remote Mapping | ${dut2_node}
| | ... | ${vni_dut2}
| | ... | ${dst_ip_range}
| | ... | ${prefix4}
| | ... | ${EMPTY}
| | ... | ${EMPTY}
| | ... | ${dut1_to_dut2_if2_ip4}
| | Vpp Add Lisp Adjacency | ${dut2_node}
| | ... | ${vni_dut2}
| | ... | ${dst_ip_range}
| | ... | ${prefix4}
| | ... | ${src_ip_range}
| | ... | ${prefix4}
