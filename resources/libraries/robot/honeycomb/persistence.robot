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
| Library | resources/libraries/python/honeycomb/HcPersistence.py
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
| Restart Honeycomb
| | [Documentation] | Restarts Honeycomb without clearing persistence data.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Restart Honeycomb \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Log Persisted Configuration | ${node}
| | Configure Honeycomb service on DUTs | ${node}

| Restart VPP
| | [Documentation] | Restarts VPP and waits until it reconnects with Honeycomb.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Restart VPP \| ${nodes['DUT1']} \|
| | ...
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
| | ...
| | [Arguments] | ${node}
| | Wait until keyword succeeds | 2min | 20sec
| | ... | Check Honeycomb startup state | ${node}

| Restart Honeycomb and VPP
| | [Documentation] | Stops Honeycomb, restarts VPP and then starts Honeycomb\
| | ... | again.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Restart Honeycomb and VPP \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Log Persisted Configuration | ${node}
| | Setup DUT | ${node}
| | Configure Honeycomb service on DUTs | ${node}

| Multi-Feature Persistence Test Configuration
| | [Documentation] | Uses Honeycomb to set basic settings for VxLAN,\
| | ... | bridge domains, TAP, vhost-user and VLAN.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Multi-Feature Persistence Test Configuration \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Honeycomb sets interface VxLAN configuration
| | ... | ${node} | ${vx_interface} | ${vxlan_settings}
| | Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Honeycomb creates TAP interface
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | Honeycomb creates vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client}
| | Honeycomb creates sub-interface | ${node} | ${interface}
| | ... | ${sub_if_1_match} | ${sub_if_1_tags} | ${sub_if_1_settings}
| | Honeycomb configures interface state | ${node} | ${interface} | up
| | Honeycomb sets the sub-interface up
| | ... | ${node} | ${interface} | ${sub_if_id}
| | Honeycomb adds sub-interface to bridge domain
| | ... | ${node} | ${interface} | ${sub_if_id} | ${sub_bd_settings}
| | Honeycomb configures tag rewrite
| | ... | ${node} | ${interface} | ${sub_if_id} | ${tag_rewrite_pop_1}

| Multi-Feature persistence Test Verification
| | [Documentation] | Uses Honeycomb and VAT to verify settings for VxLAN,\
| | ... | bridge domains, TAP, vhost-user and VLAN.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Multi-Feature persistence Test Verification \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | VxLAN Operational Data From Honeycomb Should Be
| | ... | ${node} | ${vx_interface} | ${vxlan_settings}
| | VxLAN Operational Data From VAT Should Be
| | ... | ${node} | ${vxlan_settings}
| | Bridge domain Operational Data From Honeycomb Should Be
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Bridge domain Operational Data From VAT Should Be
| | ... | ${node} | ${0} | ${bd_settings}
| | TAP Operational Data From Honeycomb Should Be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | TAP Operational Data From VAT Should Be
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | Vhost-user Operational Data From Honeycomb Should Be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client}
| | Vhost-user Operational Data From VAT Should Be
| | ... | ${node} | ${vhost_user_client}
| | Sub-interface Operational Data From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${sub_if_id} | ${sub_if_1_oper}
| | Sub-interface Operational Data From VAT Should Be
| | ... | ${node} | ${sub_if_name} | ${sub_if_1_oper}
| | Interface state from Honeycomb should be | ${node} | ${interface} | up
| | Interface state from VAT should be | ${node} | ${interface} | up
| | Sub-interface bridge domain Operational Data From Honeycomb Should Be
| | ... | ${node} | ${interface} | ${sub_if_id} | ${sub_bd_settings}
| | Sub-interface bridge domain Operational Data From VAT Should Be
| | ... | ${node} | ${sub_if_name} | ${sub_bd_settings}
| | Rewrite tag from Honeycomb should be
| | ... | ${node} | ${interface} | ${sub_if_id} | ${tag_rewrite_pop_1_oper}
| | Rewrite tag from VAT should be
| | ... | ${node} | ${sub_if_name} | ${tag_rewrite_pop_1_VAT}
| | ${data_conf}= | InterfaceAPI.Get all interfaces cfg data | ${node}
| | ${data_oper}= | InterfaceAPI.Get all interfaces oper data | ${node}
| | Compare interface lists | ${data_conf} | ${data_oper}

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
| | ...
| | [Arguments] | ${node}
| | VxLAN Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${vx_interface}
| | VxLAN Operational Data From VAT Should Be empty | ${node}
| | Honeycomb should show no bridge domains | ${node}
| | VAT should show no bridge domains | ${node}
| | TAP Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${tap_interface}
| | TAP Operational Data From VAT Should Be empty
| | ... | ${node} | ${tap_interface}
| | Vhost-user Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${vhost_interface}
| | Vhost-user Operational Data From VAT Should Be empty
| | ... | ${node}
| | interface state from Honeycomb should be
| | ... | ${node} | ${interface} | down
| | And interface state from VAT should be
| | ... | ${node} | ${interface} | down

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
| | ...
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Modify persistence files | ${node} | { | abc
| | Setup DUT | ${node}
| | Configure Honeycomb service on DUTs | ${node}

| Log persisted configuration on node
| | [Documentation] | Logs the content of Honeycomb's persitence files.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Log persisted configuration on node \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Log persisted configuration | ${node}

| Interface Persistence Setup
| | [Documentation] | Configure interface state, ipv4 and ipv6 addresses
| | ... | and neighbors.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface Persistence Setup \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Honeycomb and VPP should have default configuration | ${node}
| | Import Variables | resources/test_data/honeycomb/interface_ip.py
| | Honeycomb configures interface state | ${node} | ${interface} | up
| | Honeycomb sets interface IPv4 address with prefix
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | Honeycomb adds interface IPv4 neighbor
| | ... | ${node} | ${interface} | ${ipv4_neighbor} | ${neighbor_mac}
| | Honeycomb sets interface IPv6 address
| | ... | ${node} | ${interface} | ${ipv6_address} | ${ipv6_prefix}
| | Honeycomb adds interface IPv6 neighbor
| | ... | ${node} | ${interface} | ${ipv6_neighbor} | ${neighbor_mac}

| Interface Persistence Check
| | [Documentation] | Verify interface state, ipv4 and ipv6 addresses
| | ... | and neighbors.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface Persistence Check \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Interface state from Honeycomb should be | ${node} | ${interface} | up
| | IPv4 address from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_address} | ${ipv4_prefix}
| | IPv4 address from VAT should be
| | ... | ${node} | ${interface} | ${ipv4_address}
| | ... | ${ipv4_prefix} | ${ipv4_mask}
| | IPv4 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv4_neighbor} | ${neighbor_mac}
| | IPv6 address from Honeycomb should contain
| | ... | ${node} | ${interface} | ${ipv6_address} | ${ipv6_prefix}
| | IPv6 address from VAT should contain
| | ... | ${node} | ${interface} | ${ipv6_address} | ${ipv6_prefix}
| | IPv6 neighbor from Honeycomb should be
| | ... | ${node} | ${interface} | ${ipv6_neighbor} | ${neighbor_mac}

| Bridge Domain Persistence Setup
| | [Documentation] | Configure bridge domain, BD interface assignment
| | ... | and L2 fib entry.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Bridge Domain Persistence Setup \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Honeycomb and VPP should have default configuration | ${node}
| | Import Variables | resources/test_data/honeycomb/l2_fib.py
| | ... | ${node} | ${interface} | ${interface}
| | Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Honeycomb adds interface to bridge domain
| | ... | ${node} | ${interface} | ${bd_name} | ${if_bd_settings}
| | Honeycomb adds L2 FIB entry to bridge domain
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_cfg}

| Bridge Domain Persistence Check
| | [Documentation] | Verify bridge domain, BD interface assignment
| | ... | and L2 fib entry.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Bridge Domain Persistence Check \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Bridge domain Operational Data From Honeycomb Should Be
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Bridge domain Operational Data From VAT Should Be
| | ... | ${node} | ${0} | ${bd_settings}
| | Bridge domain Operational Interface Assignment should be
| | ... | ${node} | ${interface} | ${if_bd_settings}
| | L2 FIB Entry from Honeycomb should be
| | ... | ${node} | ${bd_name} | ${l2_fib_forward_oper}
| | L2 FIB entry from VAT should be
| | ... | ${node} | ${bd_index} | ${l2_fib_forward_vat}