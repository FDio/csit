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

*** Variables***
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/persistence.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Resource | resources/libraries/robot/honeycomb/l2_fib.robot
| Suite Setup | Run Keywords
| ... | Configure Persistence | ${node} | enable | AND
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Suite Teardown | Configure Persistence | ${node} | disable
| Force Tags | honeycomb_persist
| Documentation | *Honeycomb configuration persistence test suite.*

*** Test Cases ***
# generic cases
# ==============
| TC01: Honeycomb persists configuration through restart of both Honeycomb and VPP
| | [Documentation] | Checks if Honeycomb maintains configuration after both\
| | ... | Honeycomb and VPP are restarted.
| | [Tags] | honeycomb_sanity
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Generic Persistence test configuration | ${node} | ${interface}
| | And Generic persistence Test Verification | ${node} | ${interface}
| | And Log persisted configuration on node | ${node}
| | When Honeycomb and VPP are restarted | ${node}
| | Then Generic persistence Test Verification | ${node} | ${interface}

| TC02: Honeycomb reverts to defaults if persistence files are invalid
| | [Documentation] | Checks if Honeycomb reverts to default configuration when\
| | ... | persistence files are damaged or invalid.
| | [Tags] | honeycomb_sanity
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Generic Persistence test configuration | ${node} | ${interface}
| | And Generic persistence Test Verification | ${node} | ${interface}
| | When Persistence file is damaged during restart | ${node}
| | Then Honeycomb and VPP should have default configuration | ${node}

| TC03: Honeycomb persists configuration through restart of Honeycomb
| | [Documentation] | Checks if Honeycomb maintains configuration after it\
| | ... | is restarted.
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Generic Persistence test configuration | ${node} | ${interface}
| | And Generic persistence Test Verification | ${node} | ${interface}
| | And Log persisted configuration on node | ${node}
| | When Honeycomb is restarted | ${node}
| | Then Generic persistence Test Verification | ${node} | ${interface}

| TC04: Honeycomb persists configuration through restart of VPP
| | [Documentation] | Checks if Honeycomb updates VPP settings after VPP is\
| | ... | restarted.
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Generic Persistence test configuration | ${node} | ${interface}
| | And Generic persistence Test Verification | ${node} | ${interface}
| | And Log persisted configuration on node | ${node}
| | When VPP is restarted | ${node}
| | Then Generic persistence Test Verification | ${node} | ${interface}

# single-feature cases
# =================

| TC05: Persist configuration of IP addresses and neighbors - HC and VPP restart
| | [Documentation] | Verify persistence of interface state, IPv4 address
| | ... | and neighbor entries through restart of both Honeycomb and VPP.
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Interface Persistence Setup
| | And Interface Persistence Check
| | When Honeycomb and VPP are restarted | ${node}
| | Then Interface Persistence Check

| TC06: Persist configuration of IP addresses and neighbors - HC restart
| | [Documentation] | Verify persistence of interface state, IPv4 address
| | ... | and neighbor entries through restart of Honeycomb.
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Interface Persistence Setup
| | And Interface Persistence Check
| | When Honeycomb is restarted | ${node}
| | Then Interface Persistence Check

| TC07: Persist configuration of IP addresses and neighbors - VPP restart
| | [Documentation] | Verify persistence of interface state, IPv4 address
| | ... | and neighbor entries through restart of VPP.
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Interface Persistence Setup
| | And Interface Persistence Check
| | When VPP is restarted | ${node}
| | Then Interface Persistence Check

| TC08: Honeycomb persists configuration of bridge domains - HC and VPP restart
| | [Documentation] | Verify persistence of bridge domain, L2-FIB entry
| | ... | and Bridge domain Operational Interface Assignment through restart
| | ... | of both Honeycomb and VPP.
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Bridge Domain Persistence Setup
| | When Honeycomb and VPP are restarted | ${node}
| | Then Bridge Domain Persistence Check

| TC09: Honeycomb persists configuration of bridge domains - HC restart
| | [Documentation] | Verify persistence of bridge domain, L2-FIB entry
| | ... | and Bridge domain Operational Interface Assignment through restart
| | ... | of Honeycomb.
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Bridge Domain Persistence Setup
| | When Honeycomb is restarted | ${node}
| | Then Bridge Domain Persistence Check

| TC10: Honeycomb persists configuration of bridge domains - VPP restart
| | [Documentation] | Verify persistence of bridge domain, L2-FIB entry
| | ... | and Bridge domain Operational Interface Assignment through restart
| | ... | of VPP.
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | Given Bridge Domain Persistence Setup
| | When VPP is restarted | ${node}
| | Then Bridge Domain Persistence Check

#TODO: All other features

*** Keywords ***
| Interface Persistence Setup
| | Honeycomb and VPP should have default configuration | ${node}
| | Import Variables | resources/test_data/honeycomb/interface_ip.py
| | Honeycomb sets interface state | ${node} | ${interface} | up
| | Honeycomb sets interface ipv4 address with prefix
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | Honeycomb adds interface ipv4 neighbor
| | ... | ${node} | ${interface} | ${ipv4_neighbor} | ${neighbor_mac}
| | Honeycomb sets interface ipv6 address
| | ... | ${node} | ${interface} | ${ipv6_address} | ${ipv6_prefix}
| | Honeycomb adds interface ipv6 neighbor
| | ... | ${node} | ${interface} | ${ipv6_neighbor} | ${neighbor_mac}

| Interface Persistence Check
| | Interface state from Honeycomb should be | ${node} | ${interface} | up
| | IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}
| | IPv4 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_neighbor} | ${neighbor_mac}
| | IPv6 address from Honeycomb should contain
| | ... | ${node} | ${interface} | ${ipv6_address} | ${ipv6_prefix}
| | IPv6 address from VAT should contain
| | ... | ${node} | ${interface} | ${ipv6_address} | ${ipv6_prefix}
| | IPv6 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv6_neighbor} | ${neighbor_mac}

| Bridge Domain Persistence Setup
| | Honeycomb and VPP should have default configuration | ${node}
| | Import Variables | resources/test_data/honeycomb/l2_fib.py
| | ... | ${node} | ${interface} | ${interface}
| | Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Honeycomb adds interface to bridge domain
| | ... | ${node} | ${interface} | ${bd_name} | ${if_bd_settings}
| | Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg}

| Bridge Domain Persistence Check
| | Bridge domain Operational Data From Honeycomb Should Be
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Bridge domain Operational Data From VAT Should Be
| | ... | ${node} | ${0} | ${bd_settings}
| | Bridge domain Operational Interface Assignment should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper}
| | L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_forward_vat}
