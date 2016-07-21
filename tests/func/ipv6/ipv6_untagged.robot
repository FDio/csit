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
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/default.robot
| Variables | resources/libraries/python/IPv6NodesAddr.py | ${nodes}
| Force Tags | HW_ENV
| Suite Setup | Run Keywords | Setup ipv6 to all dut in topology | ${nodes} | ${nodes_ipv6_addr}
| ...         | AND          | Vpp nodes ra suppress link layer | ${nodes}
| ...         | AND          | Vpp nodes setup ipv6 routing | ${nodes} | ${nodes_ipv6_addr}
| ...         | AND          | Setup all TGs before traffic script
| Test Setup | Clear interface counters on all vpp nodes in topology | ${nodes}
| Documentation | *IPv6 routing test cases*
| ...
| ... | RFC2460 IPv6, RFC4443 ICMPv6, RFC4861 Neighbor Discovery.
| ... | Encapsulations: Eth-IPv6-ICMPv6 on links TG-DUT1, TG-DUT2, DUT1-DUT2;
| ... | Eth-IPv6-NS/NA on links TG-DUT. IPv6 routing tests use circular 3-node
| ... | topology TG - DUT1 - DUT2 - TG with one link between the nodes. DUT1 and
| ... | DUT2 are configured with IPv6 routing and static routes. Test ICMPv6
| ... | Echo Request packets are sent in both directions by TG on links to DUT1
| ... | and DUT2 and received on TG links on the other side of circular
| ... | topology. On receive TG verifies packets IPv6 src-addr, dst-addr and MAC
| ... | addresses.

*** Test Cases ***
| TC01: DUT replies to ICMPv6 Echo Req to its ingress interface
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req to DUT ingress interface. Make TG\
| | ... | verify ICMPv6 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 icmp echo | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes_ipv6_addr}

| TC02: DUT replies to ICMPv6 Echo Req pkt with size 64B-to-1500B-incr-1B
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 64B to 1500B with increment step
| | ... | of 1Byte. Make TG verify ICMP Echo Replies are correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 icmp echo sweep | ${nodes['TG']} | ${nodes['DUT1']} | 0 | 1452 | 1 | ${nodes_ipv6_addr}

| TC03: DUT replies to ICMPv6 Echo Req pkt with size 1500B-to-9000B-incr-10B
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 1500B to 9000B with increment
| | ... | step of 10Bytes. Make TG verify ICMPv6 Echo Replies are correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | [Setup] | Setup MTU on TG based on MTU on DUT | ${nodes['TG']} | ${nodes['DUT1']}
| | [Teardown] | Set default Ethernet MTU on all interfaces on node | ${nodes['TG']}
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${dut_port} | ${dut_node}= | Last Interface
| | ${mtu}= | Get Interface MTU | ${dut_node} | ${dut_port}
| | # ICMPv6 payload size is frame size minus size of Ehternet header, FCS,
| | # IPv6 header and ICMPv6 header
| | ${end_size}= | Evaluate | ${mtu} - 14 - 4 - 40 - 8
| | Run Keyword If | ${mtu} > 1518
| | ...            | Ipv6 icmp echo sweep | ${nodes['TG']} | ${nodes['DUT1']}
| | ...            | 1452 | ${end_size} | 10 | ${nodes_ipv6_addr}

| TC04: DUT routes to its egress interface
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req towards DUT1 egress interface\
| | ... | connected to DUT2. Make TG verify ICMPv6 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 tg to dut1 egress | ${nodes['TG']} | ${nodes['DUT1']} |
| | ...                    | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TC05: DUT1 routes to DUT2 ingress interface
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req towards DUT2 ingress interface\
| | ... | connected to DUT1. Make TG verify ICMPv6 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 tg to dut2 via dut1 | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                      | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TC06: DUT1 routes to DUT2 egress interface
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req towards DUT2 egress interface\
| | ... | connected to TG. Make TG verify ICMPv6 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 tg to dut2 egress via dut1 | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                             | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TC07: DUT1 and DUT2 route between TG interfaces
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across DUT1\
| | ... | and DUT2. Make TG verify ICMPv6 Echo Replies are correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 tg to tg routed | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...                  | ${nodes_ipv6_addr}

| TC08: DUT replies to IPv6 Neighbor Solicitation
| | [Documentation]
| | ... | On DUT configure interface IPv6 address in the main routing\
| | ... | domain. Make TG send Neighbor Solicitation message on the link
| | ... | to DUT and verify DUT Neighbor Advertisement reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 neighbor solicitation | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes_ipv6_addr}
