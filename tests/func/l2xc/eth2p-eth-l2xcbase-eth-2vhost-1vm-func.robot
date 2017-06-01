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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Library | resources.libraries.python.NodePath
| Force Tags | 3_NODE_DOUBLE_LINK_TOPO | HW_ENV | VM_ENV | VPP_VM_ENV
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *L2 cross-connect test cases*
| ...
| ... | *[Top] Network Topologies:* TG=DUT=VM 3-node topology with VM and
| ... | double parallel links.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of IPv4;
| ... | Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with L2 cross-connect
| ... | (L2XC) switching.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets are
| ... | sent in both directions by TG on links to DUT1 via VM; on receive TG
| ... | verifies packets for correctness and their IPv4 (IPv6) src-addr,
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

*** Test Cases ***
| TC01: DUT with two L2XCs switches ICMPv4 between TG and local VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT configure \
| | ... | two L2 cross-connects (L2XC), each with one untagged interface
| | ... | to TG and untagged i/f to local VM over vhost-user. [Ver] Make
| | ... | TG send ICMPv4 Echo Reqs in both directions between two of its
| | ... | i/fs to be switched by DUT to and from VM; verify all packets
| | ... | are received. [Ref]
| | ...
| | [Teardown] | Run Keywords | Stop and clear QEMU | ${dut_node} | ${vm_node}
| | ... | AND | Tear down functional test
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | When Configure vhost interfaces for L2BD forwarding | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And Configure L2XC | ${dut_node} | ${dut_to_tg_if1} | ${vhost_if1}
| | And Configure L2XC | ${dut_node} | ${dut_to_tg_if2} | ${vhost_if2}
| | And Configure VM for vhost L2BD forwarding | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send ICMPv4 bidirectionally and verify received packets | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}

| TC02: DUT with two L2XCs switches ICMPv6 between TG and local VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv6-ICMPv6. [Cfg] On DUT configure \
| | ... | two L2 cross-connects (L2XC), each with one untagged i/f to TG
| | ... | and untagged i/f to local VM over vhost-user. [Ver] Make TG send
| | ... | ICMPv6 Echo Reqs in both directions between two of its i/fs to
| | ... | be switched by DUT to and from VM; verify all packets are
| | ... | received. [Ref]
| | ...
| | [Teardown] | Run Keywords | Stop and clear QEMU | ${dut_node} | ${vm_node}
| | ... | AND | Tear down functional test
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | When Configure vhost interfaces for L2BD forwarding | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And Configure L2XC | ${dut_node} | ${dut_to_tg_if1} | ${vhost_if1}
| | And Configure L2XC | ${dut_node} | ${dut_to_tg_if2} | ${vhost_if2}
| | And Configure VM for vhost L2BD forwarding | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send ICMPv6 bidirectionally and verify received packets | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}

