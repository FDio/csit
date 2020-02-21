# Copyright (c) 2020 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.L2Util

*** Keywords ***
| Initialize L2 patch
| | [Documentation]
| | ... | Setup L2 patch topology by cross connecting two interfaces on
| | ... | each DUT. Interfaces are brought up.
| |
| | FOR | ${dut} | IN | @{duts}
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | VPP Setup Bidirectional L2 patch
| | | ... | ${nodes['${dut}']}
| | | ... | ${${dut_str}_${prev_layer}1}[0] | ${${dut_str}_${prev_layer}2}[0]
| | END
| | Set interfaces in path up
