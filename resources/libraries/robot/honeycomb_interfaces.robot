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
| | ...
| | ... | *Sets suite variables:*
| | ... | - ${node} - a DUT node
| | ... | - ${interface} - the first interface of specified node
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
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name string of an interface on the DUT node
| | ... | - state - state string to set on interface
| | ...
| | [Arguments] | ${node} | ${interface} | ${state}
| | interfaceAPI.Set interface state | ${node} | ${interface} | ${state}
| | InterfaceCLI.VPP node interfaces ready wait | ${node}

| VAT sets interface state
| | [Documentation] | Uses test API (VAT) to change the operational state
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the DUT node
| | ... | - state - state to set on interface
| | ...
| | [Arguments] | ${node} | ${interface} | ${state}
| | InterfaceCLI.Set interface state | ${node} | ${interface} | ${state}
| | InterfaceCLI.VPP node interfaces ready wait | ${node}

| Get interface state
| | [Documentation] | Uses Honeycomb API and VAT to retrieve operational state
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the DUT node
| | ... | - state - state to set on interface
| | ...
| | ... | *Return:*
| | ... | - interface operational status from Honeycomb API and VAT
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | interfaceAPI.Get interface oper info | ${node} | ${interface}
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | Return from keyword if | '${vat_data['link_up_down']}' == '1'
| | ... | up | ${api_data['oper-status']}
| | Return from keyword if | '${vat_data['link_up_down']}' == '0'
| | ... | down | ${api_data['oper-status']}
