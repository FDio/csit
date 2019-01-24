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
| Resource | resources/libraries/robot/ip/ip6.robot
| Library | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *DHCPv6 proxy test cases*
| ...
| ... | *[Top] Network Topologies:* TG = DUT
| ... |        with two links between the nodes.
| ... | *[Cfg] DUT configuration:* DUT is configured with DHCPv6 proxy.
| ... | *[Ver] TG verification:* Test DHCPv6 packets are sent
| ... |        on TG on first link to DUT and received on TG on second link.
| ... |        On receive TG verifies if DHCPv6 packets are valid
| ... | *[Ref] Applicable standard specifications:* RFC 3315


*** Variables ***
| ${dut_to_tg_if1_ip}= | 3ffe:62::1
| ${dut_to_tg_if2_ip}= | 3ffe:63::1
| ${dhcp_server_ip}= | 3ffe:63::2
| ${prefix_length}= | 64


*** Test Cases ***
| TC01: VPP proxies valid DHCPv6 request to DHCPv6 server
| | [Documentation] |
| | ... | [Top] TG=DUT
| | ... | [Cfg] On DUT setup DHCP proxy.
| | ... | [Ver] Make TG verify matching DHCPv6 packets between client and \
| | ... | DHCPv6 server through DHCPv6 proxy.
| | ... | [Ref] RFC 3315
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And Vpp Set If Ipv6 Addr | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | And Vpp Set If Ipv6 Addr | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | And VPP Route Add | ${dut_node} | ff02::1:2 | 128 | gateway=${NONE}
| | ... | interface=local | use_sw_index=${FALSE} | resolve_attempts${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server_ip}
| | ... | ${tg_to_dut_if2_mac}
| | And Vpp All Ra Suppress Link Layer | ${nodes}
| | When DHCP Proxy Config | ${dut_node} | ${dhcp_server_ip}
| | ... | ${dut_to_tg_if1_ip}
| | Then Send DHCPv6 Messages | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if1_ip} | ${dut_to_tg_if1_mac} | ${dhcp_server_ip}
| | ... | ${tg_to_dut_if2_mac} | ${tg_to_dut_if1_mac} |  ${dut_to_tg_if2_mac}
