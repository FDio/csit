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
| Library | resources.libraries.python.honeycomb.Lisp.LispKeywords
| Library | resources.libraries.python.LispUtil
| Documentation | Keywords used to test Honeycomb Lisp features.

*** Keywords ***
| Honeycomb enables LISP
| | [Documentation] | Uses Honeycomb API to enable Lisp.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables LISP \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Set Lisp state | ${node} | ${TRUE}

| Honeycomb disables LISP
| | [Documentation] | Uses Honeycomb API to disable Lisp.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables LISP \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Set Lisp state | ${node} | ${FALSE}

| Honeycomb adds locator set
| | [Documentation] | Uses Honeycomb API to enable Lisp.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Name of an interface on the node. Type: string
| | ... | - locator_set - Name for the new locator set. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds locator set \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| loc_01 \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${locator_set}
| | ...
| | Add locator | ${node} | ${interface} | ${locator_set}

| Honeycomb adds Lisp Mapping
| | [Documentation] | Uses Honeycomb API to configure a Lisp mapping.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - data - Lisp settings to use. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds Lisp Mapping \| ${nodes['DUT1']} \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${data}
| | ...
| | Configure Lisp Mapping | ${node} | ${data}

| Honeycomb removes all LISP mappings
| | [Documentation] | Uses Honeycomb API to clear the eid-table.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes all LISP mappings \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Configure lisp mapping | ${node} | ${NONE}

| LISP should not be configured
| | [Documentation] | Retrieves Lisp configuration from Honeycomb operational\
| | ... | data, and expects an empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP should not be configured \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Run keyword and Expect Error | KeyError: 'lisp-feature-data'
| | ... | Get Lisp operational data | ${node}

| LISP state from Honeycomb should be
| | [Documentation] | Retrieves Lisp state from Honeycomb operational\
| | ... | data, and compares Lisp state with expected value.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - Expected Lisp state. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP state from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| enabled \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ${data}= | Get Lisp operational data | ${node}
| | ...
| | Run keyword if | $state == 'enabled'
| | ... | Should be equal as strings
| | ... | ${data['lisp-state']['enable']} | ${True}
| | Run keyword if | $state == 'disabled'
| | ... | Should be equal as strings
| | ... | ${data['lisp-state']['enable']} | ${False}

| LISP state from VAT should be
| | [Documentation] | Retrieves Lisp state from VAT,\
| | ... | and compares Lisp state with expected value.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - Expected Lisp state. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP state from VAT should be \| ${nodes['DUT1']} \| enabled \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ...
| | ${status}= | VPP show Lisp State | ${node}
| | Should match | ${status['feature_status']} | ${state}

| LISP mapping from Honeycomb should be
| | [Documentation] | Retrieves Lisp mapping from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - settings - Expected Lisp mapping data. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP mapping from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| ${settings} \|
| | ...
| | [Arguments] | ${node} | ${settings}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['eid-table']['vni-table'][0]}
| | Compare data structures | ${data} | ${settings}

| LISP mapping from VAT should be
| | [Documentation] | Retrieves Lisp mapping from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - settings - Expected Lisp mapping data. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP mapping from VAT should be \| ${nodes['DUT1']} \
| | ... | \| ${settings} \|
| | ...
| | [Arguments] | ${node} | ${settings}
| | ...
| | ${data}= | VPP show Lisp eid table | ${node}
| | Compare data structures | ${data[0]} | ${settings}

| LISP mappings from Honeycomb should not exist
| | [Documentation] | Retrieves Lisp mappings from operational\
| | ... | data, and expects to find none.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP mappings from Honeycomb should not exist \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | Should be empty | ${data['eid-table']['vni-table']}

| LISP mappings from VAT should not exist
| | [Documentation] | Retrieves Lisp mappings from VAT,\
| | ... | and expects to receive an empty list.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP mappings from VAT should not exist \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | ${data}= | VPP show Lisp eid table | ${node}
| | Should be empty | ${data}

| Locator set from Honeycomb should be
| | [Documentation] | Retrieves Lisp locator set from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Interface that should be referenced by locator.\
| | ... | Type: dictionary
| | ... | - locator_set - Expected locator set name. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Locator set From Honeycomb Should Be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| loc01 \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${locator_set}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${loc_data}= | Set Variable
| | ... | ${data['lisp-state']['lisp-feature-data']['locator-sets']}
| | Should be equal
| | ... | ${loc_data['locator-set'][0]['name']}
| | ... | ${locator_set}
| | Should be equal
| | ... | ${loc_data['locator-set'][0]['interface'][0]['interface-ref']}
| | ... | ${interface}

| Honeycomb adds LISP adjacency
| | [Documentation] | Uses Honeycomb API to configure Lisp adjacency.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - vni - Virtual network identifier number. Type: integer
| | ... | - map - Name of an existing remote mapping. Type: string
| | ... | - adjacency - Name for the new adjacency. Type: string
| | ... | - data - Lisp adjacency settings to use. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds LISP adjacency \| ${nodes['DUT1']} \| ${1} \| map1\
| | ... | \| adj1 \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${vni} | ${map} | ${adjacency} | ${data}
| | ...
| | Add Lisp adjacency
| | ... | ${node} | ${vni} | ${map} | ${adjacency} | ${data}

| Honeycomb adds LISP map resolver
| | [Documentation] | Uses Honeycomb API to configure Lisp map resolver.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_address - IP address for the map resolver. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds LISP map resolver \| ${nodes['DUT1']} \
| | ... | \| 192.168.0.2 \|
| | ...
| | [Arguments] | ${node} | ${ip_address}
| | ...
| | Add map resolver | ${node} | ${ip_address}

| Honeycomb adds Lisp Map register
| | [Documentation] | Uses Honeycomb API to configure Lisp map register.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - add_map_register - Set boolean value of map register. Type: bool
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds Lisp Map register \| ${nodes['DUT1']} \
| | ... | \| ${True} \|
| | ...
| | [Arguments] | ${node} | ${add_map_register}
| | ...
| | Set Map Register | ${node} | ${add_map_register}

| Honeycomb sets Lisp Map request Mode
| | [Documentation] | Uses Honeycomb API to configure Lisp map request mode.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - set_map_request - Set boolean value of map request mode. Type: bool
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds Lisp Map Request Mode \| ${nodes['DUT1']} \
| | ... | \| ${True} \|
| | ...
| | [Arguments] | ${node} | ${set_map_request}
| | ...
| | Set Map Request Mode | ${node} | ${set_map_request}

| Map resolver from Honeycomb should be
| | [Documentation] | Retrieves Lisp map resolver from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_address - IP address that should be referenced in map resolver.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Map resolver From Honeycomb Should Be \| ${nodes['DUT1']} \
| | ... | \| 192.168.1.2 \|
| | ...
| | [Arguments] | ${node} | ${ip_address}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['map-resolvers']['map-resolver'][0]}
| | Should be equal | ${data['ip-address']} | ${ip_address}

| Map resolver from VAT should be
| | [Documentation] | Retrieves Lisp mapping from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_address - IP address that should be referenced in map resolver.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Map resolver From VAT Should Be \| ${nodes['DUT1']} \
| | ... | \| 192.168.1.2 \|
| | ...
| | [Arguments] | ${node} | ${ip_address}
| | ...
| | ${data}= | Vpp show Lisp map resolver | ${node}
| | Should be equal | ${data[0]['map resolver']} | ${ip_address}

| Honeycomb adds Lisp Map Server
| | [Documentation] | Uses Honeycomb API to configure Lisp Map Server.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_addresses - IP addresses for the Map Server.\
| | ... | Type: any number of strings
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds Lisp Map Server \| ${nodes['DUT1']} \
| | ... | \| 192.168.0.2 \| 192.168.0.3 \|
| | ...
| | [Arguments] | ${node} | @{ip_addresses}
| | ...
| | Add Map Server | ${node} | @{ip_addresses}

| Map Register from Honeycomb should be
| | [Documentation] | Retrieves Lisp Map Register from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - Desired state - True. Type: bool
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Map Register From Honeycomb Should Be \| ${nodes['DUT1']} \
| | ... | \| ${True} \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['map-register']}
| | Should be equal | ${data['enabled']} | ${state}

| Map Server from Honeycomb should be
| | [Documentation] | Retrieves Lisp Map Server from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_addresses - IP addresses that should be referenced\
| | ... | in Map Server. Type: any number of strings
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Map Server From Honeycomb Should Be \| ${nodes['DUT1']} \
| | ... | \| 192.168.1.2 \| 192.168.1.7 \|
| | ...
| | [Arguments] | ${node} | @{ip_addresses}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | Verify Map Server Data from Honeycomb | ${data} | ${ip_addresses}


| Map Server from VAT should be
| | [Documentation] | Retrieves Lisp mapping from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_addresses - IP addresses that should be referenced\
| | ... | in Map Server. Type: any number of strings
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Map Server From VAT Should Be \| ${nodes['DUT1']} \
| | ... | \| 192.168.1.2 \| 192.168.1.7 \|
| | ...
| | [Arguments] | ${node} | @{ip_addresses}
| | ...
| | ${data}= | Vpp show Lisp Map Server | ${node}
| | Verify Map Server Data from VAT | ${data} | ${ip_addresses}

| Map Register from VAT should be
| | [Documentation] | Retrieves Lisp mapping from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - Desired state - "enabled". Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Map Register From VAT Should Be \| ${nodes['DUT1']} \
| | ... | \| enabled \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ...
| | ${data}= | Vpp show Lisp Map Register | ${node}
| | Should be equal | ${data['state']} | ${state}

| Map Request Mode from VAT should be
| | [Documentation] | Retrieves Lisp Request Mode from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - destination - Source or Destination in Map\
| | ... | Request Mode. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Map Request Mode From VAT Should Be \| ${nodes['DUT1']} \
| | ... | \| src-dst \|
| | ...
| | [Arguments] | ${node} | ${destination}
| | ...
| | ${data}= | Vpp show Lisp Map Request Mode | ${node}
| | Should be equal | ${data['map_request_mode']} | ${destination}

| Honeycomb enables LISP PITR feature
| | [Documentation] | Uses Honeycomb API to configure Lisp PITR feature.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - locator_set - Name of an existing locator set. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables LISP PITR feature \| ${nodes['DUT1']} \| loc1 \|
| | ...
| | [Arguments] | ${node} | ${locator_set}
| | ...
| | Configure PITR | ${node} | ${locator_set}

| Honeycomb enables LISP PETR feature
| | [Documentation] | Uses Honeycomb API to configure Lisp PETR feature.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_address - IP address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables LISP PETR feature \| ${nodes['DUT1']}\
| | ... | \| 192.168.0.1 \|
| | ...
| | [Arguments] | ${node} | ${ip_address}
| | ...
| | Configure PETR | ${node} | ${ip_address}

| Honeycomb enables LISP RLOC feature
| | [Documentation] | Uses Honeycomb API to enable the Lisp RLOC feature.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables LISP RLOC feature\
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Set RLOC probe state | ${node} | ${TRUE}

| PITR config from Honeycomb should be
| | [Documentation] | Retrieves PITR config from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - locator_set - Name of locator set that should be referenced\
| | ... | in PITR config. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| PITR config from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| loc01 \|
| | ...
| | [Arguments] | ${node} | ${locator_set}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['pitr-cfg']}
| | Should be equal | ${data['locator-set']} | ${locator_set}

| PETR configuration from Honeycomb should be
| | [Documentation] | Retrieves PETR config from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_address - IP address for PETR config. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| PETR config from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| 192.168.0.1 \|
| | ...
| | [Arguments] | ${node} | ${ip_address}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['petr-cfg']['petr-address']}
| | Should be equal | ${data} | ${ip_address}

| Map Request Mode from Honeycomb should be
| | [Documentation] | Retrieves List Map Request Mode from Honeycomb\
| | ... | operational data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - destination - source-destination. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| List Map Request Mode from Honeycomb should be \| ${nodes['DUT1']}\
| | ... | \| 192.168.0.1 \|
| | ...
| | [Arguments] | ${node} | ${destination}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['map-request-mode']['mode']}
| | Should be equal | ${data} | ${destination}

| RLOC probing from Honeycomb should be
| | [Documentation] | Retrieves RLOC config from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - desired state -True/False. Type: bool
| | ...
| | ... | *Example:*
| | ...
| | ... | \| RLOC probing from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| ${True} \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['rloc-probe']['enabled']}
| | Should be equal | ${data} | ${state}

| PETR configuration from VAT should be
| | [Documentation] | Retrieves Lisp mapping from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - state of PETR config - enabled/disabled.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| PETR configuration From VAT Should Be \| ${nodes['DUT1']} \
| | ... | \| enabled \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ...
| | ${data}= | Vpp show Lisp PETR config | ${node}
| | Should be equal | ${data['status']} | ${state}

| RLOC probing from VAT should be
| | [Documentation] | Retrieves Lisp mapping from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - state of RLOC config - enabled/disabled.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| RLOC configuration From VAT Should Be \| ${nodes['DUT1']} \
| | ... | \| enabled \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ...
| | ${data}= | Vpp show Lisp RLOC config | ${node}
| | Should be equal | ${data['state']} | ${state}

| PITR config from VAT should be
| | [Documentation] | Retrieves PITR config from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - locator_set - Name of locator set that should be referenced\
| | ... | in PITR config. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| PITR config from VAT should be \| ${nodes['DUT1']} \
| | ... | \| loc01 \|
| | ...
| | [Arguments] | ${node} | ${locator_set}
| | ...
| | ${data}= | VPP show Lisp PITR | ${node}
| | Should be equal | ${data['status']} | enabled
| | Should be equal | ${data['locator_set']} | ${locator_set}

| Honeycomb disables all LISP features
| | [Documentation] | Uses Honeycomb API to remove all Lisp configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables all LISP features \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Disable Lisp | ${node}