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
| ...     | WITH NAME | interfaceCLI
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| ...     | WITH NAME | InterfaceAPI
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Documentation | Keywords used to manipulate sub-interfaces.

*** Variables ***
# Translation table used to convert values received from Honeycomb to values
# received from VAT.
| &{rewrite_operations}=
| ... | disabled=0
| ... | push-1=1
| ... | push-2=2
| ... | pop-1=3
| ... | pop-2=4
| ... | translate-1-to-1=5
| ... | translate-1-to-2=6
| ... | translate-2-to-1=7
| ... | translate-2-to-2=8

*** Keywords ***
| Honeycomb creates sub-interface
| | [Documentation] | Create a sub-interface using Honeycomb API.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - identifier - ID of sub-interface to be created. Type: integer
| | ... | - sub_interface_base_settings - Configuration data for sub-interface.\
| | ... | Type: dictionary
| | ... | - sub_interface_settings - Configuration data specific for a\
| | ... | sub-interface. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb creates sub-interface\
| | ... | \| ${nodes['DUT1']} \| sub_test \| 10 \| ${sub_interface_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${identifier}
| | ... | ${sub_interface_base_settings} | ${sub_interface_settings}
| | interfaceAPI.Create sub interface | ${node} | ${interface}
| | ... | &{sub_interface_base_settings} | &{sub_interface_settings}

| Honeycomb fails to remove sub-interface
| | [Documentation] | Honeycomb tries to remove sub-interface using Honeycomb\
| | ... | API. This operation must fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of a sub-interface on the specified node.
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to remove sub-interface\
| | ... | \| ${nodes['DUT1']} \| sub_test \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Run keyword and expect error | *HoneycombError: Not possible to remove* 500.
| | ... | interfaceAPI.Delete interface | ${node} | ${interface}

| Sub-interface configuration from Honeycomb should be
| | [Documentation] | Retrieves sub-interface configuration through Honeycomb\
| | ... | and compares it with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - base_settings - Configuration data for sub-interface.\
| | ... | Type: dictionary
| | ... | - sub_settings - Configuration data specific for a sub-interface.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface configuration from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${sub_interface_base_settings}\
| | ... | \| ${sub_interface_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${base_settings} | ${sub_settings}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${api_sub}= | Set Variable | ${api_data['v3po:sub-interface']}
| | :FOR | ${key} | IN | @{base_settings.keys()}
| | | Should be equal | ${api_data['${key}']} | ${base_settings['${key}']}
| | Should be equal as strings
| | ... | ${api_sub['super-interface']} | ${sub_settings['super-interface']}
| | Should be equal as strings
| | ... | ${api_sub['identifier']} | ${sub_settings['identifier']}
| | Should be equal as strings
| | ... | ${api_sub['vlan-type']} | ${sub_settings['vlan-type']}
| | Should be equal as strings
| | ... | ${api_sub['number-of-tags']} | ${sub_settings['number-of-tags']}
| | Run keyword if | ${sub_settings['match-any-outer-id']} == ${TRUE}
| | ... | Should be equal | ${api_sub['match-any-outer-id'][0]} | ${None}
| | Run keyword if | ${sub_settings['match-any-inner-id']} == ${TRUE}
| | ... | Should be equal | ${api_sub['match-any-inner-id'][0]} | ${None}
| | Run keyword if | ${sub_settings['exact-match']} == ${TRUE}
| | ... | Should be equal | ${api_sub['exact-match'][0]} | ${None}
| | Run keyword if | ${sub_settings['default-subif']} == ${TRUE}
| | ... | Should be equal | ${api_sub['default-subif'][0]} | ${None}

| Sub-interface configuration from VAT should be
| | [Documentation] | Retrieves sub-interface configuration through VAT and\
| | ... | compares it with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - sub_settings - Configuration data specific for a sub-interface.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface configuration from VAT should be\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${sub_interface_base_settings}\
| | ... | \| ${sub_interface_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${sub_settings}
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | Should be equal as strings | ${vat_data['sub_id']}
| | ... | ${sub_settings['identifier']}
| | Should be equal as strings | ${vat_data['sub_number_of_tags']}
| | ... | ${sub_settings['number-of-tags']}
| | Run keyword if | ${sub_settings['match-any-outer-id']} == ${TRUE}
| | ... | Should be equal as integers | ${vat_data['sub_outer_vlan_id_any']}
| | ... | ${sub_settings['match-any-outer-id']}
| | Run keyword if | ${sub_settings['match-any-inner-id']} == ${TRUE}
| | ... | Should be equal as integers | ${vat_data['sub_inner_vlan_id_any']}
| | ... | ${sub_settings['match-any-inner-id']}
| | Run keyword if | ${sub_settings['exact-match']} == ${TRUE}
| | ... | Should be equal as integers | ${vat_data['sub_exact_match']}
| | ... | ${sub_settings['exact-match']}
| | Run keyword if | ${sub_settings['default-subif']} == ${TRUE}
| | ... | Should be equal as integers | ${vat_data['sub_default']}
| | ... | ${sub_settings['default-subif']}

| Sub-interface configuration from Honeycomb should be empty
| | [Documentation] | Attempts to retrieve sub-interface configuration through\
| | ... | Honeycomb and expects to get empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of a sub-interface on the specified node. Type:\
| | ... | string
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface configuration from Honeycomb should be empty\
| | ... | \| ${nodes['DUT1']} \| sub_test \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be empty | ${api_data}

| Sub-interface configuration from VAT should be empty
| | [Documentation] | Attempts to retrieve sub-interface configuration through\
| | ... | VAT and expects to get empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of a sub-interface on the specified node. Type:\
| | ... | string
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface configuration from VAT should be empty\
| | ... | \| ${nodes['DUT1']} \| sub_test \|
| | ...
| | [Arguments] | ${node} | ${interface} |
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | Should be empty | ${vat_data}

| Honeycomb adds sub-interface to bridge domain
| | [Documentation] | Honeycomb adds the given sub-interface to bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an sub-interface on the specified node. Type:\
| | ... | string
| | ... | - bd_name - The name of bridge domain where the sub-interface will be\
| | ... | added. Type: string
| | ... | - sub_bd_setings - Parameters to be set while adding the\
| | ... | sub-interface to the bridge domain. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb adds sub-interface to bridge domain\
| | ... | \| ${nodes['DUT1']} \| sub_test \| test_bd \| ${sub_bd_setings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${bd_name} | ${sub_bd_setings}
| | interfaceAPI.Add bridge domain to interface
| | ... | ${node} | ${interface} | ${bd_name}
| | ... | split_horizon_group=${sub_bd_setings['split-horizon-group']}
| | ... | bvi=${sub_bd_setings['bridged-virtual-interface']}

| Sub-interface bridge domain configuration from Honeycomb should be
| | [Documentation] | Uses Honeycomb API to verify sub-interface assignment to\
| | ... | a bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of a sub-interface on the specified node. Type:\
| | ... | string
| | ... | - setings - Parameters to be checked. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface bridge domain configuration from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${sub_bd_setings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | ${if_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be equal | ${if_data['v3po:l2']['bridge-domain']}
| | ... | ${settings['bridge-domain']}
| | Should be equal | disabled
| | ... | ${if_data['v3po:l2']['vlan-tag-rewrite']['rewrite-operation']}

| Sub-interface bridge domain configuration from VAT should be
| | [Documentation] | Uses VAT to verify sub-interface assignment to a bridge\
| | ... | domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of a sub-interface on the specified node. Type:\
| | ... | string
| | ... | - setings - Parameters to be checked. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface bridge domain configuration from VAT should be\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${sub_bd_setings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | ${bd_data}= | VPP get bridge domain data | ${node}
| | ${bd_intf}= | Set Variable | ${bd_data[0]}
| | ${sw_if_data}= | Set Variable | ${bd_intf['sw_if'][0]}
| | Should be equal as integers | ${bd_intf['flood']} | ${bd_settings['flood']}
| | Should be equal as integers | ${bd_intf['forward']}
| | ... | ${bd_settings['forward']}
| | Should be equal as integers | ${bd_intf['learn']} | ${bd_settings['learn']}
| | Should be equal as strings | ${sw_if_data['shg']}
| | ... | ${settings['split-horizon-group']}

| Sub-interface configuration with bd and rw from Honeycomb should be
| | [Documentation] | Retrieves sub-interface configuration through Honeycomb\
| | ... | and compares it with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - base_settings - Configuration data for sub-interface.\
| | ... | Type: dictionary
| | ... | - sub_settings - Configuration data specific for a sub-interface.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface configuration with bd and rw from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${sub_interface_base_settings}\
| | ... | \| ${sub_interface_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${base_settings} | ${sub_settings}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${api_sub}= | Set Variable | ${api_data['v3po:sub-interface']}
| | Should be equal as strings | ${api_data['name']} | ${base_settings['name']}
| | Should be equal as strings | ${api_data['type']} | ${base_settings['type']}
| | Should be equal as strings
| | ... | ${api_sub['super-interface']} | ${sub_settings['super-interface']}
| | Should be equal as strings
| | ... | ${api_sub['identifier']} | ${sub_settings['identifier']}
| | Should be equal as strings
| | ... | ${api_sub['vlan-type']} | ${sub_settings['vlan-type']}
| | Should be equal as strings
| | ... | ${api_sub['number-of-tags']} | ${sub_settings['number-of-tags']}
| | Run keyword if | ${sub_settings['match-any-outer-id']} == ${TRUE}
| | ... | Should be equal | ${api_sub['match-any-outer-id'][0]} | ${None}
| | Run keyword if | ${sub_settings['match-any-inner-id']} == ${TRUE}
| | ... | Should be equal | ${api_sub['match-any-inner-id'][0]} | ${None}
| | Run keyword if | ${sub_settings['exact-match']} == ${TRUE}
| | ... | Should be equal | ${api_sub['exact-match'][0]} | ${None}
| | Run keyword if | ${sub_settings['default-subif']} == ${TRUE}
| | ... | Should be equal | ${api_sub['default-subif'][0]} | ${None}
| | Should be equal | ${api_data['v3po:l2']['bridge-domain']}
| | ... | ${base_settings['v3po:l2']['bridge-domain']}
| | ${rw_data}= | Set Variable | ${api_data['v3po:l2']['vlan-tag-rewrite']}
| | ${rw_params}= | Set Variable
| | ... | ${base_settings['v3po:l2']['vlan-tag-rewrite']}
| | Should be equal as strings | ${rw_data['rewrite-operation']}
| | ... | ${rw_params['rewrite-operation']}
| | Should be equal as strings | ${rw_data['first-pushed']}
| | ... | ${rw_params['first-pushed']}

| Rewrite tag configuration from VAT should be
| | [Documentation] | Retrieves sub-interface configuration through VAT and\
| | ... | compares values of rewrite tag parameters with settings supplied in\
| | ... | argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - rw_settings - Parameters to be set while setting the rewrite tag.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Rewrite tag configuration from VAT should be\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${rw_params} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${rw_settings}
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | Should be equal as strings | ${vat_data['vtr_op']}
| | ... | ${rewrite_operations['${rw_settings['rewrite-operation']}']}
| | Run keyword if | '${rw_settings['rewrite-operation']}' == 'push-1'
| | ... | Should be equal as strings
| | ... | ${vat_data['vtr_tag1']} | ${rw_settings['tag1']}

| Honeycomb sets rewrite tag
| | [Documentation] | Set the rewrite tag for sub-interface using Honeycomb API.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - sub_interface - name of an sub-interface on the specified node.\
| | ... | Type: string
| | ... | - rw_params - Parameters to be set while setting the rewrite tag.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb sets rewrite tag\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${rw_params} \|
| | ...
| | [Arguments] | ${node} | ${sub_interface} | ${rw_params}
| | interfaceAPI.Add vlan tag rewrite to sub interface
| | ... | ${node} | ${sub_interface} | &{rw_params}

| Honeycomb removes rewrite tag
| | [Documentation] | Remove the rewrite tag from sub-interface using Honeycomb\
| | ... | API.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - sub_interface - name of an sub-interface on the specified node.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb removes rewrite tag \| ${nodes['DUT1']} \| sub_test \|
| | ...
| | [Arguments] | ${node} | ${sub_interface}
| | interfaceAPI.Remove vlan tag rewrite from sub interface
| | ... | ${node} | ${sub_interface}

| Rewrite tag from Honeycomb should be
| | [Documentation] | Uses Honeycomb API to verify if the rewrite tag is set\
| | ... | with correct parameters.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - sub_interface - name of an sub-interface on the specified node.\
| | ... | Type: string
| | ... | - rw_params - Parameters to be checked. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Rewrite tag from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${rw_params} \|
| | ...
| | [Arguments] | ${node} | ${sub_interface} | ${rw_params}
| | ${if_data}= | interfaceAPI.Get interface oper data | ${node}
| | ... | ${sub_interface}
| | ${rw_data}= | Set Variable | ${if_data['v3po:l2']["vlan-tag-rewrite"]}
| | Should be equal as strings | ${rw_data['rewrite-operation']}
| | ... | ${rw_params['rewrite-operation']}
| | Should be equal as strings | ${rw_data['first-pushed']}
| | ... | ${rw_params['first-pushed']}

| Honeycomb fails to set wrong rewrite tag
| | [Documentation] | Honeycomb tries to set wrong rewrite tag and expects\
| | ... | error.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - sub_interface - name of an sub-interface on the specified node.\
| | ... | Type: string
| | ... | - rw_params - Parameters to be set while setting the rewrite tag.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to set wrong rewrite tag\
| | ... | \| ${nodes['DUT1']} \| sub_test \| ${rw_params} \|
| | ...
| | [Arguments] | ${node} | ${sub_interface} | ${rw_params}
| | Run keyword and expect error | *HoneycombError: * was not successful. * 400.
| | ... | interfaceAPI.Add vlan tag rewrite to sub interface | ${node}
| | ... | ${sub_interface} | &{rw_params}

| Honeycomb fails to set sub-interface up
| | [Documentation] | Honeycomb tries to set sub-interface up and expects error.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - sub_interface - name of an sub-interface on the specified node.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to set sub-interface up\
| | ... | \| ${node} \| sub_test \|
| | ...
| | [Arguments] | ${node} | ${sub_interface}
| | Run keyword and expect error | *HoneycombError: * was not successful. * 500.
| | ... | interfaceAPI.Set interface up | ${node} | ${sub_interface}
