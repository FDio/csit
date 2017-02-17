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
| Library | resources.libraries.python.IPv4Util
| Library | resources.libraries.python.TrafficScriptExecutor

*** Keywords ***
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
| | ... | of the specified interface. Any existing addresses will be removed.
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
| | ... | - prefix - length of address network prefix. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb sets interface ipv4 address with prefix \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 192.168.0.2 \| 24 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | interfaceAPI.Add first ipv4 address
| | ... | ${node} | ${interface} | ${address} | ${prefix}

| Honeycomb adds interface ipv4 address
| | [Documentation] | Uses Honeycomb API to add an ipv4 address to the\
| | ... | specified interface, without removing existing addresses.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to set. Type: string
| | ... | - prefix - length of address network prefix. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds interface ipv4 address \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 192.168.0.2 \| 24 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | interfaceAPI.Add ipv4 address
| | ... | ${node} | ${interface} | ${address} | ${prefix}

| Honeycomb fails to add interface ipv4 address
| | [Documentation] | Uses Honeycomb API to add an ipv4 address to the\
| | ... | specified interface, and expects to fail with code 500.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to set. Type: string
| | ... | - prefix - length of address network prefix. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb fails to add interface ipv4 address \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 192.168.0.2 \| 24 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | Run Keyword and Expect Error | *not successful. Status code: 500.
| | ... | Honeycomb adds interface ipv4 address
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
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.2 \| ${24} \
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${settings}= | Create Dictionary
| | ... | ip=${address} | prefix-length=${prefix}
| | Should contain | ${api_data['ietf-ip:ipv4']['address']} | ${settings}

| IPv4 address from VAT should be
| | [Documentation] | Retrieves interface ipv4 address through VAT and\
| | ... | compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to expect. Type: string
| | ... | - prefix - prefix length to expect. Type: string
| | ... | - netmask - subnet mask to expect. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 address from VAT should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.2 \| ${24} \| 255.255.255.0 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix} | ${netmask}
| | ${vpp_data}= | interfaceCLI.VPP get interface ip addresses
| | ... | ${node} | ${interface} | ipv4
| | ${settings}= | Create Dictionary
| | ... | ip=${address} | netmask=${netmask} | prefix_length=${prefix}
| | Should contain | ${vpp_data} | ${settings}

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
| | Run keyword and expect error | *KeyError:*
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
| | ... | and checks if it contains address supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - ip_address - ipv4 address of expected neighbor entry. Type: string
| | ... | - mac_address - MAC address of expected neighbor entry. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 neighbor from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.4 \| 08:00:27:60:26:ab \|
| | [Arguments] | ${node} | ${interface} | ${ip_address} | ${mac_address}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${settings}= | Create Dictionary
| | ... | ip=${ip_address} | link-layer-address=${mac_address} | origin=static
| | Should contain | ${api_data['ietf-ip:ipv4']['neighbor']} | ${settings}

| Honeycomb clears all interface ipv4 neighbors
| | [Documentation] | Uses Honeycomb API to remove all ipv4 neighbors from the\
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
| | interfaceAPI.Remove all ipv4 neighbors | ${node} | ${interface}

| IPv4 neighbor from Honeycomb should be empty
| | [Documentation] | Retrieves ipv4 neighbor list through Honeycomb\
| | ... | and expects to find no ipv4 neighbors.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 neighbor from Honeycomb should be empty \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Run keyword and expect error | *KeyError:*
| | ... | Set Variable | ${api_data['ietf-ip:ipv4']['neighbor'][0]['ip']}

| Honeycomb sets interface ipv6 address
| | [Documentation] | Uses Honeycomb API to change ipv6 address\
| | ... | of the specified interface. Existing IPv6 addresses will be removed,\
| | ... | with the exception of self-configured link-layer IPv6.
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

| Honeycomb adds interface ipv6 address
| | [Documentation] | Uses Honeycomb API to add an ipv6 address\
| | ... | to the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to set. Type: string
| | ... | - prefix - length of subnet prefix to set. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds interface ipv6 address \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 10::10 \| 64 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | interfaceAPI.Add ipv6 address
| | ... | ${node} | ${interface} | ${address} | ${prefix}

| Honeycomb fails to add interface ipv6 address
| | [Documentation] | Uses Honeycomb API to add an ipv6 address to the\
| | ... | specified interface, and expects to fail with code 500.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - address - IP address to set. Type: string
| | ... | - prefix - length of address network prefix. Type:integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb fails to add interface ipv6 address \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 10::10 \| 64 \|
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | Run Keyword and Expect Error | *not successful. Status code: 500.
| | ... | Honeycomb adds interface ipv6 address
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
| | ${settings}= | Create Dictionary
| | ... | ip=${address} | prefix-length=${prefix}
| | Should contain | ${api_data['ietf-ip:ipv6']['address']} | ${settings}

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
| | ${settings}= | Create Dictionary
| | ... | ip=${address} | prefix_length=${prefix}
| | Should contain | ${vpp_data} | ${settings}

| Honeycomb removes interface ipv6 addresses
| | [Documentation] | Removes all configured ipv6 addresses from the specified\
| | ... | interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes interface ipv6 addresses \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Remove all ipv6 addresses | ${node} | ${interface}

| IPv6 address from Honeycomb should be empty
| | [Documentation] | Retrieves interface ipv6 configuration through Honeycomb\
| | ... | and expects to find no IPv6 addresses.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv6 address from Honeycomb should be empty\| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Run keyword and expect error | *KeyError:*
| | ... | Set Variable | ${api_data['ietf-ip:ipv6']['address']}

| IPv6 address from VAT should be empty
| | [Documentation] | Retrieves interface ipv6 configuration through VAT and\
| | ... | and expects to find no ipv6 addresses.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv6 config from VAT should be empty \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Run keyword and expect error | *No JSON object could be decoded*
| | ... | InterfaceCLI.VPP get interface ip addresses
| | ... | ${node} | ${interface} | ipv6

| Honeycomb adds interface ipv6 neighbor
| | [Documentation] | Uses Honeycomb API to assign an ipv6 neighbor to the\
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
| | ... | \| Honeycomb adds interface ipv6 neighbor \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.3 \| 08:00:27:c0:5d:37 \|
| | [Arguments] | ${node} | ${interface} | ${fib_address} | ${fib_mac}
| | InterfaceAPI.Add ipv6 neighbor
| | ... | ${node} | ${interface} | ${fib_address} | ${fib_mac}

| IPv6 neighbor from Honeycomb should be
| | [Documentation] | Retrieves ipv6 neighbor list through Honeycomb\
| | ... | and checks if it contains address supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - ip_address - ipv6 address of expected neighbor entry. Type: string
| | ... | - mac_address - MAC address of expected neighbor entry. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv6 neighbor from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 192.168.0.4 \| 08:00:27:60:26:ab \|
| | [Arguments] | ${node} | ${interface} | ${ip_address} | ${mac_address}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${settings}= | Create Dictionary
| | ... | ip=${ip_address} | link-layer-address=${mac_address} | origin=static
| | Should contain | ${api_data['ietf-ip:ipv6']['neighbor']} | ${settings}

| Honeycomb clears all interface ipv6 neighbors
| | [Documentation] | Uses Honeycomb API to remove all ipv6 neighbors from the\
| | ... | specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb clears all interface ipv6 neighbors \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | interfaceAPI.Remove all ipv6 neighbors | ${node} | ${interface}

| IPv6 neighbor from Honeycomb should be empty
| | [Documentation] | Retrieves ipv6 neighbor list through Honeycomb\
| | ... | and expects to find no ipv6 neighbors.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv6 neighbor from Honeycomb should be empty \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Run keyword and expect error | *KeyError:*
| | ... | Set Variable | ${api_data['ietf-ip:ipv6']['neighbor'][0]['ip']}

| Honeycomb sets interface ethernet configuration
| | [Documentation] | Uses Honeycomb API to change interface ethernet\
| | ... | configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - ethernet - interface ethernet settings. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb sets interface ethernet configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${{'mtu': 1500}} \
| | [Arguments] | ${node} | ${interface} | ${ethernet}
| | :FOR | ${key} | IN | @{ethernet.keys()}
| | | interfaceAPI.Configure interface ethernet
| | | ... | ${node} | ${interface} | ${key} | ${ethernet['${key}']}

| Interface ethernet configuration from Honeycomb should be
| | [Documentation] | Retrieves interface ethernet configuration\
| | ... | through Honeycomb and compares with settings supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - ethernet - interface ethernet settings. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ethernet configuration from Honeycomb should be \
| | ... | should be \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \
| | ... | \| ${{'mtu': 1500}} \|
| | [Arguments] | ${node} | ${interface} | ${ethernet}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | :FOR | ${key} | IN | @{ethernet.keys()}
| | | Should be equal
| | | ... | ${api_data['v3po:ethernet']['${key}']} | ${ethernet['${key}']}

| Interface ethernet configuration from VAT should be
| | [Documentation] | Retrieves interface ethernet configuration\
| | ... | through VAT and compares with settings supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - mtu - value of maximum transmission unit expected. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ethernet configuration from VAT should be \
| | ... | should be \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1500} \|
| | [Arguments] | ${node} | ${interface} | ${mtu}
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | Should be equal | ${vat_data['mtu']} | ${mtu}

| Honeycomb sets interface vrf ID
| | [Documentation] | Uses Honeycomb API to change interface vrf\
| | ... | configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - vrf_id - vrf ID to configure. Type:integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb sets interface vrf ID \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1} \| ipv4 \|
| | [Arguments] | ${node} | ${interface} | ${vrf_id} | ${ip_version}
| | interfaceAPI.Configure interface routing
| | ... | ${node} | ${interface} | ${ip_version}-vrf-id | ${vrf_id}

| Interface vrf ID from Honeycomb should be
| | [Documentation] | Retrieves interface ethernet configuration\
| | ... | through Honeycomb and compares with settings supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - vrf_id - vrf ID to expect. Type:integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface vrf ID from Honeycomb should be \
| | ... | should be \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1} \
| | ... | \| ipv4 \|
| | [Arguments] | ${node} | ${interface} | ${vrf_id} | ${ip_version}
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface} |
| | Should be equal
| | ... | ${api_data['v3po:routing']['${ip_version}-vrf-id']} | ${vrf_id}

| Interface vrf ID from VAT should be
| | [Documentation] | Retrieves interface ethernet configuration\
| | ... | through VAT and compares with settings supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - vrf_id - vrf ID to expect. Type:integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface vrf ID from VAT should be \
| | ... | should be \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| ${1} \|
| | [Arguments] | ${node} | ${interface} | ${vrf_id}
| | ${vat_data}= | InterfaceCLI.get interface vrf table
| | ... | ${node} | ${interface}
| | Should be equal | ${vat_data} | ${vrf_id}

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

| Get Interface index from oper data
| | [Documentation] | Retrieves interface operational data and returns\
| | ... | if-index of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of the interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get Interface index from oper data \| ${nodes['DUT1']} \| local0 \|
| | [Arguments] | ${node} | ${interface}
| | ${data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Return from keyword | ${data['if-index']}

| Honeycomb should show disabled interface in oper data
| | [Documentation] | Retrieves list of disabled interfaces\
| | ... | and verifies that there is at least one.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - index - index of the interface to be checked. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb should show disabled interface in oper data \
| | ... | \|${nodes['DUT1']} \| ${vx_interface} \|
| | [Arguments] | ${node} | ${index}
| | interfaceAPI.check disabled interface | ${node} | ${index}

| Honeycomb should not show disabled interface in oper data
| | [Documentation] | Retrieves list of disabled interfaces\
| | ... | and expects to fail with a 404 - not found.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - index - index of the interface to be checked. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb should not show disabled interface in oper data \
| | ... | \|${nodes['DUT1']} \| ${vx_interface} \|
| | [Arguments] | ${node} | ${index}
| | Run keyword and expect error | *
| | ... | Honeycomb should show disabled interface in oper data
| | ... | ${node} | ${index}

| Ping verify IP address
| | [Documentation] | Sends ICMP packet from IP (with source mac) to IP
| | ... | (with dest mac), then waits for ICMP reply.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ... | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: integer
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: integer
| | ... | - tx_port - Source interface (TG-if1). Type: string
| | ... | - tx_mac - MAC address of source interface (TG-if1). Type: string
| | ... | - rx_port - Destionation interface (TG-if1). Type: string
| | ... | - rx_mac - MAC address of destination interface (TG-if1). Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Ping verify IP address \| ${nodes['TG']} \
| | ... | \| 16.0.0.1 \| 32.0.0.1 \| eth2 \| 08:00:27:cc:4f:54 \
| | ... | \| eth4 \| 08:00:27:c9:6a:d5 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_port} |
| | ... | ${tx_mac} | ${rx_port} | ${rx_mac}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --src_mac | ${tx_mac}
| | ...                 | --dst_mac | ${rx_mac}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --dst_ip | ${dst_ip}
| | ...                 | --tx_if | ${tx_port_name}
| | ...                 | --rx_if | ${rx_port_name}
| | ...                 | --timeout | ${5}
| | Run Traffic Script On Node | send_icmp_wait_for_reply.py
| | ... | ${tg_node} | ${args}
