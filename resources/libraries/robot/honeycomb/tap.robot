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
| Documentation | Keywords used to manipulate TAP interfaces.

*** Keywords ***
| Honeycomb creates TAP interface
| | [Documentation] | Uses Honeycomb API to configure a new TAP interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for TAP. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb creates TAP interface \
| | ... | \| ${nodes['DUT1']} \| tap_int1 \| ${{'host-interface-name':'tap1',\
| | ... | 'mac':'08:00:27:60:26:ab', 'id':3}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | Create TAP interface | ${node} | ${interface}
| | ... | &{settings}

| Honeycomb configures TAP interface
| | [Documentation] | Uses Honeycomb API to configure an existing TAP interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for TAP. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb configures TAP interface \
| | ... | \| ${nodes['DUT1']} \| tap_int1 \| ${{'host-interface-name':'tap1',\
| | ... | 'mac':'08:00:27:60:26:ab', 'id':3}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | Configure interface TAP | ${node} | ${interface}
| | ... | &{settings}

| Honeycomb removes TAP interface
| | [Documentation] | Uses Honeycomb API to remove a TAP interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes TAP interface \
| | ... | \| ${nodes['DUT1']} \| tap_int1 \|
| | [Arguments] | ${node} | ${interface}
| | Delete interface | ${node} | ${interface}

| TAP Operational Data From Honeycomb Should Be
| | [Documentation] | Retrieves interface TAP configuration through Honeycomb\
| | ... | and compares with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for TAP. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| TAP Operational Data From Honeycomb Should Be \
| | ... | \| ${nodes['DUT1']} \| tap_int1 \| ${{'host-interface-name':'tap1',\
| | ... | 'mac':'08:00:27:60:26:ab', 'id':3}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | ${api_data}= | Get interface oper data | ${node} | ${interface}
| | ${api_tap}= | Set Variable | ${api_data['v3po:tap-v2']}
| | Should be equal | ${api_tap['device-name']} | ${settings['device-name']}
| | ${api_mac}= | Set Variable | ${api_data['phys-address']}
| | Should be equal | ${api_mac} | ${settings['mac']}

| TAP Operational Data From VAT Should Be
| | [Documentation] | Retrieves interface TAP configuration through VAT and\
| | ... | compares with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - settings - Configuration data for TAP. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| TAP Operational Data From Honeycomb Should Be \
| | ... | \| ${nodes['DUT1']} \| ${{'host-interface-name':'tap1',\
| | ... | 'mac':'08:00:27:60:26:ab', 'id':3}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | ${vat_data}= | TAP Dump | ${node} | ${interface}
| | Should be equal | ${vat_data['dev_name']} | ${settings['dev_name']}
| | Should be equal | ${vat_data['rx_ring_sz']} | ${settings['rx_ring_sz']}
| | Should be equal | ${vat_data['tx_ring_sz']} | ${settings['tx_ring_sz']}
# other settings not accessible through VAT commands

| TAP Operational Data From Honeycomb Should Be empty
| | [Documentation] | Attempts to retrieve interface TAP configuration\
| | ... | through Honeycomb and expects to recieve an empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| TAP Operational Data From Honeycomb Should Be empty\
| | ... | \| ${nodes['DUT1']} \| tap_int1 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | Get interface oper data | ${node} | ${interface}
| | Run keyword and expect error | *KeyError: 'v3po:tap-v2' | Set Variable
| | ... | ${api_data['v3po:tap-v2']}

| TAP Operational Data From VAT Should Be empty
| | [Documentation] | Attempts to retrieve interface TAP configuration\
| | ... | through VAT and expects a "no data" error.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| TAP Operational Data From VAT Should Be empty\
| | ... | \| ${nodes['DUT1']} \| tap_int1 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${data}= | TAP Dump | ${node} | ${interface}
| | Should be empty | ${data}
