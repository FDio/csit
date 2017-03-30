# Copyright (c) 2017 Cisco and/or its affiliates.
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
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/slaac.robot
| Suite Teardown
| ... | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Force Tags | honeycomb_sanity | honeycomb_odl
| Documentation | *Honeycomb SLAAC management test suite.*
| Variables | resources/test_data/honeycomb/slaac_variables.py

*** Test Cases ***
| TC01: Honeycomb can configure SLAAC without teardown
| | [Documentation] | Checks if Honeycomb can congigure SLAAC.
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data}
| | Then SLAAC configuration from Honeycomb should be | ${node}
| | ... | ${interface} | ${slaac_data}

| TC02: Honeycomb can disable SLAAC
| | [Documentation] | Checks if Honeycomb can disable SLAAC.
| | Given SLAAC configuration from Honeycomb should be | ${node}
| | ... | ${interface} | ${slaac_data}
| | When Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Then SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}

| TC03: Honeycomb can configure SLAAC with teardown
| | [Documentation] | Checks if Honeycomb can congigure SLAAC.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data}
| | Then SLAAC configuration from Honeycomb should be | ${node}
| | ... | ${interface} | ${slaac_data}

| TC04: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_01}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_01}

| TC05: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_02}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_02}

| TC06: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_03}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_03}

| TC07: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_04}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_04}

| TC08: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_05}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_05}

| TC09: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_06}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_06}

| TC10: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_07}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_07}

| TC11: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_08}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_08}

| TC12: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_09}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_09}

| TC13: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_10}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_10}

| TC14: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_11}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_11}

| TC15: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_12}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_12}

| TC16: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_13}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_13}

| TC17: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_14}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_14}

| TC18: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Given SLAAC configuration from Honeycomb should be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface ipv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_15}
| | Then SLAAC configuration from Honeycomb should be | ${node} | ${interface}
| | ... | ${slaac_data_15}
