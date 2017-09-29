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

*** Settings ***
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/bgp.robot
| Resource | resources/libraries/robot/honeycomb/routing.robot
| Variables | resources/test_data/honeycomb/bgp.py
| ...
| Suite Setup | Run Keywords
| ... | Enable Honeycomb Feature | ${node} | BGP | AND
| ... | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Run Keywords
| ... | Tear Down Honeycomb Functional Test Suite | ${node} | AND
| ... | Disable Honeycomb Feature | ${node} | BGP
| ...
| Force Tags | HC_FUNC
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

| TC03: Honeycomb removes peer configuration
| | [Documentation] | Check if Honeycomb can remove a configured BGP peer.
| | ...
| | Given BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | When Honeycomb removes BGP peer | ${node} | ${address_internal}
| | Then No BGP peers should be configured | ${node}

| TC02: Honeycomb updates existing BGP peer - Internal
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
| | ... | ${node} | ${address_internal} | ${route_data_ipv4}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4

| TC08: Honeycomb removes IPv4 route configuration
| | [Documentation] | Check if Honeycomb can remove a configured BGP route.
| | ...
| | Given BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | And BGP Route from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${route_data_ipv4}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | When Honeycomb removes BGP route | ${node} | ${address_internal}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | Then No BGP Routes Should be Configured
| | ... | ${node} | ${address_internal} | ipv4

| TC07: Honeycomb updates existing IPv4 route using BGP
| | [Documentation] | Check if Honeycomb can update an existing BGP route.
| | ...
| | [Teardown] | Honeycomb removes BGP route | ${node} | ${address_internal}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | ...
| | Given BGP peer from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${peer_internal}
| | And No BGP Routes Should be Configured
| | ... | ${node} | ${address_internal} | ipv4
| | When Honeycomb configures BGP route
| | ... | ${node} | ${address_internal} | ${route_data_ipv4}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | And Honeycomb configures BGP route
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_update}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | Then BGP Route from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_update}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4

| TC09: Honeycomb configures a second IPv4 route
| | [Documentation] | Check if Honeycomb can configure more than one BGP route.
| | ...
| | [Teardown] | Run Keywords
| | ... | Honeycomb removes BGP route | ${node} | ${address_internal}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4 | AND
| | ... | Honeycomb removes BGP route | ${node} | ${address_internal}
| | ... | ${route_address_ipv4_2} | ${route_id_ipv4_2} | ipv4
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
| | ... | ${node} | ${address_internal} | ${route_data_ipv4}
| | ... | ${route_address_ipv4} | ${route_id_ipv4} | ipv4
| | And BGP Route from Honeycomb should be
| | ... | ${node} | ${address_internal} | ${route_data_ipv4_2}
| | ... | ${route_address_ipv4_2} | ${route_id_ipv4_2} | ipv4
