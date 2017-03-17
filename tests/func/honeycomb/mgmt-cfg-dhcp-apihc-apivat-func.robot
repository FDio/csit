# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/dhcp.robot
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.IPv4Setup
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.Routing
| Variables | resources/test_data/honeycomb/dhcp_relay.py
| Documentation | *Honeycomb DHCP relay test suite.*
| Test Setup | Clear Packet Trace on All DUTs | ${nodes}
| Suite Teardown | Restart Honeycomb and VPP | ${node}
| Force Tags | honeycomb_sanity | honeycomb_odl

*** Test Cases ***
| TC01: Honeycomb can configure DHCP relay entry
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-DHCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 configure IP addresses\
| | ... | neighbors and configure DHCP relay.
| | ... | [Ver] Send DHCP packets from TG interface to DUT. Receive all packets\
| | ... | on the second TG interface.
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ... | AND | Log DHCP relay configuration from VAT | ${node} | ipv4
| | Given DHCP relay configuration from Honeycomb should be empty | ${node}
| | When Honeycomb configures DHCP relay | ${node} | ${relay1} | ipv4 | ${0}
| | Then DHCP relay configuration from Honeycomb should contain
| | ... | ${node} | ${relay1_oper}
| | When DHCP relay test setup
| | Then Send DHCP Messages | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dhcp_server1_ip} | ${tg_to_dut_if2_mac} | ${client_ip}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_ip}

| TC02: Honeycomb can remove DHCP relay entry
| | [Teardown] | Pass Execution | No teardown necessary.
| | Given DHCP relay configuration from Honeycomb should contain
| | ... | ${node} | ${relay1_oper}
| | When Honeycomb clears DHCP relay configuration | ${node}
| | Then DHCP relay configuration from Honeycomb should be empty | ${node}
| | When DHCP relay test setup
| | Then Run keyword and expect Error | Traffic script execution failed
| | ... | Send DHCP Messages | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dhcp_server1_ip} | ${tg_to_dut_if2_mac} | ${client_ip}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_ip}

| TC03: Honeycomb can configure multiple DHCP relay entries
| | [Teardown] | Honeycomb clears DHCP relay configuration | ${node}
| | Given DHCP relay configuration from Honeycomb should be empty | ${node}
| | And Honeycomb configures DHCP relay | ${node} | ${relay2} | ipv4 | ${0}
| | Then DHCP relay configuration from Honeycomb should contain
| | ... | ${node} | ${relay2_oper}

| TC04: Honeycomb can configure DHCP relay entry with ipv6
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ... | AND | Log DHCP relay configuration from VAT | ${node} | ipv6
| | ... | AND | Honeycomb clears DHCP relay configuration | ${node}
| | Given DHCP relay configuration from Honeycomb should be empty | ${node}
| | When Honeycomb configures DHCP relay | ${node} | ${relay_v6} | ipv6 | ${0}
| | Then DHCP relay configuration from Honeycomb should contain
| | ... | ${node} | ${relay_v6_oper}
| | When DHCP relay test setup IPv6
| | Then Send DHCPv6 Messages | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if1_ip6} | ${dut_to_tg_if1_mac} | ${dhcp_server_ip6}
| | ... | ${tg_to_dut_if2_mac} | ${tg_to_dut_if1_mac} |  ${dut_to_tg_if2_mac}

*** Keywords ***
| DHCP relay test setup
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | Add ARP on DUT
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server1_ip} | ${tg_to_dut_if2_mac}
| | Add ARP on DUT
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server2_ip} | ${tg_to_dut_if2_mac}
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| | ... | ${FALSE} | ${NONE}

| DHCP relay test setup IPv6
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | And Vpp All Ra Suppress Link Layer | ${nodes}
| | Honeycomb sets interface ipv6 address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip6} | ${prefix_length_v6}
| | Honeycomb sets interface ipv6 address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip6} | ${prefix_length_v6}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dhcp_server_ip6}
| | ... | ${tg_to_dut_if2_mac}
| | And VPP Route Add | ${dut_node} | ff02::1:2 | 128 | ${NONE} | local
| | ... | ${FALSE} | ${NONE}
