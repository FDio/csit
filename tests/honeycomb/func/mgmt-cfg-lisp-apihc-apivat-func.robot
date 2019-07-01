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
| @{ip_addresses}= | 192.168.0.5 | 192.168.0.6 | 192.168.0.7 | 192.168.0.8
| ${state}= | enabled
| ${interface}= | ${node['interfaces']['port1']['name']}
| ${bd_name}= | bd_lisp
| ${bd2_name}= | bd2_lisp
| &{bd_settings}= | flood=${True} | forward=${True} | learn=${True}
| ... | unknown-unicast-flood=${True} | arp-termination=${True}

*** Settings ***
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/lisp.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Variables | resources/test_data/honeycomb/lisp/lisp.py
| ...
| Documentation | *Honeycomb Lisp test suite.*
| ...
| Suite Setup | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Force Tags | HC_FUNC

*** Test Cases ***
| TC01: Honeycomb enables LISP feature
| | [Documentation] | Check if Honeycomb can enable the LISP feature.
| | ...
| | Given LISP Should Not Be Configured | ${node}
| | When Honeycomb enables LISP | ${node}
| | Then LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}

| TC02: Honeycomb adds locator set and locator
| | [Documentation] | Check if Honeycomb can configure a locator set.
| | ...
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | When Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | Then Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}

| TC15: Honeycomb can remove configuration of LISP features
| | [Documentation] | Check if Honeycomb can disable all LISP features.
| | ...
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | When Honeycomb disables all LISP features | ${node}
| | Then LISP Should Not Be Configured | ${node}

| TC03: Honeycomb configures LISP - remote mapping - Bridge Domain
| | [Documentation] | Check if Honeycomb can configure a remote LISP mapping\
| | ... | with a bridge domain.
| | ...
| | Given Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | And Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | When Honeycomb adds LISP mapping | ${node} | ${lisp_settings_remote_bd}
| | Then LISP mapping from Honeycomb should be
| | ... | ${node} | ${remote_bd_subtable}
| | And LISP mapping from VAT should be
| | ... | ${node} | ${vat_remote_bd}

| TC04: Honeycomb can remove LISP mapping
| | [Documentation] | Check if Honeycomb can remove a configured LISP mapping.
| | ...
| | Given LISP mapping from Honeycomb should be
| | ... | ${node} | ${remote_bd_subtable}
| | And LISP mapping from VAT should be
| | ... | ${node} | ${vat_remote_bd}
| | When Honeycomb removes all LISP mappings | ${node}
| | Then LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}

| TC05: Honeycomb configures LISP - remote mapping - VRF
| | [Documentation] | Check if Honeycomb can configure a remote LISP mapping\
| | ... | with VRF.
| | ...
| | [Teardown] | Honeycomb removes all LISP mappings | ${node}
| | ...
| | Given LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}
| | When Honeycomb adds LISP mapping | ${node} | ${lisp_settings_remote_vrf}
| | Then LISP mapping from Honeycomb should be
| | ... | ${node} | ${remote_vrf_subtable}
| | And LISP mapping from VAT should be | ${node} | ${vat_remote_vrf}

| TC06: Honeycomb configures LISP - local mapping - Bridge Domain
| | [Documentation] | Check if Honeycomb can configure a local LISP mapping\
| | ... | with a bridge domain.
| | ...
| | [Teardown] | Honeycomb removes all LISP mappings | ${node}
| | ...
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

| TC07: Honeycomb configures LISP - local mapping - VRF
| | [Documentation] | Check if Honeycomb can configure a local LISP mapping\
| | ... | with VRF.
| | ...
| | [Teardown] | Honeycomb removes all LISP mappings | ${node}
| | ...
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | And LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}
| | When Honeycomb adds LISP mapping | ${node} | ${lisp_settings_local_vrf}
| | Then LISP mapping from Honeycomb should be | ${node} | ${local_vrf_subtable}
| | And LISP mapping from VAT should be | ${node} | ${vat_local_vrf}

| TC08: Honeycomb configures LISP mapping with adjacency
| | [Documentation] | Check if Honeycomb can configure local and remote LISP\
| | ... | mappings with VRF, and configure adjacency.
| | ...
| | [Teardown] | Honeycomb disables all LISP features | ${node}
| | ...
| | Given Locator Set From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${locator_set}
| | And LISP mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP mappings from VAT should not exist
| | ... | ${node}
| | And Honeycomb adds LISP mapping | ${node} | ${lisp_settings_both_vrf}
| | When Honeycomb adds LISP adjacency | ${node} | ${7} | remote_map_vrf
| | ... | adj01 | ${vrf_adjacency}
| | Then LISP mapping from Honeycomb should be
| | ... | ${node} | ${adj_subtable}

| TC09: Honeycomb configures LISP Map Resolver
| | [Documentation] | Check if Honeycomb can configure a LISP Map Resolver.
| | ...
| | [Teardown] | Honeycomb disables all LISP features | ${node}
| | Given Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb adds LISP Map Resolver | ${node} | ${ip_address}
| | Then Map Resolver from Honeycomb should be | ${node} | ${ip_address}
| | And Map Resolver from VAT should be | ${node} | ${ip_address}

| TC10: Honeycomb configures LISP Map Server
| | [Documentation] | Check if Honeycomb can configure a LISP Map Server.
| | ...
| | [Teardown] | Honeycomb disables all LISP features | ${node}
| | Given Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb adds LISP Map Server | ${node} | @{ip_addresses}
| | Then Map Server from Honeycomb should be | ${node} | @{ip_addresses}
| | And Map Server from VAT should be | ${node} | @{ip_addresses}

| TC11: Honeycomb configures LISP PETR configuration
| | [Documentation] | Check if Honeycomb can configure LISP
| | ... | PETR configuration.
| | ...
| | [Teardown] | Honeycomb disables all LISP features | ${node}
| | Given Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb enables LISP PETR feature | ${node} | ${ip_address}
| | Then PETR configuration from Honeycomb should be | ${node} | ${ip_address}
| | And PETR configuration from VAT should be | ${node} | enabled

| TC12: Honeycomb configures LISP RLOC Probing
| | [Documentation] | Check if Honeycomb can configure LISP RLOC Probing.
| | ...
| | [Teardown] | Honeycomb disables all LISP features | ${node}
| | Given Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb enables LISP RLOC feature | ${node}
| | Then RLOC Probing from Honeycomb should be | ${node} | ${True}
| | And RLOC Probing from VAT should be | ${node} | enabled

| TC13: Honeycomb configures LISP Map Register
| | [Documentation] | Check if Honeycomb can configure a LISP Map Register.
| | ...
| | [Teardown] | Honeycomb disables all LISP features | ${node}
| | Given Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | Given LISP state from Honeycomb should be | ${node} | ${state}
| | And LISP state from VAT should be | ${node} | ${state}
| | When Honeycomb adds LISP Map Register | ${node} | ${True}
| | Then Map Register from Honeycomb should be | ${node} | ${True}
| | And Map Register from VAT should be | ${node} | enabled

| TC14: Honeycomb enabled LISP PITR feature
| | [Documentation] | Check if Honeycomb can configure the LISP PITR feature.
| | ...
# HC2VPP-263 Locator set reference in operational data is incorrect
| | [Tags] | EXPECTED_FAILING
| | [Teardown] | Honeycomb disables all LISP features | ${node}
| | Given Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${interface} | ${locator_set}
| | When Honeycomb enables LISP PITR feature | ${node} | ${locator_set}
# | | Then PITR config from Honeycomb should be | ${node} | ${locator_set}
| | Then PITR config from VAT should be | ${node} | ${locator_set}

| TC16: Honeycomb can configure LISP for traffic test - IPv4
| | [Documentation]
| | ... | [Top] TG-DUT1-TG.
| | ... | [Enc] Eth-IPv4-LISP.
| | ... | [Cfg] On DUT1 configure IPv4 LISP static adjacencies with TG.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces through\
| | ... | DUT1 and verify LISP encapsulation of received packet.
| | ... | [Ref] RFC6830.
| | ...
| | [Teardown] | LISP Functional Traffic Test Teardown
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Honeycomb configures interface state
| | ... | ${dut_node} | ${dut_to_tg_if1} | up
| | And Honeycomb configures interface state
| | ... | ${dut_node} | ${dut_to_tg_if2} | up
| | And Honeycomb sets interface IPv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip4} | ${prefix_len4}
| | And Honeycomb sets interface IPv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip4} | ${prefix_len4}
| | And Honeycomb adds interface IPv4 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_ip4} | ${tg_to_dut_if1_mac}
| | And Honeycomb adds interface IPv4 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${tg_to_dut_if2_ip4} | ${tg_to_dut_if2_mac}
| | When Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${dut_to_tg_if2} | ${locator_set}
| | And Honeycomb adds LISP mapping | ${node} | ${lisp_traffic_ip4}
| | Then send packet and verify LISP encap
| | ... | ${tg_node} | ${src_ip4} | ${dst_ip4}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | ${src_rloc4} | ${dst_rloc4}

| TC17: Honeycomb can configure LISP for traffic test - IPv6
| | [Documentation]
| | ... | [Top] TG-DUT1-TG.
| | ... | [Enc] Eth-IPv6-LISP.
| | ... | [Cfg] On DUT1 configure IPv6 LISP static adjacencies with TG.
| | ... | [Ver] Make TG send ICMPv6 Echo Req between its interfaces through\
| | ... | DUT1 and verify LISP encapsulation of received packet.
| | ... | [Ref] RFC6830.
| | ...
| | [Teardown] | LISP Functional Traffic Test Teardown
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Honeycomb configures interface state
| | ... | ${dut_node} | ${dut_to_tg_if1} | up
| | And Honeycomb configures interface state
| | ... | ${dut_node} | ${dut_to_tg_if2} | up
| | And Honeycomb sets interface IPv6 address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip6} | ${prefix_len6}
| | And Honeycomb sets interface IPv6 address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip6} | ${prefix_len6}
| | And Honeycomb adds interface IPv6 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_ip6} | ${tg_to_dut_if1_mac}
| | And Honeycomb adds interface IPv6 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${tg_to_dut_if2_ip6} | ${tg_to_dut_if2_mac}
| | When Honeycomb enables LISP | ${node}
| | And Honeycomb adds locator set | ${node} | ${dut_to_tg_if2} | ${locator_set}
| | And Honeycomb adds LISP mapping | ${node} | ${lisp_traffic_ip6}
| | Then send packet and verify LISP encap
| | ... | ${tg_node} | ${src_ip6} | ${dst_ip6}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | ${src_rloc6} | ${dst_rloc6}

| TC18: Honeycomb configures LISP Map Request Mode
| | [Documentation] | Check if Honeycomb can configure LISP Map Request mode.
| | ... | Note: Map Request Mode cannot be removed once configured.
| | ...
| | [Teardown] | Honeycomb disables LISP | ${node}
| | ...
| | Given Honeycomb Enables LISP | ${node}
| | When Honeycomb sets LISP Map Request Mode | ${node} | ${True}
| | Then Map Request Mode from Honeycomb should be
| | ... | ${node} | source-destination
| | And Map Request Mode from VAT should be | ${node} | src-dst
