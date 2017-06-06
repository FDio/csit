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

*** Settings ***
| Library | resources.libraries.python.Memif

*** Keywords ***
| Set up memif interfaces on DUT node
| | [Documentation] | Create two Memif interfaces on given VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${sock1} - Socket path for first Memif interface. Type: string
| | ... | - ${sock2} - Socket path for second Memif interface. Type: string
| | ... | - ${number} - Memif interface key. Type: integer
| | ... | - ${memif_if1} - Name of the first Memif interface (Optional).
| | ... | Type: string
| | ... | - ${memif_if2} - Name of the second Memif interface (Optional).
| | ... | Type: string
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${${memif_if1}} - First Memif interface.
| | ... | - ${${memif_if2}} - Second Memif interface.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up memif interfaces on DUT node \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| 1 \|
| | ... | \| Set up memif interfaces on DUT node \
| | ... | \| ${nodes['DUT2']} \| /tmp/sock1 \| /tmp/sock2 \| 1 \
| | ... | \| dut2_memif_if1 \| dut2_memif_if2 \|
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${number}
| | ... | ${memif_if2}=memif_if1 | ${memif_if1}=memif_if2
| | ${key_1}= | Evaluate | (${number}*2)-1
| | ${key_2}= | Evaluate | (${number}*2)
| | ${memif_1}= | Create memif interface | ${dut_node} | ${sock1} | ${key_1}
| | ${memif_2}= | Create memif interface | ${dut_node} | ${sock2} | ${key_2}
| | Set Interface State | ${dut_node} | ${memif_1} | up
| | Set Interface State | ${dut_node} | ${memif_2} | up
| | Set Test Variable | ${${memif_if1}} | ${memif_1}
| | Set Test Variable | ${${memif_if2}} | ${memif_2}

| Initialize L2 xconnect for '${nr}' memif pairs in 3-node circular topology
| | [Documentation]
| | ... | Create pairs of Memif interfaces on all defined VPP nodes. Cross
| | ... | connect each Memif interface with one physical interface or virtual
| | ... | interface to create a chain accross DUT node.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | *Note:*
| | ... | Socket paths for Memif are defined in following format:
| | ... | - /tmp/memif-${number}-1
| | ... | - /tmp/memif-${number}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 xconnect for 1 Memif in 3-node circular topology
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | All Vpp Interfaces Ready Wait | ${nodes}
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| |      | ${sock1}= | Set Variable | /tmp/memif-${number}-1
| |      | ${sock2}= | Set Variable | /tmp/memif-${number}-2
| |      | ${prev_index}= | Evaluate | ${number}-1
| |      | Set up memif interfaces on DUT node | ${dut1}
| |      | ... | ${sock1} | ${sock2} | ${number} | dut1-memif-${number}-if1
| |      | ... | dut1-memif-${number}-if2
| |      | ${dut1_xconnect_if1}= | Set Variable If | ${number}==1 | ${dut1_if1}
| |      | ... | ${dut1-memif-${prev_index}-if2}
| |      | Configure L2XC | ${dut1} | ${dut1_xconnect_if1}
| |      | ... | ${dut1-memif-${number}-if1}
| |      | Set up memif interfaces on DUT node | ${dut2}
| |      | ... | ${sock1} | ${sock2} | ${number} | dut2-memif-${number}-if1
| |      | ... | dut2-memif-${number}-if2
| |      | ${dut2_xconnect_if1}= | Set Variable If | ${number}==1 | ${dut2_if1}
| |      | ... | ${dut2-memif-${prev_index}-if2}
| |      | Configure L2XC | ${dut2} | ${dut2_xconnect_if1}
| |      | ... | ${dut2-memif-${number}-if1}
| |      | Run Keyword If | ${number}==${nr} | Configure L2XC
| |      | ... | ${dut1} | ${dut1-memif-${number}-if2} | ${dut1_if2}
| |      | Run Keyword If | ${number}==${nr} | Configure L2XC
| |      | ... | ${dut2} | ${dut2-memif-${number}-if2} | ${dut2_if2}

| Create memif VPP configuration on '${nr}' LXC containers on '${dut}' node
| | [Documentation] | Create memif configuration of VPP on multiple LXC
| | ... | container on DUT node.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create memif VPP configuration on 1 LXC containers on DUT1 node \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | Run Keyword | ${dut}_${lxc_base_name}_${number}.Create VPP cfg in container
| | | ... | "memif_create_lxc.vat" | socket1=memif-${number}-1
| | | ... | socket2=memif-${numb er}-2

| Create memif VPP configuration on '${nr}' LXC containers on all DUT nodes
| | [Documentation] | Create memif configuration of VPP on multiple LXC
| | ... | container on all DUT nodes.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create memif VPP configuration on 1 LXC containers on all \
| | ... | DUT nodes \|
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Create memif VPP configuration on '${nr}' LXC containers on '${dut}' node
