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
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| Documentation | Keywords used to manipulate vhost-user unterfaces.

*** Keywords ***
| Honeycomb creates vhost-user interface
| | [Documentation] | Create a vhost-user interface using Honeycomb API.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for vhost-user interface.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb creates vhost-user interface\
| | ... | \| ${nodes['DUT1']} \| vhost_test \| ${vhost_user_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | Create vhost user interface | ${node} | ${interface}
| | ... | &{settings}

| Honeycomb removes vhost-user interface
| | [Documentation] | Remove a vhost-user interface using Honeycomb API.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb removes vhost-user interface\
| | ... | \| ${nodes['DUT1']} \| vhost_test \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Delete interface | ${node} | ${interface}

| Honeycomb configures vhost-user interface
| | [Documentation] | Configure a vhost-user interface using Honeycomb API.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for vhost-user interface.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb configures vhost-user interface\
| | ... | \| ${nodes['DUT1']} \| vhost_test \| ${new_vhost_user_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | Configure interface vhost user | ${node} | ${interface}
| | ... | &{settings}

| Vhost-user Operational Data From Honeycomb Should Be
| | [Documentation] | Retrieves interface vhost-user configuration through\
| | ... | Honeycomb and compares it with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for vhost-user interface.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Vhost-user Operational Data From Honeycomb Should Be\
| | ... | \| ${nodes['DUT1']} \| vhost_test \| ${vhost_user_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | ${api_data}= | Get interface oper data | ${node} | ${interface}
| | ${api_vhost}= | Set Variable | ${api_data['v3po:vhost-user']}
| | :FOR | ${key} | IN | @{settings.keys()}
| | | Should be equal | ${api_vhost['${key}']} | ${settings['${key}']}

| Vhost-user Operational Data From VAT Should Be
| | [Documentation] | Retrieves interface vhost-user configuration through VAT\
| | ... | and compares it with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - settings - Configuration data for vhost-user interface.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Vhost-user Operational Data From VAT Should Be\
| | ... | \| ${nodes['DUT1']} \| vhost_test \|
| | ...
| | ... | *Note:*
| | ... | Due to the difficulty of identifying newly created interfaces by name\
| | ... | or by sw_index, this keyword assumes there is only one vhost-user\
| | ... | interface present on the specified node.
| | ...
| | [Arguments] | ${node} | ${settings}
| | &{translate}= | Create dictionary | server=1 | client=0
| | ${vat_data}= | vhost user Dump | ${node}
| | ${vat_data}= | Set Variable | ${vat_data[0]}
| | Should be equal | ${vat_data['sock_filename']} | ${settings['socket']}
| | should be equal as strings | ${vat_data['is_server']}
| | ... | ${translate['${settings['role']}']}

| Vhost-user Operational Data From Honeycomb Should Be empty
| | [Documentation] | Attempts to retrieve interface vhost-user configuration\
| | ... | through Honeycomb and expects to recieve an empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Vhost-user Operational Data From Honeycomb Should Be empty\
| | ... | \| ${nodes['DUT1']} \| vhost_test \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | Get interface oper data | ${node} | ${interface}
| | Run keyword and expect error | *KeyError: 'v3po:vhost-user'
| | ... | Should be empty | ${api_data['v3po:vhost-user']}

| Vhost-user Operational Data From VAT Should Be empty
| | [Documentation] | Attempts to retrieve interface vhost-user configuration\
| | ... | through VAT and expects a "no data" error.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Vhost-user Operational Data From VAT Should Be empty\
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Run Keyword And Expect Error | ValueError: No JSON object could be decoded
| | ... | vhost user Dump | ${node}

| Honeycomb fails setting vhost-user on different interface type
| | [Documentation] | Attempts to set vhost-user settings on an ethernet\
| | ... | type interface and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for vhost-user. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails setting vhost-user on different interface type\
| | ... | \| ${nodes['DUT1']} \| ${interface} \| ${vhost_user_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | Run Keyword And Expect Error | HoneycombError: * Status code: 500.
| | ... | Configure interface vhost user | ${node} | ${interface}
| | ... | &{settings}

| Honeycomb fails setting invalid vhost-user configuration
| | [Documentation] | Attempts to create a vhost-user interface with invalid\
| | ... | configuration and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings_list - Bad configuration data for vhost-user. Type: list
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb fails setting invalid vhost-user configuration\
| | ... | \| ${nodes['DUT1']} \| vhost_test \| ${vhost_user_settings} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | Run Keyword And Expect Error | HoneycombError: * Status code: 400.
| | ... | Configure interface vhost user | ${node} | ${interface}
| | ... | &{settings}
