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
| Setup variables for interface test suite
| | [Documentation] | Creates suite scope variables 'node' and 'interface'.
| | ... | 'node' can be any DUT type node in test topology.
| | ...
| | ... | *Sets suite variables:*
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of the first interface on the specified node
| | ...
| | :FOR | ${node} | IN | @{nodes.values()}
| | | Run Keyword If | $node['type'] == 'DUT'
| | | ... | Run Keywords | Set Suite Variable | ${node} | AND | Exit For Loop
| | Set Suite Variable | ${interface}
| | ... | ${node['interfaces'].values()[0]['name']}

| Honeycomb sets interface state
| | [Documentation] | Uses Honeycomb API to change the operational state
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ...
| | ... | *Uses suite variables:*
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | [Arguments] | ${state}
| | interfaceAPI.Set interface state | ${node} | ${interface} | ${state}
| | InterfaceCLI.VPP node interfaces ready wait | ${node}

| VAT sets interface state
| | [Documentation] | Uses test API (VAT) to change the operational state
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ...
| | ... | *Uses suite variables:*
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | [Arguments] | ${state}
| | InterfaceCLI.Set interface state | ${node} | ${interface} | ${state}
| | InterfaceCLI.VPP node interfaces ready wait | ${node}

| Interface state (Honeycomb) should be
| | [Arguments] | ${state}
| | [Documentation] | Retrieves interface state through Honeycomb and compares
| | ... | with state supplied in argument
| | ...
| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ...
| | ... | *Uses suite variables:*
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | ${api_data}= | interfaceAPI.Get interface oper info | ${node} | ${interface}
| | ${api_state}= | Set Variable | ${api_data['oper-status']}
| | Should be equal | ${api_state} | ${state}

| Interface state (VAT) should be
| | [Arguments] | ${state}
| | [Documentation] | Retrieves interface state through VAT and compares
| | ... | with state supplied in argument

| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ...
| | ... | *Uses suite variables:*
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | ... | _NOTE:_ Vat returns state as int (1/0) instead of string (up/down).
| | ... | This keyword also handles translation.
| | ...
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | ${vat_state}= | Set Variable if
| | ... | ${vat_data['link_up_down']} == 1 | up | down
| | Should be equal | ${vat_state} | ${state}

| Interface state is
| | [Arguments] | ${state}
| | [Documentation] | Ensures that the interface under test is
| | ... | in the specified state.
| | ...
| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ...
| | VAT sets interface state | ${state}
