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
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/ipv4.robot
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | SKIP_VPP_PATCH
| Suite Setup | Run Keywords
| ... | Configure all DUTs before test | AND
| ... | Configure all TGs for traffic script | AND
| ... | Update All Interface Data On All Nodes | ${nodes} | AND
| ... | Configure DUT nodes for IPv4 testing
| Test Setup | Run Keywords | Save VPP PIDs | AND
| ... | Reset VAT History On All DUTs | ${nodes} | AND
| ... | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Run Keywords
| ... | Show packet trace on all DUTs | ${nodes} | AND
| ... | Show VAT History On All DUTs | ${nodes} | AND
| ... | Verify VPP PID in Teardown
| Documentation | *IPv4 routing test cases*
| ...
| ... | RFC791 IPv4, RFC826 ARP, RFC792 ICMPv4. Encapsulations: Eth-IPv4-ICMPv4
| ... | on links TG-DUT1, TG-DUT2, DUT1-DUT2. IPv4 routing tests use circular
| ... | 3-node topology TG - DUT1 - DUT2 - TG with one link between the nodes.
| ... | DUT1 and DUT2 are configured with IPv4 routing and static routes. Test
| ... | ICMPv4 Echo Request packets are sent in both directions by TG on links
| ... | to DUT1 and DUT2 and received on TG links on the other side of circular
| ... | topology. On receive TG verifies packets IPv4 src-addr, dst-addr and MAC
| ... | addresses.

*** Test Cases ***

| TC01: DUT replies to ICMPv4 Echo Req to its ingress interface
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req to DUT ingress interface. Make TG\
| | ... | verify ICMP Echo Reply is correct.
| | [Tags] | VM_ENV
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${0}
| | Route traffic from interface '${src_port}' on node '${src_node}' to interface '${dst_port}' on node '${dst_node}' '${hops}' hops away using IPv4

| TC02: DUT routes IPv4 to its egress interface
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req towards DUT1 egress interface\
| | ... | connected to DUT2. Make TG verify ICMPv4 Echo Reply is correct.
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hops}= | Set Variable | ${0}
| | Route traffic from interface '${src_port}' on node '${src_node}' to interface '${dst_port}' on node '${dst_node}' '${hops}' hops away using IPv4

| TC03: DUT1 routes IPv4 to DUT2 ingress interface
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req towards DUT2 ingress interface\
| | ... | connected to DUT1. Make TG verify ICMPv4 Echo Reply is correct.
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${1}
| | Route traffic from interface '${src_port}' on node '${src_node}' to interface '${dst_port}' on node '${dst_node}' '${hops}' hops away using IPv4

| TC04: DUT1 routes IPv4 to DUT2 egress interface
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req towards DUT2 egress interface\
| | ... | connected to TG. Make TG verify ICMPv4 Echo Reply is correct.
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hops}= | Set Variable | ${1}
| | Route traffic from interface '${src_port}' on node '${src_node}' to interface '${dst_port}' on node '${dst_node}' '${hops}' hops away using IPv4

| TC05: DUT1 and DUT2 route IPv4 between TG interfaces
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across DUT1\
| | ... | and DUT2. Make TG verify ICMPv4 Echo Replies are correct.
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${2}
| | Route traffic from interface '${src_port}' on node '${src_node}' to interface '${dst_port}' on node '${dst_node}' '${hops}' hops away using IPv4

| TC06: DUT replies to ICMPv4 Echo Reqs with size 64B-to-1500B-incr-1B
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 64B to 1500B with increment step
| | ... | of 1Byte. Make TG verify ICMP Echo Replies are correct.
| | Execute IPv4 ICMP echo sweep | ${nodes['TG']} | ${nodes['DUT1']} | 0 | 1452 | 1

| TC07: DUT replies to ICMPv4 Echo Reqs with size 1500B-to-9000B-incr-10B
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

| TC08: DUT replies to ARP request
| | [Tags] | VM_ENV | SKIP_VPP_PATCH
| | [Documentation]
| | ... | Make TG send ARP Request to DUT and verify ARP Reply is correct.\
| | Send ARP request and verify response | ${nodes['TG']} | ${nodes['DUT1']}
