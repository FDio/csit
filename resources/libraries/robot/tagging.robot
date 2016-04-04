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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath

*** Keywords ***

| Node path computed for 3-node topology
| | [Arguments] | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...         | ${nodes['TG']}
| | [Documentation] | Create interface variables for 3-node topology.
| | ... |
| | ... | *Arguments:*
| | ... | ${nodes['TG']} - Node attached to the path. Type: dictionary
| | ... | ${nodes['DUT1']} - Node attached to the path. Type: dictionary
| | ... | ${nodes['DUT2']} - Node attached to the path. Type: dictionary
| | ... | ${nodes['TG']} - Node attached to the path. Type: dictionary
| | ... |
| | ... | *Return:*
| | ... | ${tg} - Variable for node in path. Type: dictionary
| | ... | ${dut1} - Variable for node in path. Type: dictionary
| | ... | ${dut2} - Variable for node in path. Type: dictionary
| | ... | ${tg_if1} - First interface of TG node. Type: str
| | ... | ${tg_if2} - Second interface of TG node. Type: str
| | ... | ${dut1_if1} - First interface of first DUT node. Type: str
| | ... | ${dut1_if2} - Second interface of first DUT node. Type: str
| | ... | ${dut2_if1} - First interface of second DUT node. Type: str
| | ... | ${dut2_if2} - Second interface of second DUT node. Type: str
| | ... |
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

| VLAN subinterfaces initialized on 3-node topology
| | [Arguments] | ${subid} | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | [Documentation] | Create subinterfaces in 3-node topology.
| | ... |
| | ... | *Arguments:*
| | ... | ${subid} - Sub-interface ID. Type: int
| | ... | ${outer_vlan_id} - Outer VLAN ID. Type: int
| | ... | ${inner_vlan_id} - Inner VLAN ID. Type: int
| | ... | ${type_subif} - Type of sub-interface. Type: str
| | ... |
| | ... | *Return:*
| | ... | ${subif_name_1} - Name of sub-interface on first DUT. Type: str
| | ... | ${subif_index_1} - SW index of sub-interface on first DUT. Type: int
| | ... | ${subif_name_2} - Name of sub-interface on second DUT. Type: str
| | ... | ${subif_index_2} - SW index of sub-interface on second DUT. Type: int
| | ... |
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
