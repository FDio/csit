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
| ${ip_address}= | 192.168.0.4
| @{ip_addresses}= | 192.168.0.4 | 192.168.0.5 | 192.168.0.6 | 192.168.0.7
| ${state}= | enabled
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
| Force Tags | HC_FUNC

*** Test Cases ***
| TC01: Honeycomb enables LISP feature
| | [Documentation] | Check if Honeycomb can enable the Lisp feature.
| | Given Lisp Should Not Be Configured | ${node}
| | When Honeycomb enables LISP | ${node}
| | Then LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}

| TC02: Honeycomb adds locator set and locator
| | [Documentation] | Check if Honeycomb can configure a locator set.
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | When Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | Then Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}

| TC03: Honeycomb configures Lisp - remote mapping - Bridge Domain
| | [Documentation] | Check if Honeycomb can configure a remote Lisp mapping\
| | ... | with a bridge domain.
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | When Honeycomb adds LISP mapping | ${node} | ${lisp_settings_remote_bd}
| | Then LISP mapping from Honeycomb should be
| | ... | ${node} | ${remote_bd_subtable}
| | And LISP mapping from VAT should be
| | ... | ${node} | ${vat_remote_bd}

| TC04: Honeycomb can remove Lisp mapping
| | [Documentation] | Check if Honeycomb can remove a configured Lisp mapping.
| | Given LISP mapping from Honeycomb should be
| | ... | ${node} | ${remote_bd_subtable}
| | And LISP mapping from VAT should be
| | ... | ${node} | ${vat_remote_bd}
| | When Honeycomb removes all lisp mappings | ${node}
| | Then LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}

| TC05: Honeycomb configures Lisp - remote mapping - VRF
| | [Documentation] | Check if Honeycomb can configure a remote Lisp mapping\
| | ... | with VRF.
| | [Teardown] | Honeycomb removes all lisp mappings | ${node}
| | Given LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}
| | When Honeycomb adds LISP mapping | ${node} | ${lisp_settings_remote_vrf}
| | Then LISP mapping from Honeycomb should be
| | ... | ${node} | ${remote_vrf_subtable}
| | And LISP mapping from VAT should be | ${node} | ${vat_remote_vrf}

| TC06: Honeycomb configures Lisp - local mapping - Bridge Domain
| | [Documentation] | Check if Honeycomb can configure a local Lisp mapping\
| | ... | with a bridge domain.
| | [Teardown] | Honeycomb removes all lisp mappings | ${node}
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | And LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}
| | And Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd2_name} | ${bd_settings}
| | When Honeycomb adds LISP mapping | ${node} | ${lisp_settings_local_bd}
| | Then LISP mapping from Honeycomb should be | ${node} | ${local_bd_subtable}
| | And LISP mapping from VAT should be | ${node} | ${vat_local_bd}

| TC07: Honeycomb configures Lisp - local mapping - VRF
| | [Documentation] | Check if Honeycomb can configure a local Lisp mapping\
| | ... | with VRF.
| | [Teardown] | Honeycomb removes all lisp mappings | ${node}
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | And LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}
| | When Honeycomb adds LISP mapping | ${node} | ${lisp_settings_local_vrf}
| | Then LISP mapping from Honeycomb should be | ${node} | ${local_vrf_subtable}
| | And LISP mapping from VAT should be | ${node} | ${vat_local_vrf}

| TC08: Honeycomb configures Lisp mapping with adjacency
| | [Documentation] | Check if Honeycomb can configure local and remote Lisp\
| | ... | mappings with VRF, and configure adjacency.
| | [Teardown] | Honeycomb removes all lisp mappings | ${node}
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | And Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd2_name} | ${bd_settings}
| | And LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}
| | And Honeycomb adds LISP mapping | ${node} | ${lisp_settings_both_vrf}
| | When Honeycomb adds LISP adjacency | ${node} | ${7} | remote_map_vrf
| | ... | adj01 | ${vrf_adjacency}
| | Then Lisp mapping from Honeycomb should be
| | ... | ${node} | ${adj_subtable}

| TC09: Honeycomb configures Lisp Map Resolver
| | [Documentation] | Check if Honeycomb can configure a Lisp Map Resolver.
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb adds Lisp Map Resolver | ${node} | ${ip_address}
| | Then Map Resolver from Honeycomb should be | ${node} | ${ip_address}
| | And Map Resolver from VAT should be | ${node} | ${ip_address}

| TC10: Honeycomb configures Lisp Map Server
| | [Documentation] | Check if Honeycomb can configure a Lisp Map Server.
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb adds Lisp Map Server | ${node} | @{ip_addresses}
| | Then Map Server from Honeycomb should be | ${node} | @{ip_addresses}
| | And Map Server from VAT should be | ${node} | @{ip_addresses}

| TC11: Honeycomb configures Lisp PETR configuration
| | [Documentation] | Check if Honeycomb can configure Lisp
| | ... | PETR configuration.
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb enables LISP PETR feature | ${node} | ${ip_address}
| | Then PETR configuration from Honeycomb should be | ${node} | ${ip_address}
| | And PETR configuration from VAT should be | ${node} | enabled

| TC12: Honeycomb configures Lisp RLOC Probing
| | [Documentation] | Check if Honeycomb can configure Lisp RLOC Probing.
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb enables LISP RLOC feature | ${node}
| | Then RLOC Probing from Honeycomb should be | ${node} | ${True}
| | And RLOC Probing from VAT should be | ${node} | enabled

| TC13: Honeycomb configures Lisp Map Register
| | [Documentation] | Check if Honeycomb can configure a Lisp Map Register.
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb adds Lisp Map Register | ${node} | ${True}
| | Then Map Register from Honeycomb should be | ${node} | ${True}
| | And Map Register from VAT should be | ${node} | enabled

| TC14: Honeycomb enabled Lisp PITR feature
| | [Documentation] | Check if Honeycomb can configure the Lisp PITR feature.
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | When Honeycomb enables LISP PITR feature | ${node} | ${locator_set}
| | Then PITR config from Honeycomb should be | ${node} | ${locator_set}
| | And PITR config from VAT should be | ${node} | ${locator_set}

| TC15: Honeycomb can remove configuration of Lisp features
| | [Documentation] | Check if Honeycomb can disable all Lisp features.
| | Given Map resolver from Honeycomb should be | ${node} | ${ip_address}
| | And PITR config from Honeycomb should be | ${node} | ${locator_set}
| | When Honeycomb disables all LISP features | ${node}
| | Then Lisp Should Not Be Configured | ${node}

| TC16: Honeycomb configures Lisp Map Request Mode
| | [Documentation] | Check if Honeycomb can configure Lisp Map Request mode.
| | ... | Note: Map Request Mode cannot be removed once configured.
| | [Teardown] | Honeycomb disables LISP | ${node}
| | Given Honeycomb enables LISP | ${node}
| | When Honeycomb sets Lisp Map Request Mode | ${node} | ${True}
| | Then Map Request Mode from Honeycomb should be
| | ... | ${node} | source-destination
| | And Map Request Mode from VAT should be | ${node} | src-dst
