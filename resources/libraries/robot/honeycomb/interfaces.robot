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
| ...     | WITH NAME | interfaceCLI
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| ...     | WITH NAME | InterfaceAPI

*** Keywords ***
| Interface state is
| | [Documentation] | Uses VPP binary API to ensure that the interface under\
| | ... | test is in the specified admin state.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - state - state to set on interface. Type:string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface state is \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \
| | ... | \| up \|
| | [Arguments] | ${node} | ${interface} | ${state}
| | interfaceCLI.Set interface state | ${node} | ${interface} | ${state}
| | ... | if_type=name

| Honeycomb sets interface state
| | [Documentation] | Uses Honeycomb API to change the admin state\
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - state - state to set on interface. Type:string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb sets interface state \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| up \|
| | [Arguments] | ${node} | ${interface} | ${state}
| | interfaceAPI.Set interface state | ${node} | ${interface} | ${state}

| Interface state from Honeycomb should be
| | [Documentation] | Retrieves interface admin state through Honeycomb and\
| | ... | compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - state - expected interface state. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface state from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| up \|
| | [Arguments] | ${node} | ${interface} | ${state}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${api_state}= | Set Variable | ${api_data['admin-status']}
| | Should be equal | ${api_state} | ${state}

| Interface state from VAT should be
| | [Documentation] | Retrieves interface admin state through VAT and compares\
| | ... | with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - state - expected interface state. Type: string
| | ...
| | ... | _NOTE:_ Vat returns state as int (1/0) instead of string (up/down).
| | ... | This keyword also handles translation.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface state from VAT should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| up \|
| | [Arguments] | ${node} | ${interface} | ${state}
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | ${vat_state}= | Set Variable if
| | ... | ${vat_data['admin_up_down']} == 1 | up | down
| | Should be equal | ${vat_state} | ${state}

| Honeycomb sets interface ipv4 address
| | [Documentation] | Uses Honeycomb API to change ipv4 address\
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to set. Type: string
| | ... | - netmask - subnet mask to set. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb sets interface ipv4 address \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.2 \| 255.255.255.0 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${netmask}
| | interfaceAPI.Add first ipv4 address
| | ... | ${node} | ${interface} | ${address} | ${netmask}

| Honeycomb sets interface ipv4 address with prefix
| | [Documentation] | Uses Honeycomb API to assign an ipv4 address to the\
| | ... | specified interface. Any existing addresses will be removed.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to set. Type: string
| | ... | - prefix - length of address network prefix. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb sets interface ipv4 address with prefix \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 192.168.0.2 \| 24 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | interfaceAPI.Add first ipv4 address
| | ... | ${node} | ${interface} | ${address} | ${prefix}

| IPv4 address from Honeycomb should be
| | [Documentation] | Retrieves interface ipv4 address through Honeycomb\
| | ... | and compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to expect. Type: string
| | ... | - prefix - prefix length to expect. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 address from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.2 \| 255.255.255.0 \
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be equal | ${address}
| | ... | ${api_data['ietf-ip:ipv4']['address'][0]['ip']}
| | Should be equal | ${prefix}
| | ... | ${api_data['ietf-ip:ipv4']['address'][0]['prefix-length']}

| IPv4 address from VAT should be
| | [Documentation] | Retrieves interface ipv4 address through VAT and\
| | ... | compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to expect. Type: string
| | ... | - netmask - subnet mask to expect. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 address from VAT should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.2 \| 255.255.255.0 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${netmask}
| | ${vpp_data}= | interfaceCLI.VPP get interface ip addresses
| | ... | ${node} | ${interface} | ipv4
| | Should be equal | ${vpp_data[0]['ip']} | ${address}
| | Should be equal | ${vpp_data[0]['netmask']} | ${netmask}

| Honeycomb removes interface ipv4 addresses
| | [Documentation] | Removes all configured ipv4 addresses from the specified\
| | ... | interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes interface ipv4 addresses \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Remove all ipv4 addresses | ${node} | ${interface}

| IPv4 address from Honeycomb should be empty
| | [Documentation] | Retrieves interface ipv4 configuration through Honeycomb\
| | ... | and expects to find no IPv4 addresses.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 address from Honeycomb should be empty\| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Run keyword and expect error | *KeyError: 'ietf-ip:ipv4'
| | ... | Set Variable | ${api_data['ietf-ip:ipv4']['address']}

| IPv4 address from VAT should be empty
| | [Documentation] | Retrieves interface ipv4 configuration through VAT and\
| | ... | and expects to find no ipv4 addresses.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 config from VAT should be empty \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Run keyword and expect error | *No JSON object could be decoded*
| | ... | InterfaceCLI.VPP get interface ip addresses
| | ... | ${node} | ${interface} | ipv4

| Honeycomb adds interface ipv4 neighbor
| | [Documentation] | Uses Honeycomb API to assign an ipv4 neighbor to the\
| | ... | specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - fib_address - IP address to add to fib table. Type: string
| | ... | - fib_mac - MAC address to add to fib table. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds interface ipv4 neighbor \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.3 \| 08:00:27:c0:5d:37 \
| | [Arguments] | ${node} | ${interface} | ${fib_address} | ${fib_mac}
| | interfaceAPI.Add ipv4 neighbor
| | ... | ${node} | ${interface} | ${fib_address} | ${fib_mac}

| IPv4 neighbor from Honeycomb should be
| | [Documentation] | Retrieves ipv4 neighbor list through Honeycomb\
| | and compares with neighbor list supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - neighbors - list of ipv4 neighbor dictionaries. Type: list
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 neighbor from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.4 \| 08:00:27:60:26:ab \|
| | [Arguments] | ${node} | ${interface} | @{neighbors}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${data_neighbors}= | Set Variable | ${api_data['ietf-ip:ipv4']['neighbor']}
| | Compare data structures
| | ... | ${data_neighbors} | ${neighbors} | list_order=${False}
| | Should be equal | ${neighbor['fib_address']}
| | ... | ${api_data['ietf-ip:ipv4']['neighbor'][0]['ip']}
| | Should be equal | ${neighbor['fib_mac']}
| | ... | ${api_data['ietf-ip:ipv4']['neighbor'][0]['link-layer-address']}

| Honeycomb clears all interface ipv4 neighbors
| | [Documentation] | Uses Honeycomb API to assign an ipv4 neighbor to the\
| | ... | specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb clears all interface ipv4 neighbors \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | interfaceAPI.clear all ipv4 neighbors | ${node} | ${interface}

| Honeycomb sets interface ipv6 address
| | [Documentation] | Uses Honeycomb API to change ipv6 address\
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to set. Type: string
| | ... | - prefix - length of subnet prefix to set. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb sets interface ipv6 address \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 10::10 \| 64 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | interfaceAPI.Add first ipv6 address
| | ... | ${node} | ${interface} | ${address} | ${prefix}

| IPv6 address from Honeycomb should be
| | [Documentation] | Retrieves interface ipv6 address through Honeycomb\
| | ... | and compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to expect. Type: string
| | ... | - prefix - length of subnet prefix to expect. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv6 address from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 10::10 \| 64 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be equal | ${address}
| | ... | ${api_data['ietf-ip:ipv6']['address'][0]['ip']}
| | Should be equal | ${prefix}
| | ... | ${api_data['ietf-ip:ipv6']['address'][0]['prefix-length']}
| | Should be equal | ${fib_address}

| IPv6 address from VAT should be
| | [Documentation] | Retrieves interface ipv6 address through VAT and\
| | ... | compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to expect. Type: string
| | ... | - prefix - length of subnet prefix to expect. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv6 address from VAT should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 10::10 \| 64 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | ${vpp_data}= | interfaceCLI.VPP get interface ip addresses
| | ... | ${node} | ${interface} | ipv6
| | Should be equal | ${vpp_data[0]['ip']} | ${address}
| | Should be equal | ${vpp_data[0]['prefix-length']} | ${prefix}

| Honeycomb sets interface ethernet and routing configuration
| | [Documentation] | Uses Honeycomb API to change interface configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - ethernet - interface ethernet settings. Type: dictionary
| | ... | - routing - interface routing settings. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb sets interface ethernet and routing configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${{'mtu': 1500}} \
| | ... | \| ${{'vrf-if': 2}} \|
| | [Arguments] | ${node} | ${interface} | ${ethernet} | ${routing}
| | :FOR | ${key} | IN | @{ethernet.keys()}
| | | interfaceAPI.Configure interface ethernet
| | | ... | ${node} | ${interface} | ${key} | ${ethernet['${key}']}
| | :FOR | ${key} | IN | @{routing.keys()}
| | | interfaceAPI.Configure interface routing
| | | ... | ${node} | ${interface} | ${key} | ${routing['${key}']}

| Interface ethernet and routing configuration from Honeycomb should be
| | [Documentation] | Retrieves interface routing and ethernet configuration\
| | ... | through Honeycomb and compares with settings supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - ethernet - interface ethernet settings. Type: dictionary
| | ... | - routing - interface routing settings. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ethernet and routing configuration from Honeycomb \
| | ... | should be \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \
| | ... | \| ${{'mtu': 1500}} \| ${{'vrf-id': 2}} \|
| | [Arguments] | ${node} | ${interface} | ${ethernet} | ${routing}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | :FOR | ${key} | IN | @{ethernet.keys()}
| | | Should be equal
| | | ... | ${api_data['v3po:ethernet']['${key}']} | ${ethernet['${key}']}
| | :FOR | ${key} | IN | @{routing.keys()}
| | | Should be equal | ${api_data['${key}']} | ${routing['${key}']}

| Interface ethernet and routing configuration from VAT should be
| | [Documentation] | Retrieves interface routing and ethernet configuration\
| | ... | through VAT and compares with settings supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - mtu - value of maximum transmission unit expected. Type: integer
| | ... | - vrf-id - ID number of a VPN expected on interface. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ethernet and routing configuration from VAT \
| | ... | should be \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1500} \
| | ... | \| ${2} \|
| | [Arguments] | ${node} | ${interface} | ${mtu} | ${vrf-id}
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | Should be equal | ${vat_data['mtu']} | ${mtu}

| Interface configuration from Honeycomb should be empty
| | [Documentation] | Attempts to retrieve interface configuration through\
| | ... | Honeycomb and expects to get empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of a interface on the specified node. Type:\
| | ... | string
| | ...
| | ... | *Example:*
| | ... | \| Interface configuration from Honeycomb should be empty\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be empty | ${api_data}

| Interface configuration from VAT should be empty
| | [Documentation] | Attempts to retrieve Interface configuration through\
| | ... | VAT and expects to get empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of a Interface on the specified node. Type:\
| | ... | string
| | ...
| | ... | *Example:*
| | ... | \| Interface configuration from VAT should be empty\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface} |
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | Should be empty | ${vat_data}

| Interface indices from Honeycomb and VAT should correspond
| | [Documentation] | Uses VAT and Honeycomb to get operational data about the\
| | ... | given interface and compares the interface indexes. The interface
| | ... | index from Honeycomb should be greater than index from VAT by one.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of the interface to be checked. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface indices from Honeycomb and VAT should correspond \
| | ... | \| ${nodes['DUT1']} \| vxlan_gpe_tunnel0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ...
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | ${sw_if_index}= | EVALUATE | ${vat_data['sw_if_index']} + 1
| | Should be equal as strings
| | ... | ${api_data['if-index']} | ${sw_if_index}
