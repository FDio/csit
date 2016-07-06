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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.LispUtil
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/lisp/lisp_api.robot
# import additional Lisp settings from resource file
| Variables | resources/test_data/lisp/api/lisp_api_resources.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
| ... | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *LISP API test cases*
| ...
| ... | *[Top] Network Topologies:* DUT1 1-node topology.
| ... | *[Enc] Packet Encapsulations:* None.
| ... | *[Cfg] DUT configuration:* DUT1 gets configured with all LISP
| ... | parameters.
| ... | *[Ver] Verification:* DUT1 operational data gets verified following
| ... | configuration.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Variables ***
| ${locator_set_num}= | 3

*** Test Cases ***

| TC01: DUT can enable and disable LISP
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP enable/disable API; On \
| | ... | DUT1 enable LISP. [Ver1] Check DUT1 if LISP is enabled. [Cfg2]
| | ... | Then disable LISP. [Ver2] Check DUT1 if LISP is disabled. [Ref]
| | ... | RFC6830.
| | [Tags] | EXPECTED_FAILING
| | When Enable lisp | ${nodes['DUT1']}
| | Then Check if lisp is enabled | ${nodes['DUT1']} | ${lisp_status}
| | When Disable lisp | ${nodes['DUT1']}
| | Then Check if lisp is disabled | ${nodes['DUT1']} | ${lisp_status}

| TC02: DUT can add and delete locator_set
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP locator_set API; on \
| | ... | DUT1 configure locator_set and locator. [Ver1] Check DUT1
| | ... | configured locator_set and locator are correct. [Cfg2] Then
| | ... | remove locator_set and locator. [Ver2] check DUT1 locator_set
| | ... | and locator are removed. [Ref] RFC6830.
| | [Tags] | EXPECTED_FAILING
| | Given Lisp locator_set data is prepared
| | ... | ${nodes['DUT1']} | ${locator_set_num}
| | And   Enable lisp | ${nodes['DUT1']}
| | When Lisp locator_set data is set | ${nodes['DUT1']}
| | Then Lisp locator_set is set correctly | ${nodes['DUT1']}
| | When Delete all lisp locator_set from VPP | ${nodes['DUT1']}
| | Then Lisp locator_set should be unset | ${nodes['DUT1']}

| TC03: DUT can add, reset and delete locator_set
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP locator_set API; on \
| | ... | DUT1 configure locator_set and locator. [Ver1] Check DUT1
| | ... | locator_set and locator are correct. [Cfg2] Then reset
| | ... | locator_set and set it again. [Ver2] Check DUT1 locator_set and
| | ... | locator are correct. [Cfg3] Then remove locator_set and locator.
| | ... | [Ver3] Check DUT1 all locator_set and locators are removed.
| | ... | [Ref] RFC6830.
| | [Tags] | EXPECTED_FAILING
| | Given Lisp locator_set data use for test reset locator_set are prepared
| | ... | ${nodes['DUT1']} | ${locator_set_num}
| | And   Enable lisp | ${nodes['DUT1']}
| | When Lisp locator_set data is set | ${nodes['DUT1']}
| | Then Lisp locator_set is set correctly | ${nodes['DUT1']}
| | When Delete all lisp locator_set from VPP | ${nodes['DUT1']}
| | Then Lisp locator_set should be unset | ${nodes['DUT1']}

| TC04: DUT can add and delete eid address
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP eid API; on DUT1 \
| | ... | configure LISP eid IP address. [Ver1] Check DUT1 configured data
| | ... | is correct. [Cfg2] Remove configured data. [Ver2] Check DUT1 all
| | ... | eid IP addresses are removed. [Ref] RFC6830.
| | [Tags] | EXPECTED_FAILING
| | Given Enable lisp | ${nodes['DUT1']}
| | When Lisp eid address is set | ${nodes['DUT1']} | ${eid_table}
| | Then Lisp eid address is set correctly to eid table | ${nodes['DUT1']}
| | ...                                                 | ${eid_table}
| | When Delete all lisp eid address from VPP | ${nodes['DUT1']} | ${eid_table}
| | Then Lisp eid table should be empty | ${nodes['DUT1']}

| TC05: DUT can add and delete LISP map resolver address
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP map resolver address \
| | ... | API; on DUT1 configure LISP map resolver address. [Ver1] Check
| | ... | DUT1 configured data is correct. [Cfg2] Remove configured data.
| | ... | [Ver2] Check DUT1 all map resolver addresses are removed. [Ref]
| | ... | RFC6830.
| | Given Enable lisp | ${nodes['DUT1']}
| | When Lisp map resolver address is set | ${nodes['DUT1']} | ${map_resolver}
| | Then Lisp map resolver address is set correctly | ${nodes['DUT1']}
| | ...                                             | ${map_resolver}
| | When Delete all lisp map resolver address from VPP | ${nodes['DUT1']}
| | ...                                                | ${map_resolver}
| | Then Lip map resolver address should be empty | ${nodes['DUT1']}
