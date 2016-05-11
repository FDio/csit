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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Show packet trace on all DUTs | ${nodes}

*** Variables ***
| ${dut1_to_tg_ip}= | 3ffe:62::1
| ${dut1_to_dut2_ip}= | 3ffe:63::1
| ${dut1_to_dut2_ip_GW}= | 3ffe:63::2
| ${dut2_to_dut1_ip}= | 3ffe:72::1
| ${dut2_to_tg_ip}= | 3ffe:73::1
| ${test_dst_ip}= | 3ffe:64::1
| ${test_src_ip}= | 3ffe:61::1
| ${prefix_length}= | 64

*** Test Cases ***
| VPP drops packets based on IPv6 source addresses
| | [Documentation] | Create classify table on VPP, add source IP address
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Vpp Set If Ipv6 Addr | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Set If Ipv6 Addr  | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | ${table_index} | ${skip_n} | ${match_n}= | When Vpp Create Classify Table
| | ... | ${dut1_node} | ip6 | src
| | And Vpp Configure Classify Session
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip6 | src | ${test_src_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ip6 | ${table_index}
| | And Add Ip Neighbor
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send packet from Port to Port should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}


| VPP drops packets based on IPv6 destination addresses
| | [Documentation] | Create classify table on VPP, add destination IP address
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Vpp Set If Ipv6 Addr | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Set If Ipv6 Addr  | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | ${table_index} | ${skip_n} | ${match_n}= | When Vpp Create Classify Table
| | ... | ${dut1_node} | ip6 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip6 | dst | ${test_dst_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ip6 | ${table_index}
| | And Add Ip Neighbor
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send packet from Port to Port should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}


| VPP drops packets based on IPv6 src-addr and dst-addr
| | [Documentation] | Create classify table on VPP, add source and destination
| | ...             | IP address of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Vpp Set If Ipv6 Addr | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Set If Ipv6 Addr  | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | ${table_index_1} | ${skip_n_1} | ${match_n_1}=
| | ... | When Vpp Create Classify Table | ${dut1_node} | ip6 | src
| | ${table_index_2} | ${skip_n_2} | ${match_n_2}=
| | ... | When Vpp Create Classify Table | ${dut1_node} | ip6 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1_node} | deny | ${table_index_1} | ${skip_n_1} | ${match_n_2}
| | ... | ip6 | src | ${test_src_ip}
| | And Vpp Configure Classify Session
| | ... | ${dut1_node} | deny | ${table_index_2} | ${skip_n_2} | ${match_n_2}
| | ... | ip6 | dst | ${test_dst_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ip6 | ${table_index_1}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ip6 | ${table_index_2}
| | And Add Ip Neighbor
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send packet from Port to Port should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
