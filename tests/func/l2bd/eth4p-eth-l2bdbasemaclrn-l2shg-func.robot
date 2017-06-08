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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *L2 bridge-domain test cases*
| ...
| ... | *[Top] Network Topologies:* TG=DUT1=DUT2=TG 3-node circular topology
| ... | with double parallel links.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply
| ... | to all links.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) switching combined with MAC learning enabled
| ... | and Split Horizon Groups (SHG).
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets
| ... | are sent in both directions by TG on links to DUT1 and DUT2; on
| ... | receive TG verifies packets for correctness and their IPv4 (IPv6)
| ... | src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2

| ${shg1}= | 3
| ${shg2}= | 4

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2BD (MAC learn) and SHG switch between four TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 and \
| | ... | DUT2 configure four i/fs into L2BD with MAC learning and the
| | ... | same SHG on i/fs towards TG. [Ver] Make TG verify ICMPv4 Echo
| | ... | Req pkts are switched thru DUT1 and DUT2 in both directions and
| | ... | are correct on receive; verify no pkts are switched thru SHG
| | ... | isolated interfaces. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Configure path for 3-node BD-SHG test | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['DUT2']}
| | And Set interfaces in 3-node BD-SHG test up
| | When Create bridge domain | ${dut1_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_tg_if1}
| | ... | ${bd_id1} | ${shg1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_tg_if2}
| | ... | ${bd_id1} | ${shg1}
| | And Add interface to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${bd_id1}
| | And Create bridge domain | ${dut2_node} | ${bd_id2}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg_if1}
| | ... | ${bd_id2} | ${shg2}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_tg_if2}
| | ... | ${bd_id2} | ${shg2}
| | And Add interface to bridge domain | ${dut2_node} | ${dut2_to_dut1}
| | ... | ${bd_id2}
| | Then Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if1} | ${tg_to_dut2_if1}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if1} | ${tg_to_dut2_if2}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if2} | ${tg_to_dut2_if1}
| | And Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut1_if2} | ${tg_to_dut2_if2}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMPv4 bidirectionally and verify received packets
| | | ... | ${tg_node} | ${tg_to_dut1_if1} | ${tg_to_dut1_if2}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMPv4 bidirectionally and verify received packets
| | | ... | ${tg_node} | ${tg_to_dut2_if1} | ${tg_to_dut2_if2}
