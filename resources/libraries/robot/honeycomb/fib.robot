# Copyright (c) 2018 Bell Canada, Pantheon Technologies and/or its affiliates.
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
| Library | resources.libraries.python.honeycomb.FIB.FibKeywords
| Documentation | Keywords used to test Honeycomb FIB tables.

*** Keywords ***
| Honeycomb configures FIB table
| | [Documentation] | Uses Honeycomb API to configure a FIB table.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type:string
| | ... | - vrf - vrf-id the new table will belong to. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures FIB table \| ${nodes['DUT1']} \
| | ... | \| ipv4 \| ${vrf} \|
| | [Arguments] | ${node} | ${ip_version} | ${vrf}
| | Configure FIB table | ${node} | ${ip_version} | ${vrf}

| FIB table data from Honeycomb should contain
| | [Documentation] | Uses Honeycomb API to retrieve operational data about\
| | ... | a FIB table, and compares with the data provided.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type:string
| | ... | - vrf - vrf-id the new table will belong to. Type: integer
| | ... | - expected_data - Data to compare against. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| FIB table data from Honeycomb should contain \| ${nodes['DUT1']} \
| | ... | \| ipv4 \| ${data} \|
| | [Arguments] | ${node} | ${ip_version} | ${vrf} | ${expected_data}
| | ${data}= | Get FIB Table Oper | ${node} | ${ip_version} | ${vrf}
| | Should Contain | ${data} | ${expected_data}

| Honeycomb removes FIB configuration
| | [Documentation] | Uses Honeycomb API to remove Honeycomb-created\
| | ... | FIB configuration from the node. Entries configured automatically\
| | ... | by VPP will not be removed.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type:string
| | ... | - vrf - vrf-id the new table will belong to. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes FIB configuration \| ${nodes['DUT1']} \
| | ... | \| ${ip_version} \| ${vrf} \|
| | [Arguments] | ${node} | ${ip_version} | ${vrf}
| | Delete FIB table | ${node} | ${ip_version} | ${vrf}
