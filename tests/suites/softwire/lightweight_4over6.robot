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
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/map.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *Lightweight 4 over 6 test cases*
| ...
| ... | LW4o6 is a subset of MAP-E, with per-subscriber rules. It uses the
| ... | same tunneling mechanism and configuration as MAP-E. It does not use
| ... | embedded address bits.
| ...
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP on TG_if1-DUT,
| ... | Eth-IPv6-IPv4-UDP on TG_if2_DUT.
| ... | *[Cfg] DUT configuration:* DUT1 is configured as lwAFTR.
| ... | *[Ver] TG verification:* Test UDP ICMP Echo Request in IPv4 are
| ... | sent to lwAFTR and are verified by TG for correctness their
| ... | encapsulation in IPv6 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC7596 RFC7597.

*** Variables ***
| ${dut_ip4}= | 10.0.0.1
| ${dut_ip6}= | 2001:0::1
| ${ipv4_prefix_len}= | 24
| ${ipv6_prefix_len}= | 64

| ${lw_ipv4_pfx}= | 20.0.0.1/32
| ${lw_ipv6_pfx}= | 2001:1::/64
| ${lw_ipv6_src}= | 2001:1::1
| ${lw_psid_length}= | ${8}
| ${lw_psid_offset}= | ${6}
| ${lw_rule_psid}= | ${52}
| ${lw_rule_ipv6_dst}= | 2001:1::2
| ${test_ipv4_inside}= | 20.0.0.1
| ${test_ipv4_outside}= | 10.0.0.100
# test_port depends on psid, length, offset
| ${test_port}= | ${1232}
| ${test_icmp_id}= | ${1232}

*** Test Cases ***
| TC01: Encapsulate IPv4 into IPv6. IPv6 dst depends on IPv4 and UDP destination
| | [Documentation]
| | ... | [Top] TG=DUT1. \
| | ... | [Enc] Eth-IPv4-UDP on TG_if1-DUT, Eth-IPv6-IPv4-UDP on TG_if2_DUT.
| | ... | [Cfg] On DUT1 configure Map domain and Map rule.
| | ... | [Ver] Make TG send non-encapsulated UDP to DUT; verify TG received
| | ... |       IPv4oIPv6 encapsulated packet is correct.
| | ... | [Ref] RFC7596 RFC7597
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
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
| | Then Send IPv4 UDP and check headers for lightweight 4over6
| |      ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| |      ... | ${dut_to_tg_if1_mac} | ${test_ipv4_inside} | ${test_ipv4_outside}
| |      ... | ${test_port} | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac}
| |      ... | ${lw_rule_ipv6_dst} | ${lw_ipv6_src}

TC02: Encapsulate IPv4 ICMP into IPv6. IPv6 dst depends on IPv4 addr and ICMP ID
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Enc] Eth-IPv4-ICMP(type 0 and 8) on TG_if1-DUT, Eth-IPv6-IPv4-ICMP
| | ... |       on TG_if2_DUT
| | ... | [Cfg] On DUT1 configure Map domain and Map rule.
| | ... | [Ver] Make TG send non-encapsulated ICMP to DUT; verify TG received
| | ... |       IPv4oIPv6 encapsulated packet is correct Checks IPv6
| | ... |       destination based on ICMP Identifier field.
| | ... | [Ref] RFC7596 section 8.1
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
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
| | Then Send IPv4 ICMP and check headers for lightweight 4over6
| |      ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| |      ... | ${dut_to_tg_if1_mac} | ${test_ipv4_inside} | ${test_ipv4_outside}
| |      ... | ${test_icmp_id} | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac}
| |      ... | ${lw_rule_ipv6_dst} | ${lw_ipv6_src}
