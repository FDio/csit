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
#| Library | Collections
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/map.robot
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Suite Setup | Run Keywords
| ... | Setup all DUTs before test | AND
| ... | Setup all TGs before traffic script
| Test Teardown | Run Keywords
| ... | Show packet trace on all DUTs | ${nodes} | AND
| ... | Show vpp trace dump on all DUTs
| Documentation | *TBD - module and test docs*


*** Variables ***
| ${dut_ip4}= | 10.0.0.1
| ${dut_ip6}= | 2001:0::1
| ${dut_ip6_gw}= | 2001:0::2
| ${ipv4_prefix_len}= | 24
| ${ipv6_prefix_len}= | 64
| ${ipv6_src}= | 2001:db8:ffff::1
| ${ipv4_outside}= | 100.0.0.1
#todo: replace with this ip
| ${destination_ipv4}= | 20.169.201.219


*** Test Cases ***
| TCXX: BMR, then an IPv4 prefix is assigned
| | [Tags] | EXPECTED_FAILING
| | [Documentation] |
| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
| | ... | IPv4 prefix length + ea bits length < 32 (o + r < 32)
| | ... | psid_length = 0, ip6_prefix < 64, ip4_prefix <= 32
| | [Setup] | Set interfaces and IP addresses
| | [Template] | KW will be named later
# |=================|===============|=============|============|=============|==========|================|==========|==================================|
# | ipv4_pfx        | ipv6_pfx      | ipv6_src    | ea_bit_len | psid_offset | psid_len | ipv4_dst       | dst_port | expected_ipv6_dst                |
# |=================|===============|=============|============|=============|==========|================|==========|==================================|
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_src} | ${4}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a000::14a0:0:0          |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_src} | ${8}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a900::14a9:0:0          |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_src} | ${10}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c0::14a9:c000:0       |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_src} | ${16}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9::14a9:c900:0       |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_src} | ${20}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9:d000:0:14a9:c9d0:0 |
| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_src} | ${23}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9:da00:0:14a9:c9da:0 |
| | 20.169.201.0/24 | 2001:db8::/32 | ${ipv6_src} | ${4}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:d000::14a9:c9d0:0       |
| | 20.169.201.0/24 | 2001:db8::/32 | ${ipv6_src} | ${7}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:da00::14a9:c9da:0       |


| TCXX: BMR, full IPv4 address is to be assigned
| | [Tags] | tmp
| | [Documentation] |
| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
| | ... | IPv4 prefix length + ea bits length == 32 (o + r == 32)
| | ... | psid_length = 0, ip6_prefix < 64, ip4_prefix <= 32
| | [Setup] | Set interfaces and IP addresses
| | [Template] | KW will be named later
# |===================|===============|=============|============|=============|==========|================|==========|==================================|
# | ipv4_pfx          | ipv6_pfx      | ipv6_src    | ea_bit_len | psid_offset | psid_len | ipv4_dst       | dst_port | expected_ipv6_dst                |
# |===================|===============|=============|============|=============|==========|================|==========|==================================|
| | 20.0.0.0/8        | 2001:db8::/32 | ${ipv6_src} | ${24}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9c9:db00:0:14a9:c9db:0 |
| | 20.160.0.0/12     | 2001:db8::/32 | ${ipv6_src} | ${20}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:9c9d:b000:0:14a9:c9db:0 |
| | 20.169.0.0/16     | 2001:db8::/32 | ${ipv6_src} | ${16}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:c9db::14a9:c9db:0       |
| | 20.169.200.0/22   | 2001:db8::/32 | ${ipv6_src} | ${10}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:76c0::14a9:c9db:0       |
| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_src} | ${8}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:db00::14a9:c9db:0       |
| | 20.169.201.208/28 | 2001:db8::/32 | ${ipv6_src} | ${4}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:b000::14a9:c9db:0       |
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_src} | ${0}       | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8::14a9:c9db:0            |

| | 20.0.0.0/8        | 2001:db8::/40 | ${ipv6_src} | ${24}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:a9:c9db:0:14a9:c9db:0   |
| | 20.160.0.0/12     | 2001:db8::/44 | ${ipv6_src} | ${20}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:9:c9db:0:14a9:c9db:0    |
| | 20.169.0.0/16     | 2001:db8::/48 | ${ipv6_src} | ${16}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:0:c9db:0:14a9:c9db:0    |
| | 20.169.200.0/22   | 2001:db8::/54 | ${ipv6_src} | ${10}      | ${0}        | ${0}     | 20.169.201.219 | ${1232}  | 2001:db8:0:1db:0:14a9:c9db:0     |



| TCXX: BMR, shared IPv4 address is to be assigned
#| | [Tags] | tmp
| | [Documentation] |
| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
| | ... | o + r > 32
| | ... |
| | [Setup] | Set interfaces and IP addresses
| | [Template] | KW will be named later
# | ipv4_pfx    | ipv6_pfx      | ipv6_src    | ea_bit_len | psid_offset | psid_len | ipv4_dst | dst_port | expected_ipv6_dst
#
| | 20.0.0.0/8        | 2001::/16     | ${ipv6_src} | ${48} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:a9c9:db34::14a9:c9db:34 != 2001:a9c9:db00:34:0:14a9:c9db:34
| | 20.169.0.0/16     | 2001::/16     | ${ipv6_src} | ${48} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:c9db:3400::14a9:c9db:34 != 2001:c9db:0:34:0:14a9:c9db:34
| | 20.169.201.0/24   | 2001::/16     | ${ipv6_src} | ${48} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db34::14a9:c9db:34 != 2001:db00:0:34:0:14a9:c9db:34
| | 20.169.201.219/32 | 2001::/16     | ${ipv6_src} | ${48} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:3400::14a9:c9db:34 != 2001::34:0:14a9:c9db:34


| | 20.0.0.0/8        | 2001::/24     | ${ipv6_src} | ${40} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:a9:c9db:3400:0:14a9:c9db:34 != 2001:a9:c9db:34:0:14a9:c9db:34
| | 20.169.0.0/16     | 2001::/24     | ${ipv6_src} | ${40} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:c9:db34::14a9:c9db:34 != 2001:c9:db00:34:0:14a9:c9db:34
| | 20.169.201.0/24   | 2001::/24     | ${ipv6_src} | ${40} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db:3400::14a9:c9db:34 != 2001:db:0:34:0:14a9:c9db:34
| | 20.169.201.219/32 | 2001::/24     | ${ipv6_src} | ${40} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:34::14a9:c9db:34 != 2001::34:0:14a9:c9db:34
| | 20.169.0.0/16     | 2001::/16     | ${ipv6_src} | ${40} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:c9db:3400::14a9:c9db:34 != 2001:c9db:0:3400:0:14a9:c9db:34
| | 20.169.201.219/32 | 2001::/16     | ${ipv6_src} | ${40} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:3400::14a9:c9db:34 != 2001::3400:0:14a9:c9db:34


| | 20.0.0.0/8        | 2001:db8::/32 | ${ipv6_src} | ${32} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# ok
| | 20.169.0.0/16     | 2001:db8::/32 | ${ipv6_src} | ${32} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:c9db:3400:0:14a9:c9db:34 != 2001:db8:c9db:34:0:14a9:c9db:34
| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_src} | ${32} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:db34::14a9:c9db:34 != 2001:db8:db00:34:0:14a9:c9db:34
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_src} | ${32} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:3400::14a9:c9db:34 != 2001:db8:0:34:0:14a9:c9db:34
| | 20.169.0.0/16     | 2001::/24     | ${ipv6_src} | ${32} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:c9:db34::14a9:c9db:34 != 2001:c9:db00:3400:0:14a9:c9db:34
| | 20.169.201.0/24   | 2001::/24     | ${ipv6_src} | ${32} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db:3400::14a9:c9db:34 != 2001:db:0:3400:0:14a9:c9db:34
| | 20.169.0.0/16     | 2001::/16     | ${ipv6_src} | ${32} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:c9db:3400::14a9:c9db:34 != 2001:c9db:34::14a9:c9db:34
| | 20.169.201.0/24   | 2001::/16     | ${ipv6_src} | ${32} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db34::14a9:c9db:34 != 2001:db00:34::14a9:c9db:34


| | 20.160.0.0/12     | 2001:db8::/32 | ${ipv6_src} | ${25} | ${6} | ${5} | 20.169.201.219 | ${1232} |
# ok
| | 20.169.0.0/16     | 2001:db8::/32 | ${ipv6_src} | ${25} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:c9db:3400:0:14a9:c9db:34 != 2001:db8:c9db:1a00:0:14a9:c9db:34
| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_src} | ${25} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:db34::14a9:c9db:34 != 2001:db8:db00:1a00:0:14a9:c9db:34
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_src} | ${25} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:3400::14a9:c9db:34 != 2001:db8:0:1a00:0:14a9:c9db:34



| | 20.169.192.0/20   | 2001:db8::/32 | ${ipv6_src} | ${17} | ${6} | ${5} | 20.169.201.219 | ${1232} |
# ok
| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_src} | ${17} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:db34::14a9:c9db:34 != 2001:db8:db1a::14a9:c9db:34
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_src} | ${17} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:3400::14a9:c9db:34 != 2001:db8:1a::14a9:c9db:34


| | 20.169.201.0/24   | 2001:db8::/32 | ${ipv6_src} | ${12} | ${6} | ${4} | 20.169.201.219 | ${1232} |
| | 20.169.201.219/32 | 2001:db8::/32 | ${ipv6_src} | ${12} | ${6} | ${8} | 20.169.201.219 | ${1232} |
# 2001:db8:3400::14a9:c9db:34 != 2001:db8:340::14a9:c9db:34




#| TCXX: BMR, ipv6 pfx longer than 48, pfx + ea bits <= 64
#| | [Tags] | tmp
#| | [Documentation] |
#| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
#| | ... |
#| | ... |
#| | [Setup] | Set interfaces and IP addresses
#| | [Template] | KW will be named later
## | ipv4_pfx    | ipv6_pfx      | ipv6_src    | ea_bit_len | psid_offset | psid_len | ipv4_dst | dst_port | expected_ipv6_dst
##
#| | 20.0.0.0/8      | 2001:db8::/32 | ${ipv6_src} | ${24} | ${0} | ${0} | 20.169.201.219 | ${1232} | 2001:db8:a9c9:db00:0:14a9:c9db:0




| TC00: configure one domain in template with different ea psid pkt dst; check dst ipv6; delete domain
| | [Documentation] | test compute v6 address \
#| | [Tags] | tmp
| | [Setup] | Set interfaces and IP addresses
| | [Template] | KW will be named later
| | ...
# | ipv4_pfx    | ipv6_pfx      | ipv6_src    | ea_bit_len | psid_offset | psid_len | ipv4_dst | dst_port | expected_ipv6_dst
#
#test
#| | 20.0.0.0/12 | 2001:db8::/49 | ${ipv6_src} | ${20} | ${6} | ${8} | 20.169.201.219 | ${1232} # unable to configure
#| | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${20}  | ${6} | ${8} | 20.1.2.163     | ${1232} | 2001:db8:0102:a000:0000:1401:02a0:0000
#| | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${20}  | ${6} | ${8} | 20.169.201.219 | ${1232} |
#| | 192.0.2.0/24  | 2001:db8:0000::/40 | ${ipv6_src} | ${16}  | ${6} | ${8} | 192.0.2.18 | ${1232} | 2001:db8:0012:3400:0000:c000:0212:0034
# 2001:db8:12:3400:0:c000:212:34




*** Keywords ***
| Set interfaces and IP addresses
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Interfaces in 2-node path are up
| | IP addresses are set on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}

| KW will be named later
| | [Arguments] | ${ipv4_pfx} | ${ipv6_pfx} | ${ipv6_src} | ${ea_bit_len} | ${psid_offset} | ${psid_len} | ${ipv4_dst} | ${dst_port} | ${expected_ipv6_dst}=${EMPTY}
| | ${domain_index}= | Map Add Domain | ${dut_node} | ${ipv4_pfx} | ${ipv6_pfx} | ${ipv6_src} | ${ea_bit_len} | ${psid_offset} | ${psid_len}
| | ${computed_ipv6_dst}= | Compute IPv6 map destination address | ${ipv4_pfx} | ${ipv6_pfx} | ${ea_bit_len} | ${psid_offset} | ${psid_len} | ${ipv4_dst} | ${dst_port}
| | ${ipv6_dst}= | Run Keyword If | "${expected_ipv6_dst}" == "${EMPTY}" | Set Variable | ${computed_ipv6_dst}
| | ... | ELSE |  Set Variable | ${expected_ipv6_dst}
| | Run Keyword If | "${expected_ipv6_dst}" != "${EMPTY}" | IP Addresses Should be Equal | ${computed_ipv6_dst} | ${expected_ipv6_dst}
| | ${ipv6_dst}= | Set Variable | ${computed_ipv6_dst}
| | Vpp Route Add | ${dut_node} | :: | 0 | ${dut_ip6_gw} | ${dut_to_tg_if2} | resolve_attempts=${NONE} | count=${NONE}
| | Add IP neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6_gw} | ${tg_to_dut_if2_mac}
| | Check with traffic script | ${ipv4_dst} | ${dst_port} | ${ipv6_dst}
| | [Teardown] | Run Keywords
| | ... | Map Del Domain | ${dut_node} | ${domain_index} | AND
| | ... | Show packet trace on all DUTs | ${nodes} | AND
| | ... | Clear packet trace on all DUTs | ${nodes}

| Check with traffic script
| | [Arguments] | ${ipv4_dst} | ${dst_port} | ${ipv6_dst}
| | Then Send IPv4 UDP and check headers for lightweight 4over6
| |      ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
| |      ... | ${dut_to_tg_if1_mac} | ${ipv4_dst} | ${ipv4_outside}
| |      ... | ${dst_port} | ${tg_to_dut_if2_mac} | ${dut_to_tg_if2_mac}
| |      ... | ${ipv6_dst} | ${ipv6_src}
