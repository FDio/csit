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
| &{tap_settings}= | tap-name=tap_test | mac=08:00:27:c0:5d:37
| ... | device-instance=${1}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/tap.robot
| Resource | resources/libraries/robot/honeycomb/notifications.robot
| Suite Setup | Run keywords
| ... | Honeycomb sets interface state
| ... | ${node} | ${interface} | down | AND
| ... | Honeycomb creates TAP interface
| ... | ${node} | ${tap_interface} | ${tap_settings}
| Documentation | *Honeycomb notifications test suite.*
| Force Tags | honeycomb_sanity

*** Test Cases ***
| Honeycomb sends notification on interface state change
| | [Documentation] | Check if Honeycomb sends a state-changed notification\
| | ... | when the state of an interface is changed.
| | Given Interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And Interface state from VAT should be | ${node} | ${interface} | down
| | And Notification listener is established | ${node}
| | When Honeycomb sets interface state | ${node} | ${interface} | up
| | Then Honeycomb should send interface state notification | ${interface} | up
| | When Honeycomb sets interface state | ${node} | ${interface} | down
| | And Honeycomb should send interface state notification | ${interface} | down

| Honeycomb sends notification on interface deletion
| | [Documentation] | Check if Honeycomb sends an interface-deleted notification
| | ... | when an interface is deleted.
| | Given TAP configuration from Honeycomb should be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | And TAP configuration from VAT should be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | And Notification listener is established | ${node}
| | When Honeycomb removes TAP interface | ${node} | ${tap_interface}
| | Then Honeycomb should send interface deleted notification | ${tap_interface}
