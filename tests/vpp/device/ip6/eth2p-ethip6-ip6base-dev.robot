# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | IP6FWD | BASE | ETH | IP6BASE
| ...
| Test Setup | Set up VPP device test
| ...
| Test Teardown | Tear down VPP device test
| ...
| Documentation | *IPv6 routing test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv6-ICMPv6 for IPv6 routing on both\
| ... | links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv6 routing and two\
| ... | static IPv6 /64 route entries.
| ... | *[Ver] TG verification:* Test ICMPv6 Echo Request packets are sent in\
| ... | one direction by TG on links to DUT1; on receive TG verifies packets\
| ... | for correctness and their IPv6 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC2460, RFC4443, RFC4861

*** Variables ***
| ${tg_to_dut_if1_ip6}= | 2001:1::2
| ${tg_to_dut_if2_ip6}= | 2001:2::2
| ${dut_to_tg_if1_ip6}= | 2001:1::1
| ${dut_to_tg_if2_ip6}= | 2001:2::1
| ${remote_host1_ip6}= | 3ffe:5f::1
| ${remote_host2_ip6}= | 3ffe:5f::2
| ${remote_host_ip6_prefix}= | 128

*** Test Cases ***
| tc01-eth2p-ethicmpv6-ip6base-device_echo-req-to-dut-ingress-interface
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req to DUT1 ingress interface. Make TG\
| | ... | verify ICMPv6 Echo Reply is correct.
| | ...
| | ${hops}= | Set Variable | ${0}
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv6 forwarding in circular topology | ${tg_to_dut_if1_ip6}
| | ... | ${tg_to_dut_if2_ip6} | ${dut_to_tg_if1_ip6} | ${dut_to_tg_if2_ip6}
| | And Suppress ICMPv6 router advertisement message | ${nodes}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv6 echo request packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${tg_to_dut_if1_ip6} | ${dut_to_tg_if1_ip6} | ${dut_to_tg_if1_mac}
| | ... | ${hops}

| tc02-eth2p-ethicmpv6-ip6base-device_echo-req-to-dut-egress-interface
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req towards DUT1 egress interface. Make TG\
| | ... | verify ICMPv6 Echo Reply is correct.
| | ...
| | ${hops}= | Set Variable | ${0}
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv6 forwarding in circular topology | ${tg_to_dut_if1_ip6}
| | ... | ${tg_to_dut_if2_ip6} | ${dut_to_tg_if1_ip6} | ${dut_to_tg_if2_ip6}
| | And Suppress ICMPv6 router advertisement message | ${nodes}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv6 echo request packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${tg_to_dut_if1_ip6} | ${dut_to_tg_if2_ip6} | ${dut_to_tg_if1_mac}
| | ... | ${hops}

| tc03-eth2p-ethicmpv6-ip6base-device_echo-req-to-tg-interface-for-local-ipv4-address
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across DUT1 for\
| | ... | locally connected IPv6 addresses. Make TG verify ICMPv6 Echo Replies\
| | ... | are correct.
| | ...
| | ${hops}= | Set Variable | ${1}
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv6 forwarding in circular topology | ${tg_to_dut_if1_ip6}
| | ... | ${tg_to_dut_if2_ip6} | ${dut_to_tg_if1_ip6} | ${dut_to_tg_if2_ip6}
| | And Suppress ICMPv6 router advertisement message | ${nodes}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv6 echo request packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_node} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if1_ip6} | ${tg_to_dut_if2_ip6} | ${dut_to_tg_if1_mac}
| | ... | ${hops} | ${dut_to_tg_if2_mac}

| tc04-eth2p-ethicmpv6-ip6base-device_echo-req-to-tg-interface-for-remote-host-ipv4-address
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across DUT1 for\
| | ... | remote host IPv6 addresses. Make TG verify ICMPv6 Echo Replies are\
| | ... | correct.
| | ...
| | ${hops}= | Set Variable | ${1}
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv6 forwarding in circular topology | ${tg_to_dut_if1_ip6}
| | ... | ${tg_to_dut_if2_ip6} | ${dut_to_tg_if1_ip6} | ${dut_to_tg_if2_ip6}
| | ... | remote_host1_ip6=${remote_host1_ip6}
| | ... | remote_host2_ip6=${remote_host2_ip6}
| | ... | remote_host_ip6_prefix=${remote_host_ip6_prefix}
| | And Suppress ICMPv6 router advertisement message | ${nodes}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv6 echo request packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_node} | ${tg_to_dut_if2}
| | ... | ${remote_host1_ip6} | ${remote_host2_ip6} | ${dut_to_tg_if1_mac}
| | ... | ${hops} | ${dut_to_tg_if2_mac}
