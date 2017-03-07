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
| Suite Setup | Run Keywords
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| ... | AND | Configure Persistence | ${node} | enable
| Suite Teardown | Configure Persistence | ${node} | disable
| Force Tags | honeycomb_sanity
| Documentation | *Honeycomb configuration persistence test suite.*

*** Test Cases ***
| TC01: Honeycomb persists configuration through restart of both Honeycomb and VPP
| | [Documentation] | Checks if Honeycomb maintains configuration after both\
| | ... | Honeycomb and VPP are restarted.
# Vxlan tunnel name is sometimes not properly restored (HONEYCOMB-301)
| | [Tags] | EXPECTED_FAILING
| | Given Honeycomb configures every setting | ${node} | ${interface}
| | And Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When Honeycomb and VPP are restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| TC02: Honeycomb persists configuration through restart of Honeycomb
| | [Documentation] | Checks if Honeycomb maintains configuration after it\
| | ... | is restarted.
# Vxlan tunnel name is sometimes not properly restored (HONEYCOMB-301)
| | [Tags] | EXPECTED_FAILING
| | Given Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When Honeycomb is restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| TC03: Honeycomb persists configuration through restart of VPP
| | [Documentation] | Checks if Honeycomb updates VPP settings after VPP is\
| | ... | restarted.
# Vxlan tunnel name is sometimes not properly restored (HONEYCOMB-301)
| | [Tags] | EXPECTED_FAILING
| | Given Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When VPP is restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| TC04: Honeycomb reverts to defaults if persistence files are invalid
| | [Documentation] | Checks if Honeycomb reverts to default configuration when\
| | ... | persistence files are damaged or invalid.
| | [Teardown] | Run keyword if test failed
| | ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| | When Persistence file is damaged during restart | ${node}
| | Then Honeycomb and VPP should have default configuration | ${node}
