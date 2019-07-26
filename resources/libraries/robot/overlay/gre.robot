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
| Resource | resources/libraries/robot/shared/interfaces.robot

*** Keywords ***
| Create GRE tunnel interface and set it up
| | [Documentation] | Create GRE tunnel interface and set it up on defined VPP node and put \
| | ... | the interface to UP state.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to create GRE tunnel. Type: dictionary
| | ... | - source_ip_address - GRE tunnel source IP address. Type: string
| | ... | - destination_ip_address - GRE tunnel destination IP address.
| | ... |   Type: string
| | ...
| | ... | *Return:*
| | ... | - name - Name of created GRE tunnel interface. Type: string
| | ... | - index - SW interface index of created GRE tunnel interface.
| | ... |   Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ${gre_name} \| ${gre_index}= \
| | ... | \| Create GRE tunnel interface and set it up \| ${dut} \
| | ... | \| 192.0.1.1 \| 192.0.1.2 \|
| | ...
| | [Arguments] | ${dut_node} | ${source_ip_address} | ${destination_ip_address}
| | ${name} | ${index}= | Create GRE tunnel interface
| | ... | ${dut_node} | ${source_ip_address} | ${destination_ip_address}
| | Set Interface State | ${dut_node} | ${index} | up
| | [Return] | ${name} | ${index}
