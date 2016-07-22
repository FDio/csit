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
# Interfaces to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}
| ${tap_interface}= | tap_test
# Configuration which will be set and verified during tests.
| &{tap_settings}= | tap-name=tap_test | mac=08:00:27:c0:5d:37
| ... | device-instance=${1}
| &{tap_settings2}= | tap-name=tap_test | mac=08:00:27:60:26:ab
| ... | device-instance=${2}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/tap.robot
| Force Tags | honeycomb_sanity
| Documentation | *Honeycomb TAP management test suite.*
| ...
| ... | Test suite uses the first interface of the first DUT node.

*** Test Cases ***
| Honeycomb configures TAP interface
| | [Documentation] | Check if Honeycomb API can configure a TAP interface.
| | Given TAP configuration from Honeycomb should be empty
| | ... | ${node} | ${tap_interface}
| | And TAP configuration from VAT should be empty
| | ... | ${node} | ${tap_interface}
| | When Honeycomb creates TAP interface
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | Then TAP configuration from Honeycomb should be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | And TAP configuration from VAT should be
| | ... | ${node} | ${tap_interface} | ${tap_settings}

| Honeycomb modifies existing TAP interface configuration
| | [Documentation] | Check if Honeycomb API can re-configure and existing TAP\
| | ... | interface with new settings.
| | Given TAP configuration from Honeycomb should be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | And TAP configuration from VAT should be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | When Honeycomb configures TAP interface
| | ... | ${node} | ${tap_interface} | ${tap_settings2}
| | Then TAP configuration from Honeycomb should be
| | ... | ${node} | ${tap_interface} | ${tap_settings2}
| | And TAP configuration from VAT should be
| | ... | ${node} | ${tap_interface} | ${tap_settings2}

| Honeycomb removes TAP interface
| | [Documentation] | Check if Honeycomb API can remove TAP interface.
| | Given TAP configuration from Honeycomb should be
| | ... | ${node} | ${tap_interface} | ${tap_settings2}
| | And TAP configuration from VAT should be
| | ... | ${node} | ${tap_interface} | ${tap_settings2}
| | When Honeycomb removes TAP interface | ${node} | ${tap_interface}
| | Then TAP configuration from Honeycomb should be empty
| | ... | ${node} | ${tap_interface}
| | And TAP configuration from VAT should be empty
| | ... | ${node} | ${tap_interface}
