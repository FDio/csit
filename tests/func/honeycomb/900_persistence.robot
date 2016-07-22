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
| Suite Setup | Restart Honeycomb and VPP and clear persisted configuration
| ... | ${node}
| Force Tags | honeycomb_persistence
| Documentation | *Honeycomb configuration persistence test suite.*

*** Test Cases ***
| Honeycomb persists configuration through restart of both Honeycomb and VPP
| | [Documentation] | Checks if Honeycomb maintains configuration after both\
| | ... | Honeycomb and VPP are restarted.
| | Given Honeycomb configures every setting | ${node} | ${interface}
| | And Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When Honeycomb and VPP are restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| Honeycomb persists configuration through restart of Honeycomb
| | [Documentation] | Checks if Honeycomb maintains configuration after it\
| | ... | is restarted.
| | Given Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When Honeycomb is restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| Honeycomb persists configuration through restart of VPP
| | [Documentation] | Checks if Honeycomb updates VPP settings after VPP is\
| | ... | restarted.
| | Given Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | When VPP is restarted | ${node}
| | Then Honeycomb and VPP should verify every setting | ${node} | ${interface}
| | And Honeycomb should show no rogue interfaces | ${node}

| Honeycomb reverts to defaults if persistence files are invalid
| | [Documentation] | Checks if Honeycomb reverts to default configuration when\
| | ... | persistence files are damaged or invalid.
| | [Teardown] | Run keyword if test failed
| | ... | Restart both systems and clear persisted configuration | ${node}
| | Given Honeycomb and VPP should not have default configuration | ${node}
| | When Persistence file is damaged during restart | ${node}
| | Then Honeycomb and VPP should have default configuration | ${node}

*** Keywords ***
| Restart Honeycomb and VPP and clear persisted configuration
| | [Documentation] | Restarts Honeycomb and VPP with default configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | Restart both systems and clear persisted configuration \
| | ... | \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Clear persisted Honeycomb configuration | ${node}
| | Setup DUT | ${node}
| | Setup Honeycomb service on DUTs | ${node}