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
| ${super_if}= | ${node['interfaces']['port1']['name']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/nsh.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/vxlan_gpe.robot
| Variables | resources/test_data/honeycomb/nsh.py
| Variables | resources/test_data/honeycomb/vxlan_gpe.py
| Documentation | *Honeycomb NSH test suite.*
| Suite Teardown | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb and VPP | ${node}
# disabled pending NSH version 17.04
#| Force Tags | honeycomb_sanity | honeycomb_odl

*** Test Cases ***
| TC01: Honeycomb can configure NSH entry
| | [Documentation] | Check if Honeycomb can configure an NSH entry.
| | Given NSH configuration from Honeycomb should be empty | ${node}
| | When Honeycomb adds NSH entry | ${node} | entry1 | ${nsh_entry1}
| | Then NSH entry from Honeycomb should be
| | ... | ${node} | entry1 | ${nsh_entry1_oper}

| TC02: Honeycomb can remove NSH entry
| | [Documentation] | Check if Honeycomb can remove an existing NSH entry.
| | Given NSH entry from Honeycomb should be
| | ... | ${node} | entry1 | ${nsh_entry1_oper}
| | When Honeycomb removes NSH entry | ${node} | entry1
| | Then NSH configuration from Honeycomb should be empty | ${node}

| TC03: Honeycomb can configure new NSH entry
| | [Documentation] | Check if Honeycomb can configure an NSH antry after one\
| | ... | has been deleted.
| | [Teardown] | Honeycomb removes NSH entry | ${node} | entry2
| | Given NSH configuration from Honeycomb should be empty | ${node}
| | When Honeycomb adds NSH entry | ${node} | entry2 | ${nsh_entry2}
| | Then NSH entry from Honeycomb should be
| | ... | ${node} | entry2 | ${nsh_entry2_oper}

| TC04: Honeycomb can configure multiple NSH entries at the same time
| | [Documentation] | Check if Honeycomb can configure an NSH entry when one\
| | ... | already exists.
| | [Teardown] | Honeycomb clears NSH configuration | ${node}
| | Given NSH configuration from Honeycomb should be empty | ${node}
| | When Honeycomb adds NSH entry | ${node} | entry1 | ${nsh_entry1}
| | And Honeycomb adds NSH entry | ${node} | entry2 | ${nsh_entry2}
| | Then NSH entry from Honeycomb should be
| | ... | ${node} | entry1 | ${nsh_entry1_oper}
| | And NSH entry from Honeycomb should be
| | ... | ${node} | entry2 | ${nsh_entry2_oper}

| TC05: Honeycomb can configure NSH map
| | [Documentation] | Check if Honeycomb can configure an NSH map.
| | Given NSH configuration from Honeycomb should be empty | ${node}
| | And Honeycomb creates VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if1}
| | ... | ${vxlan_gpe_base_settings1} | ${vxlan_gpe_settings1}
| | When Honeycomb adds NSH entry | ${node} | entry1 | ${nsh_entry1}
| | And Honeycomb adds NSH map | ${node} | map1 | ${nsh_map1}
| | Then NSH map from Honeycomb should be | ${node} | map1 | ${nsh_map1_oper}

| TC06: Honeycomb can remove NSH map
| | [Documentation] | Check if Honeycomb can remove an existing NSH map.
| | Given NSH entry from Honeycomb should be
| | ... | ${node} | entry1 | ${nsh_entry1_oper}
| | And VxLAN GPE configuration from Honeycomb should be
| | ... | ${node} | ${vxlan_gpe_if1}
| | ... | ${vxlan_gpe_base_settings1} | ${vxlan_gpe_settings1}
| | And NSH map from Honeycomb should be | ${node} | map1 | ${nsh_map1_oper}
| | When Honeycomb removes NSH map | ${node} | map1
| | Then NSH map from Honeycomb should not exist | ${node} | map1
| | And NSH entry from Honeycomb should be
| | ... | ${node} | entry1 | ${nsh_entry1_oper}

| TC07: Honeycomb can modify existing NSH map
| | [Documentation] | Check if Honeycomb can configure an NSH map after one\
| | ... | has been deleted.
| | [Teardown] | Honeycomb removes NSH map | ${node} | map1_edit
| | Given NSH map from Honeycomb should not exist | ${node} | map1_edit
| | And NSH entry from Honeycomb should be
| | ... | ${node} | entry1 | ${nsh_entry1_oper}
| | And VxLAN GPE configuration from Honeycomb should be
| | ... | ${node} | ${vxlan_gpe_if1}
| | ... | ${vxlan_gpe_base_settings1} | ${vxlan_gpe_settings1}
| | When Honeycomb adds NSH map | ${node} | map1_edit | ${nsh_map1_edit}
| | Then NSH map from Honeycomb should be
| | ... | ${node} | map1_edit | ${nsh_map1_edit_oper}
| | And NSH entry from Honeycomb should be
| | ... | ${node} | entry1 | ${nsh_entry1_oper}

| TC08: Honeycomb can configure multiple NSH maps at the same time
| | [Documentation] | Check if Honeycomb can configure and NSH map when one\
| | ... | already exists.
| | [Teardown] | Run Keywords
| | ... | Honeycomb clears NSH configuration | ${node} | AND
| | ... | Honeycomb removes VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if1} | AND
| | ... | Honeycomb removes VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if2}
| | Given NSH map from Honeycomb should not exist | ${node} | map2
| | And NSH entry from Honeycomb should be
| | ... | ${node} | entry1 | ${nsh_entry1_oper}
| | And VxLAN GPE configuration from Honeycomb should be
| | ... | ${node} | ${vxlan_gpe_if1}
| | ... | ${vxlan_gpe_base_settings1} | ${vxlan_gpe_settings1}
| | And Honeycomb creates VxLAN GPE interface
| | ... | ${node} | ${vxlan_gpe_if2}
| | ... | ${vxlan_gpe_base_settings2} | ${vxlan_gpe_settings2}
| | When Honeycomb adds NSH map | ${node} | map1 | ${nsh_map1}
| | And Honeycomb adds NSH map | ${node} | map2 | ${nsh_map2}
| | Then NSH map from Honeycomb should be
| | ... | ${node} | map1 | ${nsh_map1_oper}
| | And NSH map from Honeycomb should be
| | ... | ${node} | map2 | ${nsh_map2_oper}
