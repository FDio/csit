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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Resource | resources/libraries/robot/vat/interfaces.robot

*** Keywords ***
| VPP reports interfaces on | [Arguments] | ${node}
| | VPP reports interfaces through VAT on | ${node}
#| | VPP reports interfaces through ODL on | ${node}
#| | VPP reports interfaces through DEBUGCLI on | ${node}

| Setup MTU on TG based on MTU on DUT
| | [Documentation] | Type of the tg_node must be TG and dut_node must be DUT
| | [Arguments] | ${tg_node} | ${dut_node}
| | Append Nodes | ${tg_node} | ${dut_node}
| | Compute Path
| | ${tg_port} | ${tg_node}= | First Interface
| | ${dut_port} | ${dut_node}= | Last Interface
| | # get physical layer MTU (max. size of Ethernet frame)
| | ${mtu}= | Get Interface MTU | ${dut_node} | ${dut_port}
| | # Ethernet MTU is physical layer MTU minus size of Ethernet header and FCS
| | ${eth_mtu}= | Evaluate | ${mtu} - 14 - 4
| | Set Interface Ethernet MTU | ${tg_node} | ${tg_port} | ${eth_mtu}

