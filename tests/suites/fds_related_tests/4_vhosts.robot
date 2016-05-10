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
| ... | Test suite uses 2-node topology TG - DUT1 - TG with two links
| ... | between nodes as well as 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes. Test packets are sent in both directions
| ... | and contain Ethernet header, IPv4 header and ICMP message. Ethernet
| ... | header MAC addresses are matching MAC addresses of the TG node.

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2
| ${shg1}= | 3
| ${shg2}= | 4
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2
| ${sock3}= | /tmp/sock3
| ${sock4}= | /tmp/sock4

*** Test Cases ***
| 4 Vhost setup test
| | [Documentation] | Setup and run VM connected to VPP via Vhost-User
| | ...             | interfaces and check packet forwarding through VM via two
| | ...             | L2 bridge domains with learning enabled.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node BD testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | When VPP 4 Vhosts are created | ${dut_node}
| | ...                           | ${sock1}
| | ...                           | ${sock2}
| | ...                           | ${sock3}
| | ...                           | ${sock4}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if3}
| | ...                                     | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if4}
| | ...                                     | ${bd_id2}
| | And Interfaces on all VPP nodes in the path are up | ${dut_node}
| | And VM for 4 Vhosts are created | ${dut_node} | ${sock1}
| | ...                             | ${sock2}
| | ...                             | ${sock3}
| | ...                             | ${sock4}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}