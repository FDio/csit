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
| Documentation | VXLAN tunnel over untagged IPv4 traffic tests using bridge domain.
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/vxlan.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}

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
| VPP can pass IPv4 bidirectionally through VXLAN using bridge domain
| | [Documentation] | Create VXLAN interface on both VPP nodes. Create one
| | ...             | bridge domain (learning enabled) on both VPP nodes, add
| | ...             | VXLAN interface and interface toward TG to bridge domains
| | ...             | and check traffic bidirectionally.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And IP addresses are set on interfaces | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ...                                    | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
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

| Vpp forwards ICMPv4 packets through VXLAN tunnels in the same split-horizon group of one L2 bridge domain
| | [Documentation] | Create two VXLAN interfaces on both VPP nodes. Create one
| | ...             | bridge domain (learning enabled) on the first VPP node,
| | ...             | add VXLAN interfaces to the same split-horizon group of
| | ...             | the bridge domain where interfaces toward TG are added to.
| | ...             | Create two bridge domains (learning enabled) on the second
| | ...             | VPP node and add one VXLAN interface and one interface
| | ...             | toward TG to each of them. Check traffic bidirectionally.
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

| Vpp forwards ICMPv4 packets through VXLAN tunnels in different split-horizon groups of one L2 bridge domain
| | [Documentation] | Create two VXLAN interfaces on both VPP nodes. Create one
| | ...             | bridge domain (learning enabled) on the first VPP node,
| | ...             | add VXLAN interfaces to different split-horizon groups of
| | ...             | the bridge domain where interfaces toward TG are added to.
| | ...             | Create two bridge domains (learning enabled) on the second
| | ...             | VPP node and add one VXLAN interface and one interface
| | ...             | toward TG to each of them. Check traffic bidirectionally.
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

| VPP can pass IPv6 bidirectionally through VXLAN using bridge domain
| | [Documentation] | Create VXLAN interface on both VPP nodes. Create one
| | ...             | bridge domain (learning enabled) on both VPP nodes, add
| | ...             | VXLAN interface and interface toward TG to bridge domains
| | ...             | and check traffic bidirectionally.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | EXPECTED_FAILING
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

| Vpp forwards ICMPv6 packets through VXLAN tunnels in the same split-horizon group of one L2 bridge domain
| | [Documentation] | Create two VXLAN interfaces on both VPP nodes. Create one
| | ...             | bridge domain (learning enabled) on the first VPP node,
| | ...             | add VXLAN interfaces to the same split-horizon group of
| | ...             | the bridge domain where interfaces toward TG are added to.
| | ...             | Create two bridge domains (learning enabled) on the second
| | ...             | VPP node and add one VXLAN interface and one interface
| | ...             | toward TG to each of them. Check traffic bidirectionally.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | EXPECTED_FAILING
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

| Vpp forwards ICMPv6 packets through VXLAN tunnels in different split-horizon groups of one L2 bridge domain
| | [Documentation] | Create two VXLAN interfaces on both VPP nodes. Create one
| | ...             | bridge domain (learning enabled) on the first VPP node,
| | ...             | add VXLAN interfaces to different split-horizon groups of
| | ...             | the bridge domain where interfaces toward TG are added to.
| | ...             | Create two bridge domains (learning enabled) on the second
| | ...             | VPP node and add one VXLAN interface and one interface
| | ...             | toward TG to each of them. Check traffic bidirectionally.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | EXPECTED_FAILING
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
