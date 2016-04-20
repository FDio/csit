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
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *Bridge domain test suite.*
| ...
| ... | Test suite uses 2-node topology TGTG - DUT1 - TG with two links
| ... | between nodes as well as 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes. Test packets are sent in both directions
| ... | and contain Ethernet header, IPv4 header and ICMP message. Ethernet
| ... | header MAC addresses are matching MAC addresses of the TG node.

*** Variables ***
| ${bd_id1} = | 1
| ${bd_id2} = | 2
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

*** Test Cases ***
| VPP reports interfaces
| | [Documentation] | Report VPP interfaces on the given node
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | 3_NODE_SINGLE_LINK_TOPO
| | VPP reports interfaces on | ${nodes['DUT1']}

| Vpp forwards packets via L2 bridge domain 2 ports
| | [Documentation] | Create bridge domain (learning enabled) on one VPP node,
| | ...             | add there two interfaces and check traffic
| | ...             | bidirectionally.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 2-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | When Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id1}
| | And Interfaces on all VPP nodes in the path are up | ${dut_node}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                     | ${tg_to_dut_if2}

| Vpp forwards packets via L2 bridge domain in circular topology
| | [Documentation] | Create bridge domains (learning enabled) on two VPP nodes,
| | ...             | add two interfaces to each bridge domain and check traffic
| | ...             | bidirectionally.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | Given Path for 3-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                                     | ${nodes['DUT2']}
| | When Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_dut1}
| | ...                                     | ${bd_id2}
| | And Interfaces on all VPP nodes in the path are up | ${dut1_node}
| | ...                                                | ${dut2_node}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut1}
| | ...                                          | ${tg_to_dut2}

| Vpp forwards packets via L2 bridge domain in circular topology with static L2FIB entries
| | [Documentation] | Create bridge domains (learning disabled) on two VPP
| | ...             | nodes, add two interfaces to each bridge domain and set
| | ...             | static L2FIB entry on each interface and check traffic
| | ...             | bidirectionally.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | Given Path for 3-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                                     | ${nodes['DUT2']}
| | When Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | ...                                       | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut1}
| | ...                                                | ${dut1_node}
| | ...                                                | ${dut1_to_tg}
| | ...                                                | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut2}
| | ...                                                | ${dut1_node}
| | ...                                                | ${dut1_to_dut2}
| | ...                                                | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | ...                                      | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_dut1}
| | ...                                     | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut1}
| | ...                                                | ${dut2_node}
| | ...                                                | ${dut2_to_dut1}
| | ...                                                | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut2}
| | ...                                                | ${dut2_node}
| | ...                                                | ${dut2_to_tg}
| | ...                                                | ${bd_id2}
| | And Interfaces on all VPP nodes in the path are up | ${dut1_node}
| | ...                                                | ${dut2_node}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut1}
| | ...                                          | ${tg_to_dut2}

| VPP forwards packets through VM via two L2 bridge domains
| | [Documentation] | Setup and run VM connected to VPP via Vhost-User
| | ...             | interfaces and check packet forwarding through VM via two
| | ...             | L2 bridge domains with learning enabled.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if1}
| | ...                                     | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if2}
| | ...                                     | ${bd_id2}
| | And Interfaces on all VPP nodes in the path are up | ${dut_node}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}

| VPP forwards packets through VM via two L2 bridge domains with static L2FIB entries
| | [Documentation] | Setup and run VM connected to VPP via Vhost-User
| | ...             | interfaces and check packet forwarding through VM via two
| | ...             | L2 bridge domains with learning disabled (static L2BFIB
| | ...             | entries).
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | ...                                      | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if1}
| | ...                                     | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if1}
| | ...                                                | ${dut_node}
| | ...                                                | ${dut_to_tg_if1}
| | ...                                                | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if2}
| | ...                                                | ${dut_node}
| | ...                                                | ${vhost_if1}
| | ...                                                | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id2}
| | ...                                      | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if2}
| | ...                                     | ${bd_id2}
| | And Interfaces on all VPP nodes in the path are up | ${dut_node}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if2}
| | ...                                                | ${dut_node}
| | ...                                                | ${dut_to_tg_if2}
| | ...                                                | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if1}
| | ...                                                | ${dut_node}
| | ...                                                | ${vhost_if2}
| | ...                                                | ${bd_id2}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}
