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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.honeycomb.HcAPIKwBridgeDomain.BridgeDomainKeywords
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords

*** Keywords ***
| Honeycomb adds L2 FIB entry to bridge domain
| | [Documentation] | Add L2 FIB entry to the specified bridge domain using \
| | ... | Honyecomb API.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - l2_fib_settings - The parameters of the new L2 FIB entry. \
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb adds L2 FIB entry to bridge domain \
| | ... | \| ${nodes['DUT1']} \| test_bd \| ${l2_fib_forward_cfg} \|
| | ...
| | [Arguments] | ${node} | ${bd_name} | ${l2_fib_settings}
| | ...
| | Add L2 FIB Entry | ${node} | ${bd_name} | ${l2_fib_settings}

| L2 FIB Table from Honeycomb should be empty
| | [Documentation] | Check if the L2 FIB table in the specified bridge domain \
| | ... | is empty.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ...
| | ... | *Example:*
| | ... | \| L2 FIB Table from Honeycomb should be empty \
| | ... | \| ${nodes['DUT1']} \| test_bd \|
| | ...
| | [Arguments] | ${node} | ${bd_name}
| | ...
| | ${l2_fib_data}= | Get All L2 FIB Entries | ${node} | ${bd_name}
| | Should be empty | ${l2_fib_data}

| L2 FIB Entry from Honeycomb should be
| | [Documentation] | Retrieves the operational data about the specified L2 \
| | ... | FIB entry and checks if they are as expected.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - l2_fib_ref_data - L2 FIB entry referential data. Type: dictionay
| | ...
| | ... | *Example:*
| | ... | \| L2 FIB Entry from Honeycomb should be \
| | ... | \| ${nodes['DUT1']} \| test_bd \| ${l2_fib_forward_oper} \|
| | ...
| | [Arguments] | ${node} | ${bd_name} | ${l2_fib_ref_data}
| | ...
| | ${l2_fib_data}= | Get L2 FIB Entry | ${node} | ${bd_name}
| | ... | ${l2_fib_ref_data['phys-address']}
| | Compare Data Structures | ${l2_fib_data} | ${l2_fib_ref_data}

| Honeycomb removes L2 FIB entry
| | [Documentation] | Remove the specified L2 FIB entry from the bridge \
| | ... | domain's L2 FIB table.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - mac - MAC address used as the key in L2 FIB data structure. \
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb removes L2 FIB entry \
| | ... | \| ${nodes['DUT1']} \| test_bd \
| | ... | \| ${l2_fib_forward_oper['phys-address']} \|
| | ...
| | [Arguments] | ${node} | ${bd_name} | ${mac}
| | ...
| | Remove L2 FIB Entry | ${node} | ${bd_name} | ${mac}

| Honeycomb removes all L2 FIB entries
| | [Documentation] | Remove all L2 FIB enties from the bridge domain's L2 FIB \
| | ... | table.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb removes all L2 FIB entries \
| | ... | \| ${nodes['DUT1']} \| test_bd \|
| | ...
| | [Arguments] | ${node} | ${bd_name}
| | ...
| | Remove all L2 FIB entries | ${node} | ${bd_name}

| Honeycomb fails to add wrong L2 FIB entry
| | [Documentation] | Honeycomb tries to add a wrong L2 FIB entry and expects \
| | ... | that it fails.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - l2_fib_settings - The wrong parameters of the new L2 FIB entry. \
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to add wrong L2 FIB entry \
| | ... | \| ${nodes['DUT1']} \| test_bd \| ${l2_fib_wrong_cfg} \|
| | ...
| | [Arguments] | ${node} | ${bd_name} | ${l2_fib_settings}
| | ...
| | Run keyword and expect error | *HoneycombError: * was not successful. *00.
| | ... | Add L2 FIB Entry | ${node} | ${bd_name} | ${l2_fib_settings}

| Honeycomb fails to modify L2 FIB entry
| | [Documentation] | Honeycomb tries to modify an existing L2 FIB entry and \
| | ... | expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - mac - MAC address used as the key in L2 FIB data structure. \
| | ... | Type: string
| | ... | - param - The parameter to be modified. Type: string
| | ... | - value - The new value of the parameter. Type: string or integer
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to modify L2 FIB entry \
| | ... | \| ${nodes['DUT1']} \| test_bd \
| | ... | \| ${l2_fib_forward_oper['phys-address']} \| action \
| | ... | \| l2-fib-forward \|
| | ...
| | [Arguments] | ${node} | ${bd_name} | ${mac} | ${param} | ${value}
| | ...
| | Run keyword and expect error | *HoneycombError: * was not successful. *00.
| | ... | Modify L2 FIB Entry
| | ... | ${node} | ${bd_name} | ${mac} | ${param} | ${value}

| L2 FIB entry from VAT should be
| | [Documentation] | Retrieves the operational data about the specified L2 \
| | ... | FIB entry using VAT and checks if it is as expected.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_index - Index of the bridge domain. Type: integer
| | ... | - l2_fib_ref_data - L2 FIB entry referential data. Type: dictionay
| | ...
| | ... | *Example:*
| | ... | \| L2 FIB entry from VAT should be \
| | ... | \| ${nodes['DUT1']} \| test_bd \| ${l2_fib_forward_oper} \|
| | ...
| | [Arguments] | ${node} | ${bd_index} | ${l2_fib_ref_data}
| | ...
| | ${l2_fib_data}= | Get L2 FIB entry VAT | ${node} | ${bd_index}
| | ... | ${l2_fib_ref_data['mac']}
| | Compare Data Structures | ${l2_fib_data} | ${l2_fib_ref_data}

| L2 FIB Table from VAT should be empty
| | [Documentation] | Check if the L2 FIB table in the specified bridge domain \
| | ... | is empty. VAT is used to get operational data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_index - Index of the bridge domain. Type: integer
| | ...
| | ... | *Example:*
| | ... | \| L2 FIB Table from VAT should be empty \
| | ... | \| ${nodes['DUT1']} \| test_bd \|
| | ...
| | [Arguments] | ${node} | ${bd_index}
| | ...
| | ${l2_fib_data}= | Get L2 FIB table VAT | ${node} | ${bd_index}
| | Should be empty | ${l2_fib_data}
