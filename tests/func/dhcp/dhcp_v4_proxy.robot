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
| Resource | resources/libraries/robot/dhcp_proxy.robot
| Resource | resources/libraries/robot/ipv4.robot
| Library | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *DHCP proxy test cases*
| ...
| ... | *[Top] Network Topologies:* TG = DUT
| ... |        with two links between the nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP-BOOTP-DHCP
| ... | *[Cfg] DUT configuration:* DUT is configured with DHCP proxy.
| ... | *[Ver] TG verification:* Test DHCP packets are sent
| ... |        on TG on first link to DUT and received on TG on second link.
| ... |        On receive TG verifies if DHCP packets are valid.

*** Variables ***
| ${dut_to_tg_if1_ip}= | 172.16.0.1
| ${dut_to_tg_if2_ip}= | 192.168.0.1
| ${dhcp_server_ip}= | 192.168.0.100
| ${client_ip}= | 172.16.0.2
| ${prefix_length}= | 24

| ${discover_src_ip}= | 0.0.0.0
| ${valid_discover_dst_ip}= | 255.255.255.255
| ${invalid_discover_dst_ip}= | 255.255.255.1

*** Test Cases ***
| TC01: VPP proxies valid DHCPv4 request to DHCPv4 server
| | [Documentation] |
| | ... | [Top] TG=DUT \
| | ... | [Enc] Eth-IPv4-UDP-BOOTP-DHCP
| | ... | [Cfg] On DUT setup DHCP proxy.
| | ... | [Ver] Make TG verify matching DHCP packets between client and DHCP
| | ... | server through DHCP proxy.
| | ...
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| | ... | ${FALSE} | ${NONE}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server_ip}
| | ... | ${tg_to_dut_if2_mac}
| | When DHCP Proxy Config | ${dut_node} | ${dhcp_server_ip}
| | ... | ${dut_to_tg_if1_ip}
| | Then Send DHCP Messages | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dhcp_server_ip} | ${tg_to_dut_if2_mac} | ${client_ip}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_ip}

| TC02: VPP proxy ignores invalid DHCPv4 request
| | [Documentation] |
| | ... | [Top] TG=DUT \
| | ... | [Enc] Eth-IPv4-UDP-BOOTP-DHCP
| | ... | [Cfg] On DUT setup DHCP proxy.
| | ... | [Ver] Make TG verify matching invalid DHCP packets are dropped.
| | ...
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| | ... | ${FALSE} | ${NONE}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server_ip}
| | ... | ${tg_to_dut_if2_mac}
| | When DHCP Proxy Config | ${dut_node} | ${dhcp_server_ip}
| | ... | ${dut_to_tg_if1_ip}
| | Then Send DHCP DISCOVER | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${discover_src_ip} | ${valid_discover_dst_ip}
| | And Send DHCP DISCOVER should fail | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${discover_src_ip} | ${invalid_discover_dst_ip}
