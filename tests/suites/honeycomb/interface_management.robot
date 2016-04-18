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

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb_interfaces.robot
| Suite Setup | Run keywords | Setup all DUTs before test | AND
| ... | Setup Honeycomb service on all DUTs | AND
| ... | Setup variables for interface test suite
| Suite Teardown | Stop Honeycomb service on all DUTs
| Documentation | *Honeycomb interface management test suite.*
| ...
| ... | Test suite uses the first interface of a single DUT node.

*** Test Cases ***
| Honeycomb modifies interface state
| | [Documentation] | Check if Honeycomb API can modify operational state of
| | ... | interfaces on VPP node, and can register external changes to
| | ... | operational state of VPP interfaces.
| | [Tags] | honeycomb_sanity
| | When Honeycomb sets interface state | ${node} | ${interface} | up
| | ${api_state} | ${vat_state}=
| | ... | And Get interface state | ${node} | ${interface}
| | Then Should be equal | ${api_state} | ${vat_state} | up
| | When VAT sets interface state | ${node} | ${interface} | down
| | ${api_state} | ${vat_state}=
| | ... | And Get interface state | ${node} | ${interface}
| | Then Should be equal | ${api_state} | ${vat_state} | down
