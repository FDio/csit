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
| Resource | resources/libraries/robot/shared/interfaces.robot
| Library  | resources.libraries.python.NodePath
| Library  | resources.libraries.python.LispSetup.LispStatus
| Library  | resources.libraries.python.LispSetup.LispSetup
| Library  | resources.libraries.python.LispSetup.LispGpeStatus
| Library  | resources.libraries.python.LispUtil

*** Keywords ***

| Generate LISP locator_set data
| | [Documentation] | Generate lisp locator_set data for test
| | ... | the lisp locator_set and locator API.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - locator_set_number - Number how many locator_set data
| | ... | will be generated. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - locator_set_values - New generated locator_set data.
| | ... | - locator_set_values_vat - New generated locator_set data expected\
| | ... | from VAT.
| | ...
| | ... | *Example:*
| | ... | \| Given Generate LISP locator_set data \| ${nodes['DUT1']} \
| | ... | \| ${locator_set_number} \|
| | ...
| | [Arguments] | ${dut_node} | ${locator_set_number}
| | ${locator_set_values} | ${locator_set_values_vat}=
| | ... | Generate Unique Lisp Locator Set Data
| | ... | ${dut_node} | ${locator_set_number}
| | Set Test Variable | ${locator_set_values}
| | Set Test Variable | ${locator_set_values_vat}

| Configure LISP locator_set data
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
| | ... | KW locator_set data is prepared, which will be set on the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| When Configure LISP locator_set data \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Set Lisp Locator Set | ${dut_node} | ${locator_set_values}

| LISP locator_set shpuld be configured correctly
| | [Documentation] | Test if the locator_set is set correctly on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - locator_set_values_vat - Generated locator_set data from
| | ... | KW locator_set data is prepared, which are expected from VPP via VAT.
| | ...
| | ... | *Example:*
| | ... | \| Then LISP locator_set shpuld be configured correctly \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${dut_node} | local
| | Lisp Locator S Should Be Equal
| | ... | ${locator_set_values_vat} | ${show_locator_set}

| Delete all LISP locator_set from VPP
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
| | ... | KW locator_set data is prepared, which was set on the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| When Delete all LISP locator_set from VPP \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Unset Lisp Locator Set | ${dut_node} | ${locator_set_values}

| LISP locator_set should be unset
| | [Documentation] | Test if all locator_set are unset from VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Then LISP locator_set should be unset \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${dut_node} | ${EMPTY}
| | Lisp Is Empty | ${show_locator_set}

| Lisp locator_set data use for test reset locator_set are prepared
| | [Documentation] | Generate lisp special type of locator_set data.
| | ... | This data will be use for test reset locator_set.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - locator_set_number - Number how many locator_set data
| | ... | it will generate. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - locator_set_values - New generate locator_set data.
| | ... | - locator_set_values_vat - New generated locator_set data expected\
| | ... | from VAT.
| | ...
| | ... | *Example:*
| | ... | \| Given Lisp locator_set data use for test reset locator_set \
| | ... | are prepared \| ${nodes['DUT1']} \| ${locator_set_number} \|
| | ...
| | [Arguments] | ${dut_node} | ${locator_set_number}
| | ${locator_set_values} | ${locator_set_values_vat}=
| | ... | Generate Duplicate Lisp Locator Set Data
| | ... | ${dut_node} | ${locator_set_number}
| | Set Test Variable | ${locator_set_values}
| | Set Test Variable | ${locator_set_values_vat}

| Configure LISP eid address
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
| | ... | \| When Configure LISP eid address \| ${nodes['DUT1']} \
| | ... | \| ${eid_table} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_eid}
| | Vpp Set Lisp Eid Table | ${dut_node} | ${set_eid}

| LISP eid address should be set correctly to eid table
| | [Documentation] | Test if the locator_set is set correctly on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_eid - Example eid data, which was set to the VPP node.
| | ... | Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - set_eid - Generated eid data, which will be set to the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| Then LISP eid address should be set correctly to eid table \
| | ... | \| ${nodes['DUT1']} \| ${eid_table} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_eid}
| | ${show_eid}= | Vpp Show Lisp Eid Table | ${dut_node}
| | Lisp Should Be Equal | ${set_eid} | ${show_eid}

| Delete all LISP eid address from VPP
| | [Documentation] | Delete all lisp eid address from the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_eid - Eid data which will be removed from the VPP node.
| | ... | Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| When Delete all LISP eid address from VPP \
| | ... | \| ${nodes['DUT1']} \| ${eid_table} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_eid}
| | Vpp Unset Lisp Eid Table | ${dut_node} | ${set_eid}

| LISP eid table should be empty
| | [Documentation] | Test if the eid table is empty.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Then LISP eid table should be empty \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_eid}= | Vpp Show Lisp Eid Table | ${dut_node}
| | Lisp Is Empty | ${show_eid}

| Configure LISP map resolver address
| | [Documentation] | Set the lisp map resolver address in the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_map_resolver - Map resolver data, which will be set on
| | ... | the VPP node. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| When Configure LISP map resolver address \| ${nodes['DUT1']} \
| | ... | \| ${map_resolver} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_map_resolver}
| | Vpp Set Lisp Map Resolver | ${dut_node} | ${set_map_resolver}

| LISP map resolver address should be configured correctly
| | [Documentation] | Test if the map resolver address is set correctly
| | ... | on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - set_map_resolver - Map resolver data, which was set on
| | ... | the VPP node. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Then LISP map resolver address should be configured correctly \
| | ... | \| ${nodes['DUT1']} \| ${map_resolver} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_map_resolver}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${dut_node}
| | Lisp Should Be Equal | ${set_map_resolver} | ${show_map_resolver}

| Delete all LISP map resolver address from VPP
| | [Documentation] | Delete all lisp map resolver address on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - map_resolver - Map resolver data, which will be remove from
| | ... | the VPP. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| When Delete all LISP map resolver address from VPP \
| | ... | \| ${nodes['DUT1']} \| ${map_resolver} \|
| | ...
| | [Arguments] | ${dut_node} | ${set_map_resolver}
| | Vpp Unset Lisp Map Resolver | ${dut_node} | ${set_map_resolver}

| LISP map resolver address should be empty
| | [Documentation] | Test if the map resolver are empty.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Then LISP map resolver address should be empty \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${dut_node}
| | Lisp Is Empty | ${show_map_resolver}

| Enable LISP
| | [Documentation] | Enable LISP on VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Enable LISP \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Lisp Enable Disable | ${dut_node} | enable

| LISP should be enabled
| | [Documentation] | Check if the lisp is enabled.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lisp_status_data - Lisp status data, which was set on
| | ... | the VPP node. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| LISP should be enabled \| ${nodes['DUT1']} \
| | ... | \| ${lisp_status_data} \|
| | ...
| | [Arguments] | ${dut_node} | ${lisp_status_data}
| | ${show_lisp_stat}= | Vpp Show Lisp State | ${dut_node}
| | Lisp Should Be Equal | ${show_lisp_stat} | ${lisp_status_data[1]}

| Disable LISP
| | [Documentation] | Disable LISP on VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Disable LISP \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Lisp Enable Disable | ${dut_node} | disable

| LISP Should be disabled
| | [Documentation] | LISP Should be disabled.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - lisp_status_data - Lisp status data, which was set on
| | ... | the VPP node. Type: list
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| LISP Should be disabled \| ${nodes['DUT1']} \
| | ... | \| ${lisp_status_data} \|
| | ...
| | [Arguments] | ${dut_node} | ${lisp_status_data}
| | ${show_lisp_stat}= | Vpp Show Lisp State | ${dut_node}
| | Lisp Should Be Equal | ${show_lisp_stat} | ${lisp_status_data[0]}

| Enable Lisp Gpe
| | [Documentation] | Enable Lisp Gpe on VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Enable Lisp Gpe \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Lisp Gpe Enable Disable | ${dut_node} | enable

| Disable Lisp Gpe
| | [Documentation] | Disable Lisp Gpe on VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Disable Lisp Gpe \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Lisp Gpe Enable Disable | ${dut_node} | disable
