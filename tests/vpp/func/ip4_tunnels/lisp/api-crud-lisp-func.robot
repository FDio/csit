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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/overlay/lisp_api.robot
# import additional Lisp settings from resource file
| Variables | resources/test_data/lisp/api/lisp_api_resources.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
| ... | VM_ENV | HW_ENV
| ...
| Test Setup | Set up functional test
| ...
| Test Teardown | Tear down functional test
| ...
| Documentation | *API test cases*
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
| | When Enable LISP | ${nodes['DUT1']}
| | Then LISP should be enabled | ${nodes['DUT1']} | ${lisp_status}
| | When Disable LISP | ${nodes['DUT1']}
| | Then LISP Should be disabled | ${nodes['DUT1']} | ${lisp_status}

| TC02: DUT can add and delete locator_set
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP locator_set API; on \
| | ... | DUT1 configure locator_set and locator. [Ver1] Check DUT1
| | ... | configured locator_set and locator are correct. [Cfg2] Then
| | ... | remove locator_set and locator. [Ver2] check DUT1 locator_set
| | ... | and locator are removed. [Ref] RFC6830.
| | Given Generate LISP locator_set data
| | ... | ${nodes['DUT1']} | ${locator_set_num}
| | And Enable LISP | ${nodes['DUT1']}
| | When Configure LISP locator_set data | ${nodes['DUT1']}
| | Then LISP locator_set shpuld be configured correctly | ${nodes['DUT1']}
| | When Delete all LISP locator_set from VPP | ${nodes['DUT1']}
| | Then LISP locator_set should be unset | ${nodes['DUT1']}

| TC03: DUT can add, reset and delete locator_set
| | [Tags] | EXPECTED_FAILING
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP locator_set API; on \
| | ... | DUT1 configure locator_set and locator. [Ver1] Check DUT1
| | ... | locator_set and locator are correct. [Cfg2] Then reset
| | ... | locator_set and set it again. [Ver2] Check DUT1 locator_set and
| | ... | locator are correct. [Cfg3] Then remove locator_set and locator.
| | ... | [Ver3] Check DUT1 all locator_set and locators are removed.
| | ... | [Ref] RFC6830.
| | Given Lisp locator_set data use for test reset locator_set are prepared
| | ... | ${nodes['DUT1']} | ${locator_set_num}
| | And Enable LISP | ${nodes['DUT1']}
| | When Configure LISP locator_set data | ${nodes['DUT1']}
| | Then LISP locator_set shpuld be configured correctly | ${nodes['DUT1']}
| | When Delete all LISP locator_set from VPP | ${nodes['DUT1']}
| | Then LISP locator_set should be unset | ${nodes['DUT1']}

| TC04: DUT can add and delete eid address
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP eid API; on DUT1 \
| | ... | configure LISP eid IP address. [Ver1] Check DUT1 configured data
| | ... | is correct. [Cfg2] Remove configured data. [Ver2] Check DUT1 all
| | ... | eid IP addresses are removed. [Ref] RFC6830.
| | Given Enable LISP | ${nodes['DUT1']}
| | When Configure LISP eid address | ${nodes['DUT1']} | ${eid_table}
| | Then LISP eid address should be set correctly to eid table
| | ... | ${nodes['DUT1']} | ${eid_table_vat}
| | When Delete all LISP eid address from VPP | ${nodes['DUT1']} | ${eid_table}
| | Then LISP eid table should be empty | ${nodes['DUT1']}

| TC05: DUT can add and delete LISP map resolver address
| | [Documentation]
| | ... | [Top] DUT1. [Enc] None. [Cfg1] Test LISP map resolver address \
| | ... | API; on DUT1 configure LISP map resolver address. [Ver1] Check
| | ... | DUT1 configured data is correct. [Cfg2] Remove configured data.
| | ... | [Ver2] Check DUT1 all map resolver addresses are removed. [Ref]
| | ... | RFC6830.
| | Given Enable LISP | ${nodes['DUT1']}
| | When Configure LISP map resolver address | ${nodes['DUT1']} | ${map_resolver}
| | Then LISP map resolver address should be configured correctly
| | ... | ${nodes['DUT1']} | ${map_resolver}
| | When Delete all LISP map resolver address from VPP
| | ... | ${nodes['DUT1']} | ${map_resolver}
| | Then LISP map resolver address should be empty | ${nodes['DUT1']}
