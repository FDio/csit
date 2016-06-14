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
| Resource | resources/libraries/robot/map.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *RFC 7596*

*** Variables ***
| ${dut_ip1}= | 10.10.10.1
| ${dut_ip2}= | 2001::1
| ${ipv4_prefix}= | 24
| ${ipv6_prefix}= | 64

*** Test Cases ***
| test 01
| | [Tags] | tmp
| | [Documentation] | TBD
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip1} | ${ipv4_prefix}
| |       ... | ${dut_node} | ${dut_to_tg_if2} | ${dut_ip2} | ${ipv6_prefix}
| | When Lightweight 4over6 is set | ${dut_node}
#| | Then
