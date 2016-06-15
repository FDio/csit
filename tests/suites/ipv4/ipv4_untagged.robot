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
| Force Tags | HW_ENV
| Suite Setup | Run Keywords | Setup all DUTs before test
| ...         | AND          | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| ...         | AND          | Setup DUT nodes for IPv4 testing
| Test Setup | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Run Keyword If Test Failed | Show packet trace on all DUTs | ${nodes}

*** Test Cases ***

| TC01:DUT replies to ICMPv4 Echo Req to its ingress interface
| | [Documentation] | RFC791 IPv4 RFC792 ICMPv4: Eth-IPv4-ICMPv4 on link TG-DUT:
| | ...             | On DUT configure interface IPv4 addresses and routes in the
| | ...             | main routing domain. Make TG send ICMPv4 Echo Req to DUT
| | ...             | ingress interface. Make TG verify ICMP Echo Reply is
| | ...             | correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${0}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4

| TC02:DUT routes IPv4 to its egress interface
| | [Documentation] | RFC791 IPv4: Eth-IPv4-ICMPv4 on links TG-DUT1, DUT1-DUT2:
| | ...             | On DUT1 and DUT2 configure interface IPv4 addresses and
| | ...             | routes in the main routing domain. Make TG send ICMPv4
| | ...             | Echo Req towards DUT1 egress interface connected to DUT2.
| | ...             | Make TG verify ICMPv6 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hops}= | Set Variable | ${0}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4

| TC03:DUT1 routes IPv4 to DUT2 ingress interface
| | [Documentation] | RFC791 IPv4: Eth-IPv4-ICMPv4 on links TG-DUT1, DUT1-DUT2:
| | ...             | On DUT1 and DUT2 configure interface IPv4 addresses and
| | ...             | routes in the main routing domain. Make TG send ICMPv4
| | ...             | Echo Req towards DUT2 ingress interface connected to DUT1.
| | ...             | Make TG verify ICMPv4 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${1}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4

| TC04:DUT1 routes IPv4 to DUT2 egress interface
| | [Documentation] | RFC791 IPv4: Eth-IPv4-ICMPv4 on links TG-DUT1, TG-DUT2,
| | ...             | DUT1-DUT2: On DUT1 and DUT2 configure interface IPv4
| | ...             | addresses and routes in the main routing domain. Make
| | ...             | TG send ICMPv4 Echo Req towards DUT2 egress interface
| | ...             | connected to TG. Make TG verify ICMPv4 Echo Reply is
| | ...             | correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hops}= | Set Variable | ${1}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4

| TC05:DUT1 and DUT2 route IPv4 between TG interfaces
| | [Documentation] | RFC791 IPv4: Eth-IPv4-ICMPv4 on links TG-DUT1, TG-DUT2,
| | ...             | DUT1-DUT2: On DUT1 and DUT2 configure interface IPv4
| | ...             | addresses and routes in the main routing domain. Make
| | ...             | TG send ICMPv4 Echo Req between its interfaces across
| | ...             | DUT1 and DUT2. Make TG verify ICMPv4 Echo Replies are
| | ...             | correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${2}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4
| | ${port} | ${node}= | Next Interface
| | ${port} | ${node}= | Next Interface
| | ${exp_counter_val}= | Set Variable | ${1}
| | Vpp dump stats table | ${node}
| | Check ipv4 interface counter | ${node} | ${port} | ${exp_counter_val}
| | ${port} | ${node}= | Next Interface
| | Check ipv4 interface counter | ${node} | ${port} | ${exp_counter_val}
| | ${port} | ${node}= | Next Interface
| | Vpp dump stats table | ${node}
| | Check ipv4 interface counter | ${node} | ${port} | ${exp_counter_val}
| | ${port} | ${node}= | Next Interface
| | Check ipv4 interface counter | ${node} | ${port} | ${exp_counter_val}

| TC06:DUT replies to ICMPv4 Echo Reqs with size 64B-to-1500B-incr-1B
| | [Documentation] | RFC791 IPv4: Eth-IPv4-ICMPv4 on link TG-DUT: On DUT
| | ...             | configure interface IPv4 addresses and routes in the main
| | ...             | routing domain. Make TG send ICMPv4 Echo Reqs to DUT
| | ...             | ingress interface, incrementating frame size from 64B to
| | ...             | 1500B with increment step of 1Byte. Make TG verify ICMP
| | ...             | Echo Replies are correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv4 icmp echo sweep | ${nodes['TG']} | ${nodes['DUT1']} | 0 | 1452 | 1

| TC07:DUT replies to ICMPv4 Echo Reqs with size 1500B-to-9000B-incr-10B
| | [Documentation] | RFC791 IPv4: Eth-IPv4-ICMPv4 on link TG-DUT: On DUT
| | ...             | configure interface IPv4 addresses and routes in the main
| | ...             | routing domain. Make TG send ICMPv4 Echo Reqs to DUT
| | ...             | ingress interface, incrementating frame size from 1500B
| | ...             | to 9000B with increment step of 10Bytes. Make TG verify
| | ...             | ICMPv4 Echo Replies are correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | [Documentation] | This test case cannot be run reliably on VM_ENV because
| | ...             | the virtual hosts can be connected using a bridge which
| | ...             | has its own MTU
| | [Setup] | Setup MTU on TG based on MTU on DUT | ${nodes['TG']} | ${nodes['DUT1']}
| | [Teardown] | Set default Ethernet MTU on all interfaces on node | ${nodes['TG']}
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${dut_port} | ${dut_node}= | Last Interface
| | ${mtu}= | Get Interface MTU | ${dut_node} | ${dut_port}
| | # ICMP payload size is frame size minus size of Ehternet header, FCS,
| | # IPv4 header and ICMP header
| | ${end_size}= | Evaluate | ${mtu} - 14 - 4 - 20 - 8
| | Run Keyword If | ${mtu} > 1518
| | ...            | Ipv4 icmp echo sweep | ${nodes['TG']} | ${nodes['DUT1']}
| | ...            | 1452 | ${end_size} | 10

| TC08:DUT replies to ARP request
| | [Documentation] | RFC826 ARP: Eth-ARP on link TG-DUT: On DUT configure
| | ...             | interface IPv4 address in the main routing domain. Make
| | ...             | TG send ARP Request to DUT and verify ARP Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Send ARP request and validate response | ${nodes['TG']} | ${nodes['DUT1']}
