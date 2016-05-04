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
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Library | resources.libraries.python.NodePath
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | VM_ENV
| Test Setup | Setup all DUTs before test
| Suite Setup | Setup all TGs before traffic script

*** Variables ***
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

*** Test Cases ***
| Vpp forwards ICMPv4 packets via L2 xconnect in circular topology
| | [Documentation] | Setup single link path with X-connect
| | ...             | and send ICMPv4 packet
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}
| | Send and receive ICMPv4 bidirectionally | ${tg} | ${tg_if1} | ${tg_if2}

| Vpp forwards ICMPv6 packets via L2 xconnect in circular topology
| | [Documentation] | Setup single link path with X-connect
| | ...             | and send ICMPv6 packet
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}
| | Send and receive ICMPv6 bidirectionally | ${tg} | ${tg_if1} | ${tg_if2}

| VPP forwards ICMPv4 packets through VM via L2 x-connect
| | [Documentation] | Setup double link path with X-connect via Vhost user
| | ...             | and send ICMPv4 packet
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And L2 Setup Xconnect on DUT | ${dut_node} | ${dut_to_tg_if1} | ${vhost_if1}
| | And L2 Setup Xconnect on DUT | ${dut_node} | ${dut_to_tg_if2} | ${vhost_if2}
| | And Interfaces on all VPP nodes in the path are up | ${dut_node}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}

| VPP forwards ICMPv6 packets through VM via L2 x-connect
| | [Documentation] | Setup double link path with X-connect via Vhost user
| | ...             | and send ICMPv6 packet
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And L2 Setup Xconnect on DUT | ${dut_node} | ${dut_to_tg_if1} | ${vhost_if1}
| | And L2 Setup Xconnect on DUT | ${dut_node} | ${dut_to_tg_if2} | ${vhost_if2}
| | And Interfaces on all VPP nodes in the path are up | ${dut_node}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv6 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}

