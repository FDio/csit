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

*** Variables ***
# IP addresses for IPv6 link
| ${tg_to_dut_if2_ip}= | fd00:1234::1
| ${dut_to_tg_if2_ip}= | fd00:1234::2
| ${ipv6_prefix}= | ${64}
# Configuration which will be set and verified during tests.
| ${bd1_name}= | bd-01
| ${bd2_name}= | bd-02
| &{bd_settings}= | flood=${True} | forward=${True} | learn=${True}
| ... | unknown-unicast-flood=${True} | arp-termination=${True}
| &{if_settings}= | split_horizon_group=${1} | bvi=${False}
| &{if_settings2}= | split_horizon_group=${2} | bvi=${True}
| ${vhost_interface}= | test_vhost
| &{vhost_user_server}= | socket=/tmp/soc1 | role=server
| &{vhost_user_server_edit_1}= | socket=/tmp/soc12 | role=server
| &{vhost_user_server_edit_2}= | socket=/tmp/soc12 | role=client

*** Settings ***
| Library | resources.libraries.python.honeycomb.IPv6Management
| Library | resources.libraries.python.VPPUtil
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Resource | resources/libraries/robot/honeycomb/ipv6_control.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/honeycomb/netconf.robot
| Resource | resources/libraries/robot/honeycomb/vhost_user.robot
| Variables | resources/test_data/honeycomb/netconf/triggers.py
| ...
| Suite Setup | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Run Keywords
| ... | Unconfigure IPv6 Management Interface | AND
| ... | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Force Tags | HC_FUNC | HC_REST_ONLY
| ...
| Documentation | *Honeycomb IPv6 control interface test suite.*

*** Test Cases ***
| TC01: Honeycomb sets up l2 bridge domain
| | [Documentation] | Check if Honeycomb can create bridge domains on VPP node.
| | ...
| | [Setup] | Configure IPv6 Management Interface
| | When Honeycomb creates first l2 bridge domain
| | ... | ${tunneled_node} | ${bd1_name} | ${bd_settings}
| | Then Bridge domain Operational Data From Honeycomb Should Be
| | ... | ${tunneled_node} | ${bd1_name} | ${bd_settings}

| TC02: Honeycomb removes bridge domains
| | [Documentation] | Check if Honeycomb can remove bridge domains from a VPP\
| | ... | node.
| | ...
| | Given Bridge domain Operational Data From Honeycomb Should Be
| | ... | ${tunneled_node} | ${bd1_name} | ${bd_settings}
| | When Honeycomb removes all bridge domains | ${tunneled_node}
| | Then Honeycomb should show no bridge domains | ${tunneled_node}

| TC03: Honeycomb creates vhost-user interface - server
| | [Documentation] | Check if Honeycomb creates a vhost-user interface, role:\
| | ... | server.
| | ...
| | Given vhost-user Operational Data From Honeycomb Should Be empty
| | ... | ${tunneled_node} | ${vhost_interface}
| | When Honeycomb creates vhost-user interface
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server}
| | Then vhost-user Operational Data From Honeycomb Should Be
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server}

| TC04: Honeycomb modifies vhost-user interface - server
| | [Documentation] | Check if Honeycomb can modify properties of existing\
| | ... | vhost-user interface, role: server.
| | ...
| | Given vhost-user Operational Data From Honeycomb Should Be
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server}
| | When Honeycomb configures vhost-user interface
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server_edit_1}
| | Then vhost-user Operational Data From Honeycomb Should Be
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server_edit_1}
| | When Honeycomb configures vhost-user interface
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server_edit_2}
| | Then vhost-user Operational Data From Honeycomb Should Be
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server_edit_2}
| | When Honeycomb configures vhost-user interface
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server}
| | Then vhost-user Operational Data From Honeycomb Should Be
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server}

| TC05: Honeycomb deletes vhost-user interface - server
| | [Documentation] | Check if Honeycomb can delete an existing vhost-user\
| | ... | interface, role: server.
| | ...
| | Given vhost-user Operational Data From Honeycomb Should Be
| | ... | ${tunneled_node} | ${vhost_interface} | ${vhost_user_server}
| | When Honeycomb removes vhost-user interface
| | ... | ${tunneled_node} | ${vhost_interface}
| | Then vhost-user Operational Data From Honeycomb Should Be empty
| | ... | ${tunneled_node} | ${vhost_interface}

| TC06: Honeycomb can create and delete interfaces
| | [Documentation] | Repeatedly create and delete an interface through Netconf\
| | ... | and check the reply for any errors.
| | ...
| | Given Netconf session should be established | ${tunneled_node}
| | And Honeycomb creates first L2 bridge domain
| | ... | ${tunneled_node} | bd_netconf | ${bd_settings}
| | :FOR | ${index} | IN RANGE | 20
| | | When Error trigger is sent | ${trigger_105}
| | | Then Replies should not contain RPC errors

| TC07: Honeycomb can create vlan subinterface
| | [Documentation] | Configure a Vlan sub-interface under a physical interface.
| | ...
| | Given Netconf session should be established | ${tunneled_node}
| | When Error Trigger Is Sent
| | ... | ${trigger_vlan} | interface=${interface}
| | Then Replies should not contain RPC errors

*** Keywords ***
| Configure IPv6 Management Interface
| | [Documentation] | Change one of VPP's data-plane interfaces on DUT into\
| | ... | a control-plane interface that Honeycomb can listen on. Setup IPv6\
| | ... | addresses on the link. Create an IPv4 to IPv6 tunnel on TG and create\
| | ... | suite variables.
| | ...
| | Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Stop VPP service on DUT | ${dut_node}
| | Stop Honeycomb Service on DUTs | ${dut_node}
| | Convert data-plane interface to control-plane
| | ... | ${dut_node} | ${dut_to_tg_if2}
| | Sleep | 5sec | Wait until Linux reclaims the interface.
| | ${tg_to_dut_if2_name}= | Get Interface Name by MAC
| | ... | ${tg_node} | ${tg_to_dut_if2_mac}
| | ${dut_to_tg_if2_name}= | Get Interface Name by MAC
| | ... | ${dut_node} | ${dut_to_tg_if2_mac}
| | ${tunneled_node}= | Copy Dictionary | ${dut_node}
| | Set To Dictionary | ${tunneled_node} | host | ${tg_node['host']}
| | ${interface}= | Get Interface Name | ${dut_node} | ${dut_to_tg_if1}
| | Set Suite Variable | ${interface}
| | Set Suite Variable | ${tunneled_node}
| | Set Suite Variable | ${tg_node}
| | Set Suite Variable | ${dut_node}
| | Set Suite Variable | ${dut_to_tg_if2}
| | Set Suite Variable | ${dut_to_tg_if2_name}
| | Set Suite Variable | ${tg_to_dut_if2_name}
| | Set management interface address
| | ... | ${tg_node} | ${tg_to_dut_if2_name}
| | ... | ${tg_to_dut_if2_ip} | ${ipv6_prefix}
| | Set management interface address
| | ... | ${dut_node} | ${dut_to_tg_if2_name}
| | ... | ${dut_to_tg_if2_ip} | ${ipv6_prefix}
| | Configure Control Interface Tunnel
| | ... | ${tg_node} | ${dut_node['honeycomb']['port']}
| | ... | ${dut_to_tg_if2_ip} | ${dut_node['honeycomb']['port']}
| | Configure Control Interface Tunnel
| | ... | ${tg_node} | ${dut_node['honeycomb']['netconf_port']}
| | ... | ${dut_to_tg_if2_ip} | ${dut_node['honeycomb']['netconf_port']}
| | Restart VPP service | ${dut_node}
| | Configure Honeycomb service on DUTs | ${dut_node}

| Unconfigure IPv6 Management Interface
| | [Documentation] | Remove all IP addresses from interfaces in the IPv6 link.
| | ...
| | Clear Interface Configuration | ${tg_node} | ${tg_to_dut_if2_name}
| | Clear Interface Configuration | ${dut_node} | ${dut_to_tg_if2_name}
