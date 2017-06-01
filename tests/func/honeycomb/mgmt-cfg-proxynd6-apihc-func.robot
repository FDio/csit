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

*** Variables ***
# Interface to run configuration tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}
# IPv6 addresses to configure on DUT.
| ${dut_to_tg_if1_ip}= | 10::1
| ${dut_to_tg_if2_ip}= | 11::1
# IPv6 addresses used for TG interfaces.
| ${test_src_ip}= | 10::2
| ${test_dst_ip}= | 11::2
| ${test_dst_ip2}= | 11::3
# IPv6 subnet prefix length
| ${prefix_length}= | 64

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/proxyarp.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/dhcp_proxy.robot
| Library | resources.libraries.python.Trace
| Test Setup | Clear Packet Trace on All DUTs | ${nodes}
| Suite Teardown | Restart Honeycomb And VPP | ${node}
| Force Tags | HC_FUNC
| Documentation | *Honeycomb IPv6 neighbor discovery proxy test suite.*

*** Test Cases ***
| TC01: Honeycomb can configure IPv6 ND proxy on an interface
| | [Documentation] | Check if Honeycomb can configure the IPv6 ND proxy\
| | ... | feature on an interface.
| | Given IPv6 ND proxy from Honeycomb should be empty | ${node} | ${interface}
| | And Honeycomb configures interface state | ${node} | ${interface} | up
| | When Honeycomb configures IPv6 ND proxy on interface
| | ... | ${node} | ${interface} | ${test_dst_ip}
| | Then IPv6 ND proxy from Honeycomb should be
| | ... | ${node} | ${interface} | ${test_dst_ip}

| TC02: Honeycomb can disable IPv6 ND proxy on an interface
| | [Documentation] | Check if Honeycomb can remove IPv6 ND proxy feature\
| | ... | configuration from an interface.
| | Given IPv6 ND proxy from Honeycomb should be
| | ... | ${node} | ${interface} | ${test_dst_ip}
| | When Honeycomb disables IPv6 ND proxy on interface | ${node} | ${interface}
| | Then IPv6 ND proxy from Honeycomb should be empty | ${node} | ${interface}

| TC03: Honeycomb can configure multiple IPv6 ND proxies on an interface
| | [Documentation] | Check if Honeycomb can configure two ND proxies\
| | ... | on one interface.
| | [Teardown] | Honeycomb disables IPv6 ND proxy on interface
| | ... | ${node} | ${interface}
| | Given IPv6 ND proxy from Honeycomb should be empty | ${node} | ${interface}
| | And Honeycomb configures interface state | ${node} | ${interface} | up
| | When Honeycomb configures IPv6 ND proxy on interface
| | ... | ${node} | ${interface} | ${test_dst_ip} | ${test_dst_ip2}
| | Then IPv6 ND proxy from Honeycomb should be
| | ... | ${node} | ${interface} | ${test_dst_ip} | ${test_dst_ip2}

| TC04: VPP proxies valid ICMPv6 Neighbor Discovery request
| | [Documentation] |
| | ... | [Top] TG=DUT
| | ... | [Cfg] On DUT configure IPv6 addresses and neighbors, supress router\
| | ... | advertisement and configure IPv6 Neighbor Discovery proxy.
| | ... | [Ver] Make TG send a neighbor solicitation packet to it's other\
| | ... | interface through DUT, verify DUT responds to the packet instead\
| | ... | of forwarding it. Then exchange ICMPv6 Echo request/reply to verify\
| | ... | connectivity between interfaces.
| | ... | [Ref] RFC 4389
| | ...
| | [Teardown] | Run Keywords
| | ... | Show Packet Trace on All DUTs | ${nodes} | AND
| | ... | Honeycomb disables IPv6 ND proxy on interface
| | ... | ${dut_node} | ${dut_to_tg_if2}
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb sets interface IPv6 address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | Honeycomb sets interface IPv6 address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | And Vpp Ra Suppress Link Layer | ${dut_node} | ${dut_to_tg_if1}
| | And Vpp Ra Suppress Link Layer | ${dut_node} | ${dut_to_tg_if2}
| | And Honeycomb adds interface IPv6 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${test_src_ip} | ${tg_to_dut_if1_mac}
| | And Honeycomb adds interface IPv6 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${test_dst_ip} | ${tg_to_dut_if2_mac}
| | When Honeycomb configures IPv6 ND proxy on interface
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${test_dst_ip}
| | Then Verify IPv6ND proxy | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${test_src_ip} | ${test_dst_ip}
| | ... | ${tg_to_dut_if1_mac} | ${tg_to_dut_if2_mac}
| | ... | ${dut_to_tg_if1_mac} | ${dut_to_tg_if2_mac}
