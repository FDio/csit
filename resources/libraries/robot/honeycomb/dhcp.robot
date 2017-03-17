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
| Library | resources.libraries.python.honeycomb.DHCP.DHCPRelayKeywords
| Library | resources.libraries.python.Dhcp.DhcpProxy
| Documentation | Keywords used to test Honeycomb DHCP features.

*** Keywords ***
| DHCP relay configuration from Honeycomb should be empty
| | [Documentation] | Uses Honeycomb API to retrieve DHCP relay configuration\
| | ... | and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| DHCP relay configuration from Honeycomb should be empty \
| | ... | \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Run keyword and expect error | *Status code: 404*
| | ... | Get DHCP relay oper data | ${node}

| Log DHCP relay configuration from VAT
| | [Documentation] | Uses VAT to retrieve DHCP relay configuration from VPP.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Log DHCP relay configuration from VAT \
| | ... | \| ${nodes['DUT1']} \| ipv4 \|
| | [Arguments] | ${node} | ${ip_version}
| | VPP get DHCP proxy | ${node} | ${ip_version}

| Honeycomb configures DHCP relay
| | [Documentation] | Uses Honeycomb API to configure DHCP relay.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - data - settings for the DHCP relay. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures DHCP relay \| ${nodes['DUT1']} \| ${data} \
| | ... | \| ipv4 \| ${0} \|
| | [Arguments] | ${node} | ${data} | ${ip_version} | ${vrf}
| | Add DHCP relay | ${node} | ${data} | ${ip_version} | ${vrf}

| Honeycomb clears DHCP relay configuration
| | [Documentation] | Uses Honeycomb API to delete all configured DHCP relays.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb clears DHCP relay configuration \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Clear DHCP relay configuration | ${node}

| DHCP relay configuration from Honeycomb should contain
| | [Documentation] | Retrieves oper data for DHCP relay and compares\
| | ... | with provided values.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ... | - data - expected DHCP relay settings. Type dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| DHCP relay configuration from Honeycomb should contain \
| | ... | \| ${nodes['DUT1']} \| ${data} \|
| | [Arguments] | ${node} | ${data}
| | ${oper_data}= | Get DHCP relay oper data | ${node}
| | ${oper_data}= | Set Variable | ${oper_data['relays']['relay'][0]}
| | Sort List | ${oper_data['server']}
| | Sort List | ${data['server']}
| | Should be equal | ${oper_data} | ${data}
