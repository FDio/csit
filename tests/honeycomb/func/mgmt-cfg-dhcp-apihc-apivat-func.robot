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
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/dhcp.robot
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.IPv4Setup
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.Routing
| Variables | resources/test_data/honeycomb/dhcp_relay.py
| ...
| ...
| Documentation | *Honeycomb DHCP relay test suite.*
| ...
| Suite Setup | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Force Tags | HC_FUNC

*** Test Cases ***
| TC01: Honeycomb can configure DHCP relay entry
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-DHCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 configure IP addresses\
| | ... | neighbors and configure DHCP relay.
| | ... | [Ver] Send DHCP packets from TG interface to DUT. Receive all packets\
| | ... | on the second TG interface and verify required fields.
| | ...
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ... | AND | Log DHCP relay configuration from VAT | ${node} | ipv4
| | ...
| | Given DHCP relay Operational Data From Honeycomb Should Be empty | ${node}
| | When Honeycomb configures DHCP relay | ${node} | ${relay1} | ipv4 | ${0}
| | Then DHCP relay configuration from Honeycomb should contain
| | ... | ${node} | ${relay1_oper}
| | When DHCP relay test setup
| | Then Send DHCP messages and check answer | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${dhcp_server1_ip} | ${tg_to_dut_if2_mac}
| | ... | ${client_ip} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_ip}

| TC02: Honeycomb can remove DHCP relay entry
| | [Documentation] | Remove DHCP relay configuration, and verify that\
| | ... | it was removed.
| | ...
| | Given DHCP relay configuration from Honeycomb should contain
| | ... | ${node} | ${relay1_oper}
| | When Honeycomb clears DHCP relay configuration | ${node}
| | Then DHCP relay Operational Data From Honeycomb Should Be empty | ${node}

| TC03: Honeycomb can configure multiple DHCP relay servers.
| | [Documentation] | Configure multiple DHCP relay servers and verify\
| | ... | their configuration using operational data.
| | ...
| | [Teardown] | Honeycomb clears DHCP relay configuration | ${node}
| | ...
| | Given DHCP relay Operational Data From Honeycomb Should Be empty | ${node}
| | And Honeycomb configures DHCP relay | ${node} | ${relay2} | ipv4 | ${0}
| | Then DHCP relay configuration from Honeycomb should contain
| | ... | ${node} | ${relay2_oper}

| TC04: Honeycomb can configure DHCP relay entry with ipv6
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv6-DHCPv6.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 configure IP addresses\
| | ... | neighbors and configure DHCP relay.
| | ... | [Ver] Send DHCPv6 packets from TG interface to DUT. Receive all\
| | ... | packets on the second TG interface and verify required fields.
| | ...
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ... | AND | Log DHCP relay configuration from VAT | ${node} | ipv6
| | ... | AND | Honeycomb clears DHCP relay configuration | ${node}
| | ...
| | Given DHCP relay Operational Data From Honeycomb Should Be empty | ${node}
| | When Honeycomb configures DHCP relay | ${node} | ${relay_v6} | ipv6 | ${0}
| | Then DHCP relay configuration from Honeycomb should contain
| | ... | ${node} | ${relay_v6_oper}
| | When DHCP relay test setup IPv6
| | Then Send DHCPv6 Messages | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if1_ip6} | ${dut_to_tg_if1_mac} | ${dhcp_server_ip6}
| | ... | ${tg_to_dut_if2_mac} | ${tg_to_dut_if1_mac} |  ${dut_to_tg_if2_mac}

*** Keywords ***
| DHCP relay test setup
| | Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb sets interface IPv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | Honeycomb sets interface IPv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | Add ARP on DUT | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server1_ip}
| | ... | ${tg_to_dut_if2_mac}
| | Add ARP on DUT | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server2_ip}
| | ... | ${tg_to_dut_if2_mac}
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | gateway=${NONE}
| | ... | interface=local | use_sw_index=${FALSE} | resolve_attempts=${NONE}

| DHCP relay test setup IPv6
| | Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | And Vpp All Ra Suppress Link Layer | ${nodes}
| | Honeycomb sets interface IPv6 address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip6} | ${prefix_length_v6}
| | Honeycomb sets interface IPv6 address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip6} | ${prefix_length_v6}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server_ip6}
| | ... | ${tg_to_dut_if2_mac}
| | And VPP Route Add | ${dut_node} | ff02::1:2 | 128 | gateway=${NONE}
| | ... | interface=local | use_sw_index=${FALSE} | resolve_attempts=${NONE}
