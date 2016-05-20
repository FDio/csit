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
| ...     | WITH NAME | InterfaceAPI

*** Keywords ***
| Honeycomb creates first L2 bridge domain
| | [Documentation] | Uses Honeycomb API to create a bridge domain on the \
| | ... | VPP node. Any other bridge domains will be removed in the process.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - bd_name - name of the created bridge domain. Type: string
| | ... | - settings - settings for the created bridge domain. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb creates first L2 bridge domain \| ${nodes['DUT1']} \
| | ... | \| bd-04 \| ${{flood:True, learn:False}} \|
| | [Arguments] | ${node} | ${bd_name} | ${settings}
| | Add first BD | ${node} | ${bd_name} | &{settings}

| Honeycomb creates L2 bridge domain
| | [Documentation] | Uses Honeycomb API to create a bridge domain on the \
| | ... | VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - bd_name - name of the created bridge domain. Type: string
| | ... | - settings - settings for the created bridge domain. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb creates L2 bridge domain \| ${nodes['DUT1']} \
| | ... | \| bd-04 \| ${{flood:True, learn:False}} \|
| | [Arguments] | ${node} | ${bd_name} | ${settings}
| | Add BD | ${node} | ${bd_name} | &{settings}

| Bridge domain configuration from Honeycomb should be
| | [Documentation] | Uses Honeycomb API to verify bridge domain settings\
| | ... | against provided values.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - bd_name - name of the bridge domain. Type: string
| | ... | - settings - expected settings for the bridge domain. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Bridge domain configuration from Honeycomb should be \
| | ... | \| ${nodes['DUT1']} \| bd-04 \| ${{flood:True,learn:False}} \|
| | [Arguments] | ${node} | ${bd_name} | ${settings}
| | ${api_data}= | Get bd oper data | ${node} | ${bd_name}
| | :FOR | ${key} | IN | @{settings.keys()}
| | | Should be equal | ${settings['${key}']} | ${api_data['${key}']}

| Bridge domain configuration from VAT should be
| | [Documentation] | Uses VAT to verify bridge domain settings\
| | ... | against provided values.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - bd_name - name of the bridge domain. Type: string
| | ... | - settings - expected settings for the bridge domain. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Bridge domain configuration from VAT should be \
| | ... | \| ${nodes['DUT1']} \| bd-04 \| ${{flood:True,learn:False}} \|
| | [Arguments] | ${node} | ${bd_index} | ${settings}
| | ${vat_data}= | VPP get bridge domain data | ${node}
| | ${vat_data}= | Set Variable | ${vat_data[${bd_index}]}
| | :FOR | ${key} | IN | @{settings.keys()}
| | | Run keyword if | $key in $vat_data.keys()
| | | ... | Should be equal | ${settings['${key}']} | ${vat_data['${key}']}

| Honeycomb adds interfaces to bridge domain
| | [Documentation] | Uses Honeycomb API to assign interfaces to a bridge\
| | ... | domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface1, interface2 - names of interfaces to assign to bridge\
| | ... | domain. Type: string
| | ... | - bd_name - name of the bridge domain. Type: string
| | ... | - settings - bridge domain specific interface settings.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds interfaces to bridge domain \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| GigabitEthernet0/9/0 \| bd-04 \
| | ... | \| ${{split_horizon_group:2, bvi:False}} \|
| | [Arguments] | ${node} | ${interface1} | ${interface2} | ${bd_name}
| | ... | ${settings}
| | interfaceAPI.Add bridge domain to interface
| | ... | ${node} | ${interface1} | ${bd_name} | &{settings}
| | interfaceAPI.Add bridge domain to interface
| | ... | ${node} | ${interface2} | ${bd_name} | &{settings}

| Honeycomb should show interfaces assigned to bridge domain
| | [Documentation] | Uses Honeycomb API to verify interface assignment to\
| | ... | bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface1, interface2 - names of interfaces to assign to bridge\
| | ... | domain. Type: string
| | ... | - bd_name - name of the bridge domain. Type: string
| | ... | - settings - bridge domain specific interface settings.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb should show interfaces assigned to bridge domain \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| GigabitEthernet0/9/0 \
| | ... | \| bd-04 \| ${{split_horizon_group:2, bvi:False}} \|
| | [Arguments] | ${node} | ${interface1} | ${interface2} | ${bd_name}
| | ... | ${settings}
| | ${if1_data}= | interfaceAPI.Get interface oper data
| | ... | ${node} | ${interface1}
| | ${if2_data}= | interfaceAPI.Get interface oper data
| | ... | ${node} | ${interface2}
| | Should be equal | ${if1_data['v3po:l2']['bridge-domain']}
| | ... | ${if2_data['v3po:l2']['bridge-domain']} | ${bd_name}
| | Should be equal | ${if1_data['v3po:l2']['split-horizon-group']}
| | ... | ${if2_data['v3po:l2']['split-horizon-group']}
| | ... | ${settings['split_horizon_group']}
| | Should be equal | ${if1_data['v3po:l2']['bridged-virtual-interface']}
| | ... | ${if2_data['v3po:l2']['bridged-virtual-interface']}
| | ... | ${settings['bvi']}

| VAT should show interfaces assigned to bridge domain
| | [Documentation] | Uses VAT to verify interface assignment to\
| | ... | bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - index - index of bridge domains on VPP node. Starts from 0,\
| | ... | new BDs reuse numbers after a bridge domain is removed. Type: int
| | ... | - interface1, interface2 - names of interfaces to assign to bridge\
| | ... | domain. Type: string
| | ... | - settings - bridge domain specific interface settings.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VAT should show interfaces assigned to bridge domain \
| | ... | \| ${nodes['DUT1']} \| ${4} \| GigabitEthernet0/8/0 \
| | ... | \| GigabitEthernet0/9/0 \| ${{split_horizon_group:2, bvi:False}} \|
| | [Arguments] | ${node} | ${index} | ${interface1} | ${interface2}
| | ... | ${settings}
| | ${if1_index}= | Get interface sw index | ${node} | ${interface1}
| | ${if2_index}= | Get interface sw index | ${node} | ${interface2}
| | ${if_indices}= | Create list | ${if1_index} | ${if2_index}
| | ${bd_data}= | VPP get bridge domain data | ${node}
| | ${bd_interfaces}= | Set Variable | ${bd_data[${index}]['sw_if']}
| | @{bd_interfaces}= | Create List | ${bd_interfaces[0]} | ${bd_interfaces[1]}
| | :FOR | ${interface} | IN | @{bd_interfaces}
| | | Should contain | ${if_indices} | ${interface['sw_if_index']}
| | | Should be equal | ${interface['shg']} | ${settings['split_horizon_group']}

| Honeycomb removes all bridge domains
| | [Documentation] | Uses Honeycomb API to remove all bridge domains from the \
| | ... | VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes all bridge domains \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Remove all bds | ${node}

| Honeycomb should show no bridge domains
| | [Documentation] | Uses Honeycomb API to verify the removal of all\
| | ... | bridge domains.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb should show no bridge domains \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | ${bd_data}= | Get all BDs oper data | ${node}
| | Should be empty | ${bd_data}

| VAT should show no bridge domains
| | [Documentation] | Uses VAT to verify the removal of all bridge domains.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VAT should show no bridge domains \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Run Keyword And Expect Error | ValueError: No JSON object could be decoded
| | ... | VPP get bridge domain data | ${node}
