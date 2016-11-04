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
| Test Setup | Func Test Setup
| Test Teardown | Func Test Teardown
| Documentation | *Vpn routed forwarding - baseline IPv6*
| ... | *[Top] Network Topologies:* TG=DUT1=DUT2=TG 3-node topology with two
| ... | links in between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv6-ICMPv6
| ... | *[Cfg] DUT configuration:* Each DUT is configured with two VRF tables;
| ... | Separation of traffic is tested by IP packets; Neighbors and Routes are
| ... | set on DUT nodes; IP addresses are set on DUT interfaces.
| ... | *[Ver] TG verification:* Test ICMPv6 Echo Request packets
| ... | are sent by TG on link to DUT1, DUT2 or back to TG; On receipt TG
| ... | verifies packets for correctness and their IPv6 src-addr, dst-addr,
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${fib_table_1}= | 9
| ${fib_table_2}= | 99

| ${dut1_to_tg_ip1}= | 2001:62::3
| ${dut1_to_tg_ip2}= | 2001:62::4
| ${dut2_to_tg_ip1}= | 2003:62::3
| ${dut2_to_tg_ip2}= | 2003:62::4

| ${dut1_to_dut2_ip1}= | 2002:62::1
| ${dut1_to_dut2_ip2}= | 2002:62::2
| ${dut2_to_dut1_ip1}= | 2002:62::3
| ${dut2_to_dut1_ip2}= | 2002:62::4

| ${tg_dut1_ip1}= | 2001:62::1
| ${tg_dut1_ip2}= | 2001:62::2
| ${tg_dut2_ip1}= | 2003:62::1
| ${tg_dut2_ip2}= | 2003:62::2

| ${ip_prefix}= | 64
| ${timeout}= | 5

*** Test Cases ***
| TC01: TG packets routed to DUT ingress interface, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to DUT1->TG-if1 and from
| | ... | TG->DUT1-if2 to DUT1->TG-if2 and checked if arrived.
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Node replies to ICMP echo request | ${tg_node}
| | ... | ${tg_to_dut1_if1} | ${dut1_to_tg_if1_mac}
| | ... | ${tg_to_dut1_if1_mac} | ${dut1_to_tg_ip1}
| | ... | ${tg_dut1_ip1} | ${timeout}
| | And Node replies to ICMP echo request | ${tg_node}
| | ... | ${tg_to_dut1_if2} | ${dut1_to_tg_if2_mac}
| | ... | ${tg_to_dut1_if2_mac} | ${dut1_to_tg_ip2}
| | ... | ${tg_dut1_ip2} | ${timeout}

| TC02: TG packets routed to DUT egress interface, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to DUT1->DUT2-if1 and from
| | ... | TG->DUT1-if2 to DUT1->DUT2-if2 and checked if arrived.
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut1_to_dut2_ip1} | ${tg_dut1_ip1} | ${timeout}
| | And Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut1_to_dut2_ip2} | ${tg_dut1_ip2} | ${timeout}

| TC03: TG packets routed to DUT2 ingress interface through DUT1, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to DUT2->DUT1-if1 and from
| | ... | TG->DUT1-if2 to DUT2->DUT1-if2 and checked if arrived.
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut2_to_dut1_ip1} | ${tg_dut1_ip1} | ${timeout}
| | And Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut2_to_dut1_ip2} | ${tg_dut1_ip2} | ${timeout}

| TC04: TG packets routed to DUT2 egress interface through DUT1, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to DUT2->TG-if1 and from
| | ... | TG->DUT1-if2 to DUT2->TG-if2 and checked if arrived.
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut2_to_tg_ip1} | ${tg_dut1_ip1} | ${timeout}
| | And Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut2_to_tg_ip2} | ${tg_dut1_ip2} | ${timeout}

| TC05: TG packets routed to TG through DUT1 and DUT2, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to TG->DUT2-if1 and from
| | ... | TG->DUT1-if2 to TG->DUT2-if2 and checked if arrived.
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Send Packet And Check Headers | ${tg_node} | ${tg_dut1_ip1}
| | ... | ${tg_dut2_ip1} | ${tg_to_dut1_if1} | ${tg_to_dut1_if1_mac}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut2_if1} | ${dut2_to_tg_if1_mac}
| | ... | ${tg_to_dut2_if1_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${tg_dut1_ip2} | ${tg_dut2_ip2} | ${tg_to_dut1_if2}
| | ... | ${tg_to_dut1_if2_mac} | ${dut1_to_tg_if2_mac} | ${tg_to_dut2_if2}
| | ... | ${dut2_to_tg_if2_mac} | ${tg_to_dut2_if2_mac}

| TC06: TG packets not routed to DUT ingress interface in different VRF, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to DUT1->TG-if2 where it
| | ... | should not arrive.
| | [Tags] | SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut1_to_tg_ip2} | ${tg_dut1_ip1} | ${timeout}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut1_to_tg_ip1} | ${tg_dut1_ip2} | ${timeout}

| TC07: TG packets not routed to DUT egress interface in different VRF, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to DUT1->DUT2-if2 where it
| | ... | should not arrive.
| | [Tags] | SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut1_to_dut2_ip2} | ${tg_dut1_ip1} | ${timeout}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut1_to_dut2_ip1} | ${tg_dut1_ip2} | ${timeout}


| TC08: TG packets not routed to DUT2 ingress interface in different VRF through DUT1, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to DUT2->DUT1-if2 where it
| | ... | should not arrive.
| | [Tags] | SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut2_to_dut1_ip2} | ${tg_dut1_ip1} | ${timeout}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut2_to_dut1_ip1} | ${tg_dut1_ip2} | ${timeout}

| TC09: TG packets not routed to DUT2 egress interface in different VRF through DUT1, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to DUT2->TG-if2 where it
| | ... | should not arrive.
| | [Tags] | SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if1}
| | ... | ${dut1_to_tg_if1_mac} | ${tg_to_dut1_if1_mac}
| | ... | ${dut2_to_tg_ip2} | ${tg_dut1_ip1} | ${timeout}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Node replies to ICMP echo request
| | ... | ${tg_node} | ${tg_to_dut1_if2}
| | ... | ${dut1_to_tg_if2_mac} | ${tg_to_dut1_if2_mac}
| | ... | ${dut2_to_tg_ip1} | ${tg_dut1_ip2} | ${timeout}

| TC10: TG packets not routed to TG in different VRF through DUT1 and DUT2, VPP configured with two VRFs
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG.
| | ... | [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] DUT1 and DUT2 are both configured with two fib tables. Each
| | ... | table is assigned to 2 interfaces to separate the traffic. Interfaces
| | ... | are configured with IP addresses from *Variables*. Neighbors are
| | ... | configured for each DUTs ingress/egress ports, and each VRF is
| | ... | configured with just one route.
| | ... | [Ver] Packet is sent from TG->DUT1-if1 to TG->DUT2-if2 where it
| | ... | should not arrive.
| | [Tags] | SKIP_PATCH
| | Given Path for Double-Link 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in Double-Link 3-node path are UP
| | When Setup Env - 2xVRF Each Node
| | Then Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send Packet And Check Headers | ${tg_node} | ${tg_dut1_ip1}
| | ... | ${tg_dut2_ip2} | ${tg_to_dut1_if1}
| | ... | ${tg_to_dut1_if1_mac} | ${dut1_to_tg_if1_mac} | ${tg_to_dut2_if2}
| | ... | ${dut2_to_tg_if2_mac} | ${tg_to_dut2_if2_mac}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send Packet And Check Headers | ${tg_node} | ${tg_dut1_ip2}
| | ... | ${tg_dut2_ip1} | ${tg_to_dut1_if2}
| | ... | ${tg_to_dut1_if2_mac} | ${dut1_to_tg_if2_mac} | ${tg_to_dut2_if1}
| | ... | ${dut2_to_tg_if1_mac} | ${tg_to_dut2_if1_mac}

*** Keywords ***
| Setup Env - 2xVRF Each Node
| | [Documentation]
| | ... | Environment is set up with 2 fib tables on each DUT. DUT1-TG-IF1 and \
| | ... | DUT1-DUT2-IF1 are assigned to FIB1, and DUT1-TG-IF2 and DUT1-DUT2-IF2
| | ... | are assigned to FIB2 (the same done on DUT2, just opposite).
| | ... | IP addresses and IP Neighbors are subsequently set for interfaces.
| | ... | The last setting is route for each fib table.
| | ...
| | ${dut1_if1_idx}= | Get Interface SW Index
| | ... | ${dut1_node} | ${dut1_to_dut2_if1}
| | ${dut1_if2_idx}= | Get Interface SW Index
| | ... | ${dut1_node} | ${dut1_to_dut2_if2}
| | ${dut2_if1_idx}= | Get Interface SW Index
| | ... | ${dut2_node} | ${dut2_to_dut1_if1}
| | ${dut2_if2_idx}= | Get Interface SW Index
| | ... | ${dut2_node} | ${dut2_to_dut1_if2}

| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_dut2_if1} | ${fib_table_1} | ipv6=${TRUE}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_dut2_if2} | ${fib_table_2} | ipv6=${TRUE}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_tg_if1} | ${fib_table_1} | ipv6=${TRUE}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_tg_if2} | ${fib_table_2} | ipv6=${TRUE}

| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${dut2_to_dut1_if1} | ${fib_table_1} | ipv6=${TRUE}
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${dut2_to_dut1_if2} | ${fib_table_2} | ipv6=${TRUE}
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${dut2_to_tg_if1} | ${fib_table_1} | ipv6=${TRUE}
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${dut2_to_tg_if2} | ${fib_table_2} | ipv6=${TRUE}

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

| | And Add IP Neighbor | ${dut1_node} | ${dut1_to_tg_if1}
| | ... | ${tg_dut1_ip1} | ${tg_to_dut1_if1_mac} | vrf=${fib_table_1}
| | And Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2_if1}
| | ... | ${dut2_to_dut1_ip1} | ${dut2_to_dut1_if1_mac} | vrf=${fib_table_1}
| | And Add IP Neighbor | ${dut2_node} | ${dut2_to_tg_if1}
| | ... | ${tg_dut2_ip1} | ${tg_to_dut2_if1_mac} | vrf=${fib_table_1}
| | And Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1_if1}
| | ... | ${dut1_to_dut2_ip1} | ${dut1_to_dut2_if1_mac} | vrf=${fib_table_1}

| | And Add IP Neighbor | ${dut1_node} | ${dut1_to_tg_if2}
| | ... | ${tg_dut1_ip2} | ${tg_to_dut1_if2_mac} | vrf=${fib_table_2}
| | And Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2_if2}
| | ... | ${dut2_to_dut1_ip2} | ${dut2_to_dut1_if2_mac} | vrf=${fib_table_2}
| | And Add IP Neighbor | ${dut2_node} | ${dut2_to_tg_if2}
| | ... | ${tg_dut2_ip2} | ${tg_to_dut2_if2_mac} | vrf=${fib_table_2}
| | And Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1_if2}
| | ... | ${dut1_to_dut2_ip2} | ${dut1_to_dut2_if2_mac} | vrf=${fib_table_2}

| | And Vpp Route Add | ${dut1_node} | ${tg_dut2_ip1} | ${ip_prefix}
| | ... | ${dut2_to_dut1_ip1} | ${dut1_to_dut2_if1} | vrf=${fib_table_1}
| | And Vpp Route Add | ${dut2_node} | ${tg_dut1_ip1} | ${ip_prefix}
| | ... | ${dut1_to_dut2_ip1} | ${dut2_to_dut1_if1} | vrf=${fib_table_1}

| | And Vpp Route Add | ${dut1_node} | ${tg_dut2_ip2} | ${ip_prefix}
| | ... | ${dut2_to_dut1_ip2} | ${dut1_to_dut2_if2} | vrf=${fib_table_2}
| | And Vpp Route Add | ${dut2_node} | ${tg_dut1_ip2} | ${ip_prefix}
| | ... | ${dut1_to_dut2_ip2} | ${dut2_to_dut1_if2} | vrf=${fib_table_2}

| | Vpp All RA Suppress Link Layer | ${nodes}
