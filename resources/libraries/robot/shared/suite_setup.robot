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

"""Keywords used in suite setup."""

*** Settings ***
| Documentation | Suite setup keywords.

*** Keywords ***
| Setup suite
| | [Documentation]
| | ... | Common test setup for tests.
| | ... |
| | ... | Compute path for testing on two given nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if1_mac - 1st TG interface MAC address.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - tg_if2_mac - 2nd TG interface MAC address.
| | ... | - dut{n} - DUTx node
| | ... | - dut{n}_if1 - 1st DUT interface.
| | ... | - dut{n}_if2 - 2nd DUT interface.
| | ...
| | [Arguments] | ${iface_model}=virtual
| | ...
| | ${iface_model_list}= | Create list | ${iface_model}
| | Append Node | ${nodes['TG']}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Append Node | ${nodes['${dut}']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_if1} | ${tg}= | First Interface
| | :FOR | ${dut} | IN | @{duts}
| | | ${dutx_if1} | ${dutx}= | Next Interface
| | | ${dutx_if2} | ${dutx}= | Next Interface
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | Set Suite Variable | ${${dut_str}} | ${dutx}
| | | Set Suite Variable | ${${dut_str}_if1} | ${dutx_if1}
| | | Set Suite Variable | ${${dut_str}_if2} | ${dutx_if2}
| | | Set Suite Variable | ${${dut_str}_if1_mac} | ${nodes['${dut}']} | ${dutx_if1}
| | | Set Suite Variable | ${${dut_str}_if2_mac} | ${nodes['${dut}']} | ${dutx_if2}
| | ${tg_if2} | ${tg}= | Last Interface
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if1_mac}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${tg_if2_mac}
