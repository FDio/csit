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
| Library | resources.libraries.python.IPv4Util.IPv4Util
| Library | resources.libraries.python.IPv4Setup.IPv4Setup
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Cop
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.InterfaceUtil

*** Keywords ***
| Setup Nodes And Variables
| | [Documentation] | Setup of test variables and bring interfaces up.
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - ${tg_if1} - Iterface of TG towards DUT (1st).
| | ... | - ${tg_if2} - Interface of TG towards DUT (2nd).
| | ... | - ${dut1_if1} - Interface of DUT towards TG (1st).
| | ... | - ${dut1_if2} - Interface of DUT towards TG (2nd).
| | ... | - ${dut2_if1} - Interface of DUT2 towards DUT (1st).
| | ... | - ${dut2_if2} - Interface of DUT2 towards TG (2nd).
| | ... | - ${dut1} - DUT1 node.
| | ... | - ${dut2} - DUT2 node.
| | ... | - ${tg} - TG node.
| | ... | - ${tg_if1_mac} - MAC address of TG interface (1st).
| | ... | - ${tg_if2_mac} - MAC address of TG interface (2nd).
| | ... | - ${dut1_if1_mac} - MAC address of DUT1 interface (1st).
| | ... | - ${dut1_if2_mac} - MAC address of DUT1 interface (2nd).
| | ...
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} |
| | ... | ${nodes['TG']}
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
| | Set Test Variable | ${dut1}
| | Set Test Variable | ${dut2}
| | Set Test Variable | ${tg}
| | Set Test Variable | ${tg_if1_mac}
| | Set Test Variable | ${tg_if2_mac}
| | Set Test Variable | ${dut1_if1_mac}
| | Set Test Variable | ${dut1_if2_mac}
| | Set Interface State | ${tg} | ${tg_if1} | up
| | Set Interface State | ${tg} | ${tg_if2} | up
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | All Vpp Interfaces Ready Wait | ${nodes}

| Set Xconnect, ARP, and One Route
| | [Documentation] | Setup for ONE way packet flow only.
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Set Interface Address | ${dut1} | ${dut1_if1} | ${dut1_if1_ip} |
| | ... | ${ip_prefix}
| | Set Interface Address | ${dut1} | ${dut1_if2} | ${dut1_if2_ip} |
| | ... | ${ip_prefix}
| | Add Arp On Dut | ${dut1} | ${dut1_if1} | ${dut1_if1_ip_GW} | ${tg_if1_mac}
| | Add Arp On Dut | ${dut1} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | Vpp Route Add | ${dut1} | ${dst_ip_prefix} | ${dst_ip_prefix_length} |
| | ... | ${dut1_if2_ip_GW} | ${dut1_if2}

| Set Xconnect and One Route
| | [Documentation] | Setup for ONE way packet flow only.
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Set Interface Address | ${dut1} | ${dut1_if1} | ${dut1_if1_ip} |
| | ... | ${ip_prefix}
| | Set Interface Address | ${dut1} | ${dut1_if2} | ${dut1_if2_ip} |
| | ... | ${ip_prefix}
| | Vpp Route Add | ${dut1} | ${test_dst_ip} | ${ip_prefix} |
| | ... | ${dut1_if2_ip_GW} | ${dut1_if2}