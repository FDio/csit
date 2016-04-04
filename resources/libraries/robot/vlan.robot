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
| Resource | resources/libraries/robot/l2_xconnect.robot
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.NodePath

*** Variables ***
| ${subid}= | 10
| ${outer_vlan_id}= | 100
| ${inner_vlan_id}= | 200
| ${type_subif}= | two_tags

*** Keywords ***
| VLAN interfaces with two tags rewrite initialized on 3-node topology
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...          | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | Set Test Variable | ${tg}
| | Set Test Variable | ${tg_if1}
| | Set Test Variable | ${tg_if2}
| | Set Test Variable | ${dut1}
| | Set Test Variable | ${dut1_if1}
| | Set Test Variable | ${dut1_if2}
| | Set Test Variable | ${dut2}
| | Set Test Variable | ${dut2_if1}
| | Set Test Variable | ${dut2_if2}
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | ${subif_name_1} | ${subif_index_1}= | Create subinterface | ${dut1}
| | ...                                 | ${dut1_if2} | ${subid}
| | ...                                 | ${outer_vlan_id} | ${inner_vlan_id}
| | ...                                 | ${type_subif}
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | ${subif_name_2} | ${subif_index_2}= | Create subinterface | ${dut2}
| | ...                                 | ${dut2_if1} | ${subid}
| | ...                                 | ${outer_vlan_id} | ${inner_vlan_id}
| | ...                                 | ${type_subif}
| | Set test variable | ${subif_index_1}
| | Set test variable | ${subif_index_2}

| L2 tag rewrite pop 2 tags setup on interfaces
| | L2 tag rewrite pop 2 tags | ${dut1} | ${subif_index_1}
| | L2 tag rewrite pop 2 tags | ${dut2} | ${subif_index_2}

| Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if2} | ${subif_index_2}

