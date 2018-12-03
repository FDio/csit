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
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | IP4FWD | BASE | ETH | IP4BASE
| ...
| Test Setup | Set up VPP device test
| ...
| Test Teardown | Tear down VPP device test
| ...
| Documentation | *IPv4 routing test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for IPv4 routing on both\
| ... | links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and two\
| ... | static IPv4 /24 route entries.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in\
| ... | one direction by TG on links to DUT1; on receive TG verifies packets\
| ... | for correctness and their IPv4 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

*** Test Cases ***

| tc01-eth2p-ethicmpv4-ip4base-device_echo-req-to-dut-ingress-interface
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req to DUT1 ingress interface. Make TG\
| | ... | verify ICMP Echo Reply is correct.
| | ...
| | ${hops}= | Set Variable | ${0}
| | ${tg_to_dut_if1_ip4}= | Set Variable | 10.10.10.2
| | ${tg_to_dut_if2_ip4}= | Set Variable | 20.20.20.2
| | ${dut_to_tg_if1_ip4}= | Set Variable | 10.10.10.1
| | ${dut_to_tg_if2_ip4}= | Set Variable | 20.20.20.1
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv4 forwarding in circular topology | ${tg_to_dut_if1_ip4}
| | ... | ${tg_to_dut_if2_ip4} | ${dut_to_tg_if1_ip4} | ${dut_to_tg_if2_ip4}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv4 ping packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${tg_to_dut_if1_ip4} | ${dut_to_tg_if1_ip4} | ${dut_to_tg_if1_mac}
| | ... | ${hops}

| tc02-eth2p-ethicmpv4-ip4base-device_echo-req-to-dut-egress-interface
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req towards DUT1 egress interface. Make TG\
| | ... | verify ICMP Echo Reply is correct.
| | ...
| | ${hops}= | Set Variable | ${0}
| | ${tg_to_dut_if1_ip4}= | Set Variable | 10.10.10.2
| | ${tg_to_dut_if2_ip4}= | Set Variable | 20.20.20.2
| | ${dut_to_tg_if1_ip4}= | Set Variable | 10.10.10.1
| | ${dut_to_tg_if2_ip4}= | Set Variable | 20.20.20.1
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv4 forwarding in circular topology | ${tg_to_dut_if1_ip4}
| | ... | ${tg_to_dut_if2_ip4} | ${dut_to_tg_if1_ip4} | ${dut_to_tg_if2_ip4}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv4 ping packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${tg_to_dut_if1_ip4} | ${dut_to_tg_if2_ip4} | ${dut_to_tg_if1_mac}
| | ... | ${hops}

| tc03-eth2p-ethicmpv4-ip4base-device_echo-req-to-tg-interface-for-local-ipv4-address
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across DUT1 for\
| | ... | locally connected IPv4 addresses. Make TG verify ICMPv4 Echo Replies\
| | ... | are correct.
| | ...
| | ${hops}= | Set Variable | ${1}
| | ${tg_to_dut_if1_ip4}= | Set Variable | 10.10.10.2
| | ${tg_to_dut_if2_ip4}= | Set Variable | 20.20.20.2
| | ${dut_to_tg_if1_ip4}= | Set Variable | 10.10.10.1
| | ${dut_to_tg_if2_ip4}= | Set Variable | 20.20.20.1
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv4 forwarding in circular topology | ${tg_to_dut_if1_ip4}
| | ... | ${tg_to_dut_if2_ip4} | ${dut_to_tg_if1_ip4} | ${dut_to_tg_if2_ip4}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv4 ping packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_node} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if1_ip4} | ${tg_to_dut_if2_ip4} | ${dut_to_tg_if1_mac}
| | ... | ${hops}

| tc04-eth2p-ethicmpv4-ip4base-device_echo-req-to-tg-interface-for-remote-host-ipv4-address
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across DUT1 for\
| | ... | remote host IPv4 addresses. Make TG verify ICMPv4 Echo Replies are\
| | ... | correct.
| | ...
| | ${hops}= | Set Variable | ${1}
| | ${tg_to_dut_if1_ip4}= | Set Variable | 10.10.10.2
| | ${tg_to_dut_if2_ip4}= | Set Variable | 20.20.20.2
| | ${dut_to_tg_if1_ip4}= | Set Variable | 10.10.10.1
| | ${dut_to_tg_if2_ip4}= | Set Variable | 20.20.20.1
| | ${remote_host1_ip4}= | Set Variable | 192.168.0.1
| | ${remote_host2_ip4}= | Set Variable | 192.168.0.2
| | ${remote_host_ip4_prefix}= | Set Variable | 32
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv4 forwarding in circular topology | ${tg_to_dut_if1_ip4}
| | ... | ${tg_to_dut_if2_ip4} | ${dut_to_tg_if1_ip4} | ${dut_to_tg_if2_ip4}
| | ... | remote_host1_ip4=${remote_host1_ip4}
| | ... | remote_host2_ip4=${remote_host2_ip4}
| | ... | remote_host_ip4_prefix=${remote_host_ip4_prefix}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv4 ping packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_node} | ${tg_to_dut_if2}
| | ... | ${remote_host1_ip4} | ${remote_host2_ip4} | ${dut_to_tg_if1_mac}
| | ... | ${hops}
