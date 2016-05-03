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
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/iacl.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.IPv6Util.IPv6Util
| Library | resources.libraries.python.IPv6Setup.IPv6Setup
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO | COP
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Show packet trace on all DUTs | ${nodes}

*** Variables ***
| ${dut1_if1_ip}= | 3ffe:62::1
| ${dut1_if2_ip}= | 3ffe:63::1
| ${dut1_if2_ip_GW}= | 3ffe:63::2
| ${dut2_if1_ip}= | 3ffe:72::1
| ${dut2_if2_ip}= | 3ffe:73::1
| ${test_dst_ip}= | 3ffe:64::1
| ${test_src_ip}= | 3ffe:61::1
| ${prefix_length}= | 64

| ${acl_method}= | deny
| ${ip_version}= | ip6
| ${src_direction}= | src
| ${dst_direction}= | dst

*** Test Cases ***
| VPP drops packets based on IPv6 source addresses
| | [Documentation] | iACL - ipv 6 test
| | Given Node path computed for 3-node topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in path are up
| | And IPv6 Addresses set on the node interfaces
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip} | ${dut1_if2} | ${dut1_if2_ip}
| | ... | ${prefix_length}
| | ${table_index} | ${skip_n} | ${match_n}= | When Classify Add Table
| | ... | ${dut1} | ${ip_version} | ${src_direction}
| | And Classify Session
| | ... | ${dut1} | ${acl_method} | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${ip_version} | ${src_direction} | ${test_src_ip}
| | And Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ${ip_version} | ${table_index}
| | And Add Ip Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | And Vpp Route Add
| | ... | ${dut1} | ${test_dst_ip} | ${prefix_length} | ${dut1_if2_ip_GW}
| | ... | ${dut1_if2}
| | And L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Then Send ICMPv6 packet should failed
| | ... | ${tg} | ${tg_if2} | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${test_src_ip} | ${test_dst_ip}


| VPP drops packets based on IPv6 destination addresses
| | [Documentation] | iACL - ipv 6 test
| | Given Node path computed for 3-node topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in path are up
| | And IPv6 Addresses set on the node interfaces
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip} | ${dut1_if2} | ${dut1_if2_ip}
| | ... | ${prefix_length}
| | ${table_index} | ${skip_n} | ${match_n}= | When Classify Add Table
| | ... | ${dut1} | ${ip_version} | ${dst_direction}
| | And Classify Session
| | ... | ${dut1} | ${acl_method} | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${ip_version} | ${dst_direction} | ${test_dst_ip}
| | And Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ${ip_version} | ${table_index}
| | And Add Ip Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | And Vpp Route Add
| | ... | ${dut1} | ${test_dst_ip} | ${prefix_length} | ${dut1_if2_ip_GW}
| | ... | ${dut1_if2}
| | And L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Then Send ICMPv6 packet should failed
| | ... | ${tg} | ${tg_if2} | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${test_src_ip} | ${test_dst_ip}


| VPP drops packets based on IPv6 src-addr and dst-addr
| | [Documentation] | iACL - ipv 6 test
| | Given Node path computed for 3-node topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in path are up
| | And IPv6 Addresses set on the node interfaces
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip} | ${dut1_if2} | ${dut1_if2_ip}
| | ... | ${prefix_length}
| | ${table_index_1} | ${skip_n_1} | ${match_n_1}= | When Classify Add Table
| | ... | ${dut1} | ${ip_version} | ${src_direction}
| | ${table_index_2} | ${skip_n_2} | ${match_n_2}= | When Classify Add Table
| | ... | ${dut1} | ${ip_version} | ${dst_direction}
| | And Classify Session
| | ... | ${dut1} | ${acl_method} | ${table_index_1} | ${skip_n_1} | ${match_n_2}
| | ... | ${ip_version} | ${src_direction} | ${test_src_ip}
| | And Classify Session
| | ... | ${dut1} | ${acl_method} | ${table_index_2} | ${skip_n_2} | ${match_n_2}
| | ... | ${ip_version} | ${dst_direction} | ${test_dst_ip}
| | And Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ${ip_version} | ${table_index_1}
| | And Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ${ip_version} | ${table_index_2}
| | And Add Ip Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | And Vpp Route Add
| | ... | ${dut1} | ${test_dst_ip} | ${prefix_length} | ${dut1_if2_ip_GW}
| | ... | ${dut1_if2}
| | And L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Then Send ICMP packet should failed
| | ... | ${tg} | ${tg_if2} | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${test_src_ip} | ${test_dst_ip}
