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
| ...
| Suite Setup | Run Keywords
| ... | Configure Persistence | ${node} | enable | AND
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| ...
| Suite Teardown | Configure Persistence | ${node} | disable
| ...
| Force Tags | HC_PERSIST | HC_REST_ONLY
| ...
| Documentation | *Honeycomb configuration persistence test suite.*

*** Test Cases ***
# multi-feature cases
# ===================
| TC01: Honeycomb persists configuration through restart of both Honeycomb and VPP
| | [Documentation] | Checks if Honeycomb maintains configuration after both\
| | ... | Restart Honeycomb and VPP.
| | ...
| | [Tags] | HC_FUNC
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Multi-Feature Persistence test configuration | ${node} | ${interface}
| | And Multi-Feature persistence Test Verification | ${node} | ${interface}
| | And Log persisted configuration on node | ${node}
| | When Restart Honeycomb and VPP in pesistence test | ${node}
| | Then Multi-Feature persistence Test Verification | ${node} | ${interface}

| TC02: Honeycomb reverts to defaults if persistence files are invalid
| | [Documentation] | Checks if Honeycomb reverts to default configuration when\
| | ... | persistence files are damaged or invalid.
| | ...
| | [Tags] | HC_FUNC
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Multi-Feature Persistence test configuration | ${node} | ${interface}
| | And Multi-Feature persistence Test Verification | ${node} | ${interface}
| | When Persistence file is damaged during restart | ${node}
| | Then Honeycomb and VPP should have default configuration | ${node}

| TC03: Honeycomb persists configuration through restart of Honeycomb
| | [Documentation] | Checks if Honeycomb maintains configuration after it\
| | ... | is restarted.
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Multi-Feature Persistence test configuration | ${node} | ${interface}
| | And Multi-Feature persistence Test Verification | ${node} | ${interface}
| | And Log persisted configuration on node | ${node}
| | When Restart Honeycomb | ${node}
| | Then Multi-Feature persistence Test Verification | ${node} | ${interface}

| TC04: Honeycomb persists configuration through restart of VPP
| | [Documentation] | Checks if Honeycomb updates VPP settings after VPP is\
| | ... | restarted.
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Multi-Feature Persistence test configuration | ${node} | ${interface}
| | And Multi-Feature persistence Test Verification | ${node} | ${interface}
| | And Log persisted configuration on node | ${node}
| | When Restart VPP | ${node}
| | Then Multi-Feature persistence Test Verification | ${node} | ${interface}

# single-feature cases
# ====================

| TC05: Persist configuration of IP addresses and neighbors - HC and VPP restart
| | [Documentation] | Verify persistence of interface state, IPv4 address
| | ... | and neighbor entries through restart of both Honeycomb and VPP.
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Interface Persistence Setup | ${node}
| | And Interface Persistence Check | ${node}
| | When Restart Honeycomb and VPP in pesistence test | ${node}
| | Then Interface Persistence Check | ${node}

| TC06: Persist configuration of IP addresses and neighbors - HC restart
| | [Documentation] | Verify persistence of interface state, IPv4 address
| | ... | and neighbor entries through restart of Honeycomb.
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Interface Persistence Setup | ${node}
| | And Interface Persistence Check | ${node}
| | When Restart Honeycomb | ${node}
| | Then Interface Persistence Check | ${node}

| TC07: Persist configuration of IP addresses and neighbors - VPP restart
| | [Documentation] | Verify persistence of interface state, IPv4 address
| | ... | and neighbor entries through restart of VPP.
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Interface Persistence Setup | ${node}
| | And Interface Persistence Check | ${node}
| | When Restart VPP | ${node}
| | Then Interface Persistence Check | ${node}

| TC08: Honeycomb persists configuration of bridge domains - HC and VPP restart
| | [Documentation] | Verify persistence of bridge domain, L2-FIB entry
| | ... | and Bridge domain Operational Interface Assignment through restart
| | ... | of both Honeycomb and VPP.
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Bridge Domain Persistence Setup | ${node}
| | When Restart Honeycomb and VPP in pesistence test | ${node}
| | Then Bridge Domain Persistence Check | ${node}

| TC09: Honeycomb persists configuration of bridge domains - HC restart
| | [Documentation] | Verify persistence of bridge domain, L2-FIB entry
| | ... | and Bridge domain Operational Interface Assignment through restart
| | ... | of Honeycomb.
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Bridge Domain Persistence Setup | ${node}
| | When Restart Honeycomb | ${node}
| | Then Bridge Domain Persistence Check | ${node}

| TC10: Honeycomb persists configuration of bridge domains - VPP restart
| | [Documentation] | Verify persistence of bridge domain, L2-FIB entry
| | ... | and Bridge domain Operational Interface Assignment through restart
| | ... | of VPP.
| | ...
| | [Teardown]
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | ...
| | Given Bridge Domain Persistence Setup | ${node}
| | When Restart VPP | ${node}
| | Then Bridge Domain Persistence Check | ${node}

#TODO: All other features
