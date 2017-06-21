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

*** Keywords ***
| Honeycomb sets interface VxLAN configuration
| | [Documentation] | Uses Honeycomb API to configure a VxLAN tunnel.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for VxLAN. Type: dictionary
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb sets interface VxLAN configuration \
| | ... | \|${nodes['DUT1']} \| vxlan_01 \| ${{'src':'192.168.0.2',\
| | ... | 'dst':'192.168.0.3', 'vni':5, 'encap-vrf-id':0}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | Create VxLAN interface | ${node} | ${interface}
| | ... | &{settings}

| Honeycomb removes VxLAN tunnel settings
| | [Documentation] | Uses Honeycomb API to disable a VxLAN tunnel and remove\
| | ... | it from configuration data.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes VxLAN tunnel \| ${nodes['DUT1']} \| vxlan_01 \|
| | [Arguments] | ${node} | ${interface}
| | Delete interface | ${node} | ${interface}

| VxLAN Operational Data From Honeycomb Should Be
| | [Documentation] | Retrieves interface VxLAN configuration through Honeycomb\
| | ... | and compares with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for VxLAN. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VxLAN Operational Data From Honeycomb Should Be \
| | ... | \|${nodes['DUT1']} \| vxlan_01 \| ${{'src':'192.168.0.2',\
| | ... | 'dst':'192.168.0.3', 'vni':5, 'encap-vrf-id':0}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | ${api_data}= | Get interface oper data | ${node} | ${interface}
| | ${api_vxlan}= | Set Variable | ${api_data['v3po:vxlan']}
| | :FOR | ${key} | IN | @{settings.keys()}
| | | Should be equal | ${api_vxlan['${key}']} | ${settings['${key}']}

| VxLAN Operational Data From VAT Should Be
| | [Documentation] | Retrieves interface VxLAN configuration through VAT and\
| | ... | compares with settings supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - settings - Configuration data for VxLAN. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VxLAN Operational Data From Honeycomb Should Be \
| | ... | \|${nodes['DUT1']} \| ${{'src':'192.168.0.2',\
| | ... | 'dst':'192.168.0.3', 'vni':5, 'encap-vrf-id':0}} \|
| | ...
| | ... | *Note:*
| | ... | Due to the difficulty of identifying newly created interfaces by name\
| | ... | or by sw_index, this keyword assumes there is only one VxLAN tunnel\
| | ... | present on the specified node.
| | [Arguments] | ${node} | ${settings}
| | ${vat_data}= | VxLAN Dump | ${node}
| | ${vat_data}= | Set Variable | ${vat_data[0]}
| | Should be equal | ${vat_data['dst_address']} | ${settings['dst']}
| | Should be equal | ${vat_data['src_address']} | ${settings['src']}
| | Should be equal | ${vat_data['vni']} | ${settings['vni']}
| | Should be equal
| | ... | ${vat_data['encap_vrf_id']} | ${settings['encap-vrf-id']}

| VxLAN Operational Data From Honeycomb Should Be empty
| | [Documentation] | Attempts to retrieve interface VxLAN configuration\
| | ... | through Honeycomb and expects to recieve an empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VxLAN Operational Data From Honeycomb Should Be empty\
| | ... | \|${nodes['DUT1']} \| vxlan_01 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | Get interface oper data | ${node} | ${interface}
| | Run keyword and expect error | *KeyError: 'v3po:vxlan' | Set Variable
| | ... | ${api_data['v3po:vxlan']}

| VxLAN Operational Data From VAT Should Be empty
| | [Documentation] | Attempts to retrieve interface VxLAN configuration\
| | ... | through VAT and expects a "no data" error.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VxLAN Operational Data From VAT Should Be empty\
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Run Keyword And Expect Error | ValueError: No JSON object could be decoded
| | ... | VxLAN Dump | ${node}

| Honeycomb fails setting VxLan on different interface type
| | [Documentation] | Attempts to set VxLAN settings on an ethernet\
| | ... | type interface and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings - Configuration data for VxLAN. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb fails setting VxLan on different interface type\
| | ... | \|${nodes['DUT1']} \| GigabitEthernet0/9/0 \| ${{'src':'192.168.0.2',\
| | ... | 'dst':'192.168.0.3', 'vni':5, 'encap-vrf-id':0}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings}
| | Run Keyword And Expect Error | HoneycombError: * Status code: 500.
| | ... | Configure interface vxlan
| | ... | ${node} | ${interface} | &{settings}

| Honeycomb fails setting invalid VxLAN configuration
| | [Documentation] | Attempts to create a VxLAN interface with invalid\
| | ... | configuration and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - settings_list - Bad configuration data for VxLAN. Type: list
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb fails setting invalid VxLAN configuration\
| | ... | \|${nodes['DUT1']} \| vxlan_01 \| ${{'src':'abcd', 'vni':-3}} \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${settings_list}
| | :FOR | ${settings} | IN | @{settings_list}
| | | Run Keyword And Expect Error | HoneycombError: * Status code: 500.
| | | ... | Create VxLAN interface
| | | ... | ${node} | ${interface} | &{settings}
