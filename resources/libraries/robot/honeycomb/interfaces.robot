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
| Library | resources/libraries/python/HoneycombUtil.py
| Library | resources.libraries.python.InterfaceUtil
| ... | WITH NAME | InterfaceCLI
| Library | resources.libraries.python.HoneycombAPIKeywords.InterfaceKeywords
| ... | WITH NAME | interfaceAPI

*** Keywords ***
| Honeycomb sets interface state
| | [Arguments] | ${node} | ${interface} | ${state}
| | [Documentation] | Uses Honeycomb API to change the admin state
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | interfaceAPI.Set interface state | ${node} | ${interface} | ${state}

| Interface state from Honeycomb should be
| | [Arguments] | ${node} | ${interface} | ${state}
| | [Documentation] | Retrieves interface admin state through Honeycomb and
| | ... | compares with state supplied in argument
| | ...
| | ... | *Arguments:*
| | ... | - state - expected interface state
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | ${api_data}= | interfaceAPI.Get interface oper info | ${node} | ${interface}
| | ${api_state}= | Set Variable | ${api_data['admin-status']}
| | Should be equal | ${api_state} | ${state}

| Interface state from VAT should be
| | [Arguments] | ${node} | ${interface} | ${state}
| | [Documentation] | Retrieves interface admin state through VAT and compares
| | ... | with state supplied in argument
| | ...
| | ... | *Arguments:*
| | ... | - state - expected interface state
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | ... | _NOTE:_ Vat returns state as int (1/0) instead of string (up/down).
| | ... | This keyword also handles translation.
| | ...
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | ${vat_state}= | Set Variable if
| | ... | ${vat_data['admin_up_down']} == 1 | up | down
| | Should be equal | ${vat_state} | ${state}

| Interface state is
| | [Arguments] | ${node} | ${interface} | ${state}
| | [Documentation] | Uses VPP binary API to ensure that the interface under
| | ... | test is in the specified admin state.
| | ...
| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | interfaceAPI.Set interface state | ${node} | ${interface} | ${state}
