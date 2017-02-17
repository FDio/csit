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
| @{ipv4_address}= | 192.168.0.2 | ${24}
| @{ipv4_address2}= | 192.168.1.2 | ${24}
| ${ipv4_mask}= | 255.255.255.0
| ${ipv4_prefix}= | ${24}
| @{ipv4_neighbor}= | 192.168.0.4 | 08:00:27:c0:5d:37
| @{ipv4_neighbor2}= | 192.168.1.4 | 08:00:27:c0:5d:37
| &{ipv4_settings}= | mtu=${9000}
| @{ipv6_address}= | 10::10 | ${64}
| @{ipv6_address2}= | 11::10 | ${64}
| @{ipv6_neighbor}= | 10::11 | 08:00:27:c0:5d:37
| @{ipv6_neighbor2}= | 11::11 | 08:00:27:c0:5d:37
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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv6.robot
| Force Tags | honeycomb_sanity
| Suite Setup | Vpp nodes ra suppress link layer | ${nodes}
| Suite Teardown
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Documentation | *Honeycomb interface management test suite.*

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
| | ... | ${ipv4_address[0]} | ${ipv4_mask}
| | Then IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address[0]} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | @{ipv4_address} | ${ipv4_mask}

| TC03: Honeycomb removes IPv4 address from interface
| | [Documentation] | Check if Honeycomb API can remove configured ipv4\
| | ... | addresses from interface.
| | Given IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv4_address}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | @{ipv4_address} | ${ipv4_mask}
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
| | ... | ${node} | ${interface} | @{ipv4_address2}
| | Then IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv4_address2}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | @{ipv4_address2} | ${ipv4_mask}

| TC05: Honeycomb modifies IPv4 neighbor table
| | [Documentation] | Check if Honeycomb API can add and remove ARP entries.
| | [Teardown] | Honeycomb clears all interface ipv4 neighbors
| | ... | ${node} | ${interface}
| | Given IPv4 neighbor from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | When Honeycomb adds interface ipv4 neighbor
| | ... | ${node} | ${interface} | @{ipv4_neighbor}
| | Then IPv4 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv4_neighbor}

| TC06: Honeycomb modifies interface configuration - IPv6
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv6.
| | [Teardown] | Honeycomb removes interface ipv6 addresses | ${node}
| | ... | ${interface}
| | Given IPv6 address from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | And IPv6 address from VAT should be empty
| | ... | ${node} | ${interface}
| | When Honeycomb sets interface ipv6 address
| | ... | ${node} | ${interface} | @{ipv6_address}
| | Then IPv6 address from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv6_address}
| | And IPv6 address from VAT should be
| | ... | ${node} | ${interface} | @{ipv6_address}

| TC07: Honeycomb modifies IPv6 neighbor table
| | [Documentation] | Check if Honeycomb API can add and remove ARP entries.
| | [Teardown] | Honeycomb clears all interface ipv6 neighbors
| | ... | ${node} | ${interface}
| | Given IPv6 neighbor from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | When Honeycomb adds interface ipv6 neighbor
| | ... | ${node} | ${interface} | @{ipv6_neighbor}
| | Then IPv6 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv6_neighbor}

| TC08: Honeycomb modifies interface configuration - MTU
| | [Documentation] | Check if Honeycomb API can configure interface\
| | ... | MTU value.
| | When Honeycomb sets interface ethernet configuration
| | ... | ${node} | ${interface} | ${ethernet}
| | Then Interface ethernet configuration from Honeycomb should be
| | ... | ${node} | ${interface} | ${ethernet}
| | And Interface ethernet configuration from VAT should be
| | ... | ${node} | ${interface} | ${ethernet['mtu']}

| TC09: Honeycomb modifies interface configuration - vrf
| | [Documentation] | Check if Honeycomb API can configure interface\
| | ... | vrf ID.
| | [Teardown] | Honeycomb sets interface vrf ID
| | ... | ${node} | ${interface} | ${0} | ipv4
| | When Honeycomb sets interface vrf ID
| | ... | ${node} | ${interface} | ${1} | ipv4
| | Then Interface vrf ID from Honeycomb should be
| | ... | ${node} | ${interface} | ${1} | ipv4
| | And Interface vrf ID from VAT should be
| | ... | ${node} | ${interface} | ${1}

| TC10: Honeycomb can configure multiple IP addresses on one interface
| | [Documentation] | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-ICMP; Eth-IPv6-ICMPv6
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set two IPv4 addresses\
| | ... | and two IPv6 addresses on first interfaces to TG and add ARP entries\
| | ... | for each address.
| | ... | [Ver] Send ICMP packets from TG to DUT, using different sets\
| | ... | of source and destination IP addresses. Receive an ICMP reply\
| | ... | for every packet sent.
| | When Honeycomb sets interface ipv4 address with prefix
| | ... | ${node} | ${interface} | @{ipv4_address}
| | And Honeycomb adds interface ipv4 address
| | ... | ${node} | ${interface} | @{ipv4_address2}
| | And Honeycomb sets interface ipv6 address
| | ... | ${node} | ${interface} | @{ipv6_address}
| | And Honeycomb adds interface ipv6 address
| | ... | ${node} | ${interface} | @{ipv6_address2}
| | Then IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv4_address}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | @{ipv4_address} | ${ipv4_mask}
| | And IPv6 address from Honeycomb should be
| | ... | ${node} | ${interface} | @{ipv6_address}
| | And IPv6 address from VAT should be
| | ... | ${node} | ${interface} | @{ipv6_address}
| | When Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Honeycomb sets interface state | ${dut_node} | ${interface} | up
| | And Honeycomb adds interface ipv4 neighbor | ${dut_node} | ${interface}
| | ... | @{ipv4_neighbor}
| | And Honeycomb adds interface ipv4 neighbor | ${dut_node} | ${interface}
| | ... | @{ipv4_neighbor2}
| | And Honeycomb adds interface ipv6 neighbor | ${dut_node} | ${interface}
| | ... | @{ipv6_neighbor}
| | And Honeycomb adds interface ipv6 neighbor | ${dut_node} | ${interface}
| | ... | @{ipv6_neighbor2}
| | Then Ping Verify IP address | ${nodes['TG']}
| | ... | ${ipv4_neighbor[0]} | ${ipv4_address[0]}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}
| | And Ping Verify IP address | ${nodes['TG']}
| | ... | ${ipv4_neighbor2[0]} | ${ipv4_address2[0]}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}
| | And Ping Verify IP address | ${nodes['TG']}
| | ... | ${ipv6_neighbor[0]} | ${ipv6_address[0]}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}
| | And Ping Verify IP address | ${nodes['TG']}
| | ... | ${ipv6_neighbor2[0]} | ${ipv6_address2[0]}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}

TC11: Honeycomb fails to configure two IPv4 addresses from the same subnet
| | [Documentation] | Check if Honeycomb can configure two IPv4 addresses in\
| | ... | the same subnet onto a single interface. It should not be possible.
| | [Teardown] | Honeycomb removes interface ipv4 addresses | ${node}
| | ... | ${interface}
| | When Honeycomb sets interface ipv4 address with prefix
| | ... | ${node} | ${interface} | 192.168.0.1 | ${9}
| | Then Honeycomb fails to add interface ipv4 address
| | ... | ${node} | ${interface} | 192.168.0.2 | ${9}
| | And Honeycomb fails to add interface ipv4 address
| | ... | ${node} | ${interface} | 192.232.0.2 | ${9}

TC12: Honeycomb fails to configure two IPv6 addresses from the same subnet
| | [Documentation] | Check if Honeycomb can configure two IPv6 addresses in\
| | ... | the same subnet onto a single interface. It should not be possible.
| | [Tags] | EXPECTED_FAILING
# Subnet validation on IPv6 not supported.
| | [Teardown] | Honeycomb removes interface ipv6 addresses | ${node}
| | ... | ${interface}
| | When Honeycomb sets interface ipv6 address
| | ... | ${node} | ${interface} | 10::FF10 | ${64}
| | Then Honeycomb fails to add interface ipv6 address
| | ... | ${node} | ${interface} | 10::FF11 | ${64}
| | And Honeycomb fails to add interface ipv6 address
| | ... | ${node} | ${interface} | 10::FFFF | ${64}