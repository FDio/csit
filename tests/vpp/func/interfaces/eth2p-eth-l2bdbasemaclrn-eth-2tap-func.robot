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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.Tap
| Library  | resources.libraries.python.Namespaces
| Library  | resources.libraries.python.IPUtil
| ...
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | SKIP_TEST
| ...
| Test Setup | Set up TAP functional test
| ...
| Test Teardown | Tear down TAP functional test with Linux bridge | ${bid_TAP}
| ...
| Documentation | *Tap Interface Traffic Tests*
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG)
| ... | are set depending on test case; Namespaces (NM)
| ... | are set on DUT1 with attached linux-TAP.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets
| ... | are sent by TG on link to DUT1; On receipt TG verifies packets
| ... | for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${bid_from_TG}= | 19
| ${bid_to_TG}= | 20
| ${bid_TAP}= | tapBr

| ${tap_int1}= | tap_int1
| ${tap_int2}= | tap_int2

*** Test Cases ***
| TC01: Tap Interface Simple BD
| | [Documentation]
| | ... | [Top] TG-DUT1-TG.
| | ... | [Enc] Eth-IPv4-ICMPv4.
| | ... | [Cfg] On DUT1 configure two L2BD with two if's for each L2BD with MAC\
| | ... | learning and one L2BD joining two linux-TAP interfaces created by VPP\
| | ... | located in namespace.
| | ... | [Ver] Packet sent from TG is passed through all L2BD and received\
| | ... | back on TG. Then src_ip, dst_ip and MAC are checked.
| | ...
| | Given Configure path in 2-node circular topology | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1}
| | ${int2}= | And Add Tap Interface | ${dut_node} | ${tap_int2}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | And Set Interface State | ${dut_node} | ${int2} | up
| | And Create bridge domain | ${dut_node}
| | ... | ${bid_from_TG} | learn=${TRUE}
| | And Create bridge domain | ${dut_node}
| | ... | ${bid_to_TG} | learn=${TRUE}
| | And Linux Add Bridge | ${dut_node}
| | ... | ${bid_TAP} | ${tap_int1} | ${tap_int2}
| | And Add interface to bridge domain | ${dut_node}
| | ... | ${int1} | ${bid_to_TG} | 0
| | And Add interface to bridge domain | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${bid_to_TG} | 0
| | And Add interface to bridge domain | ${dut_node}
| | ... | ${int2} | ${bid_from_TG} | 0
| | And Add interface to bridge domain | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${bid_from_TG} | 0
| | Then Send ICMP packet and verify received packet | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if2}
