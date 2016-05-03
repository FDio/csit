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
| Resource | resources/libraries/robot/testing_path.robot
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
| ${tag_rewrite_method}= | pop-2

*** Test Cases ***
| VPP can push and pop two VLAN tags to traffic transferring through xconnect
| | [Documentation] | Push two tags on DUT 1 to traffic sent from TG,
| | ...             | pop two tags on DUT 2 from this traffic
| | ...             | and receive untagged traffic on TG.
| | ...
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut2_node} | ${dut2_to_dut1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1_node} | ${subif_index_1} | ${dut2_node} | ${subif_index_2}
| | ... | ${tag_rewrite_method}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1_node} | ${dut1_to_tg} | ${subif_index_1}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${subif_index_2}
| | Then Send and receive ICMPv4 | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
