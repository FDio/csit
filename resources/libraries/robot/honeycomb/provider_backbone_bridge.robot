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
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| ...     | WITH NAME | IfAPI

*** Keywords ***
| Honeycomb Creates PBB Sub Interface
| | [Documentation] | Uses Honeycomb API to set PBB sub-interface on an\
| | ... | interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - sub_if_id - Sub-interface ID. Type: string
| | ... | - params - Parameters of the sub-interface to be created.
| | ... | Type - dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb creates PBB sub interface \| ${node} \| ${super_if}\
| | ... | \| ${cfg_pbb_sub_if_1} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${params}
| | ...
| | IfAPI.Set Interface Up | ${node} | ${super_if}
| | IfAPI.Create PBB Sub Interface
| | ... | ${node} | ${super_if} | ${params}

| Honeycomb Removes PBB Sub Interface
| | [Documentation] | Uses Honeycomb API to remove PBB sub-interface from its\
| | ... | super interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - sub_if_id - Sub-interface ID. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb Removes PBB sub interface\
| | ... | \| ${node} \| ${super_if} \|
| | ...
| | [Arguments] | ${node} | ${super_if}
| | ...
| | Delete PBB Sub Interface | ${node} | ${super_if}

| PBB Sub Interface Operational Data From Honeycomb Should Be
| | [Documentation] | Retrieves PBB sub-interface operational data from
| | ... | Honeycomb and compares with expected configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - sub_if_id - Sub-interface ID. Type: string
| | ... | - expected_params - Expected operational data. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| PBB sub interface operational data from Honeycomb should be\
| | ... | \| ${node} \| ${super_if} \| ${cfg_pbb_sub_if_1_ID}\
| | ... | \| ${oper_pbb_sub_if_1} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${sub_if_id} | ${expected_params}
| | ...
| | ${data}= | IfAPI.Get PBB Sub Interface Oper Data
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | Compare data structures | ${data} | ${expected_params}

| PBB Sub Interface Operational Data From Honeycomb Should Be Empty
| | [Documentation] | Retrieves interface BPP configuration from Honeycomb,\
| | ... | and expects an empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - sub_if_id - Sub-interface ID. Type: string
| | ...
| | ... | *Example:*
| | ... | \| PBB sub interface operational data from Honeycomb should be empty\
| | ... | \| ${node} \| ${super_if} \| ${cfg_pbb_sub_if_1_ID} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | ${data}= | IfAPI.Get PBB Sub Interface Oper Data
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | Should be empty | ${data}

| Honeycomb Fails to Create PBB Sub Interface
| | [Documentation] | Uses Honeycomb API to set PBB sub-interface with wrong\
| | ... | parameter(s) and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - sub_if_id - Sub-interface ID. Type: string
| | ... | - params - Parameters of the sub-interface to be created.
| | ... | Type - dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to create PBB sub interface\
| | ... | \| ${node} \| ${super_if} \| ${cfg_pbb_sub_if_no_vlan_tag} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${params}
| | ...
| | IfAPI.Set Interface Up | ${node} | ${super_if}
| | Run keyword and expect error | *HoneycombError*not successful*.
| | ... | IfAPI.Create PBB Sub Interface
| | ... | ${node} | ${super_if} | ${params}
