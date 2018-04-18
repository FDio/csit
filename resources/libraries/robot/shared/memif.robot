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
| Documentation | Memif interface keyword library.

*** Keywords ***
| Set up memif interfaces on DUT node
| | [Documentation] | Create two Memif interfaces on given VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${filename1} - Socket filename for 1st Memif interface. Type: string
| | ... | - ${filename2} - Socket filename for 2nd Memif interface. Type: string
| | ... | - ${mid} - Memif interface ID. Type: integer
| | ... | - ${memif_if1} - Name of the first Memif interface (Optional).
| | ... | Type: string
| | ... | - ${memif_if2} - Name of the second Memif interface (Optional).
| | ... | Type: string
| | ... | - ${rxq} - RX queues. Type: integer
| | ... | - ${txq} - TX queues. Type: integer
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${${memif_if1}} - 1st Memif interface.
| | ... | - ${${memif_if2}} - 2nd Memif interface.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up memif interfaces on DUT node \
| | ... | \| ${nodes['DUT1']} \| sock1 \| sock2 \| 1 \|
| | ... | \| Set up memif interfaces on DUT node \
| | ... | \| ${nodes['DUT2']} \| sock1 \| sock2 \| 1 \
| | ... | \| dut2_memif_if1 \| dut2_memif_if2 \| 1 \| 1 \|
| | ...
| | [Arguments] | ${dut_node} | ${filename1} | ${filename2} | ${mid}=${1}
| | ... | ${memif_if1}=memif_if1 | ${memif_if2}=memif_if2 | ${rxq}=${1}
| | ... | ${txq}=${1}
| | ${sid_1}= | Evaluate | (${mid}*2)-1
| | ${sid_2}= | Evaluate | (${mid}*2)
| | ${memif_1}= | Create memif interface | ${dut_node}
| | ... | ${filename1}${mid}-${sid_1} | ${mid} | ${sid_1} | rxq=${rxq}
| | ... | txq=${txq} | role=slave
| | ${memif_2}= | Create memif interface | ${dut_node}
| | ... | ${filename2}${mid}-${sid_2} | ${mid} | ${sid_2} | rxq=${rxq}
| | ... | txq=${txq} | role=slave
| | Set Interface State | ${dut_node} | ${memif_1} | up
| | Set Interface State | ${dut_node} | ${memif_2} | up
| | Set Test Variable | ${${memif_if1}} | ${memif_1}
| | Set Test Variable | ${${memif_if2}} | ${memif_2}
