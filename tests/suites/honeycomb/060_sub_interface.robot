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
| Suite Teardown | Honeycomb removes all bridge domains | ${node}
| Force Tags | honeycomb_sanity
| Documentation | *Honeycomb sub-interface management test suite.*
| ...
| ...           | This test suite tests if it is posible to create, modify and \
| ...           | delete a sub-interface.

*** Variables ***
# Test interface 1 and its sub-interface parameters:
| ${super_if}= | ${node['interfaces']['port1']['name']}
| ${sub_if_id}= | ${sub_if_1_settings['identifier']}
| ${sub_if_name}= | ${super_if}.${sub_if_id}

# IP addresses configured on sub-interface during tests
| &{ipv4}=   | address=192.168.0.4 | netmask=255.255.255.0 | prefix-lenght=${24}
| &{ipv4_2}= | address=192.168.0.5 | netmask=255.255.0.0 | prefix-lenght=${16}

*** Test Cases ***
| Honycomb creates sub-interface
| | [Documentation] | Check if Honeycomb creates a sub-interface.
| | ...
| | Given interface state is | ${node} | ${super_if} | down
| | And sub-interface configuration from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | And interface configuration from VAT should be empty
| | ... | ${node} | ${sub_if_name}
| | When Honeycomb creates sub-interface | ${node} | ${super_if}
| | ... | ${sub_if_1_match} | ${sub_if_1_tags} | ${sub_if_1_settings}
| | Then run keyword and continue on failure
| | ... | Sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${sub_if_1_oper}
| | And run keyword and continue on failure
| | ... | Sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_if_name} | ${sub_if_1_oper}
| | And sub-interface indices from Honeycomb and VAT should correspond
| | ... | ${node} | ${super_if} | ${sub_if_id}

| Honeycomb sets interface and sub-interface up
| | [Documentation] | Honeycomb changes the state of interface up and then \
| | ... | changes the state of its sub-interface up, in this order.
| | ...
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | down
| | And interface state from VAT should be
| | ... | ${node} | ${super_if} | down
| | When Honeycomb sets interface state
| | ... | ${node} | ${super_if} | up
| | Then interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | up
| | And interface state from VAT should be
| | ... | ${node} | ${super_if} | up
| | Given run keyword and continue on failure
| | ... | Sub-interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | down | down
| | And run keyword and continue on failure
| | ... | Sub-interface state from VAT should be
| | ... | ${node} | ${sub_if_name} | down | down
| | When Honeycomb sets the sub-interface up
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | Then run keyword and continue on failure
| | ... | Sub-interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | up | up
| | And sub-interface state from VAT should be
| | ... | ${node} | ${sub_if_name} | up | up

| Honeycomb sets sub-interface down while its super-interface is up
| | [Documentation] | Honeycomb sets the sub-interface down while its \
| | ... | super-interface is up. It must be possible.
| | ...
| | [Teardown] | Set super and sub interfaces up
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given sub-interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | up | up
| | And sub-interface state from VAT should be
| | ... | ${node} | ${sub_if_name} | up | up
| | And interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | up
| | And interface state from VAT should be
| | ... | ${node} | ${super_if} | up
| | When Honeycomb sets the sub-interface down
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | Then sub-interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | down | down
| | And sub-interface state from VAT should be
| | ... | ${node} | ${sub_if_name} | down | down
| | And interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | up
| | And interface state from VAT should be
| | ... | ${node} | ${super_if} | up

| Honeycomb sets interface and sub-interface down
| | [Documentation] | Honeycomb changes the state of interface down and then \
| | ... | changes the state of its sub-interface down, in this order.
| | ...
| | [Teardown] | Set super and sub interfaces down
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | up
| | And interface state from VAT should be
| | ... | ${node} | ${super_if} | up
| | When Honeycomb sets interface state
| | ... | ${node} | ${super_if} | down
| | Then interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | down
| | And interface state from VAT should be
| | ... | ${node} | ${super_if} | down
| | Given sub-interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | up | down
| | And sub-interface state from VAT should be
| | ... | ${node} | ${sub_if_name} | up | down
| | When Honeycomb sets the sub-interface down
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | Then sub-interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | down | down
| | And sub-interface state from VAT should be
| | ... | ${node} | ${sub_if_name} | down | down

| Honeycomb fails to set sub-interface up while its super-interface is down
| | [Documentation] | Honeycomb tries to set the sub-interface up while its \
| | ... | super-interface is down. It must not be possible.
| | ...
| | Given interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | down
| | And interface state from VAT should be
| | ... | ${node} | ${super_if} | down
| | And sub-interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | down | down
| | And sub-interface state from VAT should be
| | ... | ${node} | ${sub_if_name} | down | down
| | When Honeycomb fails to set sub-interface up
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | Then interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | down
| | And interface state from VAT should be
| | ... | ${node} | ${super_if} | down
| | And sub-interface state from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | down | down
| | And sub-interface state from VAT should be
| | ... | ${node} | ${sub_if_name} | down | down

| Honeycomb fails to delete sub-interface
| | [Documentation] | Check if Honeycomb can delete an existing sub-interface.
| | ...
| | [Setup] | Set super and sub interfaces down
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${sub_if_1_oper}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_if_name} | ${sub_if_1_oper}
| | When Honeycomb fails to remove all sub-interfaces
| | ... | ${node} | ${super_if}
| | Then sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${sub_if_1_oper}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_if_name} | ${sub_if_1_oper}

| Honeycomb adds sub-interface to new bridge domain
| | [Documentation] | Check if Honeycomb adds a sub-interface to bridge domain.
| | ...
| | [Setup] | Set super and sub interfaces down
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${sub_if_1_oper}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_if_name} | ${sub_if_1_oper}
| | When Honeycomb creates L2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Then bridge domain configuration from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | When Honeycomb adds sub-interface to bridge domain
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${sub_bd_settings}
| | Then sub-interface bridge domain configuration from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${sub_bd_settings}
| | And sub-interface bridge domain configuration from VAT should be
| | ... | ${node} | ${sub_if_name} | ${sub_bd_settings}
| | And sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_if_name} | ${sub_if_1_oper}

| Honeycomb enables tag-rewrite pop 1
| | [Documentation] | Check if Honeycomb enables tag-rewrite and sets its \
| | ... | parameters correctly. Case: pop 1.
| | ...
| | [Teardown] | Honeycomb disables tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_pop_1}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_pop_1_oper}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_pop_1_VAT}

| Honeycomb enables tag-rewrite push
| | [Documentation] | Check if Honeycomb enables tag-rewrite and sets its \
| | ... | parameters correctly. Case: push.
| | ...
| | [Teardown] | Honeycomb disables tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_push}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_push_oper}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_push_VAT}

| Honeycomb enables tag-rewrite translate 1-2
| | [Documentation] | Check if Honeycomb enables tag-rewrite and sets its \
| | ... | parameters correctly. Case: translate 1-2.
| | ...
| | [Teardown] | Honeycomb disables tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_translate_1_2}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${tag_rewrite_translate_1_2_oper}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_translate_1_2_VAT}

| Honeycomb disables tag-rewrite
| | [Documentation] | Check if Honeycomb disables the tag-rewrite.
| | ...
| | [Teardown] | Honeycomb disables tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_pop_1}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_pop_1_oper}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_disabled}
| | Then rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_disabled_VAT}

| Honeycomb enables tag-rewrite pop 1 again
| | [Documentation] | Check if Honeycomb can enable tag-rewrite again, once it \
| | ... | was disabled by Honeycomb.
| | ...
| | [Teardown] | Honeycomb disables tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_pop_1}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_pop_1_oper}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_pop_1_VAT}

| Honeycomb modifies the tag-rewrite
| | [Documentation] | Honeycomb sets the tag-rewrite:
| | ... | 1. pop 1, then
| | ... | 2. push, then
| | ... | 3. translate 1 - 2
| | ... | Then Honeycomb disables the tag-rewrite.
| | ...
| | [Teardown] | Honeycomb disables tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Given rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_pop_1}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_pop_1_oper}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_pop_1_VAT}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_push}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_push_oper}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_push_VAT}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_translate_1_2}
| | Then rewrite tag from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${tag_rewrite_translate_1_2_oper}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_translate_1_2_VAT}
| | When Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_disabled}
| | Then rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_disabled_VAT}

| Honeycomb fails to set wrong vlan-type in tag-rewrite
| | [Documentation] | Check that Honeycomb does not accept wrong values of \
| | ... | vlan-type in tag-rewrite.
| | ...
| | Given rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | When Honeycomb fails to set wrong rewrite tag
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${tag_rewrite_translate_1_2_wrong}
| | Then rewrite tag from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | And rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_disabled_VAT}

| Honeycomb configures sub-interface ipv4 address
| | [Documentation] | Check if Honeycomb can configure an ipv4 address on the\
| | ... | sub-interface.
| | ...
| | When Honeycomb sets sub-interface ipv4 address
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${ipv4['address']} | ${ipv4['prefix-lenght']}
| | Then sub-interface ipv4 address from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${ipv4['address']} | ${ipv4['prefix-lenght']}
| | And sub-interface ipv4 address from VAT should be
| | ... | ${node} | ${sub_if_name}
| | ... | ${ipv4['address']} | ${ipv4['prefix-lenght']}

| Honeycomb removes sub-interface ipv4 address
| | [Documentation] | Check if Honeycomb can remove configured ipv4 addresses\
| | ... | from the sub-interface.
| | ...
| | Given sub-interface ipv4 address from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${ipv4['address']} | ${ipv4['prefix-lenght']}
| | And sub-interface ipv4 address from VAT should be
| | ... | ${node} | ${sub_if_name}
| | ... | ${ipv4['address']} | ${ipv4['prefix-lenght']}
| | When Honeycomb removes all sub-interface ipv4 addresses
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | Then sub-interface ipv4 address from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | And sub-interface ipv4 address from VAT should be empty
| | ... | ${node} | ${sub_if_name}

| Honeycomb modifies existing sub-interface ipv4 address
| | [Documentation] | Check if Honeycomb can modify an ipv4 address already\
| | ... | configured on the sub-interface.
| | [Teardown] | Honeycomb removes all sub-interface ipv4 addresses
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | Given sub-interface ipv4 address from Honeycomb should be empty
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | And sub-interface ipv4 address from VAT should be empty
| | ... | ${node} | ${sub_if_name}
| | When Honeycomb sets sub-interface ipv4 address
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${ipv4['address']} | ${ipv4['prefix-lenght']}
| | And Honeycomb sets sub-interface ipv4 address
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${ipv4_2['address']} | ${ipv4_2['prefix-lenght']}
| | Then sub-interface ipv4 address from Honeycomb should be
| | ... | ${node} | ${super_if} | ${sub_if_id}
| | ... | ${ipv4_2['address']} | ${ipv4_2['prefix-lenght']}
| | And sub-interface ipv4 address from VAT should be
| | ... | ${node} | ${sub_if_name}
| | ... | ${ipv4_2['address']} | ${ipv4_2['prefix-lenght']}



*** Keywords ***
| Set super and sub interfaces up
| | [Documentation] | Honeycomb sets super-interface and sub-interface up, in \
| | ... | this order.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super interface. Type: string
| | ... | - identifier - Sub-interface identifier. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | \| Set super and sub interfaces up\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ...
| | Honeycomb sets interface state
| | ... | ${node} | ${super_interface} | up
| | Honeycomb sets the sub-interface up
| | ... | ${node} | ${super_interface} | ${identifier}

| Set super and sub interfaces down
| | [Documentation] | Honeycomb sets super-interface and sub-interface down, in\
| | ... | this order.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_interface - Super interface. Type: string
| | ... | - identifier - Sub-interface identifier. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | \| Set super and sub interfaces down\
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_interface} | ${identifier}
| | ...
| | Honeycomb sets interface state
| | ... | ${node} | ${super_interface} | down
| | Honeycomb sets the sub-interface down
| | ... | ${node} | ${super_interface} | ${identifier}

| Honeycomb disables tag rewrite
| | [Documentation] |
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - super_if - Super-interface. Type: string
| | ... | - identifier - Sub-interface ID. Type: integer or string
| | ...
| | ... | *Example:*
| | ... | \| Honeycomb disables tag rewrite \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 1 \|
| | ...
| | [Arguments] | ${node} | ${super_if} | ${sub_if_id}
| | ...
| | Honeycomb configures tag rewrite
| | ... | ${node} | ${super_if} | ${sub_if_id} | ${tag_rewrite_disabled}
