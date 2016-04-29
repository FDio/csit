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
| Library | resources/libraries/python/HoneycombUtil.py
| Library | resources.libraries.python.InterfaceUtil
| ... | WITH NAME | interfaceCLI
| Library | resources.libraries.python.HcAPIKwInterfaces.InterfaceKeywords
| ... | WITH NAME | InterfaceAPI

*** Keywords ***
| Interface state is
| | [Arguments] | ${node} | ${interface} | ${state}
| | [Documentation] | Uses VPP binary API to ensure that the interface under\
| | ... | test is in the specified admin state.
| | ...
| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | interfaceCLI.Set interface state | ${node} | ${interface} | ${state}

| Honeycomb sets interface state
| | [Arguments] | ${node} | ${interface} | ${state}
| | [Documentation] | Uses Honeycomb API to change the admin state\
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - state - state to set on interface
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | interfaceAPI.Set interface state | ${node} | ${interface} | ${state}

| Interface state from Honeycomb should be
| | [Arguments] | ${node} | ${interface} | ${state}
| | [Documentation] | Retrieves interface admin state through Honeycomb and\
| | ... | compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - state - expected interface state
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | ${api_state}= | Set Variable | ${api_data['admin-status']}
| | Should be equal | ${api_state} | ${state}

| Interface state from VAT should be
| | [Arguments] | ${node} | ${interface} | ${state}
| | [Documentation] | Retrieves interface admin state through VAT and compares\
| | ... | with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - state - expected interface state
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | ... | _NOTE:_ Vat returns state as int (1/0) instead of string (up/down).
| | ... | This keyword also handles translation.
| | ...
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | ${vat_state}= | Set Variable if
| | ... | ${vat_data['admin_up_down']} == 1 | up | down
| | Should be equal | ${vat_state} | ${state}

| Honeycomb sets interface ipv4 configuration
| | [Arguments] | ${node} | ${interface} | ${address} | ${netmask} | ${fib_address} | ${fib_mac} | ${settings}
| | [Documentation] | Uses Honeycomb API to change ipv4 configuration\
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - address - IP address to set
| | ... | - netmask - subnet mask to set
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ... | - enabled - whether to enable or disable ipv4 for this interface
| | ...
| | interfaceAPI.Add first ipv4 address
| | ... | ${node} | ${interface} | ${address} | ${netmask}
| | interfaceAPI.Add first ipv4 neighbor
| | ... | ${node} | ${interface} | ${fib_address} | ${fib_mac}
| | :FOR | ${key} | IN | @{settings.keys()}
| | | interfaceAPI.Configure interface ipv4
| | | ... | ${node} | ${interface} | ${key} | ${settings['${key}']}

| IPv4 config from Honeycomb should be
| | [Arguments] | ${node} | ${interface} | ${address} | ${netmask} | ${fib_address} | ${fib_mac} | ${settings}
| | [Documentation] | Retrieves interface ipv4 configuration through Honeycomb\
| | ... | and compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - address - expected IP address
| | ... | - netmask - expected subnet mask
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ... | - enabled - whether ipv4 should be enabled or disabled
| | ...
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be equal | ${address} | ${api_data['ietf-ip:ipv4']['address'][0]['ip']}
| | Should be equal | ${netmask} | ${api_data['ietf-ip:ipv4']['address'][0]['netmask']}
| | :FOR | ${key} | IN | @{settings.keys()}
| | | Should be equal | ${settings['{key']} | ${api_data['ietf-ip:ipv4']['{$key}']}

| IPv4 config from VAT should be
| | [Arguments] | ${node} | ${interface} | ${address} | ${netmask}
| | [Documentation] | Retrieves interface ipv4 configuration through VAT and\
| | ... | compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - address - expected IP address
| | ... | - netmask - expected subnet mask
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ... | - enabled - whether ipv4 should be enabled or disabled
| | ...
| | ${vpp_data}= | interfaceCLI.VPP get interface ip addresses
| | ... | ${node} | ${interface} | ipv4
| | Should be equal | ${vpp_data[0]['ip']} | ${address}
| | Should be equal | ${vpp_data[0]['netmask']} | ${netmask}

| Honeycomb sets interface ipv6 configuration
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix} | ${fib_address} | ${fib_mac} | ${settings}
| | [Documentation] | Uses Honeycomb API to change ipv6 configuration\
| | ... | of the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - address - IP address to set
| | ... | - netmask - subnet mask to set
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | interfaceAPI.Add first ipv6 address
| | ... | ${node} | ${interface} | ${address} | ${prefix}
| | interfaceAPI.Add first ipv6 neighbor
| | ... | ${node} | ${interface} | ${fib_address} | ${fib_mac}
| | :FOR | ${key} | IN | @{settings.keys()}
| | | interfaceAPI.Configure interface ipv6
| | | ... | ${node} | ${interface} | ${key} | ${settings['${key}']}

| IPv6 config from Honeycomb should be
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix} | ${fib_address} | ${fib_mac} | ${settings}
| | [Documentation] | Retrieves interface ipv6 configuration through Honeycomb\
| | ... | and compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - address - expected IP address
| | ... | - netmask - expected subnet mask
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be equal | ${address} | ${api_data['ietf-ip:ipv6']['address'][0]['ip']}
| | Should be equal | ${prefix} | ${api_data['ietf-ip:ipv6']['address'][0]['netmask']}
| | :FOR | ${key} | IN | @{settings.keys()}
| | | Should be equal | ${settings['{key']} | ${api_data['ietf-ip:ipv6']['{$key}']}

| IPv6 config from VAT should be
| | [Arguments] | ${node} | ${interface} | ${address} | ${prefix}
| | [Documentation] | Retrieves interface ipv6 configuration through VAT and\
| | ... | compares with state supplied in argument.
| | ...
| | ... | *Arguments:*
| | ... | - address - expected IP address
| | ... | - prefix - length of subnet prefix
| | ... | - node - dictionary of information about a DUT node
| | ... | - interface - name of an interface on the specified node
| | ...
| | ${vpp_data}= | interfaceCLI.VPP get interface ip addresses
| | ... | ${node} | ${interface} | ipv6
| | Should be equal | ${vpp_data[0]['ip']} | ${address}
| | Should be equal | ${vpp_data[0]['prefix-length']} | ${prefix}

| Honeycomb sets interface ethernet and routing configuration
| | [Arguments] | ${node} | ${interface} | ${ethernet} | ${routing}
| | [Documentation] | Uses Honeycomb API to change interface configuration.
| | ...
| | ... | *Arguments:*
| | ... | - address - IP address to set
| | ... | - netmask - subnet mask to set
| | ... | - mtu - value of maximum transmission unit to set on interface
| | ... | - vrf-id - ID number of a VPN to set on interface
| | ...
| | interfaceAPI.Configure interface ethernet
| | ... | ${node} | ${interface} | mtu | ${ethernet}
| | interfaceAPI.Configure interface routing
| | ... | ${node} | ${interface} | vrf-id | ${routing}

| Interface ethernet and routing configuration from Honeycomb should be
| | [Arguments] | ${node} | ${interface} | ${ethernet} | ${routing}
| | [Documentation] | Retrieves interface routing and ethernet configuration\
| | ... | through Honeycomb and compares with settings supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - address - expected IP address
| | ... | - netmask - expected subnet mask
| | ... | - mtu - value of maximum transmission unit expected on interface
| | ... | - vrf-id - ID number of a VPN expected on interface
| | ...
| | ${api_data}= | interfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be equal | ${api_data['mtu']} | ${ethernet}
| | Should be equal | ${api_data['vrf-id']} | ${routing}

| Interface ethernet and routing configuration from VAT should be
| | [Arguments] | ${node} | ${interface} | ${ethernet} | ${routing}
| | [Documentation] | Retrieves interface routing and ethernet configuration\
| | ... | through VAT and compares with settings supplied in arguments.
| | ...
| | ... | *Arguments:*
| | ... | - address - expected IP address
| | ... | - netmask - expected subnet mask
| | ... | - mtu - value of maximum transmission unit expected on interface
| | ... | - vrf-id - ID number of a VPN expected on interface
| | ...
| | ${vat_data}= | InterfaceCLI.VPP get interface data | ${node} | ${interface}
| | Should be equal | ${vat_data['mtu']} | ${ethernet}
| | Should be equal | ${vat_data['sub_inner_vlan_id']} | ${routing}