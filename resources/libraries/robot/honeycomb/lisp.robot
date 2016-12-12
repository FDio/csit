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
| Honeycomb enables Lisp
| | [Documentation] | Uses Honeycomb API to enable Lisp.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb enables Lisp \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | ...
| | Set Lisp state | ${node} | enable

| Honeycomb adds locator set
| | [Documentation] | Uses Honeycomb API to enable Lisp.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Name of an interface on the node. Type: string
| | ... | - locator_set - Name for the new locator set. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb enables Lisp \| ${nodes['DUT1']} \| GigabitEthernet0/8/0\
| | ... | \| loc_01 \|
| | [Arguments] | ${node} | ${interface} | ${locator_set}
| | Add locator | ${node} | ${interface} | ${locator_set}

| Honeycomb adds Lisp mapping
| | [Documentation] | Uses Honeycomb API to configure a Lisp mapping.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - data - Lisp settings to use. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb adds Lisp mapping \| ${nodes['DUT1']} \| ${data} \|
| | [Arguments] | ${node} | ${data}
| | Configure lisp mapping | ${node} | ${data}

| Honeycomb removes all Lisp mappings
| | [Documentation] | Uses Honeycomb API to clear the eid-table.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb removes all Lisp mappings \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Configure lisp mapping | ${node} | ${NONE}

| Lisp should not be configured
| | [Documentation] | Retrieves Lisp configuration from Honeycomb operational\
| | ... | data, and expects an empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Lisp should not be configured \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | ...
| | ${data}= | Get Lisp operational data | ${node}
| | Should be equal as strings | ${data['lisp-state']['enable']} | False
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | Should match | ${data['pitr-cfg']['locator-set']} | N/A
| | Variable should not exist | ${data['eid-table']['vni-table'][0]}

| Lisp state From Honeycomb Should Be
| | [Documentation] | Retrieves Lisp state from Honeycomb operational\
| | ... | data, and compares Lisp state with expected value.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - Expected Lisp state. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Lisp state From Honeycomb Should Be \| ${nodes['DUT1']} \
| | ... | \| enabled \|
| | [Arguments] | ${node} | ${state}
| | ${data}= | Get Lisp operational data | ${node}
| | Run keyword if | $state == 'enabled'
| | ... | Should be equal as strings
| | ... | ${data['lisp-state']['enable']} | ${True}
| | Run keyword if | $state == 'disabled'
| | ... | Should be equal as strings
| | ... | ${data['lisp-state']['enable']} | ${False}

| Lisp state From VAT Should Be
| | [Documentation] | Retrieves Lisp state from VAT,\
| | ... | and compares Lisp state with expected value.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - Expected Lisp state. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Lisp state From VAT Should Be \| ${nodes['DUT1']} \| enabled \|
| | [Arguments] | ${node} | ${state}
| | ${status}= | VPP show Lisp State | ${node}
| | Should match | ${status['feature_status']} | ${state}

| Lisp mapping From Honeycomb Should Be
| | [Documentation] | Retrieves Lisp mapping from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - settings - Expected Lisp mapping data. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Lisp mapping From Honeycomb Should Be \| ${nodes['DUT1']} \
| | ... | \| ${settings} \|
| | [Arguments] | ${node} | ${settings}
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['eid-table']['vni-table'][0]}
| | Compare data structures | ${data} | ${settings}

| Lisp mapping From VAT Should Be
| | [Documentation] | Retrieves Lisp mapping from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - settings - Expected Lisp mapping data. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Lisp mapping From VAT Should Be \| ${nodes['DUT1']} \
| | ... | \| ${settings} \|
| | [Arguments] | ${node} | ${settings}
| | ${data}= | VPP show Lisp eid table | ${node}
| | Compare data structures | ${data[0]} | ${settings}

| Lisp mappings from Honeycomb should not exist
| | [Documentation] | Retrieves Lisp mappings from operational\
| | ... | data, and expects to find none.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Lisp mappings from Honeycomb should not exist \
| | ... | \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | Should be empty | ${data['eid-table']['vni-table']}

| Lisp mappings from VAT should not exist
| | [Documentation] | Retrieves Lisp mappings from VAT,\
| | ... | and expects to receive an empty list.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Lisp mappings from VAT should not exist \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
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
| | ... | \| Locator set From Honeycomb Should Be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| loc01 \|
| | [Arguments] | ${node} | ${interface} | ${locator_set}
| | ${data}= | Get Lisp operational data | ${node}
| | ${loc_data}= | Set Variable
| | ... | ${data['lisp-state']['lisp-feature-data']['locator-sets']}
| | Should be equal
| | ... | ${loc_data['locator-set'][0]['name']}
| | ... | ${locator_set}
| | Should be equal
| | ... | ${loc_data['locator-set'][0]['interface'][0]['interface-ref']}
| | ... | ${interface}

| Honeycomb adds Lisp adjacency
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
| | ... | \| Honeycomb adds Lisp adjacency \| ${nodes['DUT1']} \| ${1} \| map1\
| | ... | \| adj1 \| ${data} \|
| | [Arguments] | ${node} | ${vni} | ${map} | ${adjacency} | ${data}
| | Add Lisp adjacency
| | ... | ${node} | ${vni} | ${map} | ${adjacency} | ${data}

| Honeycomb adds Lisp Map resolver
| | [Documentation] | Uses Honeycomb API to configure Lisp map resolver.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_address - IP address for the map resolver. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb adds Lisp Map resolver \| ${nodes['DUT1']} \
| | ... | \| 192.168.0.2 \|
| | [Arguments] | ${node} | ${ip_address}
| | Add map resolver | ${node} | ${ip_address}

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
| | ... | \| Map resolver From Honeycomb Should Be \| ${nodes['DUT1']} \
| | ... | \| 192.168.1.2 \|
| | [Arguments] | ${node} | ${ip_address}
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
| | ... | \| Map resolver From VAT Should Be \| ${nodes['DUT1']} \
| | ... | \| 192.168.1.2 \|
| | [Arguments] | ${node} | ${ip_address}
| | ${data}= | Vpp show Lisp map resolver | ${node}
| | Should be equal | ${data[0]['map resolver']} | ${ip_address}

| Honeycomb enables Lisp PITR feature
| | [Documentation] | Uses Honeycomb API to configure Lisp PITR feature.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - locator_set - Name of an existing locator set. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb enables Lisp PITR feature \| ${nodes['DUT1']} \| loc1 \|
| | [Arguments] | ${node} | ${locator_set}
| | Configure PITR | ${node} | ${locator_set}

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
| | ... | \| PITR config from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| loc01 \|
| | [Arguments] | ${node} | ${locator_set}
| | ${data}= | Get Lisp operational data | ${node}
| | ${data}= | Set Variable | ${data['lisp-state']['lisp-feature-data']}
| | ${data}= | Set Variable | ${data['pitr-cfg']}
| | Should be equal | ${data['locator-set']} | ${locator_set}

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
| | ... | \| PITR config from VAT should be \| ${nodes['DUT1']} \
| | ... | \| loc01 \|
| | [Arguments] | ${node} | ${locator_set}
| | ${data}= | VPP show Lisp PITR | ${node}
| | Should be equal | ${data['status']} | enabled
| | Should be equal | ${data['locator_set']} | ${locator_set}

| Honeycomb disables all Lisp features
| | [Documentation] | Uses Honeycomb API to remove all Lisp configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb disables all Lisp features \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Disable Lisp | ${node}