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
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${number}=${1}
| | ... | ${memif_if1}=memif_if1 | ${memif_if2}=memif_if2
| | ${key_1}= | Evaluate | (${number}*2)-1
| | ${key_2}= | Evaluate | (${number}*2)
| | ${memif_1}= | Create memif interface | ${dut_node} | ${sock1} | ${key_1}
| | ${memif_2}= | Create memif interface | ${dut_node} | ${sock2} | ${key_2}
| | Set Interface State | ${dut_node} | ${memif_1} | up
| | Set Interface State | ${dut_node} | ${memif_2} | up
| | Set Test Variable | ${${memif_if1}} | ${memif_1}
| | Set Test Variable | ${${memif_if2}} | ${memif_2}
