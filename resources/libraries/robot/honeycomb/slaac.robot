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
| Library | resources.libraries.python.honeycomb.Routing.RoutingKeywords
| Library | resources.libraries.python.Trace
| Documentation | Keywords used to test SLAAC using Honeycomb.

*** Keywords ***
| Honeycomb configures SLAAC
| | [Documentation] | Uses Honeycomb API to configure SLAAC on the specified\
| | ... | interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ... | - slaac_data - data needed to configure SLAAC. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures SLAAC \| ${node} \| ${interface} \
| | ... | \| ${slaac_data} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${slaac_data}
| | Configure interface SLAAC
| | ... | ${node} | ${interface} | ${slaac_data}

| SLAAC Operational Data From Honeycomb Should Be
| | [Documentation] | Retrieves SLAAC operational data and verifies that\
| | ... | SLAAC is configured with the provided interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ... | - slaac_data - data to compare configuration SLAAC with.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| SLAAC Operational Data From Honeycomb Should Be \
| | ... | \| ${node} \| ${interface} \| ${slaac_data} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${slaac_data}
| | ${data}= | Get interface SLAAC oper data | ${node} | ${interface}
| | Dictionaries should be equal | ${data} | ${slaac_data}

| SLAAC Operational Data From Honeycomb Should Be empty
| | [Documentation] | Checks whether SLAAC configuration from Honeycomb \
| | ... | is empty.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| SLAAC Operational Data From Honeycomb Should Be empty \
| | ... | \| ${node} \| ${interface} \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Run keyword and expect error | HoneycombError*404*
| | ... | Get interface SLAAC oper data | ${node} | ${interface}

| Honeycomb removes SLAAC configuration
| | [Documentation] | Uses Honeycomb API to remove SLAAC confirugation\
| | ... | from the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes SLAAC configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Configure interface SLAAC | ${node} | ${interface}

| SLAAC test teardown
| | [Documentation] | Uses Honeycomb API to remove SLAAC confirugation\
| | ... | and reset interface state.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes SLAAC configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | And Honeycomb configures interface state | ${node} | ${interface} | down
| | Honeycomb removes interface IPv6 addresses | ${node} | ${interface}
