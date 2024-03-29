# Copyright (c) 2022 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
|
| Documentation | Keywords for VLAN tests

*** Keywords ***
| Initialize VLAN sub-interfaces in 3-node circular topology
| | [Arguments] | ${DUT1} | ${INT1} | ${DUT2} | ${INT2} | ${SUB_ID}
| | ... | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID} | ${TYPE_SUBIF}
| | [Documentation] | Create two subinterfaces on DUTs.
| |
| | ... | *Arguments:*
| | ... | - DUT1 - Node to add sub-interface.
| | ... | - INT1 - Interface key on which create sub-interface.
| | ... | - DUT2 - Node to add sub-interface.
| | ... | - INT2 - Interface key on which create sub-interface.
| | ... | - SUB_ID - ID of the sub-interface to be created.
| | ... | - OUTER_VLAN_ID - Outer VLAN ID.
| | ... | - INNER_VLAN_ID - Inner VLAN ID.
| | ... | - TYPE_SUBIF - Type of sub-interface.
| |
| | ... | _Set testcase variables with name and index of created interfaces:_
| | ... | - subif_name_1
| | ... | - subif_index_1
| | ... | - subif_name_2
| | ... | - subif_index_2
| |
| | Set Interface State | ${DUT1} | ${INT1} | up
| | Set Interface State | ${DUT2} | ${INT2} | up
| | ${INT1_name}= | Get interface name | ${DUT1} | ${INT1}
| | ${subif_name_1} | ${subif_index_1}= | Create subinterface | ${DUT1}
| | ... | ${INT1_name} | ${SUB_ID} | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID}
| | ... | ${TYPE_SUBIF}
| | ${INT2_name}= | Get interface name | ${DUT2} | ${INT2}
| | ${subif_name_2} | ${subif_index_2}= | Create subinterface | ${DUT2}
| | ... | ${INT2_name} | ${SUB_ID} | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID}
| | ... | ${TYPE_SUBIF}
| | Set Interface State | ${DUT1} | ${subif_index_1} | up
| | Set Interface State | ${DUT2} | ${subif_index_2} | up
| | Set Test Variable | ${subif_name_1}
| | Set Test Variable | ${subif_index_1}
| | Set Test Variable | ${subif_name_2}
| | Set Test Variable | ${subif_index_2}

| Initialize VLAN dot1q sub-interfaces in circular topology
| | [Arguments] | ${DUT1} | ${INT1} | ${DUT2}=${None} | ${INT2}=${None}
| | ... | ${SUB_ID}=10
| | [Documentation] | Create two dot1q subinterfaces on DUTs.
| |
| | ... | *Arguments:*
| | ... | - DUT1 - Node to add sub-interface.
| | ... | - INT1 - Interface key on which create VLAN sub-interface.
| | ... | - DUT2 - Node to add sub-interface.
| | ... | - INT2 - Interface key on which create VLAN sub-interface.
| | ... | - SUB_ID - ID of the sub-interface to be created.
| |
| | ... | _Set testcase variables with name and index of created interfaces:_
| | ... | - subif_name_1
| | ... | - subif_index_1
| | ... | - subif_name_2
| | ... | - subif_index_2
| |
| | ... | *Example:*
| |
| | ... | \| Initialize VLAN dot1q sub-interfaces in circular topology \
| | ... | \| ${nodes['DUT1']} \| ${dut1_if2} \| ${nodes['DUT2']} \
| | ... | \| ${dut1_if2} \| 10 \|
| |
| | Set Interface State | ${DUT1} | ${INT1} | up
| | Run Keyword If | ${DUT2} != ${None}
| | ... | Set Interface State | ${DUT2} | ${INT2} | up
| | ${INT1_NAME}= | Get interface name | ${DUT1} | ${INT1}
| | ${INT2_NAME}= | Run Keyword If | ${DUT2} != ${None}
| | ... | Get interface name | ${DUT2} | ${INT2}
| | ${subif_name_1} | ${subif_index_1}= | Create Vlan Subinterface
| | ... | ${DUT1} | ${INT1_NAME} | ${SUB_ID}
| | ${subif_name_2} | ${subif_index_2}=
| | ... | Run Keyword If | ${DUT2} != ${None}
| | ... | Create Vlan Subinterface | ${DUT2} | ${INT2_NAME} | ${SUB_ID}
| | Set Interface State | ${DUT1} | ${subif_index_1} | up
| | Run Keyword If | ${DUT2} != ${None}
| | ... | Set Interface State | ${DUT2} | ${subif_index_2} | up
| | Set Test Variable | ${subif_name_1}
| | Set Test Variable | ${subif_index_1}
| | Run Keyword If | ${DUT2} != ${None}
| | ... | Set Test Variable | ${subif_name_2}
| | Run Keyword If | ${DUT2} != ${None}
| | ... | Set Test Variable | ${subif_index_2}

| Configure L2 tag rewrite method on interfaces
| | [Arguments] | ${DUT1} | ${SUB_INT1} | ${DUT2}=${None} | ${SUB_INT2}=${None}
| | ... | ${TAG_REWRITE_METHOD}=${None}
| | [Documentation] | Setup tag rewrite on sub-interfaces on DUTs.
| |
| | ... | *Arguments:*
| | ... | - DUT1 - Node to rewrite tags.
| | ... | - SUB_INT1 - Interface on which rewrite tags.
| | ... | - DUT2 - Node to rewrite tags.
| | ... | - SUB_INT2 - Interface on which rewrite tags.
| | ... | - TAG_REWRITE_METHOD - Method of tag rewrite.
| |
| | L2 Vlan tag rewrite | ${DUT1} | ${SUB_INT1} | ${TAG_REWRITE_METHOD}
| | Run Keyword If | ${DUT2} != ${None}
| | ... | L2 Vlan tag rewrite | ${DUT2} | ${SUB_INT2} | ${TAG_REWRITE_METHOD}

| Configure L2 tag rewrite method on interface
| | [Documentation] | Set L2 tag rewrite on (sub-)interface on DUT
| |
| | ... | *Arguments:*
| | ... | - dut_node - Node to set L2 tag rewrite method. Type: dictionary
| | ... | - interface - (Sub-)interface name or SW index to set L2 tag rewrite
| | ... | method. Type: string or integer
| | ... | - tag_rewrite_method - Tag rewrite method. Type: string
| | ... | - push_dot1q - True to push tags as Dot1q, False to push tags as
| | ... | Dot1ad (Optional). Type: boolean
| | ... | - tag1_id - VLAN tag1 ID (Optional). Type: integer
| | ... | - tag2_id - VLAN tag2 ID (Optional). Type: integer
| |
| | ... | *Return:*
| |
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Configure L2 tag rewrite method on interface \| ${nodes['DUT1']} \
| | ... | \| 9 \| pop-1 \|
| | ... | \| Configure L2 tag rewrite method on interface \| ${nodes['DUT2']} \
| | ... | \| 10 \| translate-1-2 \| push_dot1q=${False} \| tag1_id=10 \
| | ... | \| tag1_id=20 \|
| |
| | [Arguments] | ${dut_node} | ${interface} | ${tag_rewrite_method}
| | ... | ${push_dot1q}=${True} | ${tag1_id}=${None} | ${tag2_id}=${None}
| |
| | ${result}= | Evaluate | isinstance($interface, int)
| | ${interface_name}= | Run Keyword If | ${result}
| | ... | Set Variable | ${interface}
| | ... | ELSE | Get interface name | ${dut_node} | ${interface}
| | L2 Vlan Tag Rewrite | ${dut_node} | ${interface_name}
| | ... | ${tag_rewrite_method} | push_dot1q=${push_dot1q} | tag1_id=${tag1_id}
| | ... | tag2_id=${tag2_id}
