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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| ...     | WITH NAME | InterfaceAPI
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Documentation | Keywords used to manipulate sub-interfaces.

*** Keywords ***
| Honeycomb creates sub-interface
| | [Documentation] | Create a sub-interface using Honeycomb API.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super-interface where a sub-interface will be\
| | ... | created. Type: string
| | ... | - match - Match type. Type: string
| | ... | - tags - List of tags to be set while creating the sub-interface.\
| | ... | Type: list
| | ... | - sub_interface_settings - Sub-inteface parameters to be set while\
| | ... | creating the sub-interface. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb creates sub-interface\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0\
| | ... | \| vlan-tagged-exact-match \| ${sub_if_1_tags}\
| | ... | \| ${sub_if_1_settings} \|
| | ...
| | [Arguments] | ${node} | ${super_interface}
| | ... | ${match} | ${tags} | ${sub_interface_settings}
| | ...
| | interfaceAPI.Create sub interface | ${node} | ${super_interface}
| | ... | ${match} | ${tags} | &{sub_interface_settings}

| Sub-interface configuration from Honeycomb should be
| | [Documentation] | Retrieves sub-interface configuration through Honeycomb\
| | ... | and compares it with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - sub_if_settings - Operational data for sub-interface to be checked.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface configuration from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1\
| | ... | \| ${sub_if_1_params} \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ... | ${sub_if_settings}
| | ...
| | ${api_data}= | interfaceAPI.Get sub interface oper data
| | ... | ${node} | ${super_interface} | ${identifier}
| | interfaceAPI.Compare Data Structures | ${api_data} | ${sub_if_settings}

| Sub-interface configuration from Honeycomb should be empty
| | [Documentation] | Retrieves sub-interface configuration through Honeycomb \
| | ... | and expects no data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface configuration from Honeycomb should be empty\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ...
| | Run keyword and expect error | *KeyError: 'sub-interface'*
| | ... | interfaceAPI.Get sub interface oper data
| | ... | ${node} | ${super_interface} | ${identifier}

| Sub-interface state from Honeycomb should be
| | [Documentation] | Retrieves sub-interface configuration through Honeycomb \
| | ... | and checks the administrative and operational state.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - admin_state - Required administrative state - up or down. \
| | ... | Type: string
| | ... | - oper_state - Required operational state - up or down. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface state from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \| up \| up \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ... | ${admin_state} | ${oper_state}
| | ...
| | ${api_data}= | interfaceAPI.Get sub interface oper data
| | ... | ${node} | ${super_interface} | ${identifier}
| | Should be equal | ${api_data['admin-status']} | ${admin_state}
| | Should be equal | ${api_data['oper-status']} | ${oper_state}

| Sub-interface configuration from VAT should be
| | [Documentation] | Retrieves sub-interface configuration through VAT and\
| | ... | compares it with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - sub_interface - Name of an sub-interface on the specified node.\
| | ... | Type: string
| | ... | - sub_interface_settings - Operational data specific for a\
| | ... | sub-interface to be checked. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface configuration from VAT should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0.1 \| ${sub_if_1_params} \|
| | ...
| | [Arguments] | ${node} | ${sub_interface} | ${sub_interface_settings}
| | ...
| | ${vat_data}= | InterfaceCLI.VPP get interface data
| | ... | ${node} | ${sub_interface}
| | Should be equal as strings | ${vat_data['sub_id']}
| | ... | ${sub_interface_settings['identifier']}
| | Should be equal as strings
| | ... | ${vat_data['interface_name']} | ${sub_interface}
| | Run keyword if | ${vat_data['link_up_down']} == 0
| | ... | Should be equal as strings
| | ... | ${sub_interface_settings['oper-status']} | down
| | Run keyword if | ${vat_data['link_up_down']} == 1
| | ... | Should be equal as strings
| | ... | ${sub_interface_settings['oper-status']} | up

| Sub-interface state from VAT should be
| | [Documentation] | Retrieves sub-interface configuration through VAT and \
| | ... | checks the administrative and operational state.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - sub_interface - Name of an sub-interface on the specified node. \
| | ... | Type: string
| | ... | - admin_state - Required administrative state - up or down. \
| | ... | Type: string
| | ... | - oper_state - Required operational state - up or down. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface state from VAT should be \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0.1 \| up \| up \|
| | ...
| | [Arguments] | ${node} | ${sub_interface} | ${admin_state} | ${oper_state}
| | ...
| | ${vat_data}= | InterfaceCLI.VPP get interface data
| | ... | ${node} | ${sub_interface}
| | Run keyword if | '${admin_state}' == 'down'
| | ... | Should be equal as strings | ${vat_data['admin_up_down']} | 0
| | Run keyword if | '${admin_state}' == 'up'
| | ... | Should be equal as strings | ${vat_data['admin_up_down']} | 1
| | Run keyword if | '${oper_state}' == 'down'
| | ... | Should be equal as strings | ${vat_data['link_up_down']} | 0
| | Run keyword if | '${oper_state}' == 'up'
| | ... | Should be equal as strings | ${vat_data['link_up_down']} | 1

| Sub-interface indices from Honeycomb and VAT should correspond
| | [Documentation] | Uses VAT and Honeycomb to get operational data about the\
| | ... | given sub-interface and compares the interface indexes. The
| | ... | sub-interface index from Honeycomb should be greater than index from
| | ... | VAT by one.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Sub-interface indices from Honeycomb and VAT should correspond \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ...
| | ${api_data}= | interfaceAPI.Get sub interface oper data
| | ... | ${node} | ${super_interface} | ${identifier}
| | ${vat_data}= | InterfaceCLI.VPP get interface data
| | ... | ${node} | ${super_interface}.${identifier}
| | ${sw_if_index}= | EVALUATE | ${vat_data['sw_if_index']} + 1
| | Should be equal as strings
| | ... | ${api_data['if-index']} | ${sw_if_index}

| Honeycomb sets the sub-interface up
| | [Documentation] | Honeycomb sets the sub-interface up.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | Honeycomb sets the sub-interface up\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ...
| | interfaceAPI.Set sub interface state
| | ... | ${node} | ${super_interface} | ${identifier} | up

| Honeycomb sets the sub-interface down
| | [Documentation] | Honeycomb sets the sub-interface down.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | Honeycomb sets the sub-interface down\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ...
| | interfaceAPI.Set sub interface state
| | ... | ${node} | ${super_interface} | ${identifier} | down

| Honeycomb fails to set sub-interface up
| | [Documentation] | Honeycomb tries to set sub-interface up and expects error.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to set sub-interface up\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ...
| | Run keyword and expect error | *HoneycombError: * was not successful. * 500.
| | ... | interfaceAPI.Set sub interface state
| | ... | ${node} | ${super_interface} | ${identifier} | up

| Honeycomb adds sub-interface to bridge domain
| | [Documentation] | Honeycomb adds the given sub-interface to bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - sub_bd_setings - Bridge domain parameters to be set while adding\
| | ... | the sub-interface to the bridge domain. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb adds sub-interface to bridge domain\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \| ${bd_settings} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier} | ${sub_bd_setings}
| | ...
| | interfaceAPI.Add bridge domain to sub interface
| | ... | ${node} | ${super_if} | ${identifier} | ${sub_bd_setings}

| Sub-interface bridge domain configuration from Honeycomb should be
| | [Documentation] | Uses Honeycomb API to verify sub-interface assignment to\
| | ... | a bridge domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - settings - Bridge domain parameters to be checked. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface bridge domain configuration from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \| ${bd_settings} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier} | ${settings}
| | ...
| | ${if_data}= | interfaceAPI.Get BD data from sub interface
| | ... | ${node} | ${super_if} | ${identifier}
| | Should be equal | ${if_data['bridge-domain']}
| | ... | ${settings['bridge-domain']}

| Sub-interface bridge domain configuration from VAT should be
| | [Documentation] | Uses VAT to verify sub-interface assignment to a bridge\
| | ... | domain.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Name of a sub-interface on the specified node. Type:\
| | ... | string
| | ... | - setings - Parameters to be checked. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Sub-interface bridge domain configuration from VAT should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0.1 \| ${sub_bd_setings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | ...
| | ${bd_data}= | VPP get bridge domain data | ${node}
| | ${bd_intf}= | Set Variable | ${bd_data[0]}
| | ${sw_if_data}= | Set Variable | ${bd_intf['sw_if'][0]}
| | Should be equal as integers | ${bd_intf['flood']} | ${bd_settings['flood']}
| | Should be equal as integers | ${bd_intf['forward']}
| | ... | ${bd_settings['forward']}
| | Should be equal as integers | ${bd_intf['learn']} | ${bd_settings['learn']}
| | Should be equal as strings | ${sw_if_data['shg']}
| | ... | ${settings['split-horizon-group']}

| Honeycomb fails to remove all sub-interfaces
| | [Documentation] | Honeycomb tries to remove all sub-interfaces using\
| | ... | Honeycomb API. This operation must fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to remove all sub-interfaces\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${super_if}
| | ...
| | Run keyword and expect error | *HoneycombError:*not successful. * code: 500.
| | ... | interfaceAPI.Remove all sub interfaces
| | ... | ${node} | ${super_if}

| Honeycomb configures tag rewrite
| | [Documentation] | Honeycomb configures tag-rewrite
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - settings - tag-rewrite parameters. Type: dictionary.
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb configures tag rewrite\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1\
| | ... | \| ${tag_rewrite_push} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier} | ${settings}
| | ...
| | interfaceAPI.Configure tag rewrite
| | ... | ${node} | ${super_if} | ${identifier} | ${settings}

| Rewrite tag from Honeycomb should be empty
| | [Documentation] | Checks if the tag-rewrite is empty or does not exist.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | \| Rewrite tag from Honeycomb should be empty\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier}
| | ...
| | Run keyword and expect error | *Hon*Error*oper*does not contain*tag-rewrite*
| | ... | interfaceAPI.Get tag rewrite oper data
| | ... | ${node} | ${super_if} | ${identifier}

| Rewrite tag from Honeycomb should be
| | [Documentation] | Checks if the operational data retrieved from Honeycomb\
| | ... | are as expected.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - settings - tag-rewrite operational parameters to be checked.\
| | ... | Type: dictionary.
| | ...
| | ... | *Example:*
| | ... | \| Rewrite tag from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1\
| | ... | \| ${tag_rewrite_push_oper} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier} | ${settings}
| | ${api_data}= | interfaceAPI.Get tag rewrite oper data
| | ... | ${node} | ${super_if} | ${identifier}
| | interfaceAPI.Compare Data Structures | ${api_data} | ${settings}

| Rewrite tag from VAT should be
| | [Documentation] | Retrieves sub-interface configuration through VAT and\
| | ... | compares values of rewrite tag parameters with settings supplied in\
| | ... | argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of a sub-interface on the specified node.\
| | ... | Type: string
| | ... | - rw_settings - Parameters to be set while setting the rewrite tag.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Rewrite tag from VAT should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0.1 \| ${rw_params} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${rw_settings}
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | interfaceAPI.Compare Data Structures | ${vat_data} | ${rw_settings}

| Honeycomb fails to set wrong rewrite tag
| | [Documentation] | Honeycomb tries to set wrong rewrite tag and expects\
| | ... | an error.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - settings - tag-rewrite parameters. Type: dictionary.
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails to set wrong rewrite tag\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1\
| | ... | \| ${tag_rewrite_push_WRONG} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier} | ${settings}
| | Run keyword and expect error | *HoneycombError: * was not successful. *00.
| | ... | interfaceAPI.Configure tag rewrite
| | ... | ${node} | ${super_if} | ${identifier} | ${settings}

| VAT disables tag-rewrite
| | [Documentation] | The keyword disables the tag-rewrite using VAT.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - sub_interface - Name of an sub-interface on the specified node.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ... | \| VAT disables tag-rewrite\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0.1 \|
| | ...
| | [Arguments] | ${node} | ${sub_interface}
| | ...
| | ${sw_if_index}= | interfaceCLI.Get sw if index | ${node} | ${sub_interface}
| | L2 tag rewrite | ${node} | ${sw_if_index} | disable

| Honeycomb sets sub-interface ipv4 address
| | [Documentation] | Uses Honeycomb API to configure an ipv4 address on the\
| | ... | spcified sub-interface. Replaces any existing ipv4 addresses.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - address - IPv4 address to set. Type: string
| | ... | - prefix - IPv4 network prefix length to set. Type: integer
| | ...
| | ... | *Example:*
| | ... | \| | Honeycomb sets sub-interface ipv4 address\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1} \
| | ... | \| 192.168.0.2 \| ${24} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier} | ${address} | ${prefix}
| | Add ipv4 address to sub_interface
| | ... | ${node} | ${super_if} | ${identifier} | ${address} | ${prefix}

| Sub-interface ipv4 address from Honeycomb should be
| | [Documentation] | Uses Honeycomb API to verify ipv4 address configuration\
| | ... | on the specified sub-interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ... | - address - IPv4 address to expect. Type: string
| | ... | - prefix - IPv4 network prefix length to expect. Type: integer
| | ...
| | ... | *Example:*
| | ... | \| sub-interface ipv4 address from Honeycomb should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1} \
| | ... | \| 192.168.0.2 \| ${24} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier} | ${address} | ${prefix}
| | ${if_data}= | interfaceAPI.Get sub interface oper data
| | ... | ${node} | ${super_if} | ${identifier}
| | Should be equal
| | ... | ${if_data['ipv4']['address'][0]['ip']} | ${address}
| | Should be equal
| | ... | ${if_data['ipv4']['address'][0]['prefix-length']} | ${prefix}

| Sub-interface ipv4 address from VAT should be
| | [Documentation] | Uses VAT to verify ipv4 address configuration\
| | ... | on the specified sub-interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - sub_interface - Name of an sub-interface on the specified node.\
| | ... | Type: string
| | ... | - address - IPv4 address to expect. Type: string
| | ... | - prefix - IPv4 network prefix length to expect. Type: integer
| | ...
| | ... | *Example:*
| | ... | \| sub-interface ipv4 address from VAT should be\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0.1 \|
| | ...
| | [Arguments] | ${node} | ${sub_interface} | ${address} | ${prefix}
| | ${data}= | VPP get interface ip addresses
| | ... | ${node} | ${sub_interface} | ipv4
| | Should be equal | ${data[0]['ip']} | ${address}
#TODO: update based on resolution of bug https://jira.fd.io/browse/VPP-132
| | Should be equal | ${data[0]['prefix_length']} | ${prefix}

| Honeycomb removes all sub-interface ipv4 addresses
| | [Documentation] | Uses Honeycomb API to remove all configured ipv4\
| | ... | addresses from the sub-interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb removes all sub-interface ipv4 addresses\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier}
| | Remove all ipv4 addresses from sub_interface
| | ... | ${node} | ${super_if} | ${identifier}

| Sub-interface ipv4 address from Honeycomb should be empty
| | [Documentation] | Uses Honeycomb API to verify that ipv4 address\
| | ... | configuration on the specified sub-interface is empty.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | \| sub-interface ipv4 address from Honeycomb should be empty\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1} \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${identifier}
| | ${if_data}= | interfaceAPI.Get sub interface oper data
| | ... | ${node} | ${super_if} | ${identifier}
| | Run keyword and expect error | *KeyError: 'address'*
| | ... | Set Variable | ${if_data['ipv4']['address'][0]['ip']}

| Sub-interface ipv4 address from VAT should be empty
| | [Documentation] | Uses VAT to verify that ipv4 address\
| | ... | configuration on the specified sub-interface is empty.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - sub_interface - Name of an sub-interface on the specified node.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ... | \| sub-interface ipv4 address from VAT should be empty\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0.1 \|
| | ...
| | [Arguments] | ${node} | ${sub_interface}
| | Run keyword and expect error | *No JSON object could be decoded*
| | ... | VPP get interface ip addresses | ${node} | ${sub_interface} | ipv4
