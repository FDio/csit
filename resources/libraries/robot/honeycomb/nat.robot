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
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| Library | resources.libraries.python.honeycomb.NAT.NATKeywords
| Library | resources.libraries.python.NAT.NATUtil
| Documentation | Keywords used to test Honeycomb NAT node.

*** Keywords ***
| NAT Operational Data From Honeycomb Should Be empty
| | [Documentation] | Uses Honeycomb API to retrieve NAT operational data\
| | ... | and expects to find only default values.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - default_settings - NAT default settings. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NAT Operational Data From Honeycomb Should Be empty \
| | ... | \| ${nodes['DUT1']} \| ${default_settings} \|
| | [Arguments] | ${node} | ${default_settings}
| | ${data}= | Get NAT Oper data | ${node}
| | Compare data structures | ${data} | ${default_settings}

| Honeycomb configures NAT entry
| | [Documentation] | Uses Honeycomb API to configure a static NAT entry.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - data - NAT entry to configure. Type: dictionary
| | ... | - instance - NAT instance on VPP node. Type: integer
| | ... | - index - Index of NAT entry. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures NAT entry \| ${nodes['DUT1']} \| ${data} \
| | ... | \| ${0} \| ${1} \|
| | [Arguments] | ${node} | ${data} | ${instance}=0 | ${index}=1
| | Configure NAT entries | ${node} | ${data} | ${instance} | ${index}

| NAT entries from Honeycomb should be
| | [Documentation] | Uses Honeycomb API to retrieve NAT operational data\
| | ... | and compares against expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - settings - NAT entry to expect. Type: dictionary
| | ... | - instance - NAT instance on VPP node. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NAT entries from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| ${settings} \| ${0} \|
| | [Arguments] | ${node} | ${settings} | ${instance}=0
| | ${data}= | Get NAT Oper data | ${node}
| | ${data}= | Set Variable
| | ... | ${data['nat-instances']['nat-instance'][${instance}]['mapping-table']}
| | Compare data structures | ${data} | ${settings}

| Honeycomb configures NAT on interface
| | [Documentation] | Uses Honeycomb API to configure NAT on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ... | - direction - NAT direction parameter, inbound or outbound.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures NAT on interface \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| outbound \|
| | [Arguments] | ${node} | ${interface} | ${direction}
| | Configure NAT on interface
| | ... | ${node} | ${interface} | ${direction}

| Honeycomb removes NAT interface configuration
| | [Documentation] | Uses Honeycomb API to remove an existing NAT interface\
| | ... | configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ... | - direction - NAT direction parameter, inbound or outbound.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes NAT interface configuration \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| outbound \|
| | [Arguments] | ${node} | ${interface} | ${direction}
| | Configure NAT on interface
| | ... | ${node} | ${interface} | ${direction} | ${True}

| NAT interface Operational Data From Honeycomb Should Be
| | [Documentation] | Uses Honeycomb API to retrieve interface operational data\
| | ... | and compares the NAT section against expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ... | - direction - NAT direction parameter, inbound or outbound.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NAT interface Operational Data From Honeycomb Should Be \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| outbound \|
| | [Arguments] | ${node} | ${interface} | ${direction}
| | ${data}= | Get interface oper data | ${node} | ${interface}
| | Variable should exist | ${data['interface-nat:nat']['${direction}']}

| NAT interface Operational Data From Honeycomb Should Be empty
| | [Documentation] | Uses Honeycomb API to retrieve interface operational data\
| | ... | and expects to find no data for the given direction.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ... | - direction - NAT direction parameter, inbound or outbound.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NAT interface Operational Data From Honeycomb Should Be empty \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| outbound \|
| | [Arguments] | ${node} | ${interface} | ${direction}
| | ${data}= | Get interface oper data | ${node} | ${interface}
| | Variable should not exist | ${data['interface-nat:nat']['${direction}']}

| NAT interface Operational Data From VAT Should Be
| | [Documentation] | Uses Honeycomb API to retrieve NAT configured interfaces\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - settings - settings to expect. Type: dictionary
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| NAT interface Operational Data From VAT Should Be \
| | ... | \| ${nodes['DUT1']} \| ${settings} \|
| | [Arguments] | ${node} | ${settings}
| | ${data}= | VPP get NAT interfaces | ${node}
| | Compare data structures | ${data} | ${settings}
