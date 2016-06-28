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
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.IPUtil
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Run Keyword | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *Tap Interface Traffic Tests*
| ... | *(Top) Network Topologies:* TG=DUT1=DUT2=TG 3-node topology with two
| ... | links in between nodes.
| ... | *(Enc) Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4.
| ... | *(Cfg) DUT configuration:*Each DUT is configured with two VRF tables;
| ... | Separation of traffic is tested by IP packets; Basic ARP and ROUTES are
| ... | set on DUT nodes; IP addresses are set on DUT interfaces.
| ... | *(Ver) TG verification:* Test ICMPv4 Echo Request packets
| ... | are sent by TG on link to DUT1, DUT2 or back to TG; On receipt TG
| ... | verifies packets for correctness and their IPv4 src-addr, dst-addr,
| ... | and MAC addresses.
| ... | *(Ref) Applicable standard specifications:*

*** Variables ***
| ${fib_table_1}= | 9
| ${fib_table_2}= | 99

| ${dut1_to_tg_ip1}= | 10.0.0.3
| ${dut1_to_tg_ip2}= | 10.0.0.4
| ${dut2_to_tg_ip1}= | 30.0.0.3
| ${dut2_to_tg_ip2}= | 30.0.0.4

| ${dut1_to_dut2_ip1}= | 20.0.0.1
| ${dut1_to_dut2_ip2}= | 20.0.0.2
| ${dut2_to_dut1_ip1}= | 20.0.0.3
| ${dut2_to_dut1_ip2}= | 20.0.0.4

| ${tg_dut1_ip1}= | 10.0.0.1
| ${tg_dut1_ip2}= | 10.0.0.2
| ${tg_dut2_ip1}= | 30.0.0.1
| ${tg_dut2_ip2}= | 30.0.0.2

| ${ip_prefix}= | 24

*** Test Cases ***
| TC01: TG packets routed to DUT ingress interface, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to DUT1->TG-if1 and from
| | ... | TG->DUT1-if2 to DUT1->TG-if2 and checked if arrived.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Node replies to ICMP echo request | ${tg_node}
| | ... | ${tg_to_dut1_if1} | ${dut1_to_tg_if1_mac}
| | ... | ${tg_to_dut1_if1_mac} | ${dut1_to_tg_ip1} | ${tg_dut1_ip1}
| | And Node replies to ICMP echo request | ${tg_node}
| | ... | ${tg_to_dut1_if2} | ${dut1_to_tg_if2_mac}
| | ... | ${tg_to_dut1_if2_mac} | ${dut1_to_tg_ip2} | ${tg_dut1_ip2}

| TC02: TG packets routed to DUT egress interface, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to DUT1->DUT2-if1 and from
| | ... | TG->DUT1-if2 to DUT1->DUT2-if2 and checked if arrived.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut1_to_dut2_ip1} | ${tg_dut1_ip1}
| | And Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut1_to_dut2_ip2} | ${tg_dut1_ip2}

| TC03: TG packets routed to DUT2 ingress interface through DUT1, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to DUT2->DUT1-if1 and from
| | ... | TG->DUT1-if2 to DUT2->DUT1-if2 and checked if arrived.
| | ... | (Ref)
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut2_to_dut1_ip1} | ${tg_dut1_ip1}
| | And Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut2_to_dut1_ip2} | ${tg_dut1_ip2}

| TC04: TG packets routed to DUT2 egress interface through DUT1, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to DUT2->TG-if1 and from
| | ... | TG->DUT1-if2 to DUT2->TG-if2 and checked if arrived.
| | ... | (Ref)
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut2_to_tg_ip1} | ${tg_dut1_ip1}
| | And Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut2_to_tg_ip2} | ${tg_dut1_ip2}

| TC05: TG packets routed to TG through DUT1 and DUT2, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to TG->DUT2-if1 and from
| | ... | TG->DUT1-if2 to TG->DUT2-if2 and checked if arrived.
| | ... | (Ref)
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Send Packet And Check Headers | ${tg_node} | ${tg_dut1_ip1}
| | ... | ${tg_dut2_ip1} | ${tg_to_dut1_if1} | ${tg_to_dut1_if1_mac}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut2_if1} | ${dut2_to_tg_if1_mac}
| | ... | ${tg_to_dut2_if1_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${tg_dut1_ip2} | ${tg_dut2_ip2} | ${tg_to_dut1_if2}
| | ... | ${tg_to_dut1_if2_mac} | ${dut1_to_tg_if2_mac} | ${tg_to_dut2_if2}
| | ... | ${dut2_to_tg_if2_mac} | ${tg_to_dut2_if2_mac}

| TC06: TG packets routed to DUT ingress interface in different VRF, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to DUT1->TG-if2 where it
| | ... | should not arrive.
| | ... | (Ref)
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | timeout |
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut1_to_tg_ip2} | ${tg_dut1_ip1}

| TC07: TG packets routed to DUT egress interface in different VRF, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to DUT1->DUT2-if2 where it
| | ... | should not arrive.
| | ... | (Ref)
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut1_to_dut2_ip2} | ${tg_dut1_ip1}

| TC08: TG packets routed to DUT2 ingress interface in different VRF through DUT1, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to DUT2->DUT1-if2 where it
| | ... | should not arrive.
| | ... | (Ref)
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut2_to_dut1_ip2} | ${tg_dut1_ip1}

| TC09: TG packets routed to DUT2 egress interface in different VRF through DUT1, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to DUT2->TG-if2 where it
| | ... | should not arrive.
| | ... | (Ref)
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut2_to_tg_ip2} | ${tg_dut1_ip1}

| TC10: TG packets routed to TG in different VRF through DUT1 and DUT2, VPP configured with two VRFs
| | [Documentation]
| | ... | (Top) TG=DUT1=DUT2=TG.
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. On every ingress
| | ... | and egress port on DUT is configured ARP and each DUT is configured
| | ... | with one route.
| | ... | (Ver) Packet is send from TG->DUT1-if1 to TG->DUT2-if2 where it
| | ... | should not arrive.
| | ... | (Ref)
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node testing are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send Packet And Check Headers | ${tg_node} | ${tg_dut1_ip1}
| | ... | ${tg_dut2_ip2} | ${tg_to_dut1_if1}
| | ... | ${tg_to_dut1_if1_mac} | ${dut1_to_tg_if1_mac} | ${tg_to_dut2_if2}
| | ... | ${dut2_to_tg_if2_mac} | ${tg_to_dut2_if2_mac}

*** Keywords ***
| Setup Env - 2xVRF Each Node
| | ${dut1_if1_idx}= | Get Interface SW Index
| | ... | ${dut1_node} | ${dut1_to_dut2_if1}
| | ${dut1_if2_idx}= | Get Interface SW Index
| | ... | ${dut1_node} | ${dut1_to_dut2_if2}
| | ${dut2_if1_idx}= | Get Interface SW Index
| | ... | ${dut2_node} | ${dut2_to_dut1_if1}
| | ${dut2_if2_idx}= | Get Interface SW Index
| | ... | ${dut2_node} | ${dut2_to_dut1_if2}
| | And Add fib table | ${dut1_node}
| | ... | ${tg_dut2_ip1} | ${ip_prefix} | ${fib_table_1}
| | ... | via ${dut2_to_dut1_ip1} sw_if_index ${dut1_if1_idx} multipath
| | And Add fib table | ${dut1_node}
| | ... | ${tg_dut2_ip2} | ${ip_prefix} | ${fib_table_2}
| | ... | via ${dut1_to_dut2_ip2} sw_if_index ${dut1_if2_idx} multipath
| | And Add fib table | ${dut2_node}
| | ... | ${tg_dut1_ip1} | ${ip_prefix} | ${fib_table_1}
| | ... | via ${dut2_to_dut1_ip1} sw_if_index ${dut2_if1_idx} multipath
| | And Add fib table | ${dut2_node}
| | ... | ${tg_dut1_ip2} | ${ip_prefix} | ${fib_table_2}
| | ... | via ${dut2_to_dut1_ip2} sw_if_index ${dut2_if2_idx} multipath

| | Assign Fib Table To Interface
| | ... | ${dut1_node} | ${dut1_to_dut2_if1} | ${fib_table_1}
| | Assign Fib Table To Interface
| | ... | ${dut1_node} | ${dut1_to_dut2_if2} | ${fib_table_2}
| | Assign Fib Table To Interface
| | ... | ${dut1_node} | ${dut1_to_tg_if1} | ${fib_table_1}
| | Assign Fib Table To Interface
| | ... | ${dut1_node} | ${dut1_to_tg_if2} | ${fib_table_2}

| | Assign Fib Table To Interface
| | ... | ${dut2_node} | ${dut2_to_dut1_if1} | ${fib_table_1}
| | Assign Fib Table To Interface
| | ... | ${dut2_node} | ${dut2_to_dut1_if2} | ${fib_table_2}
| | Assign Fib Table To Interface
| | ... | ${dut2_node} | ${dut2_to_tg_if1} | ${fib_table_1}
| | Assign Fib Table To Interface
| | ... | ${dut2_node} | ${dut2_to_tg_if2} | ${fib_table_2}

| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_tg_if1} | ${dut1_to_tg_ip1} | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_tg_if2} | ${dut1_to_tg_ip2} | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_dut2_if1}
| | ... | ${dut1_to_dut2_ip1} | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_dut2_if2}
| | ... | ${dut1_to_dut2_ip2} | ${ip_prefix}

| | And Set Interface Address
| | ... | ${dut2_node} | ${dut2_to_tg_if1} | ${dut2_to_tg_ip1} | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut2_node} | ${dut2_to_tg_if2} | ${dut2_to_tg_ip2} | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut2_node} | ${dut2_to_dut1_if1}
| | ... | ${dut2_to_dut1_ip1} | ${ip_prefix}
| | And Set Interface Address
| | ... | ${dut2_node} | ${dut2_to_dut1_if2}
| | ... | ${dut2_to_dut1_ip2} | ${ip_prefix}

| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_tg_if1}
| | ... | ${tg_dut1_ip1} | ${tg_to_dut1_if1_mac} | vrf=${fib_table_1}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_dut2_if1}
| | ... | ${dut2_to_dut1_ip1} | ${dut2_to_dut1_if1_mac} | vrf=${fib_table_1}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_tg_if1}
| | ... | ${tg_dut2_ip1} | ${tg_to_dut2_if1_mac} | vrf=${fib_table_1}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_dut1_if1}
| | ... | ${dut1_to_dut2_ip1} | ${dut1_to_dut2_if1_mac} | vrf=${fib_table_1}

| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_tg_if2}
| | ... | ${tg_dut1_ip2} | ${tg_to_dut1_if2_mac} | vrf=${fib_table_2}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_dut2_if2}
| | ... | ${dut2_to_dut1_ip2} | ${dut2_to_dut1_if2_mac} | vrf=${fib_table_2}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_tg_if2}
| | ... | ${tg_dut2_ip2} | ${tg_to_dut2_if2_mac} | vrf=${fib_table_2}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_dut1_if2}
| | ... | ${dut1_to_dut2_ip2} | ${dut1_to_dut2_if2_mac} | vrf=${fib_table_2}

| | And Vpp Route Add | ${dut1_node} | ${tg_dut2_ip1} | ${ip_prefix}
| | ... | ${dut2_to_dut1_ip1} | ${dut1_to_dut2_if1} | vrf=${fib_table_1}
| | And Vpp Route Add | ${dut2_node} | ${tg_dut1_ip1} | ${ip_prefix}
| | ... | ${dut1_to_dut2_ip1} | ${dut2_to_dut1_if1} | vrf=${fib_table_1}

| | And Vpp Route Add | ${dut1_node} | ${tg_dut2_ip2} | ${ip_prefix}
| | ... | ${dut2_to_dut1_ip2} | ${dut1_to_dut2_if2} | vrf=${fib_table_2}
| | And Vpp Route Add | ${dut2_node} | ${tg_dut1_ip2} | ${ip_prefix}
| | ... | ${dut1_to_dut2_ip2} | ${dut2_to_dut1_if2} | vrf=${fib_table_2}
