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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/telemetry/span.robot
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.IPv4Util
| Library  | resources.libraries.python.IPv4Setup
| Library  | resources.libraries.python.telemetry.SPAN
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | EXPECTED_FAILING
# TODO: Remove EXPECTED_FAILING tag once functionality is implemented (VPP-185)
| Test Setup | Func Test Setup
| Test Teardown | Func Test Teardown
| Documentation | *SPAN test suite*
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two
| ... | links between nodes.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with SPAN mirroring from
| ... | the first DUT1-TG interface to the second one.
| ... | *[Ver] TG verification:* Test ARP or ICMP packets are sent by TG
| ... | on first link to DUT1; On receipt through second link TG verifies
| ... | the copy of packet sent and the copy of DUT's reply packet.
| ... | *[Ref] Applicable standard specifications: None?*

*** Variables ***
| ${tg_to_dut_if1_ip4}= | 192.168.1.1
| ${dut_to_tg_if1_ip4}= | 192.168.1.2
| ${prefix}= | 24

*** Test Cases ***
| TC01: DUT mirrors L2 packets from one interface to another
| | [Documentation]
| | ... | [Top] TG=DUT1
| | ... | [Cfg] On DUT1 configure IPv4 address and set SPAN mirroring\
| | ... | from one DUT interface to the other.
| | ... | [Ver] Make TG send an ARP packet to DUT through one interface,\
| | ... | then receive a copy of sent packet and of DUT's ARP reply\
| | ... | on the second interface.
| | Given Path For 2-node Testing Is Set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces In 2-node Path Are Up
| | And Set interface Address | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${dut_to_tg_if1_ip4} | ${prefix}
| | And Set SPAN Mirroring | ${dut_node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Then Send Packet And Check Received Copies | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg__if1_mac} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if1_ip4} | ${dut_to_tg_if1_ip4} | ARP

| TC02: DUT mirrors IPv4 packets from one interface to another
| | [Documentation]
| | ... | [Top] TG=DUT1
| | ... | [Cfg] On DUT1 configure IPv4 address, add ARP entry for one TG \
| | ... | interface and set SPAN mirroring from one DUT interface to the other.
| | ... | [Ver] Make TG send an ICMP packet to DUT through one interface,\
| | ... | then receive a copy of sent packet and of DUT's ICMP reply\
| | ... | on the other interface.
| | Given Path For 2-node Testing Is Set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces In 2-node Path Are Up
| | And Set interface Address | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${dut_to_tg_if1_ip4} | ${prefix}
| | And Add ARP on DUT | ${dut_node} | ${dut_to_tg_if1} | ${tg_to_dut_if1_ip4}
| | ... | ${tg_to_dut_if1_mac}
| | And Set SPAN Mirroring | ${dut_node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Then Send Packet And Check Received Copies | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg__if1_mac} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if1_ip4} | ${dut_to_tg_if1_ip4} | ICMP
