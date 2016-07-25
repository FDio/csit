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


*** Test Cases ***
| TCXX: BMR, then an IPv4 prefix is assigned
| | [Tags] | tmp
| | [Documentation] |
| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
| | ... | o + r < 32
| | ... |
| | [Setup] | Set interfaces and IP addresses
| | [Template] | KW will be named later
#
# | ipv4_pfx | ipv6_pfx | ipv6_src | ea_bit_len | psid_offset | psid_len | ipv4_dst | dst_port | expected_ipv6_dst
#
#test
| | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${20}  | ${6} | ${8} | 20.1.2.163 | ${1232} | 2001:db8:0102:0000:0000:1400:0000:00
#| | 20.0.0.0/16 | 2001:db8::/32 | ${ipv6_src} | ${16}      | ${6}        | ${8}     | 20.0.6.5 | ${1232}


#| | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${4}  | ${6} | ${8} | 20.0.6.5 | ${1232} |
#| | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${4}  | ${6} | ${8} | 20.0.6.5 | ${1232} | 2001:db8:0034:0000:0000:1400:0000:0000
# | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${8}  | ${6} | ${8} | 20.0.6.5 | ${1232} |
# | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${16} | ${6} | ${8} | 20.0.6.5 | ${1232} |
# | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${20} | ${6} | ${8} | 20.0.6.5 | ${1232} |
# | 20.0.0.0/8  | 2001:db8::/32 | ${ipv6_src} | ${23} | ${6} | ${8} | 20.0.6.5 | ${1232} |
# | 20.0.0.0/24 | 2001:db8::/32 | ${ipv6_src} | ${4}  | ${6} | ${8} | 20.0.6.5 | ${1232} |
# | 20.0.0.0/24 | 2001:db8::/32 | ${ipv6_src} | ${7}  | ${6} | ${8} | 20.0.6.5 | ${1232} |


#| TCXX: BMR, full IPv4 address is to be assigned
#| | [Tags] | tmp
#| | [Documentation] |
#| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
#| | ... | o + r = 32
#| | ... |
#| | [Setup] | Set interfaces and IP addresses
#| | [Template] | KW will be named later
## | ipv4_pfx    | ipv6_pfx      | ipv6_src    | ea_bit_len | psid_offset | psid_len | ipv4_dst | dst_port | expected_ipv6_dst
##
#| | 20.0.0.0/16 | 2001:db8::/32 | ${ipv6_src} | ${16}      | ${6}        | ${8}     | 20.0.6.5 | ${1232}  |



#| TCXX: BMR, shared IPv4 address is to be assigned
#| | [Tags] | tmp
#| | [Documentation] |
#| | ... | Basic Mapping Rule https://tools.ietf.org/html/rfc7597#section-5.2\
#| | ... | o + r > 32
#| | ... |
#| | [Setup] | Set interfaces and IP addresses
#| | [Template] | KW will be named later
## | ipv4_pfx    | ipv6_pfx      | ipv6_src    | ea_bit_len | psid_offset | psid_len | ipv4_dst | dst_port | expected_ipv6_dst
##
#| | 20.0.0.0/16 | 2001:db8::/32 | ${ipv6_src} | ${16}      | ${6}        | ${8}     | 20.0.6.5 | ${1232}  |






#| TC00: configure one domain in template with different ea psid pkt dst; check dst ipv6; delete domain
#| | [Documentation] | TBD
##| | [Tags] | tmp
#| | [Setup] | Set interfaces and IP addresses
#| | [Template] | KW will be named later
#| | ...
## | ipv4_pfx    | ipv6_pfx      | ipv6_src    | ea_bit_len | psid_offset | psid_len | ipv4_dst | dst_port | expected_ipv6_dst
##
#| | 20.0.0.0/16 | 2001:db8::/32 | ${ipv6_src} | ${16}      | ${6}        | ${8}     | 20.0.6.5 | ${1232}
#| | 20.0.0.0/16 | 2001:db8::/40 | ${ipv6_src} | ${16}      | ${6}        | ${8}     | 20.0.6.5 | ${1232}
#| | 20.0.0.0/16 | 2001:db8::/48 | ${ipv6_src} | ${16}      | ${6}        | ${8}     | 20.0.6.5 | ${1232}



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
#TODO: check computed with expected_ipv6_dst
#| | Run Keyword If | "${expected_ipv6_dst}" != "${EMPTY}" | ipv6 addresses should be same | ${computed_ipv6_dst} | ${expected_ipv6_dst}
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


