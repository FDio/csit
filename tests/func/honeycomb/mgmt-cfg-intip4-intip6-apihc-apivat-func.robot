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
| &{ipv4_settings}= | mtu=${9000}
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
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Force Tags | honeycomb_sanity
| Suite Teardown | Run Keyword If Any Tests Failed
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Documentation | *Honeycomb interface management test suite.*
| ...
| ... | Test suite uses the first interface of the first DUT node.

*** Test Cases ***
| TC01: Honeycomb configures and reads interface state
| | [Documentation] | Check if Honeycomb API can modify the admin state of\
| | ... | VPP interfaces.
| | Given Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And Interface state from VAT should be | ${node} | ${interface} | down
| | When Honeycomb sets interface state | ${node} | ${interface} | up
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | up
| | And Interface state from VAT should be | ${node} | ${interface} | up
| | When Honeycomb sets interface state | ${node} | ${interface} | down
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And Interface state from VAT should be | ${node} | ${interface} | down

| TC02: Honeycomb modifies interface IPv4 address with netmask
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv4\
| | ... | with address and netmask provided.
| | Given IPv4 address from Honeycomb should be empty | ${node} | ${interface}
| | And ipv4 address from VAT should be empty | ${node} | ${interface}
| | When Honeycomb sets interface ipv4 address | ${node} | ${interface}
| | ... | ${ipv4_address} | ${ipv4_mask}
| | Then IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_mask}

| TC03: Honeycomb removes IPv4 address from interface
| | [Documentation] | Check if Honeycomb API can remove configured ipv4\
| | ... | addresses from interface.
| | Given IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_mask}
| | When Honeycomb removes interface ipv4 addresses | ${node} | ${interface}
| | Then IPv4 address from Honeycomb should be empty | ${node} | ${interface}
| | And ipv4 address from VAT should be empty | ${node} | ${interface}

| TC04: Honeycomb modifies interface IPv4 address with prefix
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv4\
| | ... | with address and prefix provided.
| | [Teardown] | Honeycomb removes interface ipv4 addresses | ${node}
| | ... | ${interface}
| | Given IPv4 address from Honeycomb should be empty | ${node} | ${interface}
| | And ipv4 address from VAT should be empty | ${node} | ${interface}
| | When Honeycomb sets interface ipv4 address with prefix
| | ... | ${node} | ${interface} | ${ipv4_address2} | ${ipv4_prefix}
| | Then IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address2} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address2} | ${ipv4_mask}

| TC05: Honeycomb modifies IPv4 neighbor table
| | [Documentation] | Check if Honeycomb API can add and remove ARP entries.
# Operational data and VAT dump not available (HONEYCOMB-111)
| | [Tags] | EXPECTED_FAILING
| | [Teardown] | Honeycomb clears all interface ipv4 neighbors
| | ... | ${node} | ${interface}
| | When Honeycomb adds interface ipv4 neighbor
| | ... | ${node} | ${interface} | @{ipv4_neighbor}
| | Then IPv4 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv4_neighbor}

| TC06: Honeycomb modifies interface configuration - IPv6
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv6.
# Configuring IPv6 not implemented (HONEYCOMB-102)
| | [Tags] | EXPECTED_FAILING
| | When Honeycomb sets interface ipv6 address
| | ... | ${node} | ${interface} | @{ipv6_address}
| | Then IPv6 address from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv6_address}
| | And IPv6 address from VAT should be
| | ... | ${node} | ${interface} | @{ipv6_address}

# TODO: Honeycomb modifies IPv6 neighbor table

| TC07: Honeycomb modifies interface configuration - MTU
| | [Documentation] | Check if Honeycomb API can configure interface\
| | ... | MTU value.
# Configuring MTU not implemented (HONEYCOMB-126)
| | [Tags] | EXPECTED_FAILING
| | When Honeycomb sets interface ethernet configuration
| | ... | ${node} | ${interface} | ${ethernet}
| | Then Interface ethernet configuration from Honeycomb should be
| | ... | ${node} | ${interface} | ${ethernet}
| | And Interface ethernet configuration from VAT should be
| | ... | ${node} | ${interface} | ${ethernet['mtu']}

# TODO: Honeycomb configures routing on interface
