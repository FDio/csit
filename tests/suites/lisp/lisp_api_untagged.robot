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
| Documentation | LISP API test.
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.LispUtil
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/lisp/lisp_api.robot
# import additional Lisp settings from resource file
| Variables | tests/suites/lisp/resources/lisp_api_resources.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
| ... | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}

*** Variables ***
| ${locator_set_num}= | 3

*** Test Cases ***

Vpp can enable and disable Lisp
| | [Documentation] | Test lisp enable/disable API.
| | ...             | Enable lisp on the VPP node,
| | ...             | check if the lisp on the vpp node is enabled.
| | ...             | Then disable lisp on the vpp node and check if
| | ...             | the lisp is disabled on the vpp node.
| | When Enable lisp | ${nodes['DUT1']}
| | Then Check if lisp is enabled | ${nodes['DUT1']} | ${lisp_status}
| | When Disable lisp | ${nodes['DUT1']}
| | Then Check if lisp is disabled | ${nodes['DUT1']} | ${lisp_status}

| VPP can add and delete locator_set
| | [Documentation] | Test lisp locator_set API
| | ...             | Set locator_set and locator on the VPP node,
| | ...             | check the configured data and then remove it.
| | ...             | Check if all locator_set and locators was unset
| | ...             | from the VPP node.
| | ...
| | Given Lisp locator_set data is prepared
| | ... | ${nodes['DUT1']} | ${locator_set_num}
| | And   Enable lisp | ${nodes['DUT1']}
| | When Lisp locator_set data is set | ${nodes['DUT1']}
| | Then Lisp locator_set is set correctly | ${nodes['DUT1']}
| | When Delete all lisp locator_set from VPP | ${nodes['DUT1']}
| | Then Lisp locator_set should be unset | ${nodes['DUT1']}

| VPP can add, reset and delete locator_set
| | [Documentation] | Test lisp locator_set API
| | ...             | Set locator_set and locator on the VPP node,
| | ...             | then reset locator_set and set it again.
| | ...             | Check the configured data and then remove it.
| | ...             | Check if all locator_set and locators was unset
| | ...             | from the VPP node.
| | ...
| | Given Lisp locator_set data use for test reset locator_set are prepared
| | ... | ${nodes['DUT1']} | ${locator_set_num}
| | And   Enable lisp | ${nodes['DUT1']}
| | When Lisp locator_set data is set | ${nodes['DUT1']}
| | Then Lisp locator_set is set correctly | ${nodes['DUT1']}
| | When Delete all lisp locator_set from VPP | ${nodes['DUT1']}
| | Then Lisp locator_set should be unset | ${nodes['DUT1']}

| Vpp can add and delete eid address
| | [Documentation] | Test lisp eid API
| | ...             | Set lisp eid IP address on the VPP node,
| | ...             | check the configured data and then remove it.
| | ...             | Check if all eid IP address was unset
| | ...             | from the VPP node.
| | ...
| | Given Enable lisp | ${nodes['DUT1']}
| | When Lisp eid address is set | ${nodes['DUT1']} | ${eid_table}
| | Then Lisp eid address is set correctly to eid table | ${nodes['DUT1']}
| | ...                                                 | ${eid_table}
| | When Delete all lisp eid address from VPP | ${nodes['DUT1']} | ${eid_table}
| | Then Lisp eid table should be empty | ${nodes['DUT1']}

| Vpp can add and delete lisp map resolver address
| | [Documentation] | Test lisp map resolver address API
| | ...             | Set lisp map resolver address on the VPP node,
| | ...             | check the configured data and then remove it.
| | ...             | Check if all map resolver address was unset
| | ...             | from the VPP node.
| | ...
| | Given Enable lisp | ${nodes['DUT1']}
| | When Lisp map resolver address is set | ${nodes['DUT1']} | ${map_resolver}
| | Then Lisp map resolver address is set correctly | ${nodes['DUT1']}
| | ...                                             | ${map_resolver}
| | When Delete all lisp map resolver address from VPP | ${nodes['DUT1']}
| | ...                                                | ${map_resolver}
| | Then Lip map resolver address should be empty | ${nodes['DUT1']}
