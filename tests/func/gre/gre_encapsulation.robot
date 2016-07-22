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
| Resource | resources/libraries/robot/traffic.robot
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Trace
| Force Tags | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *GREoIPv4 test cases*
| ...
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes; TG-DUT1-DUT2-TG 3-node circular topology with single
| ... | links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-GRE-IPv4-ICMPv4 on DUT1-DUT2,
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for routing over GRE tunnel; Eth-IPv4-ICMPv4
| ... | on TG_if1-DUT, Eth-IPv4-GRE-IPv4-ICMPv4 on TG_if2_DUT for GREoIPv4
| ... | encapsulation and decapsulation verification.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4 routing
| ... | and static routes. GREoIPv4 tunnel is configured between DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets are
| ... | sent in both directions by TG on links to DUT1 and DUT2; GREoIPv4
| ... | encapsulation and decapsulation are verified separately by TG; on
| ... | receive TG verifies packets for correctness and their IPv4 (IPv6)
| ... | src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC2784.

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
| TC01: DUT1 and DUT2 route over GREoIPv4 tunnel between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv4-GRE-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure GREoIPv4 tunnel with IPv4 routes towards each other.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across
| | ... | both DUTs and GRE tunnel between them; verify IPv4 headers on
| | ... | received packets are correct. [Ref] RFC2784.
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
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
| | And   Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${net2_host_address}
| |       ... | ${tg_to_dut2_mac}
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
| | Then Send Packet And Check Headers | ${tg_node}
| |      ... | ${net1_host_address} | ${net2_host_address}
| |      ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| |      ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}

| TC02: DUT encapsulates IPv4 into GREoIPv4 tunnel - GRE header verification
| | [Documentation]
| | ... | [Top] TG=DUT1. [Enc] Eth-IPv4-ICMPv4 on TG_if1-DUT, \
| | ... | Eth-IPv4-GRE-IPv4-ICMPv4 on TG_if2_DUT. [Cfg] On DUT1 configure
| | ... | GREoIPv4 tunnel with IPv4 route towards TG. [Ver] Make TG send
| | ... | non-encapsulated ICMPv4 Echo Req to DUT; verify TG received
| | ... | GREoIPv4 encapsulated packet is correct. [Ref] RFC2784.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut1_ip_address} | ${prefix}
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${net1_gw_address} | ${prefix}
| | And  Add Arp On Dut | ${dut_node} | ${dut_to_tg_if2} | ${dut2_ip_address}
| |      ... | ${tg_to_dut_if2_mac}
| | ${dut1_gre_interface} | ${dut1_gre_index}=
| | | ... | When GRE tunnel interface is created and up
| | |     |      ... | ${dut_node} | ${dut1_ip_address} | ${dut2_ip_address}
| | And  IP addresses are set on interfaces
| |      ... | ${dut_node} | ${dut1_gre_index} | ${dut1_gre_ip} | ${prefix}
| | And  Vpp Route Add | ${dut_node} | ${net2_address} | ${prefix}
| |      ... | ${dut2_gre_ip} | ${dut1_gre_index}
| | Then Send ICMPv4 and check received GRE header
| |      ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| |      ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if2_mac}
| |      ... | ${net1_host_address} | ${net2_host_address}
| |      ... | ${dut1_ip_address} | ${dut2_ip_address}

| TC03: DUT decapsulates IPv4 from GREoIPv4 tunnel - IPv4 header verification
| | [Documentation]
| | ... | [Top] TG=DUT1. [Enc] Eth-IPv4-ICMPv4 on TG_if1-DUT, \
| | ... | Eth-IPv4-GRE-IPv4-ICMPv4 on TG_if2_DUT. [Cfg] On DUT1 configure
| | ... | GREoIPv4 tunnel towards TG. [Ver] Make TG send ICMPv4 Echo Req
| | ... | encapsulated into GREoIPv4 towards VPP; verify TG received IPv4
| | ... | de-encapsulated packet is correct. [Ref] RFC2784.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut1_ip_address} | ${prefix}
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${net1_gw_address} | ${prefix}
| | And  Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1} | ${net1_host_address}
| |      ... | ${tg_to_dut_if1_mac}
| | ${dut1_gre_interface} | ${dut1_gre_index}=
| | | ... | When GRE tunnel interface is created and up
| | |     |      ... | ${dut_node} | ${dut1_ip_address} | ${dut2_ip_address}
| | And  IP addresses are set on interfaces
| |      ... | ${dut_node} | ${dut1_gre_index} | ${dut1_gre_ip} | ${prefix}
| | Then Send GRE and check received ICMPv4 header
| |      ... | ${tg_node} | ${tg_to_dut_if2} | ${tg_to_dut_if1}
| |      ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if1_mac}
| |      ... | ${net2_host_address} | ${net1_host_address}
| |      ... | ${dut2_ip_address} | ${dut1_ip_address}
