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
| ${node}= | ${nodes['DUT1']}
| ${interface}= | ${node['interfaces'].values()[0]['name']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Suite Setup | Run keywords | Setup all DUTs before test | AND
| ... | Setup Honeycomb service on DUTs | ${node}
| Suite Teardown | Stop Honeycomb service on DUTs | ${node}
| Documentation | *Honeycomb interface management test suite.*
| ...
| ... | Test suite uses the first interface of the first DUT node.

*** Test Cases ***
| Honeycomb modifies interface state
| | [Documentation] | Check if Honeycomb API can modify the admin state of
| | ... | VPP interfaces.
| | [Tags] | honeycomb_sanity
| | Given Interface state is | ${node} | ${interface} | down
| | When Honeycomb sets interface state | ${node} | ${interface} | up
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | up
| | And Interface state from VAT should be | ${node} | ${interface} | up
| | When Honeycomb sets interface state | ${node} | ${interface} | down
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And Interface state from VAT should be | ${node} | ${interface} | down
