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
| Test Teardown | Tear down TAP functional test
| ...
| Documentation | *Tap Interface CRUD Tests*
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* No packet sent.
| ... | *[Cfg] DUT configuration:* Add/Modify/Delete linux-TAP on DUT1.
| ... | *[Ver] Verification:* Check dump of tap interfaces for correctness.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${tap_int1}= | tap_int1
| ${tap_int2}= | tap_int2
| ${mod_tap_name}= | tap_int1MOD

*** Test Cases ***
| TC01: Tap Interface Modify And Delete
| | [Documentation]
| | ... | [Top] TG-DUT1-TG.
| | ... | [Enc] Eth-IPv4-ICMPv4.
| | ... | [Cfg] Set two TAP interfaces.
| | ... | [Ver] Verify that TAP interface can be modified, deleted, and no\
| | ... | other TAP interface is affected.
| | ...
| | Given Configure path in 2-node circular topology | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1}
| | ${int2}= | And Add Tap Interface | ${dut_node} | ${tap_int2}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | And Set Interface State | ${dut_node} | ${int2} | up
| | When Modify Tap Interface | ${dut_node} | ${int1} | ${mod_tap_name}
| | Then Check Tap Present | ${dut_node} | ${mod_tap_name}
| | When Delete Tap Interface | ${dut_node} | ${int1}
| | Then Run Keyword And Expect Error
| | ... | Tap interface :${mod_tap_name} does not exist
| | ... | Check Tap Present | ${dut_node} | ${mod_tap_name}
| | And Check Tap Present | ${dut_node} | ${tap_int2}
| | When Delete Tap Interface | ${dut_node} | ${int2}
| | Then Run Keyword And Expect Error
| | ... | ValueError: No JSON object could be decoded
| | ... | Check Tap Present | ${dut_node} | ${tap_int2}
