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
| Documentation | TBD
#TODO: documentation
#TODO: reformat file
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/gre.robot
| Resource | resources/libraries/robot/l3_traffic.robot
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}

*** Variables ***
| ${dut1_ip_address}= | 192.168.1.1
| ${dut2_ip_address}= | 192.168.1.2
| ${dut1_gre_ip_address}= | 172.16.0.1
| ${dut2_gre_ip_address}= | 172.16.0.2

| ${traffic_src_ip}= | 192.168.0.100
| ${traffic_dst_ip}= | 192.168.2.100


*** Test Cases ***
| VPP can route IPv4 traffic from GRE tunnel
| | Given Path for 3-node testing is set | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And   Interfaces in 3-node path are up
| | And   IP addresses are set on interfaces
| |       ...         | ${dut1_node} | ${dut1_to_dut2} | 192.168.1.1 | 24
| |       ...         | ${dut1_node} | ${dut1_to_tg}   | 192.168.0.1 | 24
| |       ...         | ${dut2_node} | ${dut2_to_dut1} | 192.168.1.2 | 24
| |       ...         | ${dut2_node} | ${dut2_to_tg}   | 192.168.2.2 | 24
| | And   VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_ip_address}
| | And   VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_ip_address}
| | ${dut1_gre_interface} | ${dut1_gre_index}=
| | | ... | When GRE tunnel interface is created and up | ${dut1_node} | ${dut1_ip_address} | ${dut2_ip_address}
| | ${dut2_gre_interface} | ${dut2_gre_index}=
| | | ... | And  GRE tunnel interface is created and up | ${dut2_node} | ${dut2_ip_address} | ${dut1_ip_address}
| | And  IP addresses are set on interfaces
| |       ...         | ${dut1_node} | ${dut1_gre_index} | ${dut1_gre_ip_address} | 24
| |       ...         | ${dut2_node} | ${dut2_gre_index} | ${dut2_gre_ip_address} | 24
| | And  Vpp Route Add | ${dut1_node} | 192.168.2.0 | 24 | ${dut2_gre_ip_address} | ${dut1_gre_index}
| | Then Send and receive ICMPv4 | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2} | ${dut1_node} | ${dut1_to_tg}

#| VPP can encapsulate IPv4 traffic in GRE
#| VPP can route IPv4 traffic from GRE tunnel
#| can ping tunnel address local
#| can ping tunnel address remote

