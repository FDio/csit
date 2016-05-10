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
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/iacl.robot
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
| ${dut1_if1_ip}= | 192.168.1.1
| ${dut1_if2_ip}= | 192.168.2.1
| ${dut1_if2_ip_GW}= | 192.168.2.2
| ${test_dst_ip}= | 32.0.0.1
| ${test_src_ip}= | 16.0.0.1
| ${prefix_length}= | 24

*** Test Cases ***
| VPP drops packets based on IPv4 source addresses
| | [Documentation] | Create classify table on VPP, add source IP address
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Node path computed for 3-node topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in path are up
| | And IPv4 Addresses set on the node interfaces
| | ... | ${dut1_node} | ${dut1_if1} | ${dut1_if1_ip} | ${dut1_if2}
| | ... | ${dut1_if2_ip} | ${prefix_length}
| | ${table_index} | ${skip_n} | ${match_n}= | When Vpp Create Classify Table
| | ... | ${dut1_node} | ip4 | src
| | And Vpp Configure Classify Session
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | src | ${test_src_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_if1} | ip4 | ${table_index}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length} | ${dut1_if2_ip_GW}
| | ... | ${dut1_if2}
| | And L2 setup xconnect on DUT | ${dut2_node} | ${dut2_if1} | ${dut2_if2}
| | Then Send packet from Port to Port should failed | ${tg_node} |
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} |
| | ... | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}

| VPP drops packets based on IPv4 destination addresses
| | [Documentation] | Create classify table on VPP, add destination IP address
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Node path computed for 3-node topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in path are up
| | And IPv4 Addresses set on the node interfaces
| | ... | ${dut1_node} | ${dut1_if1} | ${dut1_if1_ip} | ${dut1_if2}
| | ... | ${dut1_if2_ip} | ${prefix_length}
| | ${table_index} | ${skip_n} | ${match_n}= | When Vpp Create Classify Table
| | ... | ${dut1_node} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | ${test_dst_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_if1} | ip4 | ${table_index}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length} | ${dut1_if2_ip_GW}
| | ... | ${dut1_if2}
| | And L2 setup xconnect on DUT | ${dut2_node} | ${dut2_if1} | ${dut2_if2}
| | Then Send packet from Port to Port should failed | ${tg_node} |
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} |
| | ... | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}


| VPP drops packets based on IPv4 src-addr and dst-addr
| | [Documentation] | Create classify table on VPP, add source and destination
| | ...             | IP address of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Node path computed for 3-node topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in path are up
| | And IPv4 Addresses set on the node interfaces
| | ... | ${dut1_node} | ${dut1_if1} | ${dut1_if1_ip} | ${dut1_if2}
| | ... | ${dut1_if2_ip} | ${prefix_length}
| | ${table_index_1} | ${skip_n_1} | ${match_n_1}=
| | ... | When Vpp Create Classify Table | ${dut1_node} | ip4 | src
| | ${table_index_2} | ${skip_n_2} | ${match_n_2}=
| | ... | When Vpp Create Classify Table | ${dut1_node} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1_node} | deny | ${table_index_1} | ${skip_n_1} | ${match_n_2}
| | ... | ip4 | src | ${test_src_ip}
| | And Vpp Configure Classify Session
| | ... | ${dut1_node} | deny | ${table_index_2} | ${skip_n_2} | ${match_n_2}
| | ... | ip4 | dst | ${test_dst_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_if1} | ip4 | ${table_index_1}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_if1} | ip4 | ${table_index_2}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length} | ${dut1_if2_ip_GW}
| | ... | ${dut1_if2}
| | And L2 setup xconnect on DUT | ${dut2_node} | ${dut2_if1} | ${dut2_if2}
| | Then Send packet from Port to Port should failed | ${tg_node} |
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} |
| | ... | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
