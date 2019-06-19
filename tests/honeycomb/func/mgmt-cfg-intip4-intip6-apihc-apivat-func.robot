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
| ${interface2}= | ${node['interfaces']['port2']['name']}
| ${interface3}= | ${node['interfaces']['port3']['name']}

*** Settings ***
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/fib.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Variables | resources/test_data/honeycomb/interface_ip.py
| ...
| Force Tags | HC_FUNC
| ...
| Suite Setup | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Documentation | *Honeycomb interface management test suite.*

*** Test Cases ***
| TC01: Honeycomb configures and reads interface state
| | [Documentation] | Check if Honeycomb API can modify the admin state of\
| | ... | VPP interfaces.
| | ...
| | Given Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And Interface state from VAT should be | ${node} | ${interface} | down
| | When Honeycomb configures interface state | ${node} | ${interface} | up
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | up
| | And Interface state from VAT should be | ${node} | ${interface} | up
| | When Honeycomb configures interface state | ${node} | ${interface} | down
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And Interface state from VAT should be | ${node} | ${interface} | down

| TC02: Honeycomb modifies interface IPv4 address with netmask
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv4\
| | ... | with address and netmask provided.
| | ...
| | Given IPv4 address from Honeycomb should be empty | ${node} | ${interface}
| | And ipv4 address from VAT should be empty | ${node} | ${interface}
| | When Honeycomb sets interface IPv4 address | ${node} | ${interface}
| | ... | ${ipv4_address} | ${ipv4_mask}
| | Then IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}

| TC03: Honeycomb removes IPv4 address from interface
| | [Documentation] | Check if Honeycomb API can remove configured ipv4\
| | ... | addresses from interface.
| | ...
| | Given IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}
| | When Honeycomb removes interface IPv4 addresses | ${node} | ${interface}
| | Then IPv4 address from Honeycomb should be empty | ${node} | ${interface}
| | And ipv4 address from VAT should be empty | ${node} | ${interface}

| TC04: Honeycomb modifies interface IPv4 address with prefix
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv4\
| | ... | with address and prefix provided.
| | ...
| | [Teardown] | Honeycomb removes interface IPv4 addresses | ${node}
| | ... | ${interface}
| | ...
| | Given IPv4 address from Honeycomb should be empty | ${node} | ${interface}
| | And ipv4 address from VAT should be empty | ${node} | ${interface}
| | When Honeycomb sets interface IPv4 address with prefix
| | ... | ${node} | ${interface} | ${ipv4_address2} | ${ipv4_prefix}
| | Then IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address2} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address2}
| | ... | ${ipv4_prefix} | ${ipv4_mask}

| TC05: Honeycomb modifies IPv4 neighbor table
| | [Documentation] | Check if Honeycomb API can add and remove ARP entries.
| | ...
| | [Teardown] | Honeycomb clears all interface IPv4 neighbors
| | ... | ${node} | ${interface}
| | ...
| | Given IPv4 neighbor from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | When Honeycomb adds interface IPv4 neighbor
| | ... | ${node} | ${interface} | ${ipv4_neighbor} | ${neighbor_mac}
| | Then IPv4 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_neighbor} | ${neighbor_mac}

| TC06: Honeycomb modifies interface configuration - IPv6
| | [Documentation] | Check if Honeycomb API can configure interfaces for ipv6.
| | ...
| | [Teardown] | Honeycomb removes interface IPv6 addresses | ${node}
| | ... | ${interface}
| | ...
| | Given IPv6 address from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | And IPv6 address from VAT should be empty
| | ... | ${node} | ${interface}
| | When Honeycomb sets interface IPv6 address
| | ... | ${node} | ${interface} | ${ipv6_address} | ${ipv6_prefix}
| | Then IPv6 address from Honeycomb should contain
| | ... | ${node} | ${interface} | ${ipv6_address} | ${ipv6_prefix}
| | And IPv6 address from VAT should contain
| | ... | ${node} | ${interface} | ${ipv6_address}
| | ... | ${ipv6_prefix} | ${ipv6_mask}

| TC07: Honeycomb modifies IPv6 neighbor table
| | [Documentation] | Check if Honeycomb API can add and remove ARP entries.
| | ...
| | [Teardown] | Honeycomb clears all interface IPv6 neighbors
| | ... | ${node} | ${interface}
| | ...
| | Given IPv6 neighbor from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | When Honeycomb adds interface IPv6 neighbor
| | ... | ${node} | ${interface} | ${ipv6_neighbor} | ${neighbor_mac}
| | Then IPv6 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv6_neighbor} | ${neighbor_mac}

| TC08: Honeycomb modifies interface configuration - MTU
| | [Documentation] | Check if Honeycomb API can configure interface\
| | ... | MTU value.
| | ...
| | When Honeycomb sets interface ethernet configuration
| | ... | ${node} | ${interface} | ${ethernet}
| | Then Interface ethernet Operational Data From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${ethernet}
| | ${mtu}= | Create List | ${ethernet['mtu']} | ${0} | ${0} | ${0}
| | And Interface ethernet Operational Data From VAT Should Be
| | ... | ${node} | ${interface} | ${mtu}

| TC09: Honeycomb modifies interface configuration - vrf
| | [Documentation] | Check if Honeycomb API can configure interface\
| | ... | vrf ID.
| | ...
| | [Teardown] | Honeycomb interface VRF Test Teardown | ${node} | ${interface}
| | ...
| | Honeycomb configures FIB table | ${node} | ipv4 | ${1}
| | When Honeycomb sets interface VRF ID
| | ... | ${node} | ${interface} | ${1} | ipv4
| | Then Interface VRF ID from Honeycomb should be
| | ... | ${node} | ${interface} | ${1} | ipv4
| | And Interface VRF ID from VAT should be
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
| | ...
| | [Teardown] | Multiple IP Address Test Teardown | ${node} | ${dut_to_tg_if1}
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | When Honeycomb sets interface IPv4 address with prefix
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${ipv4_address} | ${ipv4_prefix}
| | And Honeycomb adds interface IPv4 address
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${ipv4_address2} | ${ipv4_prefix}
| | And Honeycomb sets interface IPv6 address
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${ipv6_address} | ${ipv6_prefix}
| | And Honeycomb adds interface IPv6 address
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${ipv6_address2} | ${ipv6_prefix}
| | Then IPv4 address from Honeycomb should be
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${dut_node} | ${interface2} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}
| | And IPv6 address from Honeycomb should contain
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${ipv6_address} | ${ipv6_prefix}
| | And IPv6 address from VAT should contain
| | ... | ${dut_node} | ${interface2} | ${ipv6_address}
| | ... | ${ipv6_prefix} | ${ipv6_mask}
| | And Honeycomb configures interface state
| | ... | ${dut_node} | ${dut_to_tg_if1} | up
| | And Honeycomb adds interface IPv4 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${ipv4_neighbor} | ${neighbor_mac}
| | And Honeycomb adds interface IPv4 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${ipv4_neighbor2} | ${neighbor_mac2}
| | And Honeycomb adds interface IPv6 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${ipv6_neighbor} | ${neighbor_mac}
| | And Honeycomb adds interface IPv6 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${ipv6_neighbor2} | ${neighbor_mac2}
| | And Suppress ICMPv6 router advertisement message | ${nodes}
| | Then Ping and Verify IP address | ${nodes['TG']}
| | ... | ${ipv4_neighbor} | ${ipv4_address}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}
| | And Ping and Verify IP address | ${nodes['TG']}
| | ... | ${ipv4_neighbor2} | ${ipv4_address2}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}
| | And Ping and Verify IP address | ${nodes['TG']}
| | ... | ${ipv6_neighbor} | ${ipv6_address}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}
| | And Ping and Verify IP address | ${nodes['TG']}
| | ... | ${ipv6_neighbor2} | ${ipv6_address2}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}

| TC11: Honeycomb fails to configure two IPv4 addresses from the same subnet
| | [Documentation] | Check if Honeycomb can configure two IPv4 addresses in\
| | ... | the same subnet onto a single interface. It should not be possible.
| | ...
| | [Teardown] | Honeycomb removes interface IPv4 addresses | ${node}
| | ... | ${interface}
| | ...
| | When Honeycomb sets interface IPv4 address with prefix
| | ... | ${node} | ${interface} | 192.168.0.1 | ${9}
| | Then Honeycomb fails to add interface IPv4 address
| | ... | ${node} | ${interface} | 192.168.0.2 | ${9}
| | And Honeycomb fails to add interface IPv4 address
| | ... | ${node} | ${interface} | 192.232.0.2 | ${9}

| TC12: Honeycomb fails to configure two IPv6 addresses from the same subnet
| | [Documentation] | Check if Honeycomb can configure two IPv6 addresses in\
| | ... | the same subnet onto a single interface. It should not be possible.
| | ...
| | [Teardown] | Honeycomb removes interface IPv6 addresses | ${node}
| | ... | ${interface}
| | When Honeycomb sets interface IPv6 address
| | ... | ${node} | ${interface} | 10::FF10 | ${64}
| | Then Honeycomb fails to add interface IPv6 address
| | ... | ${node} | ${interface} | 10::FF11 | ${64}
| | And Honeycomb fails to add interface IPv6 address
| | ... | ${node} | ${interface} | 10::FFFF | ${64}

| TC13: Honeycomb can configure unnumbered interface
| | [Documentation] | Check if Honeycomb can configure an unnumbered interface\
| | ... | on a physical interface, borrowing the IP address of another physical\
| | ... | interface.
| | ...
# CSIT-1210: Adapt HC unnumbered interface tests to VPP 18.07 api changes
| | [Tags] | EXPECTED_FAILING
| | ...
| | Given Honeycomb sets interface IPv4 address | ${node}
| | ... | ${interface3} | ${ipv4_address} | ${ipv4_prefix}
| | When Honeycomb adds unnumbered configuration to interface
| | ... | ${node} | ${interface} | ${interface3}
| | Then Wait until Keyword succeeds | 10s | 2s
| | ... | IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface3} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface3} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}
| | And IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}

| TC14: Honeycomb removes interface unnumbered configuration
| | [Documentation] | Check if Honeycomb can remove unnumbered configuration\
| | ... | from an interface.
| | ...
# CSIT-1210: Adapt HC unnumbered interface tests to VPP 18.07 api changes
| | [Tags] | EXPECTED_FAILING
| | ...
| | Given IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface3} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface3} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}
| | And IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}
| | When Honeycomb removes unnumbered configuration from interface
| | ... | ${node} | ${interface}
| | Then Wait until Keyword succeeds | 10s | 2s
| | ... | IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface3} | ${ipv4_address} | ${ipv4_prefix}
| | And IPv4 address from VAT should be
| | ... | ${node} | ${interface3} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}
| | And IPv4 address from Honeycomb should be empty | ${node} | ${interface}
| | And ipv4 address from VAT should be empty | ${node} | ${interface}

*** Keywords ***
| Multiple IP Address Test Teardown
| | [Arguments] | ${node} | ${interface}
| | Honeycomb removes interface IPv4 addresses | ${node} | ${interface}
| | Honeycomb removes interface IPv6 addresses | ${node} | ${interface}
| | Honeycomb clears all interface IPv4 neighbors | ${node} | ${interface}
| | Honeycomb clears all interface IPv6 neighbors | ${node} | ${interface}

| Honeycomb interface VRF Test Teardown
| | [Arguments] | ${node} | ${interface}
| | Honeycomb sets interface VRF ID | ${node} | ${interface} | ${0} | ipv4
| | Honeycomb removes FIB configuration | ${node} | ipv4 | ${1}
