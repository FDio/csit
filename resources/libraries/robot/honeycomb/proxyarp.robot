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
| Library | resources.libraries.python.honeycomb.proxyARP.ProxyARPKeywords
| Documentation | Keywords used to test Honeycomb proxyARP.

*** Keywords ***
| Honeycomb configures proxyARP
| | [Documentation] | Uses Honeycomb API to configure proxyARP for a specific\
| | ... | destination IP range.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - data - Configuration to use. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures proxyARP \| ${nodes['DUT1']} \| ${data} \|
| | [Arguments] | ${node} | ${data}
| | Configure proxyARP | ${node} | ${data}

| Honeycomb removes proxyARP configuration
| | [Documentation] | Uses Honeycomb API to remove existing proxyARP\
| | ... | IP range configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes proxyARP configuration \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Remove proxyARP configuration | ${node}

| Honeycomb enables proxyARP on interface
| | [Documentation] | Uses Honeycomb API to enable the proxyARP\
| | ... | feature on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables proxyARP on interface \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Set proxyARP interface config | ${node} | ${interface} | enable

| Honeycomb disables proxyARP on interface
| | [Documentation] | Uses Honeycomb API to disable the proxyARP\
| | ... | feature on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables proxyARP on interface \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Set proxyARP interface config | ${node} | ${interface} | disable
