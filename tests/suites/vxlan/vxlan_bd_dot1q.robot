# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agrehttps://jenkins.fd.io/job/csit-vpp-functional-virl/581/ed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

*** Settings ***
| Documentation | VXLAN tunnel over Dot1Q tagged IPv4 traffic tests using bridge domain.
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/vxlan.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Vpp Show Errors Verbose | ${nodes['DUT1']}
| ...           | AND          | Vpp Show Errors Verbose | ${nodes['DUT2']}

*** Variables ***
| ${VNI}= | 23
| ${BID}= | 23
| ${VLAN}= | 10

*** Test Cases ***
| VPP can encapsulate L2 in VXLAN over IPv4 over Dot1Q
| | Given Path for VXLAN testing is set
| | ...   | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | And   Interfaces in path are up
| | And   Vlan interfaces for VXLAN are created | ${VLAN}
| |       ...                                   | ${dut1} | ${dut1s_to_dut2}
| |       ...                                   | ${dut2} | ${dut2s_to_dut1}
| | And   IP addresses are set on interfaces
| |       ...         | ${dut1} | ${dut1s_vlan_name} | ${dut1s_vlan_index}
| |       ...         | ${dut2} | ${dut2s_vlan_name} | ${dut2s_vlan_index}
| | ${dut1s_vxlan}= | When Create VXLAN interface     | ${dut1} | ${VNI}
| |                 | ...  | ${dut1s_ip_address} | ${dut2s_ip_address}
| |                   And  Interfaces are added to BD | ${dut1} | ${BID}
| |                   ...  | ${dut1s_to_tg} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | And  Create VXLAN interface     | ${dut2} | ${VNI}
| |                 | ...  | ${dut2s_ip_address} | ${dut1s_ip_address}
| |                   And  Interfaces are added to BD | ${dut2} | ${BID}
| |                   ...  | ${dut2s_to_tg} | ${dut2s_vxlan}
| | And Vpp Node Interfaces Ready Wait | ${DUT1}
| | And Vpp Node Interfaces Ready Wait | ${DUT2}
| | Then Send and receive ICMPv4 bidirectionally
| | ... | ${tg} | ${tgs_to_dut1} | ${tgs_to_dut2}
