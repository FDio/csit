# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/double_qemu_setup.robot
| Library | resources.libraries.python.VatHistory
| Library | resources.libraries.python.Trace
| ...
| Documentation | Test setup and test teardown of FDS functional tests.

*** Keywords ***
| Set up FDS functional test
| | [Documentation]
| | ... |
| | ...
| | ... | *Arguments:*
| | ... | - nodes - Nodes to reset VAT command history for. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up FDS functional test \| ${nodes} \|
| | ...
| | [Arguments] | ${nodes}
| | ...
| | Configure all DUTs before test
| | Save VPP PIDs
| | Configure all TGs for traffic script
| | Reset VAT History On All DUTs | ${nodes}

| Tear down FDS functional test
| | [Documentation]
| | ... |
| | ...
| | ... | *Arguments:*
| | ... | - nodes - Nodes to reset VAT command history for. Type: dictionary
| | ... | - dut1_node - Node nr 1 where to clean qemu. Type: dictionary
| | ... | - qemu_node1 - VM nr 1 node info dictionary. Type: string
| | ... | - dut2_node - Node nr 2 where to clean qemu. Type: dictionary
| | ... | - qemu_node2 - VM nr 2 node info dictionary. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down FDS functional test \| ${nodes}\
| | ... | \| ${dut1_node} \| ${qemu_node1} \| ${dut2_node} \| ${qemu_node2} \|
| | ...
| | [Arguments] | ${nodes} | ${dut1_node} | ${qemu_node1} | ${dut2_node}
| | ... | ${qemu_node2}
| | ...
| | Show Packet Trace on All DUTs | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Tear down QEMU | ${dut1_node} | ${qemu_node1} | qemu_node1
| | Tear down QEMU | ${dut2_node} | ${qemu_node2} | qemu_node2
| | Verify VPP PID in Teardown
