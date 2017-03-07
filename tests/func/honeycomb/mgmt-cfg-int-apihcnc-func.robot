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
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/netconf.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| ...     | WITH NAME | InterfaceAPI
| Variables | resources/test_data/honeycomb/netconf/triggers.py
| Documentation | *Netconf test suite. Contains test cases that need to bypass\
| ... | REST API.*
| Force Tags | honeycomb_sanity
| Suite Teardown
| ... | Restart Honeycomb and VPP | ${node}

*** Variables ***
| ${interface}= | ${node['interfaces']['port1']['name']}
| &{bd_settings}= | flood=${True} | forward=${True} | learn=${True}
| ... | unknown-unicast-flood=${True} | arp-termination=${True}

*** Test Cases ***
| TC01: Honeycomb can create and delete interfaces
| | [Documentation] | Repeatedly create and delete an interface through Netconf\
| | ... | and check the reply for any errors.
| | Given Netconf session is established | ${node}
| | And Honeycomb creates first L2 bridge domain
| | ... | ${node} | bd_netconf | ${bd_settings}
| | :FOR | ${index} | IN RANGE | 20
| | | When Error trigger is sent | ${trigger_105}
| | | Then Replies should not contain RPC errors

| TC02: Transaction revert test case 1
| | [Documentation] | Configure two conflicting VxLAN tunnels, then verify\
| | ... | that neither tunnel exists.
| | Given Netconf session is established | ${node}
| | ${if_data}= | And InterfaceAPI.Get all interfaces oper data | ${node}
| | When Error trigger is sent | ${trigger_revert1}
| | ${if_data_new}= | And InterfaceAPI.Get all interfaces oper data | ${node}
| | Then Should be equal | ${if_data} | ${if_data_new}

| TC03: Transaction revert test case 2
| | [Documentation] | Configure two conflicting TAP interfaces, then verify\
| | ... | that neither interface exists.
| | Given Netconf session is established | ${node}
| | ${if_data}= | And InterfaceAPI.Get all interfaces oper data | ${node}
| | When Error trigger is sent | ${trigger_revert1}
| | ${if_data_new}= | And InterfaceAPI.Get all interfaces oper data | ${node}
| | Then Should be equal | ${if_data} | ${if_data_new}

| TC04: Vlan subinterface creation
| | [Documentation] | Configure a Vlan sub-interface under a physical interface.
| | Given Netconf session is established | ${node}
| | When Error Trigger Is Sent
| | ... | ${trigger_vlan} | interface=${interface}
| | Then Replies should not contain RPC errors
