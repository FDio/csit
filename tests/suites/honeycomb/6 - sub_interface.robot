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

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/sub_interface.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Variables | tests/suites/honeycomb/resources/sub_interfaces.py
| Documentation | *Honeycomb sub-interface management test suite.*
| ...
| ...           | This test suite tests if it is posible to create, modify and\
| ...           | delete a sub-interface.

*** Variables ***
| ${node}= | ${nodes['DUT1']}

# Test interface 1 and its sub-interface parameters:
| ${interface}= | ${node['interfaces']['port1']['name']}
| ${sub_interface_id}= | 10
| ${sub_interface_name}= | ${interface}.${sub_interface_id}
| &{sub_interface_base_settings}=
| ... | name=${sub_interface_name}
| ... | type=v3po:sub-interface
| &{sub_interface_settings}=
| ... | super-interface=${interface}
| ... | identifier=${sub_interface_id}
| ... | vlan-type=802dot1ad
| ... | number-of-tags=2
| ... | outer-id=22
| ... | inner-id=33
| ... | match-any-outer-id=${FALSE}
| ... | match-any-inner-id=${FALSE}
| ... | exact-match=${TRUE}
| ... | default-subif=${TRUE}
| &{sub_interface_settings_wrong}=
| ... | super-interface=${interface}
| ... | identifier=${sub_interface_id}
| ... | vlan-type=WRONG_TYPE
| ... | number-of-tags=2
| ... | outer-id=22
| ... | inner-id=33
| ... | match-any-outer-id=${TRUE}
| ... | match-any-inner-id=${TRUE}
| ... | exact-match=${TRUE}
| ... | default-subif=${TRUE}

# Test interface 2 and its sub-interface parameters:
| ${interface2}= | ${node['interfaces']['port3']['name']}
| ${sub_interface2_name}= | ${interface2}.${sub_interface_id}
| &{sub_interface2_base_settings}=
| ... | name=${sub_interface2_name}
| ... | type=v3po:sub-interface
| ... | v3po:l2=&{bd_rw_settings}
| &{sub_interface2_settings}=
| ... | super-interface=${interface2}
| ... | identifier=${sub_interface_id}
| ... | vlan-type=802dot1ad
| ... | number-of-tags=2
| ... | outer-id=44
| ... | inner-id=55
| ... | match-any-outer-id=${FALSE}
| ... | match-any-inner-id=${FALSE}
| ... | exact-match=${TRUE}
| ... | default-subif=${FALSE}

*** Test Cases ***
| Honycomb creates sub-interface
| | [Documentation] | Check if Honeycomb creates a sub-interface.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration from Honeycomb should be empty
| | ... | ${node} | ${sub_interface_name}
| | And sub-interface configuration from VAT should be empty
| | ... | ${node} | ${sub_interface_name}
| | When Honeycomb creates sub-interface
| | ... | ${node} | ${interface} | ${sub_interface_id}
| | ... | ${sub_interface_base_settings} | ${sub_interface_settings}
| | Then sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_base_settings}
| | ... | ${sub_interface_settings}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_settings}

| Honeycomb adds sub-interface to bridge domain
| | [Documentation] | Check if Honeycomb adds a sub-interface to bridge domain.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_base_settings}
| | ... | ${sub_interface_settings}
| | When Honeycomb creates L2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Then Bridge domain configuration from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | When Honeycomb adds sub-interface to bridge domain
| | ... | ${node} | ${sub_interface_name} | ${bd_name} | ${sub_bd_settings}
| | Then sub-interface bridge domain configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_bd_settings}
| | And sub-interface bridge domain configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${sub_bd_settings}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_settings}

| Honeycomb sets vlan tag rewrite on sub-interface in bridge domain
| | [Documentation] | Check if Honeycomb adds vlan tag rewrite on sub-interface\
| | ... | in bridge domain.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_base_settings}
| | ... | ${sub_interface_settings}
| | And sub-interface bridge domain configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_bd_settings}
| | &{init_rw_params}= | Create dictionary | first-pushed=802dot1ad
| | ... | rewrite-operation=disabled
| | And rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${init_rw_params}
| | When Honeycomb sets rewrite tag
| | ... | ${node} | ${sub_interface_name} | ${rw_params}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params}
| | And rewrite tag configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_settings}

| Honeycomb edits vlan tag rewrite on sub-interface in bridge domain
| | [Documentation] | Check if Honeycomb updates vlan tag rewrite on\
| | ... | sub-interface in bridge domain.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_base_settings}
| | ... | ${sub_interface_settings}
| | And rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params}
| | When Honeycomb sets rewrite tag
| | ... | ${node} | ${sub_interface_name} | ${rw_params_edited}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_edited}
| | And rewrite tag configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_edited}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_settings}

| Honeycomb removes vlan tag rewrite from sub-interface
| | [Documentation] | Check if Honeycomb removes vlan tag rewrite from\
| | ... | sub-interface.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_base_settings}
| | ... | ${sub_interface_settings}
| | And rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_edited}
| | When Honeycomb removes rewrite tag
| | ... | ${node} | ${sub_interface_name}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}
| | And rewrite tag configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_settings}

| Honeycomb sets again vlan tag rewrite on sub-interface in bridge domain
| | [Documentation] | Check if Honeycomb adds vlan tag rewrite on sub-interface\
| | ... | in bridge domain if it was disabled before.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_base_settings}
| | ... | ${sub_interface_settings}
| | And rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}
| | When Honeycomb sets rewrite tag
| | ... | ${node} | ${sub_interface_name} | ${rw_params}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params}
| | And rewrite tag configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_settings}

| Honycomb deletes sub-interface
| | [Documentation] | Check if Honeycomb can delete an existing sub-interface.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_base_settings}
| | ... | ${sub_interface_settings}
| | When Honeycomb fails to remove sub-interface
| | ... | ${node} | ${sub_interface_name}
| | Then sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_base_settings}
| | ... | ${sub_interface_settings}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${sub_interface_settings}

| Honycomb creates sub-interface with bridge domain
| | [Documentation] | Check if Honeycomb creates a sub-interface with bridge\
| | ... | domain and rewrite tag configured.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration from Honeycomb should be empty
| | ... | ${node} | ${sub_interface2_name}
| | And sub-interface configuration from VAT should be empty
| | ... | ${node} | ${sub_interface2_name}
| | When Honeycomb creates L2 bridge domain
| | ... | ${node} | ${bd2_name} | ${bd2_settings}
| | And Honeycomb creates sub-interface
| | ... | ${node} | ${interface2} | ${sub_interface_id}
| | ... | ${sub_interface2_base_settings} | ${sub_interface2_settings}
| | Then sub-interface configuration with bd and rw from Honeycomb should be
| | ... | ${node} | ${sub_interface2_name} | ${sub_interface2_base_settings}
| | ... | ${sub_interface2_settings}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_interface2_name} | ${sub_interface2_settings}
| | And rewrite tag configuration from VAT should be
| | ... | ${node} | ${sub_interface2_name} | ${rw_params}

| Honeycomb sets wrong operation in vlan tag rewrite
| | [Documentation] | Negative test: Honeycomb tries to set a wrong value of\
| | ... | "rewrite-operation" parameter in "vlan-tag-rewrite". The operation\
| | ... | must fail.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration with bd and rw from Honeycomb should be
| | ... | ${node} | ${sub_interface2_name} | ${sub_interface2_base_settings}
| | ... | ${sub_interface2_settings}
| | And rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}
| | When Honeycomb fails to set wrong rewrite tag
| | ... | ${node} | ${sub_interface_name} | ${rw_params_wrong_op}
| | Then sub-interface configuration with bd and rw from Honeycomb should be
| | ... | ${node} | ${sub_interface2_name} | ${sub_interface2_base_settings}
| | ... | ${sub_interface2_settings}
| | And rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}
| | And rewrite tag configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}

| Honeycomb sets wrong first-pushed in vlan tag rewrite
| | [Documentation] | Negative test: Honeycomb tries to set a wrong value of\
| | ... | "first-pushed" parameter in "vlan-tag-rewrite". The operation must\
| | ... | fail.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given sub-interface configuration with bd and rw from Honeycomb should be
| | ... | ${node} | ${sub_interface2_name} | ${sub_interface2_base_settings}
| | ... | ${sub_interface2_settings}
| | And rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}
| | When Honeycomb fails to set wrong rewrite tag
| | ... | ${node} | ${sub_interface_name} | ${rw_params_wrong_pushed}
| | Then sub-interface configuration with bd and rw from Honeycomb should be
| | ... | ${node} | ${sub_interface2_name} | ${sub_interface2_base_settings}
| | ... | ${sub_interface2_settings}
| | And rewrite tag from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}
| | And rewrite tag configuration from VAT should be
| | ... | ${node} | ${sub_interface_name} | ${rw_params_disabled}

| Honeycomb sets interface and sub-interface up
| | [Documentation] | Honeycomb changes the state of interface up and then\
| | ... | changes the state of its sub-interface up, in this order.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | down
| | When Honeycomb sets interface state
| | ... | ${node} | ${interface} | up
| | Then interface state from Honeycomb should be
| | ... | ${node} | ${interface} | up
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | up
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | down
| | And interface state from VAT should be
| | ... | ${node} | ${sub_interface_name} | down
| | When Honeycomb sets interface state
| | ... | ${node} | ${sub_interface_name} | up
| | Then interface state from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | up
| | And Interface state from VAT should be
| | ... | ${node} | ${sub_interface_name} | up

| Honeycomb sets sub-interface down while its super-interface is up
| | [Documentation] | Honeycomb sets the sub-interface down while its\
| | ... | super-interface is up. It must be possible.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | up
| | And Interface state from VAT should be
| | ... | ${node} | ${sub_interface_name} | up
| | And interface state from Honeycomb should be
| | ... | ${node} | ${interface} | up
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | up
| | When Honeycomb sets interface state
| | ... | ${node} | ${sub_interface_name} | down
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | down
| | And Interface state from VAT should be
| | ... | ${node} | ${sub_interface_name} | down
| | And interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | down

| Honeycomb sets interface and sub-interface down
| | [Documentation] | Honeycomb changes the state of interface down and then\
| | ... | changes the state of its sub-interface down, in this order.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${interface} | up
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | up
| | When Honeycomb sets interface state
| | ... | ${node} | ${interface} | down
| | Then interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And Interface state from VAT should be
| | ... | ${node} | ${interface} | down
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | up
| | And interface state from VAT should be
| | ... | ${node} | ${sub_interface_name} | up
| | When Honeycomb sets interface state
| | ... | ${node} | ${sub_interface_name} | down
| | Then Interface state from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | down
| | And Interface state from VAT should be
| | ... | ${node} | ${sub_interface_name} | down

| Honeycomb fails to set sub-interface up while its super-interface is down
| | [Documentation] | Honeycomb tries to set the sub-interface up while its\
| | ... | super-interface is down. It must not be possible.
| | ...
| | [Tags] | honeycomb_sanity
| | ...
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | down
| | And interface state from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | down
| | And interface state from VAT should be
| | ... | ${node} | ${sub_interface_name} | down
| | When Honeycomb fails to set sub-interface up
| | ... | ${node} | ${sub_interface_name}
| | Then interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | down
| | And interface state from Honeycomb should be
| | ... | ${node} | ${sub_interface_name} | down
| | And interface state from VAT should be
| | ... | ${node} | ${sub_interface_name} | down
