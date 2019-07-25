# Copyright (c) 2019 Cisco and/or its affiliates.
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

*** Keywords ***
| Configure L2XC
| | [Documentation] | Setup Bidirectional Cross Connect on DUTs
| | [Arguments] | ${node} | ${if1} | ${if2} |
| | Set Interface State | ${node} | ${if1} | up
| | Set Interface State | ${node} | ${if2} | up
| | Vpp Setup Bidirectional Cross Connect | ${node} | ${if1} | ${if2}

| Initialize L2 cross connect on node
| | [Documentation]
| | ... | Setup L2 cross connect topology by connecting RX/TX of two interfaces
| | ... | on each DUT. Interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of interfaces pairs to connect. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 cross connect on node \| DUT1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${count}=${1}
| | ...
| | :FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | Vpp Setup Bidirectional Cross Connect | ${nodes['${dut}']}
| | | ... | ${${dut_str}_${prev_layer}_${id}_1}
| | | ... | ${${dut_str}_${prev_layer}_${id}_2}

| Initialize L2 cross connect
| | [Documentation]
| | ... | Setup L2 cross connect topology by connecting RX/TX of two interfaces
| | ... | on each DUT. Interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of interfaces pairs to connect. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 cross connect \| 1 \|
| | ...
| | [Arguments] | ${count}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize L2 cross connect on node | ${dut} | count=${count}
