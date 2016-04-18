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

"""IPv6 untagged test suite"""

*** Settings ***
| Documentation | IPv6 untagged test suite
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
| Test Teardown | Run Keyword If Test Failed | Show packet trace on all DUTs | ${nodes}

*** Test Cases ***
| VPP replies to ICMPv6 echo request
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 icmp echo | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes_ipv6_addr}

| VPP can process ICMPv6 echo request from min to 1500B packet size with 1B increment
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 icmp echo sweep | ${nodes['TG']} | ${nodes['DUT1']} | 0 | 1452 | 1 | ${nodes_ipv6_addr}

| VPP can process ICMPv6 echo request from 1500B to max packet size with 10B increment
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
| | # ICMPv6 payload size is frame size minus size of Ehternet header, FCS,
| | # IPv6 header and ICMPv6 header
| | ${end_size}= | Evaluate | ${mtu} - 14 - 4 - 40 - 8
| | Run Keyword If | ${mtu} > 1518
| | ...            | Ipv6 icmp echo sweep | ${nodes['TG']} | ${nodes['DUT1']}
| | ...            | 1452 | ${end_size} | 10 | ${nodes_ipv6_addr}

| TG can route to first DUT egress interface
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 tg to dut1 egress | ${nodes['TG']} | ${nodes['DUT1']} |
| | ...                    | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TG can route to second DUT through first DUT
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 tg to dut2 via dut1 | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                      | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TG can route to second DUT egress interface through first DUT
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 tg to dut2 egress via dut1 | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                             | ${nodes['DUT2']} | ${nodes_ipv6_addr}

| TG can route to TG through first and second DUT
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 tg to tg routed | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...                  | ${nodes_ipv6_addr}

| VPP replies to IPv6 Neighbor Solicitation
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Ipv6 neighbor solicitation | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes_ipv6_addr}
