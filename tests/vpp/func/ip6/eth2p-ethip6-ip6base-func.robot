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
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/default.robot
| Variables | resources/libraries/python/IPv6NodesAddr.py | ${nodes}
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | SKIP_VPP_PATCH
| Suite Setup | Run Keywords
| ... | Configure IPv6 on all DUTs in topology | ${nodes} | ${nodes_ipv6_addr} | AND
| ... | Suppress ICMPv6 router advertisement message | ${nodes} | AND
| ... | Configure IPv6 routing on all DUTs | ${nodes} | ${nodes_ipv6_addr} | AND
| ... | Configure all TGs for traffic script
| Test Setup | Run Keywords | Save VPP PIDs | AND
| ... | Reset VAT History On All DUTs | ${nodes} | AND
| ... | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Run Keywords
| ... | Show packet trace on all DUTs | ${nodes} | AND
| ... | Show VAT History On All DUTs | ${nodes}  | AND
| ... | Verify VPP PID in Teardown
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
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req to DUT ingress interface. Make TG\
| | ... | verify ICMPv6 Echo Reply is correct.
| | Send IPv6 icmp echo request to DUT1 ingress inteface and verify answer | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes_ipv6_addr}

| TC02: DUT replies to ICMPv6 Echo Req pkt with size 64B-to-1500B-incr-1B
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 64B to 1500B with increment step
| | ... | of 1Byte. Make TG verify ICMP Echo Replies are correct.
| | Execute IPv6 ICMP echo sweep | ${nodes['TG']} | ${nodes['DUT1']} | 0 | 1452 | 1 | ${nodes_ipv6_addr}

| TC03: DUT replies to ICMPv6 Echo Req pkt with size 1500B-to-9000B-incr-10B
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 1500B to 9000B with increment
| | ... | step of 10Bytes. Make TG verify ICMPv6 Echo Replies are correct.
| | [Setup] | Configure MTU on TG based on MTU on DUT | ${nodes['TG']} | ${nodes['DUT1']}
| | [Teardown] | Run keywords
| | ... | Set default Ethernet MTU on all interfaces on node | ${nodes['TG']}
| | ... | AND | Verify VPP PID in Teardown
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${dut_port} | ${dut_node}= | Last Interface
| | ${mtu}= | Get Interface MTU | ${dut_node} | ${dut_port}
| | # ICMPv6 payload size is frame size minus size of Ehternet header, FCS,
| | # IPv6 header and ICMPv6 header
| | ${end_size}= | Evaluate | ${mtu} - 14 - 4 - 40 - 8
| | Run Keyword If | ${mtu} > 1518
| | ...            | Execute IPv6 ICMP echo sweep | ${nodes['TG']} | ${nodes['DUT1']}
| | ...            | 1452 | ${end_size} | 10 | ${nodes_ipv6_addr}

| TC04: DUT routes to its egress interface
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req towards DUT1 egress interface\
| | ... | connected to DUT2. Make TG verify ICMPv6 Echo Reply is correct.
| | Send IPv6 ICMP echo request to DUT1 egress interface and verify answer | ${nodes['TG']} | ${nodes['DUT1']} |
| | ...                    | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TC05: DUT1 routes to DUT2 ingress interface
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req towards DUT2 ingress interface\
| | ... | connected to DUT1. Make TG verify ICMPv6 Echo Reply is correct.
| | Send IPv6 ICMP echo request to DUT2 via DUT1 and verify answer | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                      | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TC06: DUT1 routes to DUT2 egress interface
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req towards DUT2 egress interface\
| | ... | connected to TG. Make TG verify ICMPv6 Echo Reply is correct.
| | Send IPv6 ICMP echo request to DUT2 egress interface via DUT1 and verify answer | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                             | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TC07: DUT1 and DUT2 route between TG interfaces
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across DUT1\
| | ... | and DUT2. Make TG verify ICMPv6 Echo Replies are correct.
| | Ipv6 tg to tg routed | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...                  | ${nodes_ipv6_addr}

| TC08: DUT replies to IPv6 Neighbor Solicitation
| | [Tags] | VM_ENV
| | [Documentation]
| | ... | On DUT configure interface IPv6 address in the main routing\
| | ... | domain. Make TG send Neighbor Solicitation message on the link
| | ... | to DUT and verify DUT Neighbor Advertisement reply is correct.
| | Send IPv6 neighbor solicitation and verify answer | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes_ipv6_addr}
