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
| ${interface}= | ${node['interfaces']['port1']['name']}
| ${bd_name}= | bd_lisp
| ${bd2_name}= | bd2_lisp
| &{bd_settings}= | flood=${True} | forward=${True} | learn=${True}
| ... | unknown-unicast-flood=${True} | arp-termination=${True}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/lisp.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Variables | resources/test_data/honeycomb/lisp.py
| Documentation | *Honeycomb Lisp test suite.*
| Suite Teardown | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb and VPP | ${node}
| Force Tags | honeycomb_sanity | honeycomb_odl

*** Test Cases ***
| TC01: Honeycomb enables Lisp feature
| | [Documentation] | Check if Honeycomb can enable the Lisp feature.
| | Given Lisp Should Not Be Configured | ${node}
| | When Honeycomb Enables Lisp | ${node}
| | Then Lisp state From Honeycomb Should Be | ${node} | enabled
| | And Lisp state From VAT Should Be | ${node} | enabled

| TC02: Honeycomb adds locator set and locator
| | [Documentation] | Check if Honeycomb can configure a locator set.
| | Given Lisp state From Honeycomb Should Be | ${node} | enabled
| | When Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | Then Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}

| TC03: Honeycomb configures Lisp - remote mapping - Bridge Domain
| | [Documentation] | Check if Honeycomb can configure a remote Lisp mapping\
| | ... | with a bridge domain.
| | Given Lisp state From Honeycomb Should Be | ${node} | enabled
| | And Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | When Honeycomb adds Lisp mapping | ${node} | ${lisp_settings_remote_bd}
| | Then Lisp mapping From Honeycomb Should Be
| | ... | ${node} | ${remote_bd_subtable}
| | And Lisp mapping From VAT Should Be
| | ... | ${node} | ${vat_remote_bd}

| TC04: Honeycomb can remove Lisp mapping
| | [Documentation] | Check if Honeycomb can remove a configured Lisp mapping.
| | Given Lisp mapping From Honeycomb Should Be
| | ... | ${node} | ${remote_bd_subtable}
| | And Lisp mapping From VAT Should Be
| | ... | ${node} | ${vat_remote_bd}
| | When Honeycomb removes all lisp mappings | ${node}
| | Then Lisp mappings from Honeycomb should not exist
| | ... | ${node}
| | And Lisp mappings from VAT should not exist
| | ... | ${node}

| TC05: Honeycomb configures Lisp - remote mapping - VRF
| | [Documentation] | Check if Honeycomb can configure a remote Lisp mapping\
| | ... | with VRF.
| | [Teardown] | Honeycomb removes all lisp mappings | ${node}
| | Given Lisp mappings from Honeycomb should not exist
| | ... | ${node}
| | And Lisp mappings from VAT should not exist
| | ... | ${node}
| | When Honeycomb adds Lisp mapping | ${node} | ${lisp_settings_remote_vrf}
| | Then Lisp mapping From Honeycomb Should Be
| | ... | ${node} | ${remote_vrf_subtable}
| | And Lisp mapping From VAT Should Be | ${node} | ${vat_remote_vrf}

| TC06: Honeycomb configures Lisp - local mapping - Bridge Domain
| | [Documentation] | Check if Honeycomb can configure a local Lisp mapping\
| | ... | with a bridge domain.
| | [Teardown] | Honeycomb removes all lisp mappings | ${node}
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | And Lisp mappings from Honeycomb should not exist
| | ... | ${node}
| | And Lisp mappings from VAT should not exist
| | ... | ${node}
| | And Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd2_name} | ${bd_settings}
| | When Honeycomb adds Lisp mapping | ${node} | ${lisp_settings_local_bd}
| | Then Lisp mapping From Honeycomb Should Be | ${node} | ${local_bd_subtable}
| | And Lisp mapping From VAT Should Be | ${node} | ${vat_local_bd}

| TC07: Honeycomb configures Lisp - local mapping - VRF
| | [Documentation] | Check if Honeycomb can configure a local Lisp mapping\
| | ... | with VRF.
| | [Teardown] | Honeycomb removes all lisp mappings | ${node}
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | And Lisp mappings from Honeycomb should not exist
| | ... | ${node}
| | And Lisp mappings from VAT should not exist
| | ... | ${node}
| | When Honeycomb adds Lisp mapping | ${node} | ${lisp_settings_local_vrf}
| | Then Lisp mapping From Honeycomb Should Be | ${node} | ${local_vrf_subtable}
| | And Lisp mapping From VAT Should Be | ${node} | ${vat_local_vrf}

| TC08: Honeycomb configures Lisp mapping with adjacency
| | [Documentation] | Check if Honeycomb can configure local and remote Lisp\
| | ... | mappings with VRF, and configure adjacency.
| | [Teardown] | Honeycomb removes all lisp mappings | ${node}
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | And Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd2_name} | ${bd_settings}
| | And Lisp mappings from Honeycomb should not exist
| | ... | ${node}
| | And Lisp mappings from VAT should not exist
| | ... | ${node}
| | And Honeycomb adds Lisp mapping | ${node} | ${lisp_settings_both_vrf}
| | When Honeycomb adds Lisp adjacency | ${node} | ${7} | remote_map_vrf
| | ... | adj01 | ${vrf_adjacency}
| | Then Lisp mapping from Honeycomb should be
| | ... | ${node} | ${adj_subtable}

| TC09: Honeycomb configures Lisp map resolver
| | [Documentation] | Check if Honeycomb can configure a Lisp map resolver.
| | Given Lisp state From Honeycomb Should Be | ${node} | enabled
| | And Lisp state From VAT Should Be | ${node} | enabled
| | When Honeycomb adds Lisp Map resolver | ${node} | 192.168.0.4
| | Then Map resolver from Honeycomb should be | ${node} | 192.168.0.4
| | And Map resolver from VAT should be | ${node} | 192.168.0.4

| TC10: Honeycomb enabled Lisp PITR feature
| | [Documentation] | Check if Honeycomb can configure the Lisp PITR feature.
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | When Honeycomb enables Lisp PITR feature | ${node} | ${locator_set}
| | Then PITR config from Honeycomb should be | ${node} | ${locator_set}
| | And PITR config from VAT should be | ${node} | ${locator_set}

| TC11: Honeycomb can remove configuration of Lisp features
| | [Documentation] | Check if Honeycomb can disable all Lisp features.
| | Given Map resolver from Honeycomb should be | ${node} | 192.168.0.4
| | And PITR config from Honeycomb should be | ${node} | ${locator_set}
| | When Honeycomb disables all Lisp features | ${node}
| | Then Lisp Should Not Be Configured | ${node}
