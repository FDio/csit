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
| ... | both directions by TG on links to DUT1; on receive TG verifies packets\
| ... | for correctness and their IPv4 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

*** Test Cases ***

| TC01: DUT replies to ICMPv4 Echo Req to its ingress interface
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req to DUT ingress interface. Make TG\
| | ... | verify ICMP Echo Reply is correct.
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${0}
| | Route traffic from interface '${src_port}' on node '${src_node}' to interface '${dst_port}' on node '${dst_node}' '${hops}' hops away using IPv4

| TC02: DUT routes IPv4 to its egress interface
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req towards DUT1 egress interface\
| | ... | connected to DUT2. Make TG verify ICMPv4 Echo Reply is correct.
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface

| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}

| | ${hops}= | Set Variable | ${0}
| | Route traffic from interface '${src_port}' on node '${src_node}' to interface '${dst_port}' on node '${dst_node}' '${hops}' hops away using IPv4

| TC03: DUT1 routes IPv4 packets between TG interfaces for locally connected IPv4 addresses
| | [Tags] | TEST
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across DUT1.\
| | ... | Make TG verify ICMPv4 Echo Replies are correct.
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

| TC04: DUT1 routes IPv4 packets between TG interfaces for remote host IPv4 addresses
| | [Tags] | TEST
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across DUT1.\
| | ... | Make TG verify ICMPv4 Echo Replies are correct.
| | ...
| | ${hops}= | Set Variable | ${1}
| | ${tg_to_dut_if1_ip4}= | Set Variable | 10.10.10.2
| | ${tg_to_dut_if2_ip4}= | Set Variable | 20.20.20.2
| | ${dut_to_tg_if1_ip4}= | Set Variable | 10.10.10.1
| | ${dut_to_tg_if2_ip4}= | Set Variable | 20.20.20.1
| | ${remote_host1_ip4}= | Set Variable | 192.168.0.1
| | ${remote_host2_ip4}= | Set Variable | 192.168.0.2
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Initialize IPv4 forwarding in circular topology | ${tg_to_dut_if1_ip4}
| | ... | ${tg_to_dut_if2_ip4} | ${dut_to_tg_if1_ip4} | ${dut_to_tg_if2_ip4}
| | ... | remote_host1_ip4=${remote_host1_ip4}
| | ... | remote_host2_ip4=${remote_host2_ip4}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send IPv4 ping packet and verify headers | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_node} | ${tg_to_dut_if2}
| | ... | ${remote_host1_ip4} | ${remote_host2_ip4} | ${dut_to_tg_if1_mac}
| | ... | ${hops}



| TC04: DUT replies to ICMPv4 Echo Reqs with size 64B-to-1500B-incr-1B
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 64B to 1500B with increment step
| | ... | of 1Byte. Make TG verify ICMP Echo Replies are correct.
| | Execute IPv4 ICMP echo sweep | ${nodes['TG']} | ${nodes['DUT1']} | 0 | 1452 | 1

| TC05: DUT replies to ICMPv4 Echo Reqs with size 1500B-to-9000B-incr-10B
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 1500B to 9000B with increment
| | ... | step of 10Bytes. Make TG verify ICMPv4 Echo Replies are correct.
| | [Setup] | Configure MTU on TG based on MTU on DUT | ${nodes['TG']} | ${nodes['DUT1']}
| | [Teardown] | Run keywords
| | ... | Set default Ethernet MTU on all interfaces on node | ${nodes['TG']}
| | ... | AND | Verify VPP PID in Teardown
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${dut_port} | ${dut_node}= | Last Interface
| | ${mtu}= | Get Interface MTU | ${dut_node} | ${dut_port}
| | # ICMP payload size is frame size minus size of Ehternet header, FCS,
| | # IPv4 header and ICMP header
| | ${end_size}= | Evaluate | ${mtu} - 14 - 4 - 20 - 8
| | Run Keyword If | ${mtu} > 1518
| | ... | Execute IPv4 ICMP echo sweep | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | 1452 | ${end_size} | 10

| TC06: DUT replies to ARP request
| | [Tags] | VM_ENV | SKIP_VPP_PATCH
| | [Documentation]
| | ... | Make TG send ARP Request to DUT and verify ARP Reply is correct.\
| | Send ARP request and verify response | ${nodes['TG']} | ${nodes['DUT1']}
