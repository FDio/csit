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
| Library | resources.libraries.python.InterfaceUtil
| ...     | WITH NAME | interfaceCLI
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| ...     | WITH NAME | InterfaceAPI
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/vxlan.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Resource | resources/libraries/robot/honeycomb/tap.robot
| Resource | resources/libraries/robot/honeycomb/vhost_user.robot
# Vlan tests not implemented yet
# | Resource | resources/libraries/robot/honeycomb/vlan.robot

*** Variables ***
# Configuration which will be set and verified during tests.
| ${vx_interface}= | vx_tunnel_test
| &{vxlan_settings}= | src=192.168.0.2 | dst=192.168.0.3 | vni=${88}
| ... | encap-vrf-id=${0}
| ${bd_name}= | bd_persist
| &{bd_settings}= | flood=${True} | forward=${True} | learn=${True}
| ... | unknown-unicast-flood=${True} | arp-termination=${True}
| ${tap_interface}= | tap_test
| &{tap_settings}= | tap-name=tap_test | mac=08:00:27:c0:5d:37
| ... | device-instance=${1}
| ${vhost_interface}= | test_vhost
| &{vhost_user_server}= | socket=soc1 | role=server
# Vlan tests not implemented yet
# | ${vlan_interface}= | vlan_test
# | &{vlan_settings}= |

*** Keywords ***
| Honeycomb is restarted
| | [Documentation] | Restarts Honeycomb without clearing persistence data.
| | [Arguments] | ${dut}
| | Stop honeycomb service on DUTs | ${dut}
| | Setup Honeycomb service on DUTs | ${dut}

| VPP is restarted
| | [Documentation] | Restarts VPP and waits until it is ready.
| | [Arguments] | ${dut}
| | Setup DUT | ${dut}

| Honeycomb and VPP are restarted
| | [Documentation] | Restarts both Honeycomb and VPP together.
| | [Arguments] | ${dut}
| | Stop honeycomb service on DUTs | ${dut}
| | Setup DUT | ${dut}
| | Setup Honeycomb service on DUTs | ${dut}

| Honeycomb configures every setting
| | [Documentation] | Uses Honeycomb to set basic settings in every category.
| | [Arguments] | ${node} | ${interface}
| | Honeycomb sets interface state | ${node} | ${interface} | up
| | Honeycomb sets interface VxLAN configuration
| | ... | ${node} | ${vx_interface} | ${vxlan_settings}
| | Honeycomb creates first l2 bridge domain
| | ... | ${node} | ${bd_name} | ${bd_settings}
| | Honeycomb creates TAP interface
| | ... | ${node} | ${tap_interface} | ${tap_settings}
| | Honeycomb creates vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
# Vlan tests not implemented yet
# | | Honeycomb creates vlan subinterface
# | | ... | ${node} | ${vlan_interface} | ${vlan_settings}

| Honeycomb and VPP should verify every setting
| | [Documentation] | Uses Honeycomb and VAT to verify settings in every\
| | ... | category.
| | [Arguments] | ${node} | ${interface}
| | Interface state from Honeycomb should be | ${node} | ${interface} | up
| | Interface state from VAT should be | ${node} | ${interface} | up
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
# Vlan tests not implemented yet
# | | Vlan configuration from Honeycomb should be
# | | ${node} | ${vlan_interface} | ${vlan_settings}
# | | Vlan configuration from VAT should be
# | | ${node} | ${vlan_interface} | ${vlan_settings}

| Honeycomb should show no rogue interfaces
| | [Documentation] | Checks if operational data contains interfaces not\
| | ... | present in configuration and vice versa.
| | [Arguments] | ${node}
| | ${data_conf}= | InterfaceAPI.Get all interfaces cfg data | ${node}
| | ${data_oper}= | InterfaceAPI.Get all interfaces oper data | ${node}
| | Compare interface lists | ${data_conf} | ${data_oper}
