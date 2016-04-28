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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/gre.robot
| Resource | resources/libraries/robot/l3_traffic.robot
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Trace
| Force Tags | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *GRE test suite.*
| ...
| ... | Test suite uses 2-node topology TG - DUT1 - TG with two links
| ... | between nodes as well as 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes. Test packets are sent from TG to DUT1.
| ... | DUT1 encapsulate packet into GRE and send out from other interface.
| ... | Traffic scripts check received MAC headers, IP headers and GRE headers.

*** Variables ***
| ${net1_address}= | 192.168.0.0
| ${net1_host_address}= | 192.168.0.100
| ${net1_gw_address}= | 192.168.0.1
| ${net2_address}= | 192.168.2.0
| ${net2_host_address}= | 192.168.2.100
| ${net2_gw_address}= | 192.168.2.1
| ${dut1_ip_address}= | 192.168.1.1
| ${dut2_ip_address}= | 192.168.1.2
| ${dut1_gre_ip}= | 172.16.0.1
| ${dut2_gre_ip}= | 172.16.0.2
| ${prefix}= | 24

*** Test Cases ***
| VPP can route IPv4 traffic from GRE tunnel
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | [Documentation] | Create GRE configuration on 2 DUTs, send IP traffic and
| | ...             | check IP is not changed.
| | Given Path for 3-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| |       ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And   Interfaces in 3-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_ip_address} | ${prefix}
| |       ... | ${dut1_node} | ${dut1_to_tg}   | ${net1_gw_address} | ${prefix}
| |       ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_ip_address} | ${prefix}
| |       ... | ${dut2_node} | ${dut2_to_tg}   | ${net2_gw_address} | ${prefix}
| | And   VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_ip_address}
| | And   VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_ip_address}
| | ${dut1_gre_interface} | ${dut1_gre_index}=
| | | ... | When GRE tunnel interface is created and up
| | |     |      ... | ${dut1_node} | ${dut1_ip_address} | ${dut2_ip_address}
| | ${dut2_gre_interface} | ${dut2_gre_index}=
| | | ... | And  GRE tunnel interface is created and up
| | |     |      ... | ${dut2_node} | ${dut2_ip_address} | ${dut1_ip_address}
| | And  IP addresses are set on interfaces
| |      ... | ${dut1_node} | ${dut1_gre_index} | ${dut1_gre_ip} | ${prefix}
| |      ... | ${dut2_node} | ${dut2_gre_index} | ${dut2_gre_ip} | ${prefix}
| | And  Vpp Route Add | ${dut1_node} | ${net2_address} | ${prefix}
| |      ... | ${dut2_gre_ip} | ${dut1_gre_index}
| | Then Send and receive ICMPv4 | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
| |      ... | ${dut1_node} | ${dut1_to_tg}
| |      ... | ${net1_host_address} | ${net2_host_address}


| VPP can encapsulate IPv4 traffic in GRE
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | [Documentation] | Create GRE configuration on DUT, send IP traffic and
| | ...             | check IP is correctly encapsulate into GRE.
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut1_ip_address} | ${prefix}
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${net1_gw_address} | ${prefix}
| | ${tx_dst_mac}= | And Get interface mac | ${dut_node} | ${dut_to_tg_if1}
| | ${rx_dst_mac}= | And Get interface mac | ${tg_node} | ${tg_to_dut_if2}
| | And  Add Arp On Dut | ${dut_node} | ${dut_to_tg_if2} | ${dut2_ip_address}
| |      ... | ${rx_dst_mac}
| | ${dut1_gre_interface} | ${dut1_gre_index}=
| | | ... | When GRE tunnel interface is created and up
| | |     |      ... | ${dut_node} | ${dut1_ip_address} | ${dut2_ip_address}
| | And  IP addresses are set on interfaces
| |      ... | ${dut_node} | ${dut1_gre_index} | ${dut1_gre_ip} | ${prefix}
| | And  Vpp Route Add | ${dut_node} | ${net2_address} | ${prefix}
| |      ... | ${dut2_gre_ip} | ${dut1_gre_index}
| | Then Send ICMPv4 and check received GRE header
| |      ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| |      ... | ${tx_dst_mac} | ${rx_dst_mac}
| |      ... | ${net1_host_address} | ${net2_host_address}
| |      ... | ${dut1_ip_address} | ${dut2_ip_address}


| VPP can decapsulate IPv4 traffic in GRE
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | [Documentation] | Create GRE configuration on DUT, send GRE encapsulated
| | ...             | traffic and  check IP is received without GRE headers.
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut1_ip_address} | ${prefix}
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${net1_gw_address} | ${prefix}
| | ${tx_dst_mac}= | And Get interface mac | ${dut_node} | ${dut_to_tg_if2}
| | ${rx_dst_mac}= | And Get interface mac | ${tg_node} | ${tg_to_dut_if1}
| | And  Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1} | ${net1_host_address}
| |      ... | ${rx_dst_mac}
| | ${dut1_gre_interface} | ${dut1_gre_index}=
| | | ... | When GRE tunnel interface is created and up
| | |     |      ... | ${dut_node} | ${dut1_ip_address} | ${dut2_ip_address}
| | And  IP addresses are set on interfaces
| |      ... | ${dut_node} | ${dut1_gre_index} | ${dut1_gre_ip} | ${prefix}
| | Then Send GRE and check received ICMPv4 header
| |      ... | ${tg_node} | ${tg_to_dut_if2} | ${tg_to_dut_if1}
| |      ... | ${tx_dst_mac} | ${rx_dst_mac}
| |      ... | ${net2_host_address} | ${net1_host_address}
| |      ... | ${dut2_ip_address} | ${dut1_ip_address}
