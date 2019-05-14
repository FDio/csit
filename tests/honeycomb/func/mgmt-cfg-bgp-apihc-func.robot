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

*** Variables ***
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}
| ${dut1_to_tg_ip}= | 192.168.0.1
| ${tg_to_dut1_ip}= | 192.168.0.2
| ${dut1_to_dut2_ip}= | 192.168.1.1
| ${dut2_to_dut1_ip}= | 192.168.1.2
| ${bgp_port}= | ${179}
| ${bgp_as_number}= | ${37}
| ${prefix}= | ${24}

*** Settings ***
| Library | resources.libraries.python.honeycomb.IPv6Management
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/bgp.robot
| Resource | resources/libraries/robot/honeycomb/routing.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/honeycomb/ipv6_control.robot
| Variables | resources/test_data/honeycomb/bgp.py
| ...
| Suite Setup | Run Keywords
| ... | Enable Honeycomb Feature | ${node} | BGP | AND
| ... | Configure BGP Module | ${node} | ${dut1_to_tg_ip}
| ... | ${bgp_port} | ${bgp_as_number} | AND
| ... | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Run Keywords
| ... | Tear Down Honeycomb Functional Test Suite | ${nodes['DUT1']} | AND
| ... | Stop Honeycomb service on DUTs | ${nodes['DUT2']} | AND
| ... | Unconfigure IPv4 Management Interfaces | AND
| ... | Disable Honeycomb Feature | ${node} | BGP | AND
| ... | Disable Honeycomb Feature | ${nodes['DUT2']} | BGP
| ...
# HONEYCOMB-409: BGP configuration via ODL is currently not fully supported
| Force Tags | HC_FUNC | HC_REST_ONLY
| ...
| Documentation | *Honeycomb BGP management test suite.*

*** Test Cases ***
| TC01: Honeycomb configures BGP peer - Internal
| | [Documentation] | Check if Honeycomb can configure an internal BGP peer.
| | ...
| | When Honeycomb adds BGP peer
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | Then BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}

| TC02: Honeycomb removes peer configuration
| | [Documentation] | Check if Honeycomb can remove a configured BGP peer.
| | ...
| | Given BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | When Honeycomb removes BGP peer | ${node} | ${address_internal}
| | Then No BGP peers should be configured | ${node}

| TC03: Honeycomb updates existing BGP peer - Internal
| | [Documentation] | Check if Honeycomb can update an existing BGP peer.
| | ...
| | [Teardown] | Honeycomb removes BGP peer | ${node} | ${address_internal}
| | ...
| | Given No BGP peers should be configured | ${node}
| | When Honeycomb adds BGP peer
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | And Honeycomb adds BGP peer
| | ... | ${node} | ${address_internal} | ${peer_internal_update}
| | Then BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal_update}

| TC04: Honeycomb configures BGP peer - Application
| | [Documentation] | Check if Honeycomb can configure an application BGP peer.
| | ...
| | [Teardown] | Honeycomb removes BGP peer | ${node} | ${address_application}
| | ...
| | Given No BGP peers should be configured | ${node}
| | When Honeycomb adds BGP peer
| | ... | ${node} | ${address_application} | ${peer_application}
| | Then BGP peer from Honeycomb should be
| | ... | ${node} | ${address_application} | ${peer_application}

| TC05: Honeycomb configures a second BGP peer
| | [Documentation] | Check if Honeycomb can configure more than one BGP peer.
| | ...
| | [Teardown] | Run Keywords
| | ... | Honeycomb removes BGP peer | ${node} | ${address_internal} | AND
| | ... | Honeycomb removes BGP peer | ${node} | ${address_internal2}
| | ...
| | Given No BGP peers should be configured | ${node}
| | When Honeycomb adds BGP peer
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | And Honeycomb adds BGP peer
| | ... | ${node} | ${address_internal2} | ${peer_internal2}
| | Then BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | And BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal2} | ${peer_internal2}

| TC06: Honeycomb configures IPv4 route using BGP
| | [Documentation] | Check if Honeycomb can configure a BGP route under a peer.
| | ...
| | Given Honeycomb adds BGP peer
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | When Honeycomb configures BGP route
| | ... | ${node} | ${address_internal} | ${route_data_ipv4}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | Then BGP Route from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_oper}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4

| TC07: Honeycomb removes IPv4 route configuration
| | [Documentation] | Check if Honeycomb can remove a configured BGP route.
| | ...
| | Given BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | And BGP Route from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_oper}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | When Honeycomb removes BGP route | ${node} | ${address_internal}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | Then No BGP Routes Should exist
| | ... | ${node} | ${address_internal} | ipv4

| TC08: Honeycomb updates existing IPv4 route using BGP
| | [Documentation] | Check if Honeycomb can update an existing BGP route.
| | ...
| | [Teardown] | Honeycomb removes BGP route | ${node} | ${address_internal}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | ...
| | Given BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | And No BGP Routes Should exist
| | ... | ${node} | ${address_internal} | ipv4
| | When Honeycomb configures BGP route
| | ... | ${node} | ${address_internal} | ${route_data_ipv4}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | And Honeycomb configures BGP route
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_update}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | Then BGP Route from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_update_oper}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4

| TC09: Honeycomb configures a second IPv4 route
| | [Documentation] | Check if Honeycomb can configure more than one BGP route.
| | ...
| | [Teardown] | Run Keywords
| | ... | Honeycomb removes BGP route | ${node} | ${address_internal}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4 | AND
| | ... | Honeycomb removes BGP route | ${node} | ${address_internal}
| | ... | ${route_address_ipv4_2} | ${route_id_ipv4_2} | ipv4 | AND
| | ... | Honeycomb removes BGP peer | ${node} | ${address_internal}
| | ...
| | Given BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | When Honeycomb configures BGP route
| | ... | ${node} | ${address_internal} | ${route_data_ipv4}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | And Honeycomb configures BGP route
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_2}
| | ... | ${route_address_ipv4_2} | ${route_id_ipv4_2} | ipv4
| | Then BGP Route from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_oper}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | And BGP Route from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_2_oper}
| | ... | ${route_address_ipv4_2} | ${route_id_ipv4_2} | ipv4

| TC10: Honeycomb sends BGP OPEN messages to configured peer
| | [Documentation]
| | ... | [top] TG-DUT1-TG.
| | ... | [enc] Eth-IPv4-TCP-BGP.
| | ... | [cfg] On DUT1 give Honeycomb control over the data-plane interface
| | ... | connected to TG. Configure a BGP peer with the address of TG.
| | ... | [ver] Open a TCP listener on TG on the BGP port and listen for BGP
| | ... | OPEN message. On receive, verify message fields.
| | ...
| | [Setup] | Run Keywords
| | ... | Configure BGP Module | ${node} | ${dut1_to_dut2_ip}
| | ... | ${bgp_port} | ${bgp_as_number} | AND
| | ... | Configure IPv4 Management Interface
| | [Teardown] | Honeycomb removes BGP peer | ${dut1_node} | ${address_internal}
| | When Honeycomb adds BGP peer
| | ... | ${dut1_node} | ${address_internal} | ${peer_internal}
| | Then Receive BGP OPEN message
| | ... | ${tg_node} | ${tg_to_dut1_ip} | ${dut1_to_dut2_ip}
| | ... | ${bgp_port} | ${bgp_as_number} | ${holdtime_internal}

| TC11: Honeycomb shows connected peer in operational data
| | [Documentation]
| | ... | [top] TG-DUT1-DUT2-TG.
| | ... | [enc] Eth-IPv4-TCP-BGP.
| | ... | [cfg] On DUT1 and DUT2 give Honeycomb control over the data-plane
| | ... | interfaces connecting DUT1 ad DUT2. Configure BGP peers on DUT1
| | ... | and DUT2 with each other's IP address.
| | ... | [ver] Using Restconf, verify that Honeycomb on each DUT has the
| | ... | other DUT's entry in operational data.
| | ...
| | When Honeycomb adds BGP peer
| | ... | ${dut1_node} | ${dut2_to_dut1_ip} | ${dut2_peer}
| | And Honeycomb adds BGP peer
| | ... | ${dut2_node} | ${dut1_to_dut2_ip} | ${dut1_peer}
| | Sleep | 5s | Wait for BGP connection. Retry timer is 5 seconds.
| | Then Peer operational data from Honeycomb should be
| | ... | ${dut1_node} | ${dut2_to_dut1_ip}
| | And Peer operational data from Honeycomb should be
| | ... | ${dut2_node} | ${dut1_to_dut2_ip}

| TC12: Honeycomb sends IPv4 BGP route to connected peer
| | [Documentation]
| | ... | [top] TG-DUT1-DUT2-TG.
| | ... | [enc] Eth-IPv4-TCP-BGP.
| | ... | [cfg] On DUT1 and DUT2 give Honeycomb control over the data-plane
| | ... | interfaces connecting DUT1 ad DUT2. Configure BGP peers on DUT1
| | ... | and DUT2 with each other's IP address. On DUT2 configure a static
| | ... | IPv4 route using Honeycomb's BGP module.
| | ... | [ver] Verify that the route is present in BGP
| | ... | local RIB and VPP's routing table on each DUT.
| | ...
| | Given Peer operational data from Honeycomb should be
| | ... | ${dut1_node} | ${dut2_to_dut1_ip}
| | And Peer operational data from Honeycomb should be
| | ... | ${dut2_node} | ${dut1_to_dut2_ip}
| | When Honeycomb adds BGP peer
| | ... | ${dut2_node} | ${address_application} | ${peer_application}
| | And Honeycomb configures BGP route
| | ... | ${dut2_node} | ${address_application} | ${dut1_route}
| | ... | ${dut1_route_address} | ${dut1_route_id} | ipv4
| | And Sleep | 5s | Wait for route advertisement. Retry timer is 5 seconds.
| | Then Routing data from Honeycomb should contain
| | ... | ${dut1_node} | learned-protocol-0 | ipv4 | ${route_operational}
| | And Routing data from Honeycomb should contain
| | ... | ${dut2_node} | learned-protocol-0 | ipv4 | ${route_operational}
| | And BGP Loc-RIB table should include | ${dut1_node} | ${rib_operational}
| | And BGP Loc-RIB table should include | ${dut2_node} | ${rib_operational}

| TC13: Honeycomb sends IPv6 BGP route to connected peer
| | [Documentation]
| | ... | [top] TG-DUT1-DUT2-TG.
| | ... | [enc] Eth-IPv4-TCP-BGP.
| | ... | [cfg] On DUT1 and DUT2 give Honeycomb control over the data-plane
| | ... | interfaces connecting DUT1 ad DUT2. Configure BGP peers on DUT1
| | ... | and DUT2 with each other's IP address. On DUT2 configure a static
| | ... | IPv6 route using Honeycomb's BGP module.
| | ... | [ver] Verify that the route is present in BGP
| | ... | local RIB and VPP's routing table on each DUT.
| | ...
| | Given Peer operational data from Honeycomb should be
| | ... | ${dut1_node} | ${dut2_to_dut1_ip}
| | And Peer operational data from Honeycomb should be
| | ... | ${dut2_node} | ${dut1_to_dut2_ip}
| | And Honeycomb adds BGP peer
| | ... | ${dut2_node} | ${address_application} | ${peer_application}
| | And Honeycomb configures BGP route
| | ... | ${dut2_node} | ${address_application} | ${dut1_route_ip6}
| | ... | ${dut1_route_ip6_prefix} | ${dut1_route_ip6_id} | ipv6
| | And Sleep | 5s | Wait for route advertisement. Retry timer is 5 seconds.
| | Then Routing data from Honeycomb should contain
| | ... | ${dut1_node} | learned-protocol-0 | ipv6 | ${route_ip6_operational}
| | And Routing data from Honeycomb should contain
| | ... | ${dut2_node} | learned-protocol-0 | ipv6 | ${route_ip6_operational}
| | And BGP Loc-RIB table should include | ${dut1_node} | ${rib_ip6_operational}
| | And BGP Loc-RIB table should include | ${dut2_node} | ${rib_ip6_operational}

#TODO: Add tests once implemented in HC:
# IPv6 neighbor, L2VPN, L3VPN, linkstate, route reflector, and more

*** Keywords ***
| Configure IPv4 Management Interface
| | [Documentation] | Change one of VPP's data-plane interfaces on DUT into\
| | ... | a control-plane interface that Honeycomb can listen on. Setup IP\
| | ... | addresses on the link, create suite variables for traffic trests, set
| | ... | static ARP entries, then restart VPP and Honeycomb to apply changes.
| | ...
| | Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | ${interface}= | Get Interface Name | ${dut1_node} | ${dut1_to_tg}
| | Set Suite Variable | ${interface}
| | Set Suite Variable | ${tg_node}
| | Set Suite Variable | ${dut1_node}
| | Set Suite Variable | ${dut2_node}
| | Set Suite Variable | ${dut1_to_tg}
| | Stop VPP service on DUT | ${dut1_node}
| | Stop VPP service on DUT | ${dut2_node}
| | Stop Honeycomb Service on DUTs | ${dut1_node}
| | Stop Honeycomb Service on DUTs | ${dut2_node}
| | Convert data-plane interface to control-plane
| | ... | ${dut1_node} | ${dut1_to_tg}
| | Convert data-plane interface to control-plane
| | ... | ${dut1_node} | ${dut1_to_dut2}
| | Convert data-plane interface to control-plane
| | ... | ${dut2_node} | ${dut2_to_dut1}
| | Sleep | 5sec | Wait until OS reclaims the interfaces.
| | ${tg_to_dut1_name}= | Get Interface Name by MAC
| | ... | ${tg_node} | ${tg_to_dut1_mac}
| | ${dut1_to_tg_name}= | Get Interface Name by MAC
| | ... | ${dut1_node} | ${dut1_to_tg_mac}
| | ${dut1_to_dut2_name}= | Get Interface Name by MAC
| | ... | ${dut1_node} | ${dut1_to_dut2_mac}
| | ${dut2_to_dut1_name}= | Get Interface Name by MAC
| | ... | ${dut2_node} | ${dut2_to_dut1_mac}
| | Set Suite Variable | ${dut1_to_tg_name}
| | Set Suite Variable | ${tg_to_dut1_name}
| | Set Suite Variable | ${dut1_to_dut2_name}
| | Set Suite Variable | ${dut2_to_dut1_name}
| | Set management interface address
| | ... | ${tg_node} | ${tg_to_dut1_name}
| | ... | ${tg_to_dut1_ip} | ${prefix}
| | Set management interface address
| | ... | ${dut1_node} | ${dut1_to_tg_name}
| | ... | ${dut1_to_tg_ip} | ${prefix}
| | Set management interface address
| | ... | ${dut1_node} | ${dut1_to_dut2_name}
| | ... | ${dut1_to_dut2_ip} | ${prefix}
| | Set management interface address
| | ... | ${dut2_node} | ${dut2_to_dut1_name}
| | ... | ${dut2_to_dut1_ip} | ${prefix}
| | Set Static ARP | ${tg_node} | ${dut1_to_tg_ip} | ${dut1_to_tg_mac}
| | Set Static ARP | ${dut1_node} | ${tg_to_dut1_ip} | ${tg_to_dut1_mac}
| | Set Static ARP | ${dut1_node} | ${dut2_to_dut1_ip} | ${dut2_to_dut1_mac}
| | Set Static ARP | ${dut2_node} | ${dut1_to_dut2_ip} | ${dut1_to_dut2_mac}
| | Enable Honeycomb Feature | ${dut2_node} | BGP
| | Configure BGP Module | ${dut1_node} | ${dut1_to_dut2_ip}
| | ... | ${bgp_port} | ${bgp_as_number}
| | Configure BGP Module | ${dut2_node} | ${dut2_to_dut1_ip}
| | ... | ${bgp_port} | ${bgp_as_number}
| | Restart VPP service | ${dut1_node}
| | Restart VPP service | ${dut2_node}
| | Configure Honeycomb service on DUTs | ${dut1_node}
| | Set Up Honeycomb Functional Test Suite | ${dut2_node}

| Unconfigure IPv4 Management Interfaces
| | [Documentation] | Remove all IP addresses from the interface.
| | ...
| | Clear Interface Configuration | ${tg_node} | ${tg_to_dut1_name}
| | Clear Interface Configuration | ${dut1_node} | ${dut1_to_tg_name}
| | Clear Interface Configuration | ${dut1_node} | ${dut1_to_dut2_name}
| | Clear Interface Configuration | ${dut2_node} | ${dut2_to_dut1_name}

| Set BGP Suite Variables
| | Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Set Suite Variable | ${interface}
| | Set Suite Variable | ${tg_node}
| | Set Suite Variable | ${dut1_node}
| | Set Suite Variable | ${dut2_node}
| | Set Suite Variable | ${dut1_to_tg}
| | Set Suite Variable | ${dut1_to_tg_name}
| | Set Suite Variable | ${tg_to_dut1_name}
| | Set Suite Variable | ${dut1_to_dut2_name}
| | Set Suite Variable | ${dut2_to_dut1_name}
