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

*** Variables ***
| ${dut_ip4}= | 10.0.0.1
| ${dut_ip6}= | 2001:0::1
| ${ipv4_prefix_len}= | 24
| ${ipv6_prefix_len}= | 64

*** Settings ***
#| Library | Collections
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
| Documentation | *TBD*

*** Test Cases ***
| TC00: MAP config
| | [Tags] | tmp
| | [Documentation]
| | ... | TBD
| | ...
| | ${ipv6_src}=    | Set Variable | 2001:db8:0012:34ff::1
| | ${ipv6_pfx}=    | Set Variable | 2001:db8:0012:3400::/56
| | ${ipv4_pfx}=    | Set Variable | 192.0.2.0/24
| | ${ea_bit_len}=  | Set Variable | 16
| | ${psid_len}=    | Set Variable | 8
| | ${psid_offset}= | Set Variable | 6
| | ${domain_1}= | Create List | ${ipv4_pfx} | ${ipv6_pfx} | ${ipv6_src}  | ${ea_bit_len} | ${psid_offset} | ${psid_len}



| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip4} | ${ipv4_prefix_len}
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip6} | ${ipv6_prefix_len}
# WHEN
| | ${domain_index}= | When Map Add Domain | ${dut_node} | @{domain_1}

# THEN


