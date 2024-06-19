# Copyright (c) 2024 Cisco and/or its affiliates.
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
| Documentation | Memif interface keyword library.
|
| Library | resources.libraries.python.Memif
| Variables | resources/libraries/python/Constants.py

*** Keywords ***
| Set up memif interfaces on DUT node
| | [Documentation] | Create two Memif interfaces on given VPP node.
| | ... | Also create test variables named as the provided interface names,
| | ... | the values hold the sw_if_index values for the newly created variables.
| | ... | TODO: Add those to the current topology state properly.
| |
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - filename1 - Socket filename for 1st Memif interface. Type: string
| | ... | - filename2 - Socket filename for 2nd Memif interface. Type: string
| | ... | - mid - Memif interface ID. Type: integer, default value: ${1}
| | ... | - memif_if1 - Name of the first Memif interface (Optional).
| | ... | Type: string, default value: memif_if1
| | ... | - memif_if2 - Name of the second Memif interface (Optional).
| | ... | Type: string, default value: memif_if2
| | ... | - rxq - RX queues; 0 means do not set (Optional). Type: integer,
| | ... | default value: ${1}
| | ... | - txq - TX queues; 0 means do not set (Optional). Type: integer,
| | ... | default value: ${1}
| | ... | - role - Memif role (Optional). Type: string, default value: SLAVE
| |
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - \${\${memif_if1}} - 1st Memif interface.
| | ... | - \${\${memif_if2}} - 2nd Memif interface.
| |
| | ... | *Example:*
| |
| | ... | \| Set up memif interfaces on DUT node \
| | ... | \| \${nodes['DUT1']} \| sock1 \| sock2 \| 1 \|
| | ... | \| Set up memif interfaces on DUT node \
| | ... | \| \${nodes['DUT2']} \| sock1 \| sock2 \| 1 \
| | ... | \| dut2_memif_if1 \| dut2_memif_if2 \| 1 \| 1 \| SLAVE \|
| | ... | \| \${nodes['DUT2']} \| sock1 \| sock2 \| 1 \| rxq=0 \| txq=0 \
| | ... | \| dcr_uuid=_a5730a0a-2ba1-4fe9-91bd-79b9828e968e \|
| |
| | [Arguments] | ${dut_node} | ${filename1} | ${filename2} | ${mac} | ${mid}=${1}
| | ... | ${memif_if1}=memif_if1 | ${memif_if2}=memif_if2 | ${rxq}=${1}
| | ... | ${txq}=${1} | ${role}=MASTER
| |
| | ${sid_1}= | Evaluate | (${mid}*2)-1
| | ${sid_2}= | Evaluate | (${mid}*2)
| | ${memif_1_swindex}= | Create memif interface | ${dut_node}
| | ... | ${filename1}${mid}${DUT1_UUID}-${sid_1} | ${mid} | ${sid_1}
| | ... | rxq=${rxq} | txq=${txq} | role=${role} | mac=${mac}
| | ${memif_2_swindex}= | Create memif interface | ${dut_node}
| | ... | ${filename2}${mid}${DUT1_UUID}-${sid_2} | ${mid} | ${sid_2}
| | ... | rxq=${rxq} | txq=${txq} | role=${role} | mac=${mac}
| | Set Interface State | ${dut_node} | ${memif_1_swindex} | up
| | Set Interface State | ${dut_node} | ${memif_2_swindex} | up
| | Set Test Variable | ${${memif_if1}} | ${memif_1_swindex}
| | Set Test Variable | ${${memif_if2}} | ${memif_2_swindex}

| Set up single memif interface on DUT node
| | [Documentation] | Create single Memif interface on given VPP node.
| |
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - filename - Socket filename for Memif interface. Type: string
| | ... | - mid - Memif interface ID (Optional). Type: integer
| | ... | - sid - Memif socket ID (Optional). Type: integer
| | ... | - memif_if - Name of the Memif interface (Optional).
| | ... | Type: string
| | ... | - rxq - RX queues (Optional). Type: integer
| | ... | - txq - TX queues (Optional). Type: integer
| | ... | - role - Memif role (Optional). Type: string
| |
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${${memif_if}} - Memif interface.
| |
| | ... | *Example:*
| |
| | ... | \| Set up single memif interface on DUT node \
| | ... | \| \${nodes['DUT1']} \| sock1 \| 1 \| dut1_memif_if1 \| 1 \| 1 \
| | ... | \| SLAVE \|
| |
| | [Arguments] | ${dut_node} | ${filename} | ${mid}=${1} | ${sid}=${1}
| | ... | ${memif_if}=memif_if1 | ${rxq}=${1} | ${txq}=${1} | ${role}=MASTER
| |
| | ${memif}= | Create memif interface | ${dut_node} | ${filename}${mid}-${sid}
| | ... | ${mid} | ${sid} | rxq=${rxq} | txq=${txq} | role=${role}
| | Set Interface State | ${dut_node} | ${memif} | up
| | Set Test Variable | ${${memif_if}} | ${memif}
