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

*** Variables ***
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}
# Configuration which will be set and verified during tests.
| ${ipv4_address}= | 192.168.0.2
| ${ipv4_address2}= | 192.168.0.3
| ${ipv4_mask}= | 255.255.255.0
| ${ipv4_prefix}= | ${24}
| @{ipv4_neighbor}= | 192.168.0.4 | 08:00:27:c0:5d:37
| &{ipv4_settings}= | enabled=${True} | forwarding=${True} | mtu=${9000}
| @{ipv6_address}= | 10::10 | ${64}
| @{ipv6_neighbor}= | 10::11 | 08:00:27:c0:5d:37
| &{ipv6_settings}= | enabled=${True} | forwarding=${True} | mtu=${9000}
| ... | dup-addr-detect-transmits=${5}
| &{ethernet}= | mtu=${9000}
| &{routing}= | vrf-id=${27}
| &{vxlan_settings}= | src=10.0.1.20 | dst=10.0.3.20 | vni=${1000}
| ... | encap-vrf-id=${1000}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Force Tags | honeycomb_sanity
| Documentation | *Honeycomb interface management test suite.*
| ...
| ... | Test suite uses the first interface of the first DUT node.

*** Test Cases ***
| Honeycomb configures and reads interface state
| | [Documentation] | Check if Honeycomb API can modify the admin state of\
| | ... | VPP interfaces.
| | Given Interface state is | ${node} | ${interface} | down
| | When Honeycomb sets interface state | ${node} | ${interface} | up
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | up
| | And Interface state from VAT should be | ${node} | ${interface} | up
| | When Honeycomb sets interface state | ${node} | ${interface} | down
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And Interface state from VAT should be | ${node} | ${interface} | down

| Honeycomb modifies interface configuration - ipv4 (netmask)
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv4\
| | ... | with address and netmask provided.
| | When Honeycomb sets interface ipv4 address | ${node} | ${interface}
| | ... | ${ipv4_address} | ${ipv4_mask} | ${ipv4_settings}
| | And Honeycomb adds interface ipv4 neighbor
| | ... | ${node} | ${interface} | @{ipv4_neighbor}
| | Then IPv4 config from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | ... | @{ipv4_neighbor} | ${ipv4_settings}
| | And IPv4 config from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}

| Honeycomb removes ipv4 address from interface
| | [Documentation] | Check if Honeycomb API can remove configured ipv4\
| | ... | addresses from interface.
| | Given IPv4 config from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | ... | @{ipv4_neighbor} | ${ipv4_settings}
| | And IPv4 config from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | When Honeycomb removes interface ipv4 addresses | ${node} | ${interface}
| | Then IPv4 address from Honeycomb should be empty | ${node} |${interface}
| | And ipv4 address from VAT should be empty | ${node} | ${interface}

| Honeycomb modifies interface configuration - ipv4 (prefix)
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv4\
| | ... | with address and prefix provided.
| | [Teardown] | Honeycomb removes interface ipv4 addresses | ${node}
| | ... | ${interface}
| | When Honeycomb sets interface ipv4 address with prefix
| | ... | ${node} | ${interface} | ${ipv4_address2} | ${ipv4_prefix}
| | ... | ${ipv4_settings}
| | And Honeycomb adds interface ipv4 neighbor
| | ... | ${node} | ${interface} | @{ipv4_neighbor}
| | Then IPv4 config from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address2} | ${ipv4_prefix}
| | ... | @{ipv4_neighbor}
| | ... | ${ipv4_settings}
| | And IPv4 config from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address2} | ${ipv4_prefix}

| Honeycomb modifies interface configuration - ipv6
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv6.
| | When Honeycomb sets interface ipv6 configuration
| | ... | ${node} | ${interface} | @{ipv6_address} | @{ipv6_neighbor}
| | ... | ${ipv6_settings}
| | Then IPv6 config from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv6_address} | @{ipv6_neighbor}
| | ... | ${ipv6_settings}
| | And IPv6 config from VAT should be
| | ... | ${node} | ${interface} | @{ipv6_address}

| Honeycomb modifies interface configuration - ethernet,routing
| | [Documentation] | Check if Honeycomb API can configure interface ethernet\
| | ... | and routing settings.
| | When Honeycomb sets interface ethernet and routing configuration
| | ... | ${node} | ${interface} | ${ethernet} | ${routing}
| | Then Interface ethernet and routing configuration from Honeycomb should be
| | ... | ${node} | ${interface} | ${ethernet} | ${routing}
| | And Interface ethernet and routing configuration from VAT should be
| | ... | ${node} | ${interface} | ${ethernet['mtu']} | ${routing['vrf-id']}
