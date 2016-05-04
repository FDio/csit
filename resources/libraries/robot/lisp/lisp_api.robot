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
| Library  | resources.libraries.python.LispSetup.LispSetup
| Library  | resources.libraries.python.LispUtil

*** Keywords ***

| Lisp locator_set data is prepared
| | [Documentation] | Generate lisp locator_set data for test
| | ...             | the lisp locator_set and locator API.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${locator_set_number} - Number how many locator_set data
| | ... |                           will be generated. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${locator_set_values} - New generated locator_set data.
| | ...
| | ... | *Example:*
| | ... | \| Given Lisp locator_set data is prepared \| ${nodes['DUT1']} \
| | ... | \| ${locator_set_number} \|
| | ...
| | [Arguments] | ${dut_node} | ${locator_set_number}
| | ${locator_set_values}= | Generate Lisp Locator Set Data |
| | ...                    | ${dut_node} | ${locator_set_number}
| | Set Test Variable | ${locator_set_values}

| Lisp locator_set data is set
| | [Documentation] | Set the lisp locator_set and locator on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${locator_set_values} - Generated locator_set data from
| | ... |                           KW locator_set data is prepared,
| | ... |                           which will be set on the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| When Lisp locator_set data is set \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Set Lisp Locator Set | ${dut_node} | ${locator_set_values}

| Lisp locator_set is set correct
| | [Documentation] | Test if the locator_set is set correct on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${locator_set_values} - Generated locator_set data from
| | ... |                           KW locator_set data is prepared,
| | ... |                           which were set to VPP node.
| | ...
| | ... | *Example:*
| | ... | \| Then Lisp locator_set is set correct \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${dut_node}
| | Lisp Locator S Should Be Equal
| | ... | ${locator_set_values} | ${show_locator_set}

| Delete all lisp locator_set from VPP
| | [Documentation] | Delete all lisp locator_set on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${locator_set_values} - Generated locator_set data from
| | ... |                           KW locator_set data is prepared,
| | ... |                           which was set on the VPP node.
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
| | ... | - ${dut_node} - DUT node. Type: dictionary
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
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${locator_set_number} - Number how many locator_set data
| | ...                          | it will generate. Type: int
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${locator_set_values} - New generate locator_set data.
| | ...
| | ... | *Example:*
| | ... | \| Given Lisp locator_set data use for test reset locator_set \
| | ... |    are prepared \| ${nodes['DUT1']} \| ${locator_set_number} \|
| | ...
| | [Arguments] | ${dut_node} | ${locator_set_number}
| | ${locator_set_values}= | Generate Lisp Locator Set Reset Data |
| | ...                    | ${dut_node} | ${locator_set_number}
| | Set Test Variable | ${locator_set_values}

| Lisp eid address is prepared
| | [Documentation] | Generate lisp eid address for testing lisp eid API.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${eid_ipv4_num} - Number of generate ipv4 address. Type: int
| | ... | - ${eid_ipv6_num} - Number of generate ipv6 address. Type: int
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${set_eid} - New generate eid data.
| | ...
| | ... | *Example:*
| | ... | \| Given Lisp eid address is prepared \| ${nodes['DUT1']} \
| | ... | \| ${eid_ipv4_num} \| ${eid_ipv6_num} \|
| | ...
| | [Arguments] | ${dut_node} | ${eid_ipv4_num} | ${eid_ipv6_num}
| | ${set_eid} = | Generate Lisp Local Eid Data
| | ... | ${eid_ipv4_num} | ${eid_ipv6_num}
| | Set Test Variable | ${set_eid}

| Lisp eid address is set
| | [Documentation] | Set the lisp eid address on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${set_eid} - Generated eid data which will be set to VPP.
| | ...
| | ... | *Example:*
| | ... | \| When Lisp eid address is set \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Set Lisp Eid Table | ${dut_node} | ${set_eid}

| Lisp eid address is set correct to eid table
| | [Documentation] | Test if the locator_set is set correct on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${set_eid} - Generated eid data which will be set to the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| Then Lisp eid address is set correct to eid table \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_eid}= | Vpp Show Lisp Local Eid Table | ${dut_node}
| | Lisp Should Be Equal | ${set_eid} | ${show_eid}

| Delete all lisp eid address from VPP
| | [Documentation] | Delete all lisp eid address from the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${set_eid} - Generated eid data which was set to the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| When Delete all lisp eid address from VPP \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Unset Lisp Eid Table | ${dut_node} | ${set_eid}

| Lisp eid table should be empty
| | [Documentation] | Test if the eid table is empty.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
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

| Lisp map resolver address is prepared
| | [Documentation] | Generate map resolver address for testing
| | ...             | lisp map resolver API.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${map_resolver_ipv4_num} - Number of generate ipv4 address.
| | ... |                              Type: int
| | ... | - ${map_resolver_ipv6_num} - Number of generate ipv6 address.
| | ... |                              Type: int
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${set_map_resolver} - Generate map resolver data.
| | ...
| | ... | *Example:*
| | ... | \| Given Lisp map resolver address is prepared \
| | ... | \| ${nodes['DUT1']} \| ${map_resolver_ipv4_num} \
| | ... | \| ${map_resolver_ipv6_num} \|
| | ...
| | [Arguments] | ${dut_node} | ${map_resolver_ipv4_num} | ${map_resolver_ipv6_num}
| | ${set_map_resolver} = | Generate Lisp Map Resolver Data
| | ... | ${map_resolver_ipv4_num} | ${map_resolver_ipv6_num}
| | Set Test Variable | ${set_map_resolver}

| Lisp map resolver address is set
| | [Documentation] | Set the lisp map resolver address in the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${set_map_resolver} - Map resolver data which will be set
| | ... |                         to the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| When Lisp map resolver address is set \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Set Lisp Map Resolver | ${dut_node} | ${set_map_resolver}

| Lisp map resolver address is set correct
| | [Documentation] | Test if the map resolver address is set correct
| | ...             | on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${set_map_resolver} - Map resolver data which was set
| | ... |                         to the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| Then Lisp map resolver address is set correct \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${dut_node}
| | Lisp Should Be Equal | ${set_map_resolver} | ${show_map_resolver}

| Delete all lisp map resolver address from VPP
| | [Documentation] | Delete all lisp map resolver address on the VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | _NOTE:_ This KW requires following test case variables:
| | ... | - ${set_map_resolver} - Map resolver data which was set
| | ... |                         to the VPP node.
| | ...
| | ... | *Example:*
| | ... | \| When Delete all lisp map resolver address from VPP \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | Vpp Unset Lisp Map Resolver | ${dut_node} | ${set_map_resolver}

| Lip map resolver address should be empty
| | [Documentation] | Test if the map resolver are empty.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
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
