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
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.IPUtil
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *Vpn routed forwarding - extranet*
| ... | *[Top] Network Topologies:* TG=DUT1=DUT2=TG 3-node topology with two
| ... | links in between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4.
| ... | *[Cfg] DUT configuration:*DUT is configured with two VRF tables;
| ... | Two interfaces per VRF table; Configure per VRF static routes (set1)
| ... | and another routes (set2) where set2 is reachable cross-vrf;
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets
| ... | are sent by TG on link to DUT1 and reply is received back where
| ... | packets are verified for correctness and their IPv4 src-addr, dst-addr,
| ... | and MAC addresses are checked.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${fib_table_1}= | 9
| ${fib_table_2}= | 99

| ${src_ip} = | 10.0.0.10
| ${dst_ip1} = | 10.0.0.20
| ${dst_ip2} = | 20.0.0.20
| ${dst_ip3} = | 20.0.0.30

| ${dut1_tg_ip1}= | 10.0.0.1
| ${dut1_tg_ip2}= | 20.0.0.1
| ${dut1_dut2_ip1}= | 10.0.0.2
| ${dut1_dut2_ip2}= | 20.0.0.2

| ${ip_prefix}= | 24

*** Test Cases ***
| TC01: Packet routed within one VRF
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv4-ICMPv4.
| | ... | [Cfg] DUT1 is configured with two VRF tables and to each table, two
| | ... | interfaces are assigned. Each table also contains two routes.
| | ... | One route for basic traffic withi VRF, and second route which
| | ... | can pass traffic to another VRF table.
| | ... | [Ver] Packet is send from TG->DUT1-if1 to DUT2->TG-if1 and verified.
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env with 2 VRF
| | Send Packet And Check Headers | ${tg_node} | ${src_ip}
| | ... | ${dst_ip1} | ${tg_to_dut1_if1}
| | ... | ${tg_to_dut1_if1_mac} | ${dut1_to_tg_if1_mac} | ${tg_to_dut2_if1}
| | ... | ${dut1_to_dut2_if1_mac} | ${dut2_to_dut1_if1_mac}

| TC02: Packet routed to second VRF
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv4-ICMPv4.
| | ... | [Cfg] DUT1 is configured with two VRF tables and to each table, two
| | ... | interfaces are assigned. Each table also contains two routes.
| | ... | One route for basic traffic withi VRF, and second route which
| | ... | can pass traffic to another VRF table.
| | ... | [Ver] Packet is send from TG->DUT1-if1 to DUT2->TG-if2 and verified.
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env with 2 VRF
| | Send Packet And Check Headers | ${tg_node} | ${src_ip}
| | ... | ${dst_ip2} | ${tg_to_dut1_if1}
| | ... | ${tg_to_dut1_if1_mac} | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}

| TC03: Packet not routed to second VRF
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv4-ICMPv4.
| | ... | [Cfg] DUT1 is configured with two VRF tables and to each table, two
| | ... | interfaces are assigned. Each table also contains two routes.
| | ... | One route for basic traffic withi VRF, and second route which
| | ... | can pass traffic to another VRF table.
| | ... | [Ver] Packet is send from TG->DUT1-if1 to IP from second VRF table IP
| | ... | prefix which should be dropped.
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env with 2 VRF
| | run keyword and expect error | ICMP echo Rx timeout
| | ... | Send Packet And Check Headers | ${tg_node} | ${src_ip}
| | ... | ${dst_ip3} | ${tg_to_dut1_if1}
| | ... | ${tg_to_dut1_if1_mac} | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}


*** Keywords ***
| Setup Env with 2 VRF
| | [Documentation]
| | ... | Setup two VRF tables on DUT1 and assign two interfaces to each \
| | ... | VRF table; Set ARP on DUT1; Set up two Xconnects on DUT2

| | ${dut1_if1_idx}= | Get Interface SW Index
| | ... | ${dut1_node} | ${dut1_to_tg_if1}
| | ${dut1_if2_idx}= | Get Interface SW Index
| | ... | ${dut1_node} | ${dut1_to_tg_if2}

| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_tg_if1} | ${fib_table_1}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_tg_if2} | ${fib_table_2}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_dut2_if1} | ${fib_table_1}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_dut2_if2} | ${fib_table_2}

| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_tg_if1} | ${dut1_tg_ip1} | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_tg_if2} | ${dut1_tg_ip2}1 | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_dut2_if1} | ${dut1_dut2_ip1} | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_dut2_if2} | ${dut1_dut2_ip2} | ${ip_prefix}

| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_dut2_if2}
| | ... | ${dst_ip2} | ${dut2_to_dut1_if2_mac} | vrf=${fib_table_2}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_dut2_if1}
| | ... | ${dst_ip1} | ${dut2_to_dut1_if1_mac} | vrf=${fib_table_1}

| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1_if1} | ${dut1_to_tg_if1}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1_if2} | ${dut1_to_tg_if2}

| | And Vpp Route Add | ${dut1_node} | ${dst_ip1} | ${ip_prefix}
| | ... | ${dut1_dut2_ip1} | ${dut1_to_dut2_if1} | vrf=${fib_table_1}
| | And Vpp Route Add | ${dut1_node} | ${dst_ip2} | ${ip_prefix}
| | ... | ${dut1_dut2_ip2} | ${dut1_to_dut2_if2} | vrf=${fib_table_2}

| | And Vpp Route Add | ${dut1_node} | ${dst_ip2} | ${ip_prefix}
| | ... | ${dut1_tg_ip2} | ${dut1_to_tg_if2} | vrf=${fib_table_1}
| | ... | lookup_vrf=${fib_table_2}
| | And Vpp Route Add | ${dut1_node} | ${dst_ip1} | ${ip_prefix}
| | ... | ${dut1_tg_ip1} | ${dut1_to_tg_if1} | vrf=${fib_table_2}
| | ... | lookup_vrf=${fib_table_1}


