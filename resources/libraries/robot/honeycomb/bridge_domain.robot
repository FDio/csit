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
| Library | resources.libraries.python.InterfaceUtil
| ...     | WITH NAME | interfaceCLI

*** Keywords ***
| Honeycomb creates first L2 bridge domain
| | [Documentation] | Uses Honeycomb API to create a bridge domain on the \
| | ... | VPP node. Any other bridge domains will be removed in the process.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the created bridge domain. Type: string
| | ... | - settings - Settings for the created bridge domain. Type: dictionary
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
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the created bridge domain. Type: string
| | ... | - settings - Settings for the created bridge domain. Type: dictionary
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
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - settings - Expected settings for the bridge domain. Type: dictionary
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
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - settings - Expected settings for the bridge domain. Type: dictionary
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
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface1, interface2 - Names of interfaces to assign to bridge\
| | ... | domain. Type: string
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - settings - Bridge domain specific interface settings.\
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

| Honeycomb fails to add interfaces to bridge domain
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
| | ... | \| Honeycomb fails to add interfaces to bridge domain \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| GigabitEthernet0/9/0 \
| | ... | \| bd-04 \| ${{split_horizon_group:2, bvi:True}} \|
| | [Arguments] | ${node} | ${interface1} | ${interface2} | ${bd_name}
| | ... | ${settings}
| | Run keyword and expect error | *Failed to validate*
| | ... | Honeycomb adds interfaces to bridge domain | ${node} | ${interface1}
| | ... | ${interface2} | ${bd_name} | ${settings}

| Honeycomb should show interfaces assigned to bridge domain
| | [Documentation] | Uses Honeycomb API to verify interface assignment to\
| | ... | bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface1, interface2 - Names of interfaces to assign to bridge\
| | ... | domain. Type: string
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - settings - Bridge domain specific interface settings.\
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

| Honeycomb should not show interfaces assigned to bridge domain
| | [Documentation] | Uses Honeycomb API to verify interface assignment to\
| | ... | bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface1, interface2 - names of interfaces to check bridge domain\
| | ... | assignment on. Type: string
| | ... | - bd_name - name of the bridge domain. Type: string
| | ... | - settings - bridge domain specific interface settings.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb should not show interfaces assigned to bridge domain \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| GigabitEthernet0/9/0 \
| | ... | \| bd-04 \| ${{split_horizon_group:2, bvi:False}} \|
| | [Arguments] | ${node} | ${interface1} | ${interface2} | ${bd_name}
| | ... | ${settings}
| | Run keyword and expect error | *ValueError*
| | ... | Honeycomb should show interfaces assigned to bridge domain
| | ... | ${node} | ${interface1} | ${interface2} | ${bd_name} | ${settings}

| VAT should show interfaces assigned to bridge domain
| | [Documentation] | Uses VAT to verify interface assignment to\
| | ... | bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - index - Index of bridge domains on VPP node. Starts from 0,\
| | ... | new BDs reuse numbers after a bridge domain is removed. Type: int
| | ... | - interface1, interface2 - names of interfaces to check bridge domain\
| | ... | assignment on. Type: string
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
| | ${if1_link}= | Get interface by name | ${node} | ${interface1}
| | ${if2_link}= | Get interface by name | ${node} | ${interface2}
| | ${if_indices}= | Create list
| | ... | ${node['interfaces']['${if1_link}']['vpp_sw_index']}
| | ... | ${node['interfaces']['${if2_link}']['vpp_sw_index']}
| | ${bd_data}= | VPP get bridge domain data | ${node}
| | ${bd_interfaces}= | Set Variable | ${bd_data[${index}]['sw_if']}
| | @{bd_interfaces}= | Create List | ${bd_interfaces[0]} | ${bd_interfaces[1]}
| | :FOR | ${interface} | IN | @{bd_interfaces}
| | | Should contain | ${if_indices} | ${interface['sw_if_index']}
| | | Should be equal | ${interface['shg']} | ${settings['split_horizon_group']}

| VAT should not show interfaces assigned to bridge domain
| | [Documentation] | Uses VAT to verify interface assignment to\
| | ... | bridge domain, and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - index - index of bridge domains on VPP node. Starts from 0,\
| | ... | new BDs reuse numbers after a bridge domain is removed. Type: integer
| | ... | - interface1, interface2 - names of interfaces to check bridge domain\
| | ... | assignment on. Type: string
| | ... | - settings - bridge domain specific interface settings.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VAT should not show interfaces assigned to bridge domain \
| | ... | \| ${nodes['DUT1']} \| ${4} \| GigabitEthernet0/8/0 \
| | ... | \| GigabitEthernet0/9/0 \| ${{split_horizon_group:2, bvi:False}} \|
| | [Arguments] | ${node} | ${index} | ${interface1} | ${interface2}
| | ... | ${settings}
| | Run keyword and expect error | *No JSON object could be decoded*
| | ... | VAT should show interfaces assigned to bridge domain
| | ... | ${node} | ${index} | ${interface1} | ${interface2} | ${settings}

| Honeycomb removes all bridge domains
| | [Documentation] | Uses Honeycomb API to remove all bridge domains from the \
| | ... | VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
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
| | ... | - node - Information about a DUT node. Type: dictionary
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
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VAT should show no bridge domains \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Run Keyword And Expect Error | ValueError: No JSON object could be decoded
| | ... | VPP get bridge domain data | ${node}

| Honeycomb adds interface to bridge domain
| | [Documentation] | Uses Honeycomb API to assign interface to a bridge\
| | ... | domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Name of interface to assign to bridge domain.\
| | ... | Type: string
| | ... | - bd_name - Name of the bridge domain. Type: string
| | ... | - settings - Bridge domain specific interface settings.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds interfaces to bridge domain \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| bd-04 \
| | ... | \| ${{split_horizon_group:2, bvi:False}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${bd_name} | ${settings}
| | ...
| | interfaceAPI.Add bridge domain to interface
| | ... | ${node} | ${interface} | ${settings['bridge-domain']}
| | ... | ${settings['split-horizon-group']}
| | ... | ${settings['bridged-virtual-interface']}

| Bridge domain configuration in interface operational data should be empty
| | [Documentation] | Get interface operational data and retrieve bridge
| | ... | domain configuration from it. It should be empty.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Name of interface where the bridge domain parameters \
| | ... | will be checked.Type: string
| | ...
| | ... | *Example:*
| | ... | \| Bridge domain configuration in interface operational data should \
| | ... | be empty \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ...
| | ${if_data}= | interfaceAPI.Get BD Oper Data From Interface
| | ... | ${node} | ${interface}
| | Should be empty | ${if_data}

| Bridge domain configuration in interface operational data should be
| | [Documentation] | Get interface operational data and retrieve bridge
| | ... | domain configuration from it. Compare the data to the expected one.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Name of interface where the bridge domain parameters \
| | ... | will be checked. Type: string
| | ... | - bd_settings - The referential bridge domain data. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Bridge domain configuration in interface operational data should \
| | ... | be \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${if_bd_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${bd_settings}
| | ...
| | ${if_data}= | interfaceAPI.Get BD Oper Data From Interface
| | ... | ${node} | ${interface}
| | interfaceAPI.Compare Data Structures | ${if_data} | ${bd_settings}

| VAT removes bridge domain
| | [Documentation] Remove the specified bridge domain using VAT.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_id - Bridge domain ID. Type: integer
| | ...
| | ... | *Example:*
| | ... | \| VAT removes bridge domain \
| | ... | \| ${nodes['DUT1']} \| 1 \|
| | ...
| | [Arguments] | ${node} | ${bd_id}
| | ...
| | Delete Bridge Domain VAT | ${node} | ${bd_id}
