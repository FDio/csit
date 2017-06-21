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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.honeycomb.HcAPIKwNSH.NSHKeywords
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| Documentation | Keywords used to test Honeycomb NSH node.

*** Keywords ***
| NSH Operational Data From Honeycomb Should Be empty
| | [Documentation] | Uses Honeycomb API to retrieve NSH configuration\
| | ... | and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NSH Operational Data From Honeycomb Should Be empty \
| | ... | \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Run keyword and expect error | *Status code: 404*
| | ... | Get NSH oper data | ${node}

| Honeycomb adds NSH entry
| | [Documentation] | Uses Honeycomb API to configure an NSH entry.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - name - name for the NSH entry. Type: string
| | ... | - data - settings for the NSH entry. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures NSH entry \| ${nodes['DUT1']} \| nsh_1 \
| | ... | \| ${data} \|
| | [Arguments] | ${node} | ${name} | ${data}
| | Add NSH entry | ${node} | ${name} | ${data}

| Honeycomb removes NSH entry
| | [Documentation] | Uses Honeycomb API to delete the specified NSH entry.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - name - name of the NSH entry to be deleted. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes NSH entry \| ${nodes['DUT1']} \| nsh_1 \|
| | [Arguments] | ${node} | ${name}
| | Remove NSH entry | ${node} | ${name}

| Honeycomb adds NSH map
| | [Documentation] | Uses Honeycomb API to configure an NSH map.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - name - name for the NSH map. Type: string
| | ... | - data - settings for the NSH map. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures NSH map \| ${nodes['DUT1']} \| nsh_1 \
| | ... | \| ${data} \|
| | [Arguments] | ${node} | ${name} | ${data}
| | Add NSH map | ${node} | ${name} | ${data}

| Honeycomb removes NSH map
| | [Documentation] | Uses Honeycomb API to delete an NSH map.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - name - name of the NSH map to be deleted. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes NSH map \| ${nodes['DUT1']} \| nsh_1 \|
| | [Arguments] | ${node} | ${name}
| | Remove NSH map | ${node} | ${name}

| NSH entry from Honeycomb should be
| | [Documentation] | Retrieves oper data for NSH entry and compares\
| | ... | with provided values.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - name - name of the NSH entry. Type: string
| | ... | - data - expected NSH entry settings. Type dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NSH entry from Honeycomb should be \| ${nodes['DUT1']} \| nsh_1 \
| | ... | \| ${data} \|
| | [Arguments] | ${node} | ${name} | ${data}
| | ${oper_data}= | Get NSH oper data | ${node} | entry_name=${name}
| | Compare data structures | ${oper_data} | ${data}

| NSH map from Honeycomb should be
| | [Documentation] | Retrieves oper data for NSH map and compares\
| | ... | with provided values.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - name - name of the NSH map. Type: string
| | ... | - data - expected NSH map settings. Type dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NSH map from Honeycomb should be \| ${nodes['DUT1']} \| nsh_1 \
| | ... | \| ${data} \|
| | [Arguments] | ${node} | ${name} | ${data}
| | ${oper_data}= | Get NSH oper data | ${node} | map_name=${name}
| | Compare data structures | ${oper_data} | ${data}

| NSH map from Honeycomb should not exist
| | [Documentation] | Retrieves oper data for NSH map and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - name - name of the NSH map. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NSH map from Honeycomb should not exist \| ${nodes['DUT1']} \
| | ... | \| nsh_1 \|
| | [Arguments] | ${node} | ${name}
| | Run keyword and expect error | *Status code: 404*
| | ... | Get NSH oper data | ${node} | map_name=${name}

| Honeycomb clears NSH configuration
| | [Documentation] | Uses Honeycomb API to remove all NSH settings.
| | ...
| | [Arguments] | ${node}
| | Clear NSH settings | ${node}