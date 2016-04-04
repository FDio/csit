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
| Resource | resources/libraries/robot/tagging.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | VM_ENV
| Test Setup | Setup all DUTs before test
| Suite Setup | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}

*** Variables ***
| ${subid}= | 10
| ${outer_vlan_id}= | 100
| ${inner_vlan_id}= | 200
| ${type_subif}= | two_tags

*** Test Cases ***

| VPP can push and pop two VLAN tags to traffic transfering through xconnect
| | Given VLAN interfaces with two tags rewrite initialized on 3-node topology
| | ... | ${subid} | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | When L2 tag rewrite pop 2 tags setup on interfaces
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | Then Send and receive ICMPv4 | ${tg} | ${tg_if1} | ${tg_if2}
| | Then Send and receive ICMPv4 | ${tg} | ${tg_if2} | ${tg_if1}
