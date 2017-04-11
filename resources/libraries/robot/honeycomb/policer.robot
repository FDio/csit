# Copyright (c) 2017 Cisco and/or its affiliates.
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
#| Library | resources.libraries.python.honeycomb.Policer.PolicerKeywords
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.honeycomb.Routing.RoutingKeywords
| ...     | WITH NAME | RoutingKeywordsAPI
| Variables | resources/test_data/honeycomb/policer_variables.py
| Documentation | Keywords used to test Policer using Honeycomb.

*** Keywords ***
| Honeycomb Configures Policer
| | [Documentation] | Uses Honeycomb API to configure Policer on the specified\
| | ... | interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - policer_data - data needed to configure Policer. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb Configures Policer \| ${node} \|
| | ... | \| ${policer_data} \|
| | ...
| | [Arguments] | ${node} | ${policer_data}
| | Configure Policer
| | ... | ${node} | ${policer_data}

| Policer configuration from Honeycomb should be
| | [Documentation] | Retrieves Policer operational data and verifies that\
| | ... | Policer is configured correctly.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - policer_data - data to compare configuration Policer with.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Policer configuration from Honeycomb should be \
| | ... | \| ${node} \| \| ${policer_data} \|
| | ...
| | [Arguments] | ${node} | ${policer_data}
| | ${data}= | Get Policer oper data | ${node}
| | Should be equal | ${data[0]} | ${policer_data[0]}

| Policer configuration from Honeycomb should be empty
| | [Documentation] | Checks whether Policer configuration from Honeycomb \
| | ... | is empty.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Policer configuration from Honeycomb should be empty \
| | ... | \| ${node} \|
| | ...
| | [Arguments] | ${node}
| | Run keyword and expect error | HoneycombError*404*
| | ... | Get Policer oper data | ${node}

| Honeycomb removes Policer configuration
| | [Documentation] | Uses Honeycomb API to remove Policer confirugation\
| | ... | from the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes Policer configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node}
| | Configure Policer | ${node}

| Policer test teardown
| | [Documentation] | Uses Honeycomb API to remove Policer confirugation\
| | ... | and reset interface state.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes Policer configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node}
| | Honeycomb removes Policer configuration | ${node}
#| | And InterfaceAPI.Set Interface State | ${node} | down
#| | Honeycomb removes interface ipv6 addresses | ${node}

| Honeycomb enables Policer on interface
| | [Documentation] | Uses Honeycomb API to enable Policer on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - table_name - name of an ACL table. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables ACL on interface \| ${nodes['DUT1']} \
| | ... | \| GigabithEthernet0/8/0 \| table0 \|
| | [Arguments] | ${node} | ${interface} | ${table_name}
| | Enable Policer on interface
| | ... | ${node} | ${interface} | ${table_name}
