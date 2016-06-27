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
| Library | resources.libraries.python.honeycomb.Notifications | ${hello}
| ... | ${subscription}
| Documentation | Keywords used to test Honeycomb notifications over Netconf.

*** Variables ***
# hello message sent to Honeycomb through Netconf
| ${hello}= | <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
| ... | <capabilities><capability>urn:ietf:params:netconf:base:1.0
| ... | </capability></capabilities></hello>]]>]]>
# rpc call to add a subscription to Netconf notifications
| ${subscription}= | <netconf:rpc netconf:message-id="101"
| ... | xmlns:netconf="urn:ietf:params:xml:ns:netconf:base:1.0">
| ... | <create-subscription
| ... | xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
| ... | <stream>honeycomb</stream></create-subscription></netconf:rpc>]]>]]>

*** Keywords ***
| Notification listener is established
| | [Documentation] | Connects to Honeycomb notification service.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Notification listener is established \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Create session | ${node}
| | Add notification listener

| Honeycomb should send interface state notification
| | [Documentation] | Reads notification from Honeycomb and verifies\
| | ... | notification type, interface name and interface admin-state.
| | ...
| | ... | *Arguments:*
| | ... | - interface - name of the affected interface. Type: string
| | ... | - state - expected state of interface, 'up' or 'down'. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb should send interface state notification \
| | ... | \| GigabitEthernet0/8/0 \| up \|
| | [Arguments] | ${interface} | ${state}
| | ${reply}= | Get notification
| | Should contain | ${reply} | <interface-state-change
| | Should contain | ${reply} | <name>${interface}</name>
| | Should contain | ${reply} | <admin-status>${state}</admin-status>

| Honeycomb should send interface deleted notification
| | [Documentation] | Reads notification from Honeycomb and verifies\
| | ... | notification type and interface name.
| | ...
| | ... | *Arguments:*
| | ... | - interface - name of the deleted interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb should send interface deleted notification \
| | ... | \| temp_interface \|
| | [Arguments] | ${interface}
| | ${reply}= | Get notification
| | Should contain | ${reply} | <interface-deleted
| | Should contain | ${reply} | <name>${interface}</name>
