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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| ...
| Resource | resources/libraries/robot/shared/default.robot
| ...
| Documentation | IPv4 keywords

*** Keywords ***
| Configure IP addresses on interfaces
| | [Documentation] | Iterates through @{args} list and set interface IP address
| | ... | for every (${dut_node}, ${interface}, ${address},
| | ... | ${prefix}) tuple.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where IP address should be set to.
| | ... | Type: dictionary
| | ... | - interface - Interface name. Type: string
| | ... | - address - IP address. Type: string
| | ... | - prefix - Prefix length. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IP addresses on interfaces \
| | ... | \| ${dut1_node} \| ${dut1_to_dut2} \| 192.168.1.1 \| 24 \|
| | ... | \| ... \| ${dut1_node} \| ${dut1_to_tg} \| 192.168.2.1 \| 24 \|
| | ...
| | [Arguments] | @{args}
| | :FOR | ${dut_node} | ${interface} | ${address} | ${prefix} | IN | @{args}
| | | VPP Interface Set IP Address
| | | ... | ${dut_node} | ${interface} | ${address} | ${prefix}
