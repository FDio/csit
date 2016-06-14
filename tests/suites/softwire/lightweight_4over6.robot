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
#| Resource | resources/libraries/robot/l2_traffic.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/map.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *RFC 7596*

*** Variables ***
| ${dut_ip1}= | 10.0.0.1
| ${dut_ip2}= | 2001:0::1
| ${ipv4_prefix_len}= | 24
| ${ipv6_prefix_len}= | 64

| ${lw_ipv4_pfx}= | 20.0.0.0/24
| ${lw_ipv6_pfx}= | 2001:1::/64
| ${lw_ipv6_src}= | 2001:1::1
| ${lw_psid_length}= | ${8}
| ${lw_psid_offset}= | ${6}
| ${lw_rule_psid}= | ${52}
| ${lw_rule_ipv6_dst}= | 2001:1::2
| ${test_ipv4_dst}= | 20.0.0.1
| ${test_ipv4_src}= | 20.0.0.2
# depend on psid, length, offset
| ${test_port}= | ${1232}

*** Test Cases ***
| Encapsulate IPv4 to IPv6 softwire
| | [Tags] | tmp
| | [Documentation]
| | ... | LW4o6 is a subset of MAP-E, with per-subscriber rules. \
| | ... | It uses the same tunneling mechanism and configuration as MAP-E.
| | ... | It does not use embedded address bits.
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip1} | ${ipv4_prefix_len}
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip2} | ${ipv6_prefix_len}
| | And   Add IP Neighbor
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${lw_rule_ipv6_dst}
| |       ... | ${tg_to_dut_if2_mac}

| | ${domain_index}=
| | ... | When Map Add Domain
| |            ... | ${dut_node} | ${lw_ipv4_pfx} | ${lw_ipv6_pfx}
| |            ... | ${lw_ipv6_src} | 0 | ${lw_psid_offset}
| |            ... | ${lw_psid_length}
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} | ${lw_rule_psid}
| |            ... | ${lw_rule_ipv6_dst}
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} |  10 | 2001:1::3
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} | 200 | 2001:1::4
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} | 252 | 2001:1::5
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} | 128 | 2001:1::6
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} |  13 | 2001:1::7
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} |   2 | 2001:1::8
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} | 100 | 2001:1::9
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} |   3 | 2001:1::a
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} |  44 | 2001:1::b
| |       And  Map Add Rule
| |            ... | ${dut_node} | ${domain_index} |  18 | 2001:1::c

| | Then Send IPv4 and check headers for lightweight 4over6
| |      ... | ${tg_node}
| |      ... | ${tg_to_dut_if1}
| |      ... | ${tg_to_dut_if2}
| |      ... | ${dut_to_tg_if1_mac}
| |      ... | ${test_ipv4_dst}
| |      ... | ${test_ipv4_src}
| |      ... | ${test_port}
| |      ... | ${tg_to_dut_if2_mac}
| |      ... | ${dut_to_tg_if2_mac}
| |      ... | ${lw_rule_ipv6_dst}
| |      ... | ${lw_ipv6_src}
