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
| Variables | resources/test_data/softwire/map_e_domains.py | ${5}
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | SKIP_VPP_PATCH
| ... | SOFTWIRE
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *Test for Basic mapping rule for MAP-E*\
| ... | *[Top] Network Topologies:* TG - DUT1 - TG with two links between the
| ... | nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP on TG-to-DUT-if1.
| ... | Eth-IPv6-IPv4-UDP on TG-to-DUT-if2.
| ... | *[Cfg] DUT configuration:* DUT is configured with IPv4 on one DUT-to-TG
| ... | interface and IPv6 address on second DUT-to-TG interface. MAP-E domain
| ... | is configured in test template based on test parameters.
| ... | *[Ver] TG verification:* UDP packets in IPv4 are sent by TG to
| ... | destination in MAP domain. IPv6 packets with encapsulated IPv4 are
| ... | received on TG interface.
| ... | *[Ref] Applicable standard specifications:* RFC7597.


*** Variables ***
| ${dut_ip4}= | 10.0.0.1
| ${dut_ip6}= | 2001:0::1
| ${dut_ip4_gw}= | 10.0.0.2
| ${dut_ip6_gw}= | 2001:0::2
| ${ipv4_prefix_len}= | 24
| ${ipv6_prefix_len}= | 64
| ${ipv6_br_src}= | 2001:db8:ffff::1
| ${ipv4_outside}= | 1.0.0.1


*** Test Cases ***
| TC01: BMR, then an IPv4 prefix is assigned
| | [Documentation]
| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
| | ... | IPv4 prefix length + ea bits length < 32 (o + r < 32)
| | ... | psid_length = 0, ip6_prefix < 64, ip4_prefix <= 32
| | ...
| | ... | Arguments:
| | ...
| | ... | - ipv4_pfx
| | ... | - ipv6_pfx
| | ... | - ipv6_src
| | ... | - ea_bit_len
| | ... | - psid_offset
| | ... | - psid_len
| | ... | - ipv4_dst
| | ... | - dst_port
| | ... | - expected_ipv6_dst
| | ...
# TODO: replace setup when VPP-312 fixed
#| | [Setup] | Set Interfaces IP Addresses And Routes
| | [Setup] | Run Keywords
| | ... | Set up functional test | AND
| | ... | Set Interfaces IP Addresses And Routes
| | [Template] | Check MAP Configuration With Traffic Script
# |=================|===============|================|============|=============|==========|================|==========|==================================|
# | ipv4_pfx        | ipv6_pfx      | ipv6_src       | ea_bit_len | psid_offset | psid_len | ipv4_dst       | dst_port | expected_ipv6_dst                |
# |=================|===============|================|============|=============|==========|================|==========|==================================|
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_br_src} | ${4}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a000::14a0:0:0          |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_br_src} | ${8}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a900::14a9:0:0          |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_br_src} | ${10}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c0::14a9:c000:0       |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_br_src} | ${16}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9::14a9:c900:0       |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_br_src} | ${20}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9:d000:0:14a9:c9d0:0 |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_br_src} | ${23}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9:da00:0:14a9:c9da:0 |
| | 20.169.201.0/24 | 2001:db8::/32 | ${ipv6_br_src} | ${4}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:d000::14a9:c9d0:0       |
| | 20.169.201.0/24 | 2001:db8::/32 | ${ipv6_br_src} | ${7}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:da00::14a9:c9da:0       |


| TC02: BMR, full IPv4 address is to be assigned
| | [Documentation]
| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
| | ... | IPv4 prefix length + ea bits length == 32 (o + r == 32)
| | ... | psid_length = 0, ip6_prefix < 64, ip4_prefix <= 32
| | ...
| | ... | Arguments:
| | ...
| | ... | - ipv4_pfx
| | ... | - ipv6_pfx
| | ... | - ipv6_src
| | ... | - ea_bit_len
| | ... | - psid_offset
| | ... | - psid_len
| | ... | - ipv4_dst
| | ... | - dst_port
| | ... | - expected_ipv6_dst
| | ...
# TODO: replace setup when VPP-312 fixed
#| | [Setup] | Set Interfaces IP Addresses And Routes
| | [Setup] | Run Keywords
| | ... | Set up functional test | AND
| | ... | Set Interfaces IP Addresses And Routes
| | [Template] | Check MAP Configuration With Traffic Script
# |===================|===============|================|============|=============|==========|================|==========|==================================|
# | ipv4_pfx          | ipv6_pfx      | ipv6_src       | ea_bit_len | psid_offset | psid_len | ipv4_dst       | dst_port | expected_ipv6_dst                |
# |===================|===============|================|============|=============|==========|================|==========|==================================|
| | 20.0.0.0/8        | 2001:db8::/32 | ${ipv6_br_src} | ${24}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9:db00:0:14a9:c9db:0 |
| | 20.160.0.0/12     | 2001:db8::/32 | ${ipv6_br_src} | ${20}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:9c9d:b000:0:14a9:c9db:0 |
| | 20.169.0.0/16     | 2001:db8::/32 | ${ipv6_br_src} | ${16}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:c9db::14a9:c9db:0       |
| | 20.169.200.0/22   | 2001:db8::/32 | ${ipv6_br_src} | ${10}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:76c0::14a9:c9db:0       |
| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_br_src} | ${8}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:db00::14a9:c9db:0       |
| | 20.169.201.208/28 | 2001:db8::/32 | ${ipv6_br_src} | ${4}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:b000::14a9:c9db:0       |
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_br_src} | ${0}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8::14a9:c9db:0            |
| | 20.0.0.0/8        | 2001:db8::/40 | ${ipv6_br_src} | ${24}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9:c9db:0:14a9:c9db:0   |
| | 20.160.0.0/12     | 2001:db8::/44 | ${ipv6_br_src} | ${20}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:9:c9db:0:14a9:c9db:0    |
| | 20.169.0.0/16     | 2001:db8::/48 | ${ipv6_br_src} | ${16}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:0:c9db:0:14a9:c9db:0    |
| | 20.169.200.0/22   | 2001:db8::/54 | ${ipv6_br_src} | ${10}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:0:1db:0:14a9:c9db:0     |


| TC03: BMR, shared IPv4 address is to be assigned
| | [Documentation]
| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
| | ... | IPv4 prefix length + ea bits length > 32 (o + r > 32)
| | ... | ip6_prefix < 64, ip4_prefix <= 32
| | ...
| | ... | Arguments:
| | ...
| | ... | - ipv4_pfx
| | ... | - ipv6_pfx
| | ... | - ipv6_src
| | ... | - ea_bit_len
| | ... | - psid_offset
| | ... | - psid_len
| | ... | - ipv4_dst
| | ... | - dst_port
| | ... | - expected_ipv6_dst
| | ...
# TODO: replace setup when VPP-312 fixed
#| | [Setup] | Set Interfaces IP Addresses And Routes
| | [Setup] | Run Keywords
| | ... | Set up functional test | AND
| | ... | Set Interfaces IP Addresses And Routes
| | [Template] | Check MAP Configuration With Traffic Script
# |===================|===============|================|============|=============|==========|================|==========|===================================|
# | ipv4_pfx          | ipv6_pfx      | ipv6_src       | ea_bit_len | psid_offset | psid_len | ipv4_dst       | dst_port | expected_ipv6_dst                 |
# |===================|===============|================|============|=============|==========|================|==========|===================================|
| | 20.0.0.0/8        | 2001::/16     | ${ipv6_br_src} | ${48}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:a9c9:db34::14a9:c9db:34      |
| | 20.169.0.0/16     | 2001::/16     | ${ipv6_br_src} | ${48}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:c9db:3400::14a9:c9db:34      |
| | 20.169.201.0/24   | 2001::/16     | ${ipv6_br_src} | ${48}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db34::14a9:c9db:34           |
| | 20.169.201.219/32 | 2001::/16     | ${ipv6_br_src} | ${48}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:3400::14a9:c9db:34           |

| | 20.0.0.0/8        | 2001::/24     | ${ipv6_br_src} | ${40}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:a9:c9db:3400:0:14a9:c9db:34  |
| | 20.169.0.0/16     | 2001::/24     | ${ipv6_br_src} | ${40}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:c9:db34::14a9:c9db:34        |
| | 20.169.201.0/24   | 2001::/24     | ${ipv6_br_src} | ${40}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db:3400::14a9:c9db:34        |
| | 20.169.201.219/32 | 2001::/24     | ${ipv6_br_src} | ${40}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:34::14a9:c9db:34             |
| | 20.169.0.0/16     | 2001::/16     | ${ipv6_br_src} | ${40}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:c9db:3400::14a9:c9db:34      |
| | 20.169.201.219/32 | 2001::/16     | ${ipv6_br_src} | ${40}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:3400::14a9:c9db:34           |

| | 20.0.0.0/8        | 2001:db8::/32 | ${ipv6_br_src} | ${32}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9:db34:0:14a9:c9db:34 |
| | 20.169.0.0/16     | 2001:db8::/32 | ${ipv6_br_src} | ${32}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:c9db:3400:0:14a9:c9db:34 |
| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_br_src} | ${32}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:db34::14a9:c9db:34       |
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_br_src} | ${32}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:3400::14a9:c9db:34       |
| | 20.169.0.0/16     | 2001::/24     | ${ipv6_br_src} | ${32}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:c9:db34::14a9:c9db:34        |
| | 20.169.201.0/24   | 2001::/24     | ${ipv6_br_src} | ${32}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db:3400::14a9:c9db:34        |
| | 20.169.0.0/16     | 2001::/16     | ${ipv6_br_src} | ${32}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:c9db:3400::14a9:c9db:34      |
| | 20.169.201.0/24   | 2001::/16     | ${ipv6_br_src} | ${32}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db34::14a9:c9db:34           |

| | 20.160.0.0/12     | 2001:db8::/32 | ${ipv6_br_src} | ${25}      | ${6}        | ${5}     | 20.169.201.219 | ${1232}  | 2001:db8:9c9d:b300:0:14a9:c9db:6  |
| | 20.169.0.0/16     | 2001:db8::/32 | ${ipv6_br_src} | ${25}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:c9db:3400:0:14a9:c9db:34 |
| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_br_src} | ${25}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:db34::14a9:c9db:34       |
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_br_src} | ${25}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:3400::14a9:c9db:34       |

| | 20.169.192.0/20   | 2001:db8::/32 | ${ipv6_br_src} | ${17}      | ${6}        | ${5}     | 20.169.201.219 | ${1232}  | 2001:db8:9db3::14a9:c9db:6        |
| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_br_src} | ${17}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:db34::14a9:c9db:34       |
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_br_src} | ${17}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:3400::14a9:c9db:34       |

| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_br_src} | ${12}      | ${6}        | ${4}     | 20.169.201.219 | ${1232}  | 2001:db8:db30::14a9:c9db:3        |
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_br_src} | ${12}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  | 2001:db8:3400::14a9:c9db:34       |


| TC04: End user IPv6 prefix is 64
| | [Documentation]
| | ... | Supported End-User IPv6 prefix length is 64 bit.
| | ...
| | ... | Arguments:
| | ...
| | ... | - ipv4_pfx
| | ... | - ipv6_pfx
| | ... | - ipv6_src
| | ... | - ea_bit_len
| | ... | - psid_offset
| | ... | - psid_len
| | ... | - ipv4_dst
| | ... | - dst_port
| | ...
# TODO: replace setup when VPP-312 fixed
#| | [Setup] | Set Interfaces IP Addresses And Routes
| | [Setup] | Run Keywords
| | ... | Set up functional test | AND
| | ... | Set Interfaces IP Addresses And Routes
| | [Template] | Check MAP Configuration With Traffic Script
# |===================|=========================|================|============|=============|==========|================|==========|
# | ipv4_pfx          | ipv6_pfx                | ipv6_src       | ea_bit_len | psid_offset | psid_len | ipv4_dst       | dst_port |
# |===================|=========================|================|============|=============|==========|================|==========|
| | 20.0.0.0/8        | 2001:db8:0012:3400::/56 | ${ipv6_br_src} | ${8}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  |
| | 20.169.201.208/28 | 2001:db8:0012:3400::/56 | ${ipv6_br_src} | ${8}       | ${5}        | ${4}     | 20.169.201.219 | ${3280}  |
| | 20.0.0.0/8        | 2001:db8:0012:3400::/64 | ${ipv6_br_src} | ${0}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  |
| | 20.169.201.219/32 | 2001:db8:0012:3400::/64 | ${ipv6_br_src} | ${0}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  |


| TC05: IPv4 prefix is 0
| | [Tags] | EXPECTED_FAILING
# TODO: replace setup when VPP-312 fixed
#| | [Setup] | Set Interfaces IP Addresses And Routes
| | [Setup] | Run Keywords
| | ... | Set up functional test | AND
| | ... | Set Interfaces IP Addresses And Routes
| | [Template] | Check MAP Configuration With Traffic Script
# |===================|=========================|================|============|=============|==========|================|==========|
# | ipv4_pfx          | ipv6_pfx                | ipv6_src       | ea_bit_len | psid_offset | psid_len | ipv4_dst       | dst_port |
# |===================|=========================|================|============|=============|==========|================|==========|
| | 0.0.0.0/0         | 2001:db8:0000::/40      | ${ipv6_br_src} | ${8}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  |
| | 0.0.0.0/0         | 2001:db8:0000::/40      | ${ipv6_br_src} | ${16}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  |
| | 0.0.0.0/0         | 2001:db8::/32           | ${ipv6_br_src} | ${32}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  |
| | 0.0.0.0/0         | 2001:d00::/24           | ${ipv6_br_src} | ${40}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  |
| | 0.0.0.0/0         | 2001::/16               | ${ipv6_br_src} | ${40}      | ${6}        | ${8}     | 20.169.201.219 | ${1232}  |


| TC06: Multiple domain and check with traffic script IPv4 source IPv6 destination
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Cfg] Multiple MAP-E domains are configured, values from variable\
| | ... | file.
| | ... | [Ver] Send IPv4 to destination in configured domain and receive IPv6\
| | ... | packet.
| | ... | [Ref] RFC7597.
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
| | And Vpp Route Add | ${dut_node} | :: | 0 | gateway=${dut_ip6_gw}
| | ... | interface=${dut_to_tg_if2} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6_gw}
| | ... | ${tg_to_dut_if2_mac}
| | And Vpp Route Add | ${dut_node} | 0.0.0.0 | 0 | gateway=${dut_ip4_gw}
| | ... | interface=${dut_to_tg_if1} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4_gw}
| | ... | ${tg_to_dut_if1_mac}
| | :FOR | ${domain_set} | IN | @{domain_sets}
| | | When Map Add Domain | ${dut_node} | @{domain_set}
| | :FOR | ${ip_set} | IN | @{ip_sets}
| | | ${ipv4}= | Get From List | ${ip_set} | 0
| | | ${ipv6}= | Get From List | ${ip_set} | 1
| | | ${port}= | Get From List | ${ip_set} | 2
| | | ${ipv6_br}= | Get From List | ${ip_set} | 3
| | | Then Send IPv4 UDP And Check Headers For Lightweight 4over6
| | | ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | | ... | ${dut_to_tg_if1_mac} | ${ipv4} | ${ipv4_outside} | ${port}
| | | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac} | ${ipv6} | ${ipv6_br}
| | | And Send IPv4 UDP In IPv6 And Check Headers For Lightweight 4over6
| | | ... | ${tg_node} | ${tg_to_dut_if2} | ${tg_to_dut_if1}
| | | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac} | ${ipv6_br} | ${ipv6}
| | | ... | ${ipv4_outside} | ${ipv4} | ${port} | ${tg_to_dut_if1_mac}
| | | ... | ${dut_to_tg_if1_mac}


| TC07: Multiple domain and check with traffic script IPv6 source IPv6 destination
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Cfg] Multiple MAP-E domains are configured, values from variable\
| | ... | file.
| | ... | [Ver] Send IPv4 encapsulated in IPv6. Source and destination are from\
| | ... | configured domains. Check if VPP translate IPv6 addresses.
| | ... | [Ref] RFC7597.
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
| | And Vpp Route Add | ${dut_node} | :: | 0 | gateway=${dut_ip6_gw}
| | ... | interface=${dut_to_tg_if2} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6_gw}
| | ... | ${tg_to_dut_if2_mac}
| | And Vpp Route Add | ${dut_node} | 0.0.0.0 | 0 | gateway=${dut_ip4_gw}
| | ... | interface=${dut_to_tg_if1} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4_gw}
| | ... | ${tg_to_dut_if1_mac}
| | :FOR | ${domain_set} | IN | @{domain_sets}
| | | When Map Add Domain | ${dut_node} | @{domain_set}
| | ${ip_set_A}= | Get From List | ${ip_sets} | 0
| | ${ip_set_B}= | Get From List | ${ip_sets} | 1
| | ${ipv6_br}= | Get From List | ${ip_set_A} | 3
| | ${port_A}= | Get From List | ${ip_set_A} | 2
| | ${port_B}= | Get From List | ${ip_set_B} | 2
| | ${ipv6_A}= | Get From List | ${ip_set_A} | 1
| | ${ipv6_B}= | Get From List | ${ip_set_B} | 1
| | ${ipv4_A}= | Get From List | ${ip_set_A} | 0
| | ${ipv4_B}= | Get From List | ${ip_set_B} | 0
| | Then Send IPv4 UDP In IPv6 And Check Headers For Lightweight Hairpinning
| | ... | ${tg_node} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac}
| | ... | ${ipv6_br} | ${ipv6_A}
| | ... | ${ipv4_B} | ${ipv4_A}
| | ... | ${port_B} | ${port_A}
| | ... | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac}
| | ... | ${ipv6_B} | ${ipv6_br}


| TC08: Encapsulate IPv4 ICMP into IPv6
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Enc] Eth-IPv4-ICMP(type 0 and 8) on TG_if1-DUT, Eth-IPv6-IPv4-ICMP\
| | ... | on TG_if2_DUT.
| | ... | [Cfg] Multiple MAP-E domains are configured, values from variable\
| | ... | file.
| | ... | [Ver] Make TG send non-encapsulated ICMP to DUT; verify TG received\
| | ... | IPv4oIPv6 encapsulated packet is correct. Checks IPv6 destination\
| | ... | based on ICMP Identifier field.
| | ... | [Ref] RFC7597 section 8.2.
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
| | And Vpp Route Add | ${dut_node} | :: | 0 | gateway=${dut_ip6_gw}
| | ... | interface=${dut_to_tg_if2} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6_gw}
| | ... | ${tg_to_dut_if2_mac}
| | And Vpp Route Add | ${dut_node} | 0.0.0.0 | 0 | gateway=${dut_ip4_gw}
| | ... | interface=${dut_to_tg_if1} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4_gw}
| | ... | ${tg_to_dut_if1_mac}
| | :FOR | ${domain_set} | IN | @{domain_sets}
| | | When Map Add Domain | ${dut_node} | @{domain_set}
| | ${ip_set_A}= | Get From List | ${ip_sets} | 0
| | ${ipv4_A}= | Get From List | ${ip_set_A} | 0
| | ${ipv6_A}= | Get From List | ${ip_set_A} | 1
| | ${icmp_id_A}= | Get From List | ${ip_set_A} | 2
| | ${ipv6_br}= | Get From List | ${ip_set_A} | 3
| | Then Send IPv4 ICMP And Check Headers For Lightweight 4over6
| | ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if1_mac} | ${ipv4_A} | ${ipv4_outside}
| | ... | ${icmp_id_A} | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac}
| | ... | ${ipv6_A} | ${ipv6_br}


| TC09: Repeated ip neighbor command doesnt put FIB to broken state
| | [Documentation] |
| | ... | Original issue described in https://jira.fd.io/browse/VPP-312.
| | ... | [Top] TG=DUT1.
| | ... | [Cfg] IP address are set on interfaces, ip neighbor multiple times
| | ... | [Ver] FIB is not in broken state. The steps are add route, \
| | ... | check with traffic then add same route
| | ... | again and check with traffic script.
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | When Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
| | And Vpp Route Add | ${dut_node} | 2001:: | 16 | gateway=${dut_ip6_gw}
| | ... | interface=${dut_to_tg_if2} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6_gw}
| | ... | ${tg_to_dut_if2_mac}
| | And Vpp Route Add | ${dut_node} | 0.0.0.0 | 0 | gateway=${dut_ip4_gw}
| | ... | interface=${dut_to_tg_if1} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4_gw}
| | ... | ${tg_to_dut_if1_mac}
| | Then Check MAP Configuration With Traffic Script
| | ... | 20.0.0.0/8 | 2001::/16 | ${ipv6_br_src} | ${48} | ${6} | ${8}
| | ... | 20.169.201.219 | ${1232} | 2001:a9c9:db34::14a9:c9db:34
| | When Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
| | And Vpp Route Add | ${dut_node} | 2001:: | 16 | gateway=${dut_ip6_gw}
| | ... | interface=${dut_to_tg_if2} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6_gw}
| | ... | ${tg_to_dut_if2_mac}
| | And Vpp Route Add | ${dut_node} | 0.0.0.0 | 0 | gateway=${dut_ip4_gw}
| | ... | interface=${dut_to_tg_if1} | resolve_attempts=${NONE} | count=${NONE}
| | And Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4_gw}
| | ... | ${tg_to_dut_if1_mac}
| | Then Check MAP Configuration With Traffic Script
| | ... | 20.0.0.0/8 | 2001::/16 | ${ipv6_br_src} | ${48} | ${6} | ${8}
| | ... | 20.169.201.219 | ${1232} | 2001:a9c9:db34::14a9:c9db:34


| Bug: VPP-318
| | [Tags] | EXPECTED_FAILING
| | [Documentation] | qlen < psid length
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
| | Then Run Keyword And Expect Error | Unable to add map domain *
| | ... | Map Add Domain | ${dut_node} | 20.169.0.0/16 | 2001:db8::/32
| | ... | ${ipv6_br_src} | ${20} | ${6} | ${8}


*** Keywords ***
| Set Interfaces IP Addresses And Routes
| | Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Set interfaces in 2-node circular topology up
| | Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
| | Vpp Route Add | ${dut_node} | :: | 0 | gateway=${dut_ip6_gw}
| | ... | interface=${dut_to_tg_if2} | resolve_attempts=${NONE} | count=${NONE}
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6_gw}
| | ... | ${tg_to_dut_if2_mac}
| | Vpp Route Add | ${dut_node} | ${ipv4_outside} | 32 | gateway=${dut_ip4_gw}
| | ... | interface=${dut_to_tg_if1} | resolve_attempts=${NONE} | count=${NONE}
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4_gw}
| | ... | ${tg_to_dut_if1_mac}

| Check MAP Configuration With Traffic Script
| | [Documentation]
| | ... | Used as a test case template.\
| | ... | Configure MAP-E domain with given parameters, with traffic script send
| | ... | UDP in IPv4 packet to given UDP destination port and IP destination
| | ... | address and check if correctly received IPv6 packet. Vice versa send
| | ... | IPv6 packet and check if received IPv4 packet with correct source
| | ... | address.
| | ... | The MAP domain is deleted in teardown.
| | ... | The expected IPv6 address is compared with computed IPv6 address.
| | [Arguments] | ${ipv4_pfx} | ${ipv6_pfx} | ${ipv6_br_src} | ${ea_bit_len}
| | ... | ${psid_offset} | ${psid_len} | ${ipv4_dst} | ${dst_port}
| | ... | ${expected_ipv6_dst}=${EMPTY}
| | ${domain_index}= | Map Add Domain | ${dut_node} | ${ipv4_pfx} | ${ipv6_pfx}
| | ... | ${ipv6_br_src} | ${ea_bit_len} | ${psid_offset} | ${psid_len}
| | ${computed_ipv6_dst}= | Compute IPv6 Map Destination Address
| | ... | ${ipv4_pfx} | ${ipv6_pfx} | ${ea_bit_len} | ${psid_offset}
| | ... | ${psid_len} | ${ipv4_dst} | ${dst_port}
| | ${ipv6_dst}= | Run Keyword If | "${expected_ipv6_dst}" == "${EMPTY}"
| | ... | Set Variable | ${computed_ipv6_dst}
| | ... | ELSE | Set Variable | ${expected_ipv6_dst}
| | Run Keyword If | "${expected_ipv6_dst}" != "${EMPTY}"
| | ... | IP Addresses Should Be Equal
| | ... | ${computed_ipv6_dst} | ${expected_ipv6_dst}
| | ${ipv6_dst}= | Set Variable | ${computed_ipv6_dst}
| | Check Encapsulation With Traffic Script
| | ... | ${ipv4_dst} | ${dst_port} | ${ipv6_dst}
| | Check Decapsulation With Traffic Script
| | ... | ${ipv6_dst} | ${ipv4_dst} | ${dst_port}
| | [Teardown] | Run Keywords
| | ... | Map Del Domain | ${dut_node} | ${domain_index} | AND
| | ... | Show Packet Trace On All DUTs | ${nodes} | AND
| | ... | Clear Packet Trace On All DUTs | ${nodes} | AND
| | ... | Verify VPP PID in Teardown

| Check Encapsulation With Traffic Script
| | [Arguments] | ${ipv4_dst} | ${dst_port} | ${ipv6_dst}
| | Send IPv4 UDP And Check Headers For Lightweight 4over6
| | ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| | ... | ${dut_to_tg_if1_mac} | ${ipv4_dst} | ${ipv4_outside}
| | ... | ${dst_port} | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac}
| | ... | ${ipv6_dst} | ${ipv6_br_src}

| Check Decapsulation With Traffic Script
| | [Arguments] | ${ipv6_ce_addr} | ${ipv4_inside} | ${port}
| | Send IPv4 UDP In IPv6 And Check Headers For Lightweight 4over6
| | ... | ${tg_node} | ${tg_to_dut_if2} | ${tg_to_dut_if1}
| | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
| | ... | ${ipv6_br_src} | ${ipv6_ce_addr}
| | ... | ${ipv4_outside} | ${ipv4_inside} | ${port}
| | ... | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
