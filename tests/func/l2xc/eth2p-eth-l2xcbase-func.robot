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
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | VM_ENV | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *L2 cross-connect test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of IPv4;
| ... | Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | cross-connect (L2XC) switching.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets are
| ... | sent in both directions by TG on links to DUT1 and DUT2; on receive TG
| ... | verifies packets for correctness and their IPv4 (IPv6) src-addr,
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2XC switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 and \
| | ... | DUT2 configure L2 cross-connect (L2XC), each with one interface
| | ... | to TG and one Ethernet interface towards the other DUT. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref]
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Configure L2XC
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_dut2}
| | And Configure L2XC
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send ICMPv4 bidirectionally and verify received packets
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}

| TC02: DUT1 and DUT2 with L2XC switch ICMPv6 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv6-ICMPv6. [Cfg] On DUT1 and \
| | ... | DUT2 configure L2 cross-connect (L2XC), each with one interface
| | ... | to TG and one Ethernet interface towards the other DUT. [Ver]
| | ... | Make TG send ICMPv6 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref]
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Configure L2XC
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_dut2}
| | And Configure L2XC
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send ICMPv6 bidirectionally and verify received packets
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
