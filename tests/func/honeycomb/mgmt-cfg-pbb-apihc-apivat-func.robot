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
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/provider_backbone_bridge.robot
| Variables | resources/test_data/honeycomb/pbb/pbb.py
| Documentation | *Honeycomb provider backbone bridge test suite.*
#| Suite Teardown | Run Keyword If Any Tests Failed
#| ... | Restart Honeycomb and VPP | ${node}
| Force Tags | honeycomb_sanity | honeycomb_odl

*** Test Cases ***
# TODO: add verifications once operational data or VPP dump is available.
| TC01: Honeycomb sets PBB sub-interface
| | [Documentation] | Honeycomb creates a new PBB sub-interface.
| | ...
| | Honeycomb creates PBB sub interface | ${node} | ${super_if}
| | ... | ${cfg_pbb_sub_if_1}

| TC02: Honeycomb modifies existing PBB sub-interface
| | [Documentation] | Honeycomb modifies an existing PBB sub-interface.
| | ...
| | Honeycomb creates PBB sub interface | ${node} | ${super_if}
| | ... | ${cfg_pbb_sub_if_1_mod}

| TC03: Honeycomb deletes existing PBB sub-interface
| | [Documentation] | Honeycomb deletes an existing PBB sub-interface.
| | ...
| | Honeycomb Removes PBB sub interface
| | ... | ${node} | ${super_if}

| TC04: Honeycomb fails to set wrong destination-address for new PBB sub-interface
| | [Documentation] | Honeycomb fails to create a new PBB sub-interface with\
| | ... | wrong value of parameter destination-address, type yang:mac-address.
| | ...
| | Honeycomb fails to create PBB sub interface | ${node} | ${super_if}
| | ... | ${cfg_pbb_sub_if_wrong_dst_addr}

| TC05: Honeycomb fails to set wrong source-address for new PBB sub-interface
| | [Documentation] | Honeycomb fails to create a new PBB sub-interface with\
| | ... | wrong value of parameter source-address, type yang:mac-address.
| | ...
| | Honeycomb fails to create PBB sub interface | ${node} | ${super_if}
| | ... | ${cfg_pbb_sub_if_wrong_src_addr}

| TC06: Honeycomb fails to set wrong b-vlan-tag-vlan-id for new PBB sub-interface
| | [Documentation] | Honeycomb fails to create a new PBB sub-interface with\
| | ... | wrong value of parameter b-vlan-tag-vlan-id, type uint16, 12 bit\
| | ... | range, range 1..4095.
| | ...
| | Honeycomb fails to create PBB sub interface | ${node} | ${super_if}
| | ... | ${cfg_pbb_sub_if_wrong_vlan_tag}

| TC07: Honeycomb fails to set wrong i-tag-isid for new PBB sub-interface
| | [Documentation] | Honeycomb fails to create a new PBB sub-interface with\
| | ... | wrong value of parameter i-tag-isid, type uint32, 24 bit range,\
| | ... | range 1..16777215.
| | ...
| | Honeycomb fails to create PBB sub interface | ${node} | ${super_if}
| | ... | ${cfg_pbb_sub_if_wrong_i_tag}

| TC08: Honeycomb fails to create new PBB sub-interface without vlan tag
| | [Documentation] | Honeycomb fails to create a new PBB sub-interface without\
| | ... | parameter b-vlan-tag-vlan-id.
| | ...
| | Honeycomb fails to create PBB sub interface | ${node} | ${super_if}
| | ... | ${cfg_pbb_sub_if_no_vlan_tag}
