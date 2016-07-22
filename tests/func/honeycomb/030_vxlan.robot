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
| ${vx_interface}= | vx_tunnel_test
# Configuration which will be set and verified during tests.
| &{vxlan_settings}= | src=192.168.0.2 | dst=192.168.0.3 | vni=${88}
| ... | encap-vrf-id=${0}
| &{vxlan_settings2}= | src=192.168.0.4 | dst=192.168.0.5 | vni=${47}
| ... | encap-vrf-id=${0}
| &{vxlan_settings_ipv6}= | src=10::10 | dst=10::11 | vni=${88}
| ... | encap-vrf-id=${0}
| &{vxlan_settings_ipv6_long}= | src=10:0:0:0:0:0:0:10 | dst=10:0:0:0:0:0:0:11
| ... | vni=${88} | encap-vrf-id=${0}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/vxlan.robot
# import additional VxLAN settings from resource file
| Variables | tests/suites/honeycomb/resources/vxlan.py
| Force Tags | honeycomb_sanity
| Documentation | *Honeycomb VxLAN management test suite.*
| ...
| ... | Test suite uses the first interface of the first DUT node.

*** Test Cases ***
| Honeycomb configures VxLAN tunnel
| | [Documentation] | Check if Honeycomb API can configure VxLAN settings.
| | Given VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${vx_interface}
| | And VxLAN configuration from VAT should be empty | ${node}
| | When Honeycomb sets interface VxLAN configuration
| | ... | ${node} | ${vx_interface} | ${vxlan_settings}
| | Then VxLAN configuration from Honeycomb should be
| | ... | ${node} | ${vx_interface} | ${vxlan_settings}
| | And VxLAN configuration from VAT should be
| | ... | ${node} | ${vxlan_settings}

| Honeycomb disables VxLAN tunnel
| | [Documentation] | Check if Honeycomb API can reset VxLAN configuration.
| | Given VxLAN configuration from Honeycomb should be
| | ... | ${node} | ${vx_interface} | ${vxlan_settings}
| | And VxLAN configuration from VAT should be
| | ... | ${node} | ${vxlan_settings}
| | When Honeycomb removes VxLAN tunnel settings | ${node} | ${vx_interface}
| | Then VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${vx_interface}
| | And VxLAN configuration from VAT should be empty | ${node}

Honeycomb can configure VXLAN tunnel after one has been disabled
| | [Documentation] | Check if Honeycomb API can configure VxLAN settings again\
| | ... | after previous settings have been removed.
| | [Teardown] | Honeycomb removes VxLAN tunnel settings
| | ... | ${node} | ${vx_interface}
| | Given VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${vx_interface}
| | And VxLAN configuration from VAT should be empty | ${node}
| | When Honeycomb sets interface VxLAN configuration
| | ... | ${node} | ${vx_interface} | ${vxlan_settings2}
| | Then VxLAN configuration from Honeycomb should be
| | ... | ${node} | ${vx_interface} | ${vxlan_settings2}
| | And VxLAN configuration from VAT should be
| | ... | ${node} | ${vxlan_settings2}

| Honeycomb does not set VxLAN configuration on another interface type
| | [Documentation] | Check if Honeycomb API prevents setting VxLAN\
| | ... | on incorrect interface.
| | Given VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | And VxLAN configuration from VAT should be empty | ${node}
| | When Honeycomb fails setting VxLan on different interface type
| | ... | ${node} | ${interface} | ${vxlan_settings2}
| | Then VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | And VxLAN configuration from VAT should be empty
| | ... | ${node}

| Honeycomb does not set invalid VxLAN configuration
| | [Documentation] | Check if Honeycomb API prevents setting incorrect VxLAN\
| | ... | settings.
| | Given VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${vx_interface}
| | And VxLAN configuration from VAT should be empty | ${node}
| | When Honeycomb fails setting invalid VxLAN configuration
| | ... | ${node} | ${vx_interface} | ${vxlan_invalid}
| | Then VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${vx_interface}

| Honeycomb configures VxLAN tunnel with ipv6
| | [Documentation] | Check if Honeycomb API can configure VxLAN with\
| | ... | ipv6 settings.
| | [Teardown] | Honeycomb removes VxLAN tunnel settings
| | ... | ${node} | ${vx_interface}
| | Given VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${vx_interface}
| | And VxLAN configuration from VAT should be empty | ${node}
| | When Honeycomb sets interface VxLAN configuration
| | ... | ${node} | ${vx_interface} | ${vxlan_settings_ipv6}
| | Then VxLAN configuration from Honeycomb should be
| | ... | ${node} | ${vx_interface} | ${vxlan_settings_ipv6_long}
| | And VxLAN configuration from VAT should be
| | ... | ${node} | ${vxlan_settings_ipv6}
