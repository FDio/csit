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
| Documentation | RFC7348 VXLAN: Test L2 bridge-domain with VXLAN tunnel
| ...           | interfaces. VXLAN tunnels configured over IPv4 and dot1q VLAN
| ...           | tagged Ethernet.
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/vxlan.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}

*** Variables ***
| ${VNI}= | 23
| ${BID}= | 23
| ${VLAN}= | 10

*** Test Cases ***
| TC08: DUT1 and DUT2 with L2BD and VXLANoIPv4oVLAN tunnels switch ICMPv4 between TG links
| | [Documentation] | RFC7348 VXLAN: DUT1-DUT2 Eth-dot1q-IPv4-VXLAN-Eth-IPv4-ICMPv4:
| | ...             | TG-DUT1 TG-DUT2 Eth-dot1q-IPv4-ICMPv4: On DUT1 and DUT2 configure
| | ...             | L2 bridge-domain (MAC learning enabled), each with one
| | ...             | interface to TG and one VXLAN tunnel interface towards the
| | ...             | other DUT. Make TG send ICMPv4 Echo Req between two of its
| | ...             | interfaces, verify all packets are received.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And   Interfaces in 3-node path are up
| | And   Vlan interfaces for VXLAN are created | ${VLAN}
| |       ...                                   | ${dut1_node} | ${dut1_to_dut2}
| |       ...                                   | ${dut2_node} | ${dut2_to_dut1}
| | And   IP addresses are set on interfaces
| |       ...         | ${dut1_node} | ${dut1s_vlan_name} | ${dut1s_vlan_index}
| |       ...         | ${dut2_node} | ${dut2s_vlan_name} | ${dut2s_vlan_index}
| | ${dut1s_vxlan}= | When Create VXLAN interface     | ${dut1_node} | ${VNI}
| |                 | ...  | ${dut1s_ip_address} | ${dut2s_ip_address}
| |                   And  Interfaces are added to BD | ${dut1_node} | ${BID}
| |                   ...  | ${dut1_to_tg} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | And  Create VXLAN interface     | ${dut2_node} | ${VNI}
| |                 | ...  | ${dut2s_ip_address} | ${dut1s_ip_address}
| |                   And  Interfaces are added to BD | ${dut2_node} | ${BID}
| |                   ...  | ${dut2_to_tg} | ${dut2s_vxlan}
| | Then Send and receive ICMPv4 bidirectionally
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
