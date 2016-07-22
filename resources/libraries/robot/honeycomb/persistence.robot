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
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| ...     | WITH NAME | InterfaceAPI
| Library | resources.libraries.python.honeycomb.HcPersistence
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/vxlan.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Resource | resources/libraries/robot/honeycomb/tap.robot
| Resource | resources/libraries/robot/honeycomb/vhost_user.robot
| Resource | resources/libraries/robot/honeycomb/sub_interface.robot
| Variables | resources/test_data/honeycomb/persistence.py | ${interface}
| Documentation | Keywords used to test Honeycomb persistence.

*** Keywords ***
| Honeycomb is restarted
| | [Documentation] | Restarts Honeycomb without clearing persistence data.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb is restarted \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Setup Honeycomb service on DUTs | ${node}

| VPP is restarted
| | [Documentation] | Restarts VPP and waits until it reconnects with Honeycomb.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VPP is restarted \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Setup DUT | ${node}
| | Check VPP connection | ${node}

| Check VPP connection
| | [Documentation] | Checks if Honeycomb is connected to VPP by reading VPP\
| | ... | version number from Honeycomb operational data.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Check VPP connection \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Wait until keyword succeeds | 2min | 20sec
| | ... | Check Honeycomb startup state | ${node}

| Honeycomb and VPP are restarted
| | [Documentation] | Stops Honeycomb, restarts VPP and then starts Honeycomb\
| | ... | again.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb and VPP are restarted \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Setup DUT | ${node}
| | Setup Honeycomb service on DUTs | ${node}

| Honeycomb configures every setting
| | [Documentation] | Uses Honeycomb to set basic settings for VxLAN,\
| | ... | bridge domains, TAP, vhost-user and VLAN.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures every setting \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Honeycomb sets interface VxLAN configuration
| | ... | ${node} | ${vx_interface} | ${vxlan_settings}
| | Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Honeycomb creates TAP interface
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | Honeycomb creates vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
| | Honeycomb creates sub-interface | ${node} | ${interface}
| | ... | ${sub_if_1_match} | ${sub_if_1_tags} | ${sub_if_1_settings}
| | Honeycomb sets interface state | ${node} | ${interface} | up
| | Honeycomb sets the sub-interface up
| | ... | ${node} | ${interface} | ${sub_if_id}
| | Honeycomb adds sub-interface to bridge domain
| | ... | ${node} | ${interface} | ${sub_if_id} | ${sub_bd_settings}
| | Honeycomb configures tag rewrite
| | ... | ${node} | ${interface} | ${sub_if_id} | ${tag_rewrite_pop_1}

| Honeycomb and VPP should verify every setting
| | [Documentation] | Uses Honeycomb and VAT to verify settings for VxLAN,\
| | ... | bridge domains, TAP, vhost-user and VLAN.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb and VPP should verify every setting \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | VxLAN configuration from Honeycomb should be
| | ... | ${node} | ${vx_interface} | ${vxlan_settings}
| | VxLAN configuration from VAT should be
| | ... | ${node} | ${vxlan_settings}
| | Bridge domain configuration from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Bridge domain configuration from VAT should be
| | ... | ${node} | ${0} | ${bd_settings}
| | TAP configuration from Honeycomb should be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | TAP configuration from VAT should be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | Vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
| | Vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_server}
| | Sub-interface configuration from Honeycomb should be
| | ... | ${node} | ${interface} | ${sub_if_id} | ${sub_if_1_oper}
| | Sub-interface configuration from VAT should be
| | ... | ${node} | ${sub_if_name} | ${sub_if_1_oper}
| | Interface state from Honeycomb should be | ${node} | ${interface} | up
| | Interface state from VAT should be | ${node} | ${interface} | up
| | Sub-interface bridge domain configuration from Honeycomb should be
| | ... | ${node} | ${interface} | ${sub_if_id} | ${sub_bd_settings}
| | Sub-interface bridge domain configuration from VAT should be
| | ... | ${node} | ${sub_if_name} | ${sub_bd_settings}
| | Rewrite tag from Honeycomb should be
| | ... | ${node} | ${interface} | ${sub_if_id} | ${tag_rewrite_pop_1_oper}
| | Rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_pop_1_VAT}

| Honeycomb and VPP should have default configuration
| | [Documentation] | Uses Honeycomb and VAT to verify settings for VxLAN,\
| | ... | bridge domains, TAP, vhost-user and VLAN. Expects default\
| | ... | configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb and VPP should have default configuration \|
| | ... | ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | VxLAN configuration from Honeycomb should be empty
| | ... | ${node} | ${vx_interface}
| | VxLAN configuration from VAT should be empty | ${node}
| | Honeycomb should show no bridge domains | ${node}
| | VAT should show no bridge domains | ${node}
| | TAP configuration from Honeycomb should be empty
| | ... | ${node} | ${tap_interface}
| | TAP configuration from VAT should be empty
| | ... | ${node} | ${tap_interface}
| | Vhost-user configuration from Honeycomb should be empty
| | ... | ${node} | ${vhost_interface}
| | Vhost-user configuration from VAT should be empty
| | ... | ${node}
| | interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | down

| Honeycomb and VPP should not have default configuration
| | [Documentation] | Uses Honeycomb and VAT to verify settings for VxLAN,\
| | ... | bridge domains, TAP, vhost-user and VLAN. Expects any\
| | ... | configuration other than default.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb and VPP should not have default configuration \
| | ... | \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Run keyword and expect error | *
| | ... | Honeycomb and VPP should have default configuration | ${node}


| Honeycomb should show no rogue interfaces
| | [Documentation] | Checks if operational data contains interfaces not\
| | ... | present in configuration and vice versa.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb should show no rogue interfaces \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | ${data_conf}= | InterfaceAPI.Get all interfaces cfg data | ${node}
| | ${data_oper}= | InterfaceAPI.Get all interfaces oper data | ${node}
| | Compare interface lists | ${data_conf} | ${data_oper}

| Persistence file is damaged during restart
| | [Documentation] | Shuts down Honeycomb, modifies persistence files to\
| | ... | simulate damage, then restarts VPP and starts up Honeycomb again.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Persistence file is damaged during restart \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Modify persistence files | ${node} | { | abc
| | Setup DUT | ${node}
| | Setup Honeycomb service on DUTs | ${node}
