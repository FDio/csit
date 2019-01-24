# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/features/dhcp_proxy.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Library | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *DHCPv4 proxy test cases*
| ...
| ... | *[Top] Network Topologies:* TG = DUT
| ... |        with two links between the nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP-BOOTP-DHCP
| ... | *[Cfg] DUT configuration:* DUT is configured with DHCPv4 proxy.
| ... | *[Ver] TG verification:* Test DHCPv4 packets are sent
| ... |        on TG on first link to DUT and received on TG on second link.
| ... |        On receive TG verifies if DHCPv4 packets are valid.

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
| | ... | [Cfg] On DUT setup DHCPv4 proxy.
| | ... | [Ver] Make TG verify matching DHCPv4 packets between client and DHCPv4
| | ... | server through DHCP proxy.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | gateway=${NONE}
| | ... | interface=local | use_sw_index=${FALSE} | resolve_attempts=${NONE}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server_ip}
| | ... | ${tg_to_dut_if2_mac}
| | When DHCP Proxy Config | ${dut_node} | ${dhcp_server_ip}
| | ... | ${dut_to_tg_if1_ip}
| | Then Send DHCP messages and check answer | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${dhcp_server_ip} | ${tg_to_dut_if2_mac}
| | ... | ${client_ip} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_ip}

| TC02: VPP proxy ignores invalid DHCPv4 request
| | [Documentation] |
| | ... | [Top] TG=DUT \
| | ... | [Enc] Eth-IPv4-UDP-BOOTP-DHCP
| | ... | [Cfg] On DUT setup DHCPv4 proxy.
| | ... | [Ver] Make TG verify matching invalid DHCPv4 packets are dropped.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | gateway=${NONE}
| | ... | interface=local | use_sw_index=${FALSE} | resolve_attempts=${NONE}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server_ip}
| | ... | ${tg_to_dut_if2_mac}
| | When DHCP Proxy Config | ${dut_node} | ${dhcp_server_ip}
| | ... | ${dut_to_tg_if1_ip}
| | Then Send DHCP DISCOVER and check answer | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${discover_src_ip} | ${valid_discover_dst_ip}
| | And DHCP DISCOVER should fail | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${discover_src_ip} | ${invalid_discover_dst_ip}
