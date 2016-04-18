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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/counters.robot
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Cop
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.InterfaceUtil

*** Keywords ***
| Setup Nodes And Variables
| | [Documentation] | Setup of test variables and bring interfaces up.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - {tg_node} : Node where to start/end. Type: dictionary
| | ... | - {dut1_node} - Next node from start. Type: dictionary
| | ... | - {dut2_node} - Third node. Type: dictionary
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Setup Nodes And Variables \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1']} \| ${nodes['DUT2']} \|
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ...
| | ... | - ${tg_if1} - Iterface of TG towards DUT (1st).
| | ... | - ${tg_if2} - Interface of TG towards DUT (2nd).
| | ... | - ${dut1_if1} - Interface of DUT towards TG (1st).
| | ... | - ${dut1_if2} - Interface of DUT towards TG (2nd).
| | ... | - ${dut2_if1} - Interface of DUT2 towards DUT (1st).
| | ... | - ${dut2_if2} - Interface of DUT2 towards TG (2nd).
| | ... | - ${tg_if1_mac} - MAC address of TG interface (1st).
| | ... | - ${tg_if2_mac} - MAC address of TG interface (2nd).
| | ... | - ${dut1_if1_mac} - MAC address of DUT1 interface (1st).
| | ... | - ${dut1_if2_mac} - MAC address of DUT1 interface (2nd).
| | ...
| | [Arguments] | ${tg_node} | ${dut1_node} | ${dut2_node}
| | Append Nodes | ${tg_node} | ${dut1_node} | ${dut2_node} |
| | ... | ${tg_node}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | ${tg_if1_mac}= | Get interface mac | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get interface mac | ${tg} | ${tg_if2}
| | ${dut1_if1_mac}= | Get interface mac | ${dut1} | ${dut1_if1}
| | ${dut1_if2_mac}= | Get interface mac | ${dut1} | ${dut1_if2}
| | Set Test Variable | ${tg_if1}
| | Set Test Variable | ${tg_if2}
| | Set Test Variable | ${dut1_if1}
| | Set Test Variable | ${dut1_if2}
| | Set Test Variable | ${dut2_if1}
| | Set Test Variable | ${dut2_if2}
| | Set Test Variable | ${tg_if1_mac}
| | Set Test Variable | ${tg_if2_mac}
| | Set Test Variable | ${dut1_if1_mac}
| | Set Test Variable | ${dut1_if2_mac}
| | Set Interface State | ${tg_node} | ${tg_if1} | up
| | Set Interface State | ${tg_node} | ${tg_if2} | up
| | Set Interface State | ${dut1_node} | ${dut1_if1} | up
| | Set Interface State | ${dut1_node} | ${dut1_if2} | up
| | Set Interface State | ${dut2_node} | ${dut2_if1} | up
| | Set Interface State | ${dut2_node} | ${dut2_if2} | up
| | All Vpp Interfaces Ready Wait | ${nodes}

| Set IPv4 Interface Addresses
| | [Documentation] | Setup of interface IP addresses
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - {dut1_node} - First node. Type: dictionary
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set IPv4 Interface Addresses \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut1_node}
| | Set Interface Address | ${dut1_node} | ${dut1_if1} | ${dut1_if1_ip} |
| | ... | ${ip_prefix}
| | Set Interface Address | ${dut1_node} | ${dut1_if2} | ${dut1_if2_ip} |
| | ... | ${ip_prefix}

| Set ARP on Nodes
| | [Documentation] | Setup of ARP on one DUT
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - {dut1_node} - First node. Type: dictionary
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set ARP on Nodes \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut1_node}
| | Add Arp On Dut | ${dut1_node} | ${dut1_if1} | ${dut1_if1_ip_GW} |
| | ... | ${tg_if1_mac}
| | Add Arp On Dut | ${dut1_node} | ${dut1_if2} | ${dut1_if2_ip_GW} |
| | ... | ${tg_if2_mac}

| Set IPv6 Interface Addresses
| | [Documentation] | Setup of interface IP addresses
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - {dut1_node} - First node. Type: dictionary
| | ... | - {dut2_node} - Second node. Type: dictionary
| | ...
| | ... | *Return:*
| | ...
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set IPv6 Interface Addresses \| ${nodes['DUT1']} \|
| | ... | \| ${nodes['DUT2']} \|
| | ...
| | [Arguments] | ${dut1_node} | ${dut2_node}
| | VPP Set IF IPv6 Addr | ${dut1_node} | ${dut1_if1} | ${dut1_if1_ip} |
| | ... | ${ip_prefix}
| | VPP Set IF IPv6 Addr | ${dut1_node} | ${dut1_if2} | ${dut1_if2_ip} |
| | ... | ${ip_prefix}
| | VPP Set IF IPv6 Addr | ${dut2_node} | ${dut2_if1} | ${dut2_if1_ip} |
| | ... | ${ip_prefix}
| | VPP Set IF IPv6 Addr | ${dut2_node} | ${dut2_if2} | ${dut2_if2_ip} |
| | ... | ${ip_prefix}
