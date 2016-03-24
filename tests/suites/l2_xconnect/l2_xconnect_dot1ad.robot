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
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.InterfaceSetup
| Library | resources.libraries.python.L2Util
| Library  | resources.libraries.python.IPv4Util
| Library  | resources.libraries.python.IPUtil
| Library | resources.libraries.python.NodePath
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | VM_ENV
| Test Setup | Setup all DUTs before test
| Suite Setup | Setup all TGs before traffic script
| Suite Teardown | Show Packet Trace on All DUTs | ${nodes}

*** Variables ***
| ${subid}= | 10

*** Test Cases ***
| VPP can push two VLAN tags to traffic transfering through xconnect
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...          | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface


| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | ${vlan_int_name} | ${vlan_int_index}= | Create Subinterface | ${dut1}
| | ...                                   | ${dut1_if2} | ${subid}
| | Set Interface State | ${dut1} | ${vlan_int_index} | up
| | L2 tag rewrite pop2 | ${dut1} | ${vlan_int_index}


| | Vpp Setup Bidirectional Cross Connect | ${dut1} | ${dut1_if1} | ${vlan_int_index}

#| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${dut1_if2} |
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}

| | All Vpp Interfaces Ready Wait | ${nodes}
| | Send and receive ICMPv4 | ${tg} | ${tg_if1} | ${tg_if2}
#| | Send and receive ICMPv4 | ${tg} | ${tg_if2} | ${tg_if1}
