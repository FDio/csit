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
| ...     | WITH NAME | InterfaceAPI
| Library | resources.libraries.python.telemetry.SPAN
| Library  | resources.libraries.python.InterfaceUtil
| Library  | resources.libraries.python.IPv4Util
| Library  | resources.libraries.python.IPv4Setup
| Library  | resources.libraries.python.Trace

*** Keywords ***
| Honeycomb Configures SPAN on interface
| | [Documentation] | Uses Honeycomb API to configure SPAN on the specified\
| | ... | interface, mirroring one or more interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - dst_interface - Mirroring destination interface. Type: string
| | ... | - src_interfaces - Mirroring source interfaces. Type: list -\
| | ... | of dictionaries
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb Configures SPAN on interface \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| list of dictionaries \|
| | ...
| | [Arguments] | ${node} | ${dst_interface} | @{src_interfaces}
| | InterfaceAPI.Configure interface SPAN
| | ... | ${node} | ${dst_interface} | ${src_interfaces}

| Interface SPAN configuration from Honeycomb should be
| | [Documentation] | Retrieves interface operational data and verifies that\
| | ... | SPAN mirroring is configured with the provided interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - dst_interface - Mirroring destination interface. Type: string
| | ... | - src_interfaces - Mirroring source interfaces. Type: Argument list -\
| | ... | any number of strings
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface SPAN configuration from Honeycomb should be \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| GigabitEthernet0/9/0 \|
| | ...
| | [Arguments] | ${node} | ${dst_interface} | @{src_interfaces}
| | ${data}= | InterfaceAPI.Get interface oper data | ${node} | ${dst_interface}
| | ${data}= | Set Variable
| | ... | ${data['v3po:span']['mirrored-interfaces']['mirrored-interface']}
| | Sort list | ${data}
| | Sort list | ${src_interfaces}
| | Lists should be equal | ${data} | ${src_interfaces}

| Interface SPAN configuration from Honeycomb should be empty
| | [Documentation] | Checks whether SPAN configuration from Honeycomb is empty.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - dst_interface - Mirroring destination interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface SPAN configuration from Honeycomb should be empty \
| | ... | \| ${node} \| GigabitEthernetO/8/0 \|
| | ...
| | [Arguments] | ${node} | ${dst_interface}
| | ${data}= | Get interface oper data | ${node} | ${dst_interface}
| | Variable should not exist | ${data['v3po:span']['mirrored-interfaces']['mirrored-interface']}

| Interface SPAN configuration from VAT should be
| | [Documentation] | Retrieves SPAN configuration from VAT dump and verifies\
| | ... | that SPAN mirroring is configured with the provided interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - dst_interface - Mirroring destination interface. Type: string
| | ... | - src_interfaces - Mirroring source interfaces. Type: Argument list -\
| | ... | any number of strings
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface SPAN configuration from VAT should be \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| GigabitEthernet0/9/0 \|
| | ...
| | [Arguments] | ${node} | ${dst_interface} | @{src_interfaces}
| | ${data}= | VPP get SPAN configuration by interface
| | ... | ${node} | ${dst_interface} | name
| | Sort list | ${data}
| | Sort list | ${src_interfaces}
| | Lists should be equal | ${data} | ${src_interfaces}

| Honeycomb removes interface SPAN configuration
| | [Documentation] | Uses Honeycomb API to remove SPAN confirugation\
| | ... | from the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - dst_interface - Mirroring destination interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes interface SPAN configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${dst_interface}
| | InterfaceAPI.Configure interface SPAN | ${node} | ${dst_interface}

| Interface SPAN configuration from Honeycomb should not exist
| | [Documentation] | Retrieves interface operational data and verifies that\
| | ... | SPAN mirroring is not configured.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - dst_interface - Mirroring destination interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \|
| | [Arguments] | ${node} | ${dst_interface}
| | ${data}= | InterfaceAPI.Get interface oper data | ${node} | ${dst_interface}
| | Run keyword and expect error | *KeyError* | Set Variable
| | ... | ${data['span']['mirrored-interfaces']['mirrored-interface']}

| SPAN configuration from VAT should not exist
| | [Documentation] | Attmepts to retrieve SPAN configuration from VAT dump,\
| | ... | and expects to fail with no data retrieved.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| SPAN configuration from VAT should not exist \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Run keyword and expect error | ValueError: No JSON object could be decoded
| | ... | VPP get SPAN configuration by interface | ${node} | local0
