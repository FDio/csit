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
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/ip/map.robot
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | SOFTWIRE
| Test Setup | Run Keywords | Set up functional test
| ... | AND | Set interfaces IP addresses and routes
| Test Teardown | Tear down functional test
| Documentation | *Test for Basic mapping rule for MAP-T*\
| ... | *[Top] Network Topologies:* TG - DUT1 - TG with two links between the
| ... | nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP on TG-to-DUT-if1.
| ... | Eth-IPv6-UDP on TG-to-DUT-if2.
| ... | *[Cfg] DUT configuration:* DUT is configured with IPv4 on one DUT-to-TG
| ... | interface and IPv6 address on second DUT-to-TG interface. MAP-T domain
| ... | is configured in test template based on test parameters.
| ... | *[Ver] TG verification:* UDP packets in IPv4 are sent by TG to
| ... | destination in MAP domain. IPv6 packets with translated IPv4 addresses
| ... | are received on TG interface.
| ... | *[Ref] Applicable standard specifications:* RFC7599


*** Variables ***
| ${dut_ip4}= | 10.0.0.1
| ${dut_ip6}= | 2001:0::1
| ${dut_ip4_gw}= | 10.0.0.2
| ${dut_ip6_gw}= | 2001:0::2
| ${ipv4_prefix_len}= | 24
| ${ipv6_prefix_len}= | 64
| ${ipv6_br_src}= | 2001:db8:ffff::/96


*** Test Cases ***
| TC01: MAP-T test
| | [Documentation] |
| | ... | Test to check map-t address translation.
| | ...
| | ... | Arguments:
| | ...
| | ... | - ipv4_pfx
| | ... | - ipv6_dst_pfx
| | ... | - ipv6_src_pfx
| | ... | - ea_bit_len
| | ... | - psid_offset
| | ... | - psid_len
| | ... | - ipv4_src
| | ... | - ipv4_dst
| | ... | - dst_port
| | ...
| | [Template] | Check MAP-T configuration with traffic script
# |===================|===============|================|============|=============|==========|===========|================|==========|
# | ipv4_pfx          | ipv6_dst_pfx  | ipv6_src_pfx   | ea_bit_len | psid_offset | psid_len | ipv4_src  | ipv4_dst       | dst_port |
# |===================|===============|================|============|=============|==========|===========|================|==========|
| | 20.169.0.0/16     | 2001::/16     | ${ipv6_br_src} | ${40}      | ${0}        | ${0}     | 100.0.0.1 | 20.169.201.219 | ${1232}  |
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_br_src} | ${0}       | ${0}        | ${0}     | 100.0.0.1 | 20.169.201.219 | ${1232}  |
| | 20.0.0.0/8        | 2001:db8::/40 | ${ipv6_br_src} | ${24}      | ${0}        | ${0}     | 100.0.0.1 | 20.169.201.219 | ${1232}  |
#| | 20.169.201.0/32   | 2001:db8::/32 | ${ipv6_br_src} | ${0}       | ${6}        | ${8}     | 100.0.0.1 | 20.169.201.219 | ${1232}  |
#| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_br_src} | ${0}       | ${6}        | ${8}     | 100.0.0.1 | 20.169.201.219 | ${1232}  |


*** Keywords ***
| Set interfaces IP addresses and routes
| | Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Set interfaces in 2-node circular topology up
| | Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
| | Vpp Route Add | ${dut_node} | :: | 0 | gateway=${dut_ip6_gw}
| | ... | interface=${dut_to_tg_if2} | resolve_attempts=${NONE} | count=${NONE}
| | Add IP neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6_gw}
| | ... | ${tg_to_dut_if2_mac}
| | Vpp Route Add | ${dut_node} | 0.0.0.0 | 0 | gateway=${dut_ip4_gw}
| | ... | interface=${dut_to_tg_if1} | resolve_attempts=${NONE} | count=${NONE}
| | Add IP neighbor | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4_gw}
| | ... | ${tg_to_dut_if1_mac}

| Check MAP-T configuration with traffic script
| | [Documentation] |
| | ... | Used as a test case template.\
| | ... | Configure MAP-T domain with given parameters, with traffic script send
| | ... | UDP in IPv4 packet to given UDP destination port and IP destination
| | ... | address and check if correctly received IPv6 packet with translated
| | ... | source and destination addresses. Vice versa send IPv6 packet and
| | ... | check if received IPv4 packet with correct source and destination
| | ... | addresses.
| | ... | The MAP domain is deleted in teardown.
| | [Arguments] | ${ipv4_pfx} | ${ipv6_dst_pfx} | ${ipv6_src_pfx}
| | ... | ${ea_bit_len} | ${psid_offset} | ${psid_len}
| | ... | ${ipv4_outside} | ${ipv4_inside} | ${dst_port}
| | ${domain_index}= | Map Add Domain | ${dut_node} | ${ipv4_pfx}
| | ... | ${ipv6_dst_pfx} | ${ipv6_src_pfx} | ${ea_bit_len} | ${psid_offset}
| | ... | ${psid_len} | ${TRUE}
| | ${ipv6_ce_addr}= | Compute IPv6 map destination address
| | ... | ${ipv4_pfx} | ${ipv6_dst_pfx} | ${ea_bit_len} | ${psid_offset}
| | ... | ${psid_len} | ${ipv4_inside} | ${dst_port}
| | ${ipv6_br_addr}= | Compute IPv6 map source address
| | ... | ${ipv6_src_pfx} | ${ipv4_outside}
# Check translation from v4 to v6 with traffic script
| | Send IPv4 UDP and check IPv6 headers for MAP-T
| | ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if1_mac} | ${ipv4_inside} | ${ipv4_outside} | ${dst_port}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac}
| | ... | ${ipv6_ce_addr} | ${ipv6_br_addr}
# Check translation from v6 to v4 with traffic script
| | Send IPv6 UDP and check IPv4 headers for MAP-T
| | ... | ${tg_node} | ${tg_to_dut_if2} | ${tg_to_dut_if1}
| | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | ${ipv6_br_addr} | ${ipv6_ce_addr}
| | ... | ${dst_port}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${ipv4_outside} | ${ipv4_inside}
| | [Teardown] | Run Keywords
| | ... | Map Del Domain | ${dut_node} | ${domain_index} | AND
| | ... | Show packet trace on all DUTs | ${nodes} | AND
| | ... | Clear packet trace on all DUTs | ${nodes} | AND
| | ... | Verify VPP PID in Teardown
