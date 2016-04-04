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

| Node path computed for 3-node topology
| | [Arguments] | ${TG} | ${DUT1} | ${DUT2}
| | [Documentation] | *Create interface variables for 3-node topology.*
| | ...
| | ... | *Arguments:*
| | ... | - ${TG} - Node attached to the path. Type: dictionary
| | ... | - ${DUT1} - Node attached to the path. Type: dictionary
| | ... | - ${DUT2} - Node attached to the path. Type: dictionary
| | ...
| | ... | _Set testcase variables for nodes and interfaces._
| | ... | - ${tg} - Variable for node in path. Type: dictionary
| | ... | - ${dut1} - Variable for node in path. Type: dictionary
| | ... | - ${dut2} - Variable for node in path. Type: dictionary
| | ... | - ${tg_if1} - First interface of TG node. Type: str
| | ... | - ${tg_if2} - Second interface of TG node. Type: str
| | ... | - ${dut1_if1} - First interface of first DUT node. Type: str
| | ... | - ${dut1_if2} - Second interface of first DUT node. Type: str
| | ... | - ${dut2_if1} - First interface of second DUT node. Type: str
| | ... | - ${dut2_if2} - Second interface of second DUT node. Type: str
| | ...
| | Append Nodes | ${TG} | ${DUT1} | ${DUT2} | ${TG}
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

| Interfaces in path are up
| | [Documentation] | *Set UP state on interfaces in path on nodes.*
| | ...
| | Set Interface State | ${tg} | ${tg_if1} | up
| | Set Interface State | ${tg} | ${tg_if2} | up
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Vpp Node Interfaces Ready Wait | ${dut2}

| VLAN subinterfaces initialized on 3-node topology
| | [Arguments] | ${DUT1} | ${INT1} | ${DUT2} | ${INT2} | ${SUB_ID}
| | ...         | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID} | ${TYPE_SUBIF}
| | [Documentation] | *Create two subinterfaces on DUTs.*
| | ...
| | ... | *Arguments:*
| | ... | - ${DUT1} - Node to add sub-interface.
| | ... | - ${INT1} - Interface name on which create sub-interface.
| | ... | - ${DUT2} - Node to add sub-interface.
| | ... | - ${INT2} - Interface name on which create sub-interface.
| | ... | - ${SUB_ID} - ID of the sub-interface to be created.
| | ... | - ${OUTER_VLAN_ID} - Outer VLAN ID.
| | ... | - ${INNER_VLAN_ID} - Inner VLAN ID.
| | ... | - ${TYPE_SUBIF} - Type of sub-interface.
| | ...
| | ... | _Set testcase variables with name and index of created interfaces:_
| | ... | - ${subif_name_1}
| | ... | - ${subif_index_1}
| | ... | - ${subif_name_2}
| | ... | - ${subif_index_2}
| | ...
| | ${subif_name_1} | ${subif_index_1}= | Create subinterface | ${DUT1}
| | ...                                 | ${INT1} | ${SUB_ID}
| | ...                                 | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID}
| | ...                                 | ${TYPE_SUBIF}
| | ${subif_name_2} | ${subif_index_2}= | Create subinterface | ${DUT2}
| | ...                                 | ${INT2} | ${SUB_ID}
| | ...                                 | ${OUTER_VLAN_ID} | ${INNER_VLAN_ID}
| | ...                                 | ${TYPE_SUBIF}
| | Set Interface State | ${DUT1} | ${subif_index_1} | up
| | Set Interface State | ${DUT2} | ${subif_index_2} | up
| | Set Test Variable | ${subif_name_1}
| | Set Test Variable | ${subif_index_1}
| | Set Test Variable | ${subif_name_2}
| | Set Test Variable | ${subif_index_2}

| L2 tag rewrite pop 2 tags setup on interfaces
| | [Arguments] | ${DUT1} | ${SUB_INT1} | ${DUT2} | ${SUB_INT2}
| | ...         | ${TAG_REWRITE_METHOD}
| | [Documentation] | *Setup tag rewrite on sub-interfaces on DUTs.*
| | ...
| | ... | *Arguments:*
| | ... | - ${DUT1} - Node to rewrite tags.
| | ... | - ${SUB_INT1} - Interface on which rewrite tags.
| | ... | - ${DUT2} - Node to rewrite tags.
| | ... | - ${SUB_INT2} - Interface on which rewrite tags.
| | ... | - ${TAG_REWRITE_METHOD} - Method of tag rewrite.
| | ...
| | L2 tag rewrite | ${DUT1} | ${SUB_INT1} | ${TAG_REWRITE_METHOD}
| | L2 tag rewrite | ${DUT2} | ${SUB_INT2} | ${TAG_REWRITE_METHOD}

| Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | [Arguments] | ${DUT1} | ${INT1} | ${SUB_INT1}
| | ...         | ${DUT2} | ${INT2} | ${SUB_INT2}
| | [Documentation] | *Add interface and subinterface to bidirectional
| | ...             | L2-xconnect on DUTs.*
| | ...
| | ... | *Arguments:*
| | ... | - ${DUT1} - Node to add bidirectional cross-connect.
| | ... | - ${INT1} - Interface to add to the cross-connect.
| | ... | - ${SUB_INT1} - Sub-interface to add to the cross-connect.
| | ... | - ${DUT2} - Node to add bidirectional cross-connect.
| | ... | - ${INT2} - Interface to add to the cross-connect.
| | ... | - ${SUB_INT2} - Sub-interface to add to the cross-connect.
| | ...
| | L2 setup xconnect on DUT | ${DUT1} | ${INT1} | ${SUB_INT1}
| | L2 setup xconnect on DUT | ${DUT2} | ${INT2} | ${SUB_INT2}
