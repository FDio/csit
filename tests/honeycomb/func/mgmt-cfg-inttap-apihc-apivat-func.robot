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
| ${tap_device_name}= | tap0
# Configuration which will be set and verified during tests.
| &{tap_settings}= | host-interface-name=tap_test | mac=08:00:27:c0:5d:37
| ... | id=${1}
| &{tap_settings_oper}= | device-name=tap0 | tx-ring-size=${256}
| ... | rx-ring-size=${256} | host-interface-name=tap_test
| ... | mac=08:00:27:c0:5d:37 | id=${1}
| &{tap_settings_vat}= | dev_name=tap0 | mac=08:00:27:c0:5d:37
| ... | rx_ring_sz=${256} | tx_ring_sz=${256} | id=${1}
| &{tap_settings2}= | host-interface-name=tap_test | mac=08:00:27:60:26:ab
| ... | id=${2}
| &{tap_settings2_oper}= | device-name=tap0 | tx-ring-size=${256}
| ... | rx-ring-size=${256} | host-interface-name=tap_test
| ... | mac=08:00:27:60:26:ab | id=${1}
| &{tap_settings2_vat}= | dev_name=tap0 | mac=08:00:27:60:26:ab
| ... | rx_ring_sz=${256} | tx_ring_sz=${256} | id=${1}

*** Settings ***
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/tap.robot
| ...
| Force Tags | HC_FUNC
| ...
| Suite Setup | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Documentation | *Honeycomb TAP management test suite.*

*** Test Cases ***
| TC01: Honeycomb configures TAP interface
| | [Documentation] | Check if Honeycomb API can configure a TAP interface.
| | ...
| | Given TAP Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${tap_interface}
| | And TAP Operational Data From VAT Should Be empty
| | ... | ${node} | ${tap_interface}
| | When Honeycomb creates TAP interface
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | Then TAP Operational Data From Honeycomb Should Be
| | ... | ${node} | ${tap_interface} | ${tap_settings_oper}
| | And TAP Operational Data From VAT Should Be
| | ... | ${node} | ${tap_device_name} | ${tap_settings_vat}

| TC02: Honeycomb modifies existing TAP interface configuration
| | [Documentation] | Check if Honeycomb API can re-configure an existing TAP\
| | ... | interface with new settings.
| | ...
| | Given TAP Operational Data From Honeycomb Should Be
| | ... | ${node} | ${tap_interface} | ${tap_settings_oper}
| | And TAP Operational Data From VAT Should Be
| | ... | ${node} | ${tap_device_name} | ${tap_settings_vat}
| | When Honeycomb configures TAP interface
| | ... | ${node} | ${tap_interface} | ${tap_settings2}
| | Then TAP Operational Data From Honeycomb Should Be
| | ... | ${node} | ${tap_interface} | ${tap_settings2_oper}
| | And TAP Operational Data From VAT Should Be
| | ... | ${node} | ${tap_device_name} | ${tap_settings2_vat}

| TC03: Honeycomb removes TAP interface
| | [Documentation] | Check if Honeycomb API can remove TAP interface.
| | ...
| | Given TAP Operational Data From Honeycomb Should Be
| | ... | ${node} | ${tap_interface} | ${tap_settings2_oper}
| | And TAP Operational Data From VAT Should Be
| | ... | ${node} | ${tap_device_name} | ${tap_settings2_vat}
| | When Honeycomb removes TAP interface | ${node} | ${tap_interface}
| | Then TAP Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${tap_interface}
| | And TAP Operational Data From VAT Should Be empty
| | ... | ${node} | ${tap_device_name}
