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
| Documentation | Keywords for VLAN tests
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath

*** Keywords ***

| VLAN subinterfaces initialized on 3-node topology
| | [Arguments] | ${DUT1} | ${INT1} | ${DUT2} | ${INT2} | ${SUB_ID}
| | ...         | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID} | ${TYPE_SUBIF}
| | [Documentation] | *Create two subinterfaces on DUTs.*
| | ...
| | ... | *Arguments:*
| | ... | - DUT1 - Node to add sub-interface.
| | ... | - INT1 - Interface name on which create sub-interface.
| | ... | - DUT2 - Node to add sub-interface.
| | ... | - INT2 - Interface name on which create sub-interface.
| | ... | - SUB_ID - ID of the sub-interface to be created.
| | ... | - OUTER_VLAN_ID - Outer VLAN ID.
| | ... | - INNER_VLAN_ID - Inner VLAN ID.
| | ... | - TYPE_SUBIF - Type of sub-interface.
| | ...
| | ... | _Set testcase variables with name and index of created interfaces:_
| | ... | - subif_name_1
| | ... | - subif_index_1
| | ... | - subif_name_2
| | ... | - subif_index_2
| | ...
| | ${INT1_name}= | Get interface name | ${DUT1} | ${INT1}
| | ${subif_name_1} | ${subif_index_1}= | Create subinterface | ${DUT1}
| | ...                                 | ${INT1_name} | ${SUB_ID}
| | ...                                 | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID}
| | ...                                 | ${TYPE_SUBIF}
| | ${INT2_name}= | Get interface name | ${DUT2} | ${INT2}
| | ${subif_name_2} | ${subif_index_2}= | Create subinterface | ${DUT2}
| | ...                                 | ${INT2_name} | ${SUB_ID}
| | ...                                 | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID}
| | ...                                 | ${TYPE_SUBIF}
| | Set Interface State | ${DUT1} | ${subif_index_1} | up
| | Set Interface State | ${DUT2} | ${subif_index_2} | up
| | Set Test Variable | ${subif_name_1}
| | Set Test Variable | ${subif_index_1}
| | Set Test Variable | ${subif_name_2}
| | Set Test Variable | ${subif_index_2}

| VLAN dot1q subinterfaces initialized on 3-node topology
| | [Arguments] | ${DUT1} | ${INT1} | ${DUT2} | ${INT2} | ${SUB_ID}
| | [Documentation] | *Create two dot1q subinterfaces on DUTs.*
| | ...
| | ... | *Arguments:*
| | ... | - DUT1 - Node to add sub-interface.
| | ... | - INT1 - Interface name on which create VLAN sub-interface.
| | ... | - DUT2 - Node to add sub-interface.
| | ... | - INT2 - Interface name on which create VLAN sub-interface.
| | ... | - SUB_ID - ID of the sub-interface to be created.
| | ...
| | ... | _Set testcase variables with name and index of created interfaces:_
| | ... | - subif_name_1
| | ... | - subif_index_1
| | ... | - subif_name_2
| | ... | - subif_index_2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VLAN dot1q subinterfaces initialized on 3-node topology \
| | ... | \| ${nodes['DUT1']} \| ${dut1_if2} \| ${nodes['DUT2']} \
| | ... | \| ${dut1_if2} \| 10 \|
| | ...
| | ${INT1_NAME}= | Get interface name | ${DUT1} | ${INT1}
| | ${INT2_NAME}= | Get interface name | ${DUT2} | ${INT2}
| | ${subif_name_1} | ${subif_index_1}= | Create Vlan Subinterface
| |                 | ...               | ${DUT1} | ${INT1_NAME} | ${SUB_ID}
| | ${subif_name_2} | ${subif_index_2}= | Create Vlan Subinterface
| |                 | ...               | ${DUT2} | ${INT2_NAME} | ${SUB_ID}
| | Set Interface State | ${DUT1} | ${subif_index_1} | up
| | Set Interface State | ${DUT2} | ${subif_index_2} | up
| | Set Test Variable | ${subif_name_1}
| | Set Test Variable | ${subif_index_1}
| | Set Test Variable | ${subif_name_2}
| | Set Test Variable | ${subif_index_2}

| L2 tag rewrite method setup on interfaces
| | [Arguments] | ${DUT1} | ${SUB_INT1} | ${DUT2} | ${SUB_INT2}
| | ...         | ${TAG_REWRITE_METHOD}
| | [Documentation] | *Setup tag rewrite on sub-interfaces on DUTs.*
| | ...
| | ... | *Arguments:*
| | ... | - DUT1 - Node to rewrite tags.
| | ... | - SUB_INT1 - Interface on which rewrite tags.
| | ... | - DUT2 - Node to rewrite tags.
| | ... | - SUB_INT2 - Interface on which rewrite tags.
| | ... | - TAG_REWRITE_METHOD - Method of tag rewrite.
| | ...
| | L2 Vlan tag rewrite | ${DUT1} | ${SUB_INT1} | ${TAG_REWRITE_METHOD}
| | L2 Vlan tag rewrite | ${DUT2} | ${SUB_INT2} | ${TAG_REWRITE_METHOD}

| Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | [Arguments] | ${DUT1} | ${INT1} | ${SUB_INT1}
| | ...         | ${DUT2} | ${INT2} | ${SUB_INT2}
| | [Documentation] | *Add interface and subinterface to bidirectional
| | ...             | L2-xconnect on DUTs.*
| | ...
| | ... | *Arguments:*
| | ... | - DUT1 - Node to add bidirectional cross-connect.
| | ... | - INT1 - Interface to add to the cross-connect.
| | ... | - SUB_INT1 - Sub-interface to add to the cross-connect.
| | ... | - DUT2 - Node to add bidirectional cross-connect.
| | ... | - INT2 - Interface to add to the cross-connect.
| | ... | - SUB_INT2 - Sub-interface to add to the cross-connect.
| | ...
| | L2 setup xconnect on DUT | ${DUT1} | ${INT1} | ${SUB_INT1}
| | L2 setup xconnect on DUT | ${DUT2} | ${INT2} | ${SUB_INT2}

| Vlan Subinterface Created
| | [Documentation] | Create VLAN sub-interface on DUT.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node to add VLAN sub-intreface. Type: dictionary
| | ... | - interface - Interface to create VLAN sub-interface. Type: string
| | ... | - vlan_id - VLAN ID. Type: integer
| | ...
| | ... | *Return:*
| | ... | - vlan_name - VLAN sub-interface name. Type: string
| | ... | - vlan_index - VLAN sub-interface SW index. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Vlan Subinterface Created \| ${nodes['DUT1']} \| port3 \| 100 \|
| | ...
| | [Arguments] | ${dut_node} | ${interface} | ${vlan_id}
| | [Return] | ${vlan_name} | ${vlan_index}
| | ${interface_name}= | Get interface name | ${dut_node} | ${interface}
| | ${vlan_name} | ${vlan_index}= | Create Vlan Subinterface
| | ... | ${dut_node} | ${interface_name} | ${vlan_id}

| Tagged Subinterface Created
| | [Documentation] | Create tagged sub-interface on DUT. Type of tagged \
| | ... | sub-intreface depends on type_subif value:
| | ... | - one_tag -> VLAN
| | ... | - two_tags -> QinQ VLAN
| | ... | - two_tags dot1ad - DOT1AD
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node to add VLAN sub-intreface. Type: dictionary
| | ... | - interface - Interface to create tagged sub-interface. Type: string
| | ... | - subif_id - Sub-interface ID. Type: integer
| | ... | - outer_vlan_id - VLAN (outer) ID (Optional). Type: integer
| | ... | - inner_vlan_id - VLAN inner ID (Optional). Type: integer
| | ... | - type_subif - Sub-interface type (Optional). Type: string
| | ...
| | ... | *Return:*
| | ... | - subif_name - Sub-interface name. Type: string
| | ... | - subif_index - Sub-interface SW index. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tagged Subinterface Created \| ${nodes['DUT1']} \| port1 \| 10 \
| | ... | \| outer_vlan_id=100 \| inner_vlan_id=200 \
| | ... | \| type_subif=two_tags dot1ad \|
| | ...
| | [Arguments] | ${dut_node} | ${interface} | ${subif_id}
| | ... | ${outer_vlan_id}=${None} | ${inner_vlan_id}=${None}
| | ... | ${type_subif}=${None}
| | [Return] | ${subif_name} | ${subif_index}
| | ${interface_name}= | Get interface name | ${dut_node} | ${interface}
| | ${subif_name} | ${subif_index}= | Create Subinterface
| | ... | ${dut_node} | ${interface_name} | ${subif_id}
| | ... | outer_vlan_id=${outer_vlan_id} | inner_vlan_id=${inner_vlan_id}
| | ... | type_subif=${type_subif}

| L2 Tag Rewrite Method Is Set On Interface
| | [Documentation] | Set L2 tag rewrite on (sub-)interface on DUT
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node to set L2 tag rewrite method. Type: dictionary
| | ... | - interface - (Sub-)interface name or SW index to set L2 tag rewrite
| | ... | method. Type: string or integer
| | ... | - tag_rewrite_method - Tag rewrite method. Type: string
| | ... | - push_dot1q - True to push tags as Dot1q, False to push tags as
| | ... | Dot1ad (Optional). Type: boolean
| | ... | - tag1_id - VLAN tag1 ID (Optional). Type: integer
| | ... | - tag2_id - VLAN tag2 ID (Optional). Type: integer
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 Tag Rewrite Method Is Set On Interface \| ${nodes['DUT1']} \
| | ... | \| 9 \| pop-1 \|
| | ... | \| L2 Tag Rewrite Method Is Set On Interface \| ${nodes['DUT2']} \
| | ... | \| 10 \| translate-1-2 \| push_dot1q=${False} \| tag1_id=10 \
| | ... | \| tag1_id=20 \|
| | ...
| | [Arguments] | ${dut_node} | ${interface} | ${tag_rewrite_method}
| | ... | ${push_dot1q}=${True} | ${tag1_id}=${None} | ${tag2_id}=${None}
| | ${result}= | Evaluate | isinstance($interface, int)
| | ${interface_name}= | Run Keyword If | ${result} | Set Variable | ${interface}
| | ...                | ELSE | Get interface name | ${dut_node} | ${interface}
| | L2 Vlan Tag Rewrite | ${dut_node} | ${interface_name} | ${tag_rewrite_method}
| | ... | push_dot1q=${push_dot1q} | tag1_id=${tag1_id} | tag2_id=${tag2_id}
