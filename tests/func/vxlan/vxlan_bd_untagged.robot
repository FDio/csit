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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/vxlan.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *RFC7348 VXLAN: Bridge-domain with VXLAN test cases*
| ...
| ... | *[Top] Network topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes; TG=DUT1=DUT2=TG 3-node circular
| ... | topology with double parallel links.
| ... | *[Enc] Packet encapsulations:* Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on
| ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for L2 switching of IPv4;
| ... | Eth-IPv6-VXLAN-Eth-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on
| ... | TG-DUTn for L2 switching of IPv6.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) switching combined with static MACs, MAC learning
| ... | enabled and Split Horizon Groups (SHG) depending on test case; VXLAN
| ... | tunnels are configured between L2BDs on DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets
| ... | are sent in both directions by TG on links to DUT1 and DUT2; on receive
| ... | TG verifies packets for correctness and their IPv4 (IPv6) src-addr,
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC7348.

*** Variables ***
| ${vni_1}= | 23
| ${vni_2}= | 35

| ${bd_id1}= | 10
| ${bd_id2}= | 20
| ${bd_id3}= | 30
| ${shg1}= | 1
| ${shg2}= | 2

| ${ip4_addr1}= | 172.16.0.1
| ${ip4_addr2}= | 172.16.0.2
| ${ip4_prefix}= | 24

| ${ip6_addr1}= | 3ffe:64::1
| ${ip6_addr2}= | 3ffe:64::2
| ${ip6_prefix}= | 64

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2BD and VXLANoIPv4 tunnels switch ICMPv4 between TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2; Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure two i/fs into L2BD with MAC learning. [Ver] Make TG
| | ... | verify ICMPv4 Echo Req pkts are switched thru DUT1 and DUT2 in
| | ... | both directions and are correct on receive. [Ref] RFC7348.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${dut1_to_dut2_name}= | Get interface name | ${dut1_node} | ${dut1_to_dut2}
| | ${dut2_to_dut1_name}= | Get interface name | ${dut2_node} | ${dut2_to_dut1}
| | And IP addresses are set on interfaces | ${dut1_node} | ${dut1_to_dut2_name} | ${NONE}
| | ...                                    | ${dut2_node} | ${dut2_to_dut1_name} | ${NONE}
| | ${dut1s_vxlan}= | When Create VXLAN interface     | ${dut1_node} | ${vni_1}
| |                 | ... | ${dut1s_ip_address} | ${dut2s_ip_address}
| | And  Interfaces are added to BD | ${dut1_node} | ${bd_id1}
| | ...                             | ${dut1_to_tg} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| |                 | ... | ${dut2s_ip_address} | ${dut1s_ip_address}
| | And  Interfaces are added to BD | ${dut2_node} | ${bd_id1}
| | ...                             | ${dut2_to_tg} | ${dut2s_vxlan}
| | Then Send and receive ICMPv4 bidirectionally
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}

| TC02: DUT1 and DUT2 with L2BD and VXLANoIPv4 tunnels in SHG switch ICMPv4 between TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG. [Enc] Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2; Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 configure L2
| | ... | bridge-domain (MAC learning enabled) with two untagged interfaces
| | ... | to TG and two VXLAN interfaces towards the DUT2 and put both VXLAN
| | ... | interfaces into the same Split-Horizon-Group (SHG). On DUT2 configure
| | ... | two L2 bridge-domain (MAC learning enabled), each with one untagged
| | ... | interface to TG and one VXLAN interface towards the DUT1. [Ver] Make
| | ... | TG send ICMPv4 Echo Reqs between all four of its interfaces to be
| | ... | switched by DUT1 and DUT2; verify packets are not switched between
| | ... | TG interfaces connected to DUT2 that are isolated by SHG on DUT1.
| | ... | [Ref] RFC7348.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 3-node BD-SHG testing is set | ${nodes['TG']}
| | ...                                         | ${nodes['DUT1']}
| | ...                                         | ${nodes['DUT2']}
| | And Interfaces in 3-node BD-SHG testing are up
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${ip4_addr1}
| | ...                       | ${ip4_prefix}
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${ip4_addr2}
| | ...                       | ${ip4_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip4_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip4_addr1}
| | ${dut1s_vxlan1}= | When Create VXLAN interface | ${dut1_node} | ${vni_1}
| | | ...                                          | ${ip4_addr1} | ${ip4_addr2}
| | ${dut1s_vxlan2}= | And Create VXLAN interface | ${dut1_node} | ${vni_2}
| | | ...                                         | ${ip4_addr1} | ${ip4_addr2}
| | ${dut2s_vxlan1}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| | | ...                                         | ${ip4_addr2} | ${ip4_addr1}
| | ${dut2s_vxlan2}= | And Create VXLAN interface | ${dut2_node} | ${vni_2}
| | | ...                                         | ${ip4_addr2} | ${ip4_addr1}
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan1} | up
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan2} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan1} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan2} | up
| | And Vpp Node Interfaces Ready Wait | ${dut1_node}
| | And Vpp Node Interfaces Ready Wait | ${dut2_node}
| | And Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if2}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1s_vxlan1}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1s_vxlan2}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if1}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2s_vxlan1}
| | ...                                     | ${bd_id2}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id3}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if2}
| | ...                                     | ${bd_id3}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2s_vxlan2}
| | ...                                     | ${bd_id3}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                          | ${tg_to_dut1_if1}
| | ...                                          | ${tg_to_dut2_if1}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if1}
| | ...                                         | ${tg_to_dut2_if2}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if1}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if2}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ...                              | Send and receive ICMPv4 bidirectionally
| | | ...                            | ${tg_node} | ${tg_to_dut2_if1}
| | | ...                            | ${tg_to_dut2_if2}

| TC03: DUT1 and DUT2 with L2BD and VXLANoIPv4 tunnels in different SHGs switch ICMPv4 between TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG.[Enc] Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2; Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 configure L2
| | ... | bridge-domain (MAC learning enabled) with two untagged interfaces
| | ... | to TG and two VXLAN interfaces towards the DUT2 and put both VXLAN
| | ... | interfaces into the different Split-Horizon-Group (SHGs). On DUT2
| | ... | configure two L2 bridge-domain (MAC learning enabled), each with one
| | ... | untagged interface to TG and one VXLAN interface towards the DUT1.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between all four of its interfaces
| | ... | to be switched by DUT1 and DUT2; verify packets are switched between
| | ... | all TG interfaces. [Ref] RFC7348.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 3-node BD-SHG testing is set | ${nodes['TG']}
| | ...                                         | ${nodes['DUT1']}
| | ...                                         | ${nodes['DUT2']}
| | And Interfaces in 3-node BD-SHG testing are up
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${ip4_addr1}
| | ...                       | ${ip4_prefix}
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${ip4_addr2}
| | ...                       | ${ip4_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip4_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip4_addr1}
| | ${dut1s_vxlan1}= | When Create VXLAN interface | ${dut1_node} | ${vni_1}
| | | ...                                          | ${ip4_addr1} | ${ip4_addr2}
| | ${dut1s_vxlan2}= | And Create VXLAN interface | ${dut1_node} | ${vni_2}
| | | ...                                         | ${ip4_addr1} | ${ip4_addr2}
| | ${dut2s_vxlan1}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| | | ...                                         | ${ip4_addr2} | ${ip4_addr1}
| | ${dut2s_vxlan2}= | And Create VXLAN interface | ${dut2_node} | ${vni_2}
| | | ...                                         | ${ip4_addr2} | ${ip4_addr1}
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan1} | up
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan2} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan1} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan2} | up
| | And Vpp Node Interfaces Ready Wait | ${dut1_node}
| | And Vpp Node Interfaces Ready Wait | ${dut2_node}
| | And Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if2}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1s_vxlan1}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1s_vxlan2}
| | ...                                     | ${bd_id1} | ${shg2}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if1}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2s_vxlan1}
| | ...                                     | ${bd_id2}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id3}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if2}
| | ...                                     | ${bd_id3}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2s_vxlan2}
| | ...                                     | ${bd_id3}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                          | ${tg_to_dut1_if1}
| | ...                                          | ${tg_to_dut2_if1}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if1}
| | ...                                         | ${tg_to_dut2_if2}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if1}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if2}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut2_if1}
| | ...                                         | ${tg_to_dut2_if2}

| TC04: DUT1 and DUT2 with L2BD and VXLANoIPv6 tunnels switch ICMPv6 between TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG.[Enc] Eth-IPv6-VXLAN-Eth-IPv6-ICMPv6 on \
| | ... | DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 bridge-domain (MAC learning enabled), each with one
| | ... | interface to TG and one VXLAN tunnel interface towards the other
| | ... | DUT. [Ver] Make TG send ICMPv6 Echo Req between two of its
| | ... | interfaces to be switched by DUT1 and DUT2; verify all packets
| | ... | are received. [Ref] RFC7348.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${ip6_addr1}
| | ...                       | ${ip6_prefix}
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${ip6_addr2}
| | ...                       | ${ip6_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip6_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip6_addr1}
| | ${dut1s_vxlan}= | When Create VXLAN interface | ${dut1_node} | ${vni_1}
| | | ...                                         | ${ip6_addr1} | ${ip6_addr2}
| | And  Interfaces are added to BD | ${dut1_node} | ${bd_id1}
| | ...                             | ${dut1_to_tg} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| | | ...                                        | ${ip6_addr2} | ${ip6_addr1}
| | And  Interfaces are added to BD | ${dut2_node} | ${bd_id1}
| | ...                             | ${dut2_to_tg} | ${dut2s_vxlan}
| | Then Send and receive ICMPv6 bidirectionally
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}

| TC05: DUT1 and DUT2 with L2BD and VXLANoIPv6 tunnels in SHG switch ICMPv6 between TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG. [Enc] Eth-IPv6-VXLAN-Eth-IPv6-ICMPv6 on \
| | ... | DUT1-DUT2; Eth-IPv6-ICMPv6 on TG-DUTn. [Cfg] On DUT1 configure L2
| | ... | bridge-domain (MAC learning enabled) with two untagged interfaces
| | ... | to TG and two VXLAN interfaces towards the DUT2 and put both VXLAN
| | ... | interfaces into the same Split-Horizon-Group (SHG). On DUT2 configure
| | ... | two L2 bridge-domain (MAC learning enabled), each with one untagged
| | ... | interface to TG and one VXLAN interface towards the DUT1. [Ver] Make
| | ... | TG send ICMPv6 Echo Reqs between all four of its interfaces to be
| | ... | switched by DUT1 and DUT2; verify packets are not switched between
| | ... | TG interfaces connected to DUT2 that are isolated by SHG on DUT1.
| | ... | [Ref] RFC7348.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 3-node BD-SHG testing is set | ${nodes['TG']}
| | ...                                         | ${nodes['DUT1']}
| | ...                                         | ${nodes['DUT2']}
| | And Interfaces in 3-node BD-SHG testing are up
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${ip6_addr1}
| | ...                       | ${ip6_prefix}
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${ip6_addr2}
| | ...                       | ${ip6_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip6_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip6_addr1}
| | ${dut1s_vxlan1}= | When Create VXLAN interface | ${dut1_node} | ${vni_1}
| | | ...                                          | ${ip6_addr1} | ${ip6_addr2}
| | ${dut1s_vxlan2}= | And Create VXLAN interface | ${dut1_node} | ${vni_2}
| | | ...                                         | ${ip6_addr1} | ${ip6_addr2}
| | ${dut2s_vxlan1}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| | | ...                                         | ${ip6_addr2} | ${ip6_addr1}
| | ${dut2s_vxlan2}= | And Create VXLAN interface | ${dut2_node} | ${vni_2}
| | | ...                                         | ${ip6_addr2} | ${ip6_addr1}
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan1} | up
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan2} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan1} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan2} | up
| | And Vpp Node Interfaces Ready Wait | ${dut1_node}
| | And Vpp Node Interfaces Ready Wait | ${dut2_node}
| | And Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if2}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1s_vxlan1}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1s_vxlan2}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if1}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2s_vxlan1}
| | ...                                     | ${bd_id2}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id3}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if2}
| | ...                                     | ${bd_id3}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2s_vxlan2}
| | ...                                     | ${bd_id3}
| | Then Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                          | ${tg_to_dut1_if1}
| | ...                                          | ${tg_to_dut2_if1}
| | And Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if1}
| | ...                                         | ${tg_to_dut2_if2}
| | And Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if1}
| | And Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if2}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ...                              | Send and receive ICMPv6 bidirectionally
| | | ...                            | ${tg_node} | ${tg_to_dut2_if1}
| | | ...                            | ${tg_to_dut2_if2}

| TC06: DUT1 and DUT2 with L2BD and VXLANoIPv6 tunnels in different SHGs switch ICMPv6 between TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG.[Enc] Eth-IPv6-VXLAN-Eth-IPv6-ICMPv6 on \
| | ... | DUT1-DUT2; Eth-IPv6-ICMPv6 on TG-DUTn. [Cfg] On DUT1 configure L2
| | ... | bridge-domain (MAC learning enabled) with two untagged interfaces
| | ... | to TG and two VXLAN interfaces towards the DUT2 and put both VXLAN
| | ... | interfaces into the different Split-Horizon-Group (SHGs). On DUT2
| | ... | configure two L2 bridge-domain (MAC learning enabled), each with one
| | ... | untagged interface to TG and one VXLAN interface towards the DUT1.
| | ... | [Ver] Make TG send ICMPv6 Echo Req between all four of its interfaces
| | ... | to be switched by DUT1 and DUT2; verify packets are switched between
| | ... | all TG interfaces. [Ref] RFC7348.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 3-node BD-SHG testing is set | ${nodes['TG']}
| | ...                                         | ${nodes['DUT1']}
| | ...                                         | ${nodes['DUT2']}
| | And Interfaces in 3-node BD-SHG testing are up
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${ip6_addr1}
| | ...                       | ${ip6_prefix}
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${ip6_addr2}
| | ...                       | ${ip6_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip6_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip6_addr1}
| | ${dut1s_vxlan1}= | When Create VXLAN interface | ${dut1_node} | ${vni_1}
| | | ...                                          | ${ip6_addr1} | ${ip6_addr2}
| | ${dut1s_vxlan2}= | And Create VXLAN interface | ${dut1_node} | ${vni_2}
| | | ...                                         | ${ip6_addr1} | ${ip6_addr2}
| | ${dut2s_vxlan1}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| | | ...                                         | ${ip6_addr2} | ${ip6_addr1}
| | ${dut2s_vxlan2}= | And Create VXLAN interface | ${dut2_node} | ${vni_2}
| | | ...                                         | ${ip6_addr2} | ${ip6_addr1}
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan1} | up
| | And Set Interface State | ${dut1_node} | ${dut1s_vxlan2} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan1} | up
| | And Set Interface State | ${dut2_node} | ${dut2s_vxlan2} | up
| | And Vpp Node Interfaces Ready Wait | ${dut1_node}
| | And Vpp Node Interfaces Ready Wait | ${dut2_node}
| | And Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if2}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1s_vxlan1}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1s_vxlan2}
| | ...                                     | ${bd_id1} | ${shg2}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if1}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2s_vxlan1}
| | ...                                     | ${bd_id2}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id3}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if2}
| | ...                                     | ${bd_id3}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2s_vxlan2}
| | ...                                     | ${bd_id3}
| | Then Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                          | ${tg_to_dut1_if1}
| | ...                                          | ${tg_to_dut2_if1}
| | And Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if1}
| | ...                                         | ${tg_to_dut2_if2}
| | And Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if1}
| | And Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if2}
| | And Send and receive ICMPv6 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut2_if1}
| | ...                                         | ${tg_to_dut2_if2}
