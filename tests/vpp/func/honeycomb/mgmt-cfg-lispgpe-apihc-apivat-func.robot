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

*** Variables***
| ${interface}= | ${node['interfaces']['port1']['name']}

*** Settings ***
| Library | resources.libraries.python.Trace.Trace
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/lisp_gpe.robot
| Variables | resources/test_data/honeycomb/lisp/lisp_gpe.py
| ...
| Documentation | *Honeycomb LISP GPE test suite.*
| ...
| Suite Setup | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Force Tags | HC_FUNC

*** Test Cases ***
| TC01: Honeycomb enables LISP GPE feature
| | [Documentation] | Check if Honeycomb can enable the LISP GPE feature.
| | ...
| | Given LISP GPE Should Not Be Configured | ${node}
| | When Honeycomb enables LISP GPE | ${node}
| | Then LISP GPE state from Honeycomb should be | ${node} | enabled
| | And LISP GPE state from VAT should be | ${node} | enabled

| TC02: Honeycomb disable LISP GPE feature
| | [Documentation] | Check if Honeycomb can enable the LISP GPE feature.
| | ...
| | [Teardown] | Honeycomb enables LISP GPE | ${node}
| | Given LISP GPE state from Honeycomb should be | ${node} | enabled
| | And LISP GPE state from VAT should be | ${node} | enabled
| | When Honeycomb disables LISP GPE | ${node}
| | Then LISP GPE state from Honeycomb should be | ${node} | disabled
| | And LISP GPE state from VAT should be | ${node} | disabled

| TC03: Honeycomb configures LISP GPE mapping - negative, IPv4
| | [Documentation] | Check if Honeycomb can configure a LISP mapping\
| | ... | with VRF.
| | ...
| | Given LISP GPE mappings from Honeycomb should not exist
| | ... | ${node}
| | When Honeycomb adds first LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip4}
| | Then LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${negative_mapping_ip4}

| TC04: Honeycomb can remove LISP GPE mapping
| | [Documentation] | Check if Honeycomb can remove a configured LISP GPE\
| | ... | mapping.
| | ...
| | Given LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${negative_mapping_ip4}
| | When Honeycomb removes LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip4['id']}
| | Then LISP GPE mappings from Honeycomb should not exist
| | ... | ${node}

| TC05: Honeycomb configures LISP GPE mapping - positive, IPv4
| | [Documentation] | Check if Honeycomb can configure a LISP mapping\
| | ... | with VRF.
| | ...
| | [Teardown] | Honeycomb removes LISP GPE mapping
| | ... | ${node} | ${positive_mapping_ip4['id']}
| | Given LISP GPE mappings from Honeycomb should not exist
| | ... | ${node}
| | When Honeycomb adds first LISP GPE mapping
| | ... | ${node} | ${positive_mapping_ip4}
| | Then LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${positive_mapping_ip4}

| TC06: Honeycomb configures LISP GPE mapping - negative, IPv6
| | [Documentation] | Check if Honeycomb can configure a LISP mapping\
| | ... | with VRF.
| | ...
| | [Tags] | HC_FUNC
| | [Teardown] | Honeycomb removes LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip6['id']}
| | Given LISP GPE mappings from Honeycomb should not exist
| | ... | ${node}
| | When Honeycomb adds first LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip6}
| | Then LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${negative_mapping_ip6}

| TC07: Honeycomb configures LISP GPE mapping - positive, IPv6
| | [Documentation] | Check if Honeycomb can configure a LISP mapping\
| | ... | with VRF.
| | ...
| | [Teardown] | Honeycomb removes LISP GPE mapping
| | ... | ${node} | ${positive_mapping_ip6['id']}
| | Given LISP GPE mappings from Honeycomb should not exist
| | ... | ${node}
| | When Honeycomb adds first LISP GPE mapping
| | ... | ${node} | ${positive_mapping_ip6}
| | Then LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${positive_mapping_ip6}

| TC08: Honeycomb can modify existing LISP GPE mappping
| | [Documentation] | Check if Honeycomb can modify and existing LISP GPE\
| | ... | mapping.
| | ...
| | [Teardown] | Honeycomb removes LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip4_edit['id']}
| | Given LISP GPE mappings from Honeycomb should not exist
| | ... | ${node}
| | When Honeycomb adds first LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip4}
| | Then LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${negative_mapping_ip4}
| | When Honeycomb adds first LISP GPE mapping | ${node}
| | ... | ${negative_mapping_ip4_edit}
| | Then LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${negative_mapping_ip4_edit}

| TC09: Honeycomb can configure multiple LISP GPE mapppings
| | [Documentation] | Check if Honeycomb can configure multiple LISP GPE\
| | ... | mappings at the same time.
| | ...
| | [Teardown] | Run Keywords
| | ... | Honeycomb removes LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip4['id']}
| | ... | AND | Honeycomb removes LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip4_2['id']}
| | Given LISP GPE mappings from Honeycomb should not exist
| | ... | ${node}
| | When Honeycomb adds first LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip4}
| | And Honeycomb adds LISP GPE mapping | ${node} | ${negative_mapping_ip4_2}
| | Then LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${negative_mapping_ip4}
| | And LISP GPE mapping from Honeycomb should be
| | ... | ${node} | ${negative_mapping_ip4_2}

| TC10: Honeycomb can disable all LISP GPE features
| | [Documentation] | Check if Honeycomb can disable all LISP GPE features.
| | ...
| | Given Honeycomb adds first LISP GPE mapping
| | ... | ${node} | ${negative_mapping_ip4}
| | When Honeycomb disables all LISP GPE features | ${node}
| | Then LISP GPE mappings from Honeycomb should not exist
| | ... | ${node}
| | And LISP GPE state from Honeycomb should be | ${node} | disabled
| | And LISP GPE state from VAT should be | ${node} | disabled

| TC11: Honeycomb can configure LISP GPE for traffic test - IPv4
| | [Documentation]
| | ... | [Top] TG-DUT1-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1.
| | ... | [Ver] Case: ip4-lispgpe-ip4 - phy2lisp
| | ... | Make TG send ICMPv4 Echo Req between its interfaces through DUT1\
| | ... | LISP GPE tunnel verify LISP encapsulation of received packet.
| | ... | [Ref] RFC6830.
| | ...
| | [Teardown] | LISPGPE functional traffic test teardown
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
| | When Honeycomb enables LISP GPE | ${node}
| | And Honeycomb adds LISP GPE mapping | ${node} | ${lisp_traffic_ip4}
| | Then send packet and verify LISP GPE encap
| | ... | ${tg_node} | ${src_ip4} | ${dst_ip4}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | ${src_rloc4} | ${dst_rloc4}

| TC12: Honeycomb can configure LISP GPE for traffic test - IPv6
| | [Documentation]
| | ... | [Top] TG-DUT1-TG.
| | ... | [Enc] Eth-IPv6-LISPGPE-IPv6-ICMPv6
| | ... | [Cfg] Configure IPv6 LISP static adjacencies on DUT1.
| | ... | [Ver] Case: ip6-lispgpe-ip6 - phy2lisp
| | ... | Make TG send ICMPv6 Echo Req between its interfaces through DUT1\
| | ... | LISP GPE tunnel verify LISP encapsulation of received packet.
| | ... | [Ref] RFC6830.
| | ...
| | [Teardown] | LISPGPE functional traffic test teardown
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
| | When Honeycomb enables LISP GPE | ${node}
| | And Honeycomb adds LISP GPE mapping | ${node} | ${lisp_traffic_ip6}
| | Then send packet and verify LISP GPE encap
| | ... | ${tg_node} | ${src_ip6} | ${dst_ip6}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | ${src_rloc6} | ${dst_rloc6}
