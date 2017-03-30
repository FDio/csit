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
| Resource | resources/libraries/robot/nsh_sfc/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/ipv4.robot
| Force Tags | HW_ENV
| Suite Setup | Run Keywords
| ... | Setup all DUTs before test | AND
| ... | Setup all TGs before traffic script | AND
| ... | Update All Interface Data On All Nodes | ${nodes} | AND
| ... | Setup DUT nodes for NSH SFC Classifier functional testing
| Test Setup | Run Keywords | Save VPP PIDs | AND
| ... | Reset VAT History On All DUTs | ${nodes} | AND
| ... | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Run Keywords
| ... | Show packet trace on all DUTs | ${nodes} | AND
| ... | Show VAT History On All DUTs | ${nodes} | AND
| ... | Check VPP PID in Teardown
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

*** Variables ***
# NSH Classifier check fields
| ${nsp} | ${185}
| ${nsi} | ${255}
| ${c1} | ${3232248395}
| ${c2} | ${9}
| ${c3} | ${3232248392}
| ${c4} | ${50336437}

*** Test Cases ***
| TC01: NSH SFC Classifier functional test with 72B frame size
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req to DUT ingress interface. Make TG\
| | ... | verify ICMP Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | ${frame_size}= | Set Variable | ${72}
| | Node "${src_node}" interface "${src_port}" send ${frame_size} Bytes TCP packet to node "${dst_node}" interface "${dst_port}"

| TC02: NSH SFC Classifier functional test with 128B frame size
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req towards DUT1 egress interface\
| | ... | connected to DUT2. Make TG verify ICMPv4 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | ${frame_size}= | Set Variable | ${128}
| | Node "${src_node}" interface "${src_port}" send ${frame_size} Bytes TCP packet to node "${dst_node}" interface "${dst_port}"

| TC03: NSH SFC Classifier functional test with 256B frame size
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req towards DUT2 ingress interface\
| | ... | connected to DUT1. Make TG verify ICMPv4 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | ${frame_size}= | Set Variable | ${256}
| | Node "${src_node}" interface "${src_port}" send ${frame_size} Bytes TCP packet to node "${dst_node}" interface "${dst_port}"

| TC04: NSH SFC Classifier functional test with 512B frame size
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req towards DUT2 egress interface\
| | ... | connected to TG. Make TG verify ICMPv4 Echo Reply is correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | ${frame_size}= | Set Variable | ${512}
| | Node "${src_node}" interface "${src_port}" send ${frame_size} Bytes TCP packet to node "${dst_node}" interface "${dst_port}"

| TC05: NSH SFC Classifier functional test with 1024B frame size
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across DUT1\
| | ... | and DUT2. Make TG verify ICMPv4 Echo Replies are correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | ${frame_size}= | Set Variable | ${1024}
| | Node "${src_node}" interface "${src_port}" send ${frame_size} Bytes TCP packet to node "${dst_node}" interface "${dst_port}"

| TC06: NSH SFC Classifier functional test with 1280B frame size
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 64B to 1500B with increment step
| | ... | of 1Byte. Make TG verify ICMP Echo Replies are correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | ${frame_size}= | Set Variable | ${1280}
| | Node "${src_node}" interface "${src_port}" send ${frame_size} Bytes TCP packet to node "${dst_node}" interface "${dst_port}"

| TC07: NSH SFC Classifier functional test with 1518B frame size
| | [Documentation]
| | ... | Make TG send ICMPv4 Echo Reqs to DUT ingress interface,\
| | ... | incrementating frame size from 1500B to 9000B with increment
| | ... | step of 10Bytes. Make TG verify ICMPv4 Echo Replies are correct.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | ${frame_size}= | Set Variable | ${1518}
| | Node "${src_node}" interface "${src_port}" send ${frame_size} Bytes TCP packet to node "${dst_node}" interface "${dst_port}"
