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
# Node and interface to run tests on.
| ${node}= | ${nodes['DUT1']}
| ${interface}= | ${node['interfaces']['port1']['name']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/persistence.robot
# Restart Honeycomb and VPP to clear configuration before tests.
| Suite Setup | Run keywords
| ... | Stop Honeycomb service on DUTs | ${node} | AND
| ... | Clear persisted Honeycomb configuration | ${node} | AND
| ... | Setup DUT | ${node} | AND
| ... | Setup Honeycomb service on DUTs | ${node}
| Documentation | *Honeycomb configuration persistence test suite.*

*** Test Cases ***
| Honeycomb persists configuration through restart of both systems
| | [Documentation] | Checks if Honeycomb maintains configuration after both\
| | ... | Honeycomb and VPP are restarted.
| | [Tags] | honeycomb_sanity
| | When Honeycomb configures every setting | ${node} | ${interface}
| | And Honeycomb and VPP are restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| Honeycomb persists configuration through restart of Honeycomb
| | [Documentation] | Checks if Honeycomb maintains configuration after it\
| | ... | is restarted.
| | [Tags] | honeycomb_sanity
| | Given Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When Honeycomb is restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| Honeycomb persists configuration through restart of VPP
| | [Documentation] | Checks if Honeycomb updates VPP settings after VPP is\
| | ... | restarted.
| | [Tags] | honeycomb_sanity
| | Given Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When VPP is restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| Honeycomb reverts to defaults if persistence files are invalid
| | [Documentation] | Checks if Honeycomb reverts to default configuration when\
| | ... | persistence files are damaged or invalid.
| | [Tags] | honeycomb_sanity
| | Given Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When Persistence file is damaged during restart | ${node}
| | Then Honeycomb and VPP should have default configuration | ${node}
