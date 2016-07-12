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
| Resource | resources/libraries/robot/interfaces.robot
| Library  | resources.libraries.python.NodePath
| Library  | resources.libraries.python.LispSetup.LispStatus
| Library  | resources.libraries.python.LispSetup.LispSetup
| Library  | resources.libraries.python.LispUtil

*** Keywords ***

| Lisp locator_set data is prepared
| | [Documentation] | Generate lisp locator_set data for test
| | ...             | the lisp locator_set and locator API.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - locator_set_number - Number how many locator_set data
| | ... |                        will be generated. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - locator_set_values - New generated locator_set data.
| | ...
| | ... | *Example:*
| | ... | \| Given Lisp locator_set data is prepared \| ${nodes['DUT1']} \
| | ... | \| ${locator_set_number} \|
| | ...
| | [Arguments] | ${dut_node} | ${locator_set_number}
| | ${locator_set_values}= | Generate Unique Lisp Locator Set Data |
| | ...                    | ${dut_node} | ${locator_set_number}
| | Set Test Variable | ${locator_set_values}

| Lisp locator_set data is set
| | [Documentation] | Set the lisp locator_set and locator on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - locator_set_values - Generated locator_set data from
| | ... |                        KW locator_set data is prepared,
| | ... |                        which will be set on the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| When Lisp locator_set data is set \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Set Lisp Locator Set | ${dut_node} | ${locator_set_values}

| Lisp locator_set is set correctly
| | [Documentation] | Test if the locator_set is set correctly on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - locator_set_values - Generated locator_set data from
| | ... |                        KW locator_set data is prepared,
| | ... |                        which were set to VPP node.
| | ...
| | ... | *Example:*
| | ... | \| Then Lisp locator_set is set correctly \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${dut_node}
| | Lisp Locator S Should Be Equal
| | ... | ${locator_set_values} | ${show_locator_set}

| Delete all lisp locator_set from VPP
| | [Documentation] | Delete all lisp locator_set on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - locator_set_values - Generated locator_set data from
| | ... |                        KW locator_set data is prepared,
| | ... |                        which was set on the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| When Delete all lisp locator_set from VPP \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Unset Lisp Locator Set | ${dut_node} | ${locator_set_values}

| Lisp locator_set should be unset
| | [Documentation] | Test if all locator_set are unset from VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Then Lisp locator_set should be unset \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${dut_node}
| | Lisp Is Empty | ${show_locator_set}

| Lisp locator_set data use for test reset locator_set are prepared
| | [Documentation] | Generate lisp special type of locator_set data.
| | ...             | This data will be use for test reset locator_set.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - locator_set_number - Number how many locator_set data
| | ... |                        it will generate. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - locator_set_values - New generate locator_set data.
| | ...
| | ... | *Example:*
| | ... | \| Given Lisp locator_set data use for test reset locator_set \
| | ... |    are prepared \| ${nodes['DUT1']} \| ${locator_set_number} \|
| | ...
| | [Arguments] | ${dut_node} | ${locator_set_number}
| | ${locator_set_values}= | Generate Duplicate Lisp Locator Set Data |
| | ...                    | ${dut_node} | ${locator_set_number}
| | Set Test Variable | ${locator_set_values}

| Lisp eid address is set
| | [Documentation] | Set the lisp eid address on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_eid - Test eid data. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| When Lisp eid address is set \| ${nodes['DUT1']} \| ${eid_table} |\
| | ...
| | [Arguments] | ${dut_node} | ${set_eid}
| | Vpp Set Lisp Eid Table | ${dut_node} | ${set_eid}

| Lisp eid address is set correctly to eid table
| | [Documentation] | Test if the locator_set is set correctly on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_eid - Example eid data, which was set to the VPP node.
| | ... |                Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - set_eid - Generated eid data, which will be set to the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| Then Lisp eid address is set correctly to eid table \
| | ... | \| ${nodes['DUT1']} \| ${eid_table} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_eid}
| | ${show_eid}= | Vpp Show Lisp Local Eid Table | ${dut_node}
| | Lisp Should Be Equal | ${set_eid} | ${show_eid}

| Delete all lisp eid address from VPP
| | [Documentation] | Delete all lisp eid address from the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_eid - Eid data which will be removed from the VPP node.
| | ... |             Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| When Delete all lisp eid address from VPP \
| | ... | \| ${nodes['DUT1']} \| ${eid_table} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_eid}
| | Vpp Unset Lisp Eid Table | ${dut_node} | ${set_eid}

| Lisp eid table should be empty
| | [Documentation] | Test if the eid table is empty.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Then Lisp eid table should be empty \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_eid}= | Vpp Show Lisp Local Eid Table | ${dut_node}
| | Lisp Is Empty | ${show_eid}

| Lisp map resolver address is set
| | [Documentation] | Set the lisp map resolver address in the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_map_resolver - Map resolver data, which will be set on
| | ... |                      the VPP node. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| When Lisp map resolver address is set \| ${nodes['DUT1']} \
| | ... | \| ${map_resolver} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_map_resolver}
| | Vpp Set Lisp Map Resolver | ${dut_node} | ${set_map_resolver}

| Lisp map resolver address is set correctly
| | [Documentation] | Test if the map resolver address is set correctly
| | ...             | on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_map_resolver - Map resolver data, which was set on
| | ... |                      the VPP node. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Then Lisp map resolver address is set correctly \
| | ... | \| ${nodes['DUT1']} \| ${map_resolver} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_map_resolver}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${dut_node}
| | Lisp Should Be Equal | ${set_map_resolver} | ${show_map_resolver}

| Delete all lisp map resolver address from VPP
| | [Documentation] | Delete all lisp map resolver address on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - map_resolver - Map resolver data, which will be remove from
| | ... |                  the VPP. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| When Delete all lisp map resolver address from VPP \
| | ... | \| ${nodes['DUT1']} \| ${map_resolver} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_map_resolver}
| | Vpp Unset Lisp Map Resolver | ${dut_node} | ${set_map_resolver}

| Lip map resolver address should be empty
| | [Documentation] | Test if the map resolver are empty.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Then Lip map resolver address should be empty \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${dut_node}
| | Lisp Is Empty | ${show_map_resolver}

| Enable lisp
| | [Documentation] | Enable lisp on VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Enable lisp \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Lisp Enable Disable | ${dut_node} | enable

| Check if lisp is enabled
| | [Documentation] | Check if the lisp is enabled.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lisp_status_data - Lisp status data, which was set on
| | ... |                      the VPP node. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Check if lisp is enabled \| ${nodes['DUT1']} \
| | ... | \| ${lisp_status_data} \|
| | ...
| | [Arguments] | ${dut_node} | ${lisp_status_data}
| | ${show_lisp_stat}= | Vpp Show Lisp State | ${dut_node}
| | Lisp Should Be Equal | ${show_lisp_stat} | ${lisp_status_data[1]}

| Disable lisp
| | [Documentation] | Disable lisp on VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Disable lisp \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Lisp Enable Disable | ${dut_node} | disable

| Check if lisp is disabled
| | [Documentation] | Check if lisp is disabled.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lisp_status_data - Lisp status data, which was set on
| | ... |                      the VPP node. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Check if lisp is disabled \| ${nodes['DUT1']} \
| | ... | \| ${lisp_status_data} \|
| | ...
| | [Arguments] | ${dut_node} | ${lisp_status_data}
| | ${show_lisp_stat}= | Vpp Show Lisp State | ${dut_node}
| | Lisp Should Be Equal | ${show_lisp_stat} | ${lisp_status_data[0]}
