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
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Show packet trace on all DUTs | ${nodes}
| ...           | AND          | Vpp Show Errors | ${nodes['DUT1']}

*** Variables ***
| ${dut1_to_tg_ip}= | 192.168.1.1
| ${dut1_to_dut2_ip}= | 192.168.2.1
| ${dut1_to_dut2_ip_GW}= | 192.168.2.2
| ${test_dst_ip}= | 32.0.0.1
| ${test_src_ip}= | 16.0.0.1
| ${non_drop_dst_ip}= | 33.0.0.1
| ${non_drop_src_ip}= | 15.0.0.1
| ${prefix_length}= | 24
| ${ip_version}= | ip4
| ${l2_table}= | l2

*** Test Cases ***
| VPP drops packets based on IPv4 source addresses
| | [Documentation] | Create classify table on VPP, add source IP address
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${non_drop_src_ip} | ${test_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table L3 | ${dut1_node}
| | ... | ${ip_version} | src
| | And Vpp Configures Classify Session L3
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${ip_version} | src | ${test_src_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send packet from Port to Port should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${non_drop_src_ip} | ${test_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}

| VPP drops packets based on IPv4 destination addresses
| | [Documentation] | Create classify table on VPP, add destination IP address
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${non_drop_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${test_src_ip} | ${non_drop_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table L3 | ${dut1_node}
| | ... | ${ip_version} | dst
| | And Vpp Configures Classify Session L3
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${ip_version} | dst | ${test_dst_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send packet from Port to Port should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${test_src_ip} | ${non_drop_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}

| VPP drops packets based on IPv4 src-addr and dst-addr
| | [Documentation] | Create classify table on VPP, add source and destination
| | ...             | IP address of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${non_drop_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${non_drop_src_ip} | ${non_drop_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | ${table_index_1} | ${skip_n_1} | ${match_n_1}=
| | ... | When Vpp Creates Classify Table L3 | ${dut1_node}
| | ... | ${ip_version} | src
| | ${table_index_2} | ${skip_n_2} | ${match_n_2}=
| | ... | And Vpp Creates Classify Table L3 | ${dut1_node} | ${ip_version} | dst
| | And Vpp Configures Classify Session L3
| | ... | ${dut1_node} | deny | ${table_index_1} | ${skip_n_1} | ${match_n_2}
| | ... | ${ip_version} | src | ${test_src_ip}
| | And Vpp Configures Classify Session L3
| | ... | ${dut1_node} | deny | ${table_index_2} | ${skip_n_2} | ${match_n_2}
| | ... | ${ip_version} | dst | ${test_dst_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index_1}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index_2}
| | Then Send packet from Port to Port should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${non_drop_src_ip} | ${non_drop_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}

| VPP drops packets based on IPv4 protocol (TCP)
| | [Documentation] | Create classify table on VPP, add mask for TCP port
| | ...             | into table and setup 'deny' traffic
| | ...             | and check if TCP traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex
| | ... | ${dut1_node} | 0000000000000000000000000000000000000000000000FF
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | 000000000000000000000000000000000000000000000006
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20

| VPP drops packets based on IPv4 protocol (UDP)
| | [Documentation] | Create classify table on VPP, add mask for UDP port
| | ...             | into table and setup 'deny' traffic
| | ...             | and check if UDP traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex
| | ... | ${dut1_node} | 0000000000000000000000000000000000000000000000FF
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | 000000000000000000000000000000000000000000000011
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20

| VPP drops packets based on IPv4 TCP src ports
| | [Documentation] | Create classify table on VPP, add source TCP port
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 110 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | ${hex_mask}= | Compute Classify Hex Mask | ${ip_version} | TCP | source
| | ${hex_value}= | Compute Classify Hex Value | ${hex_mask} | 80 | 0
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex | ${dut1_node} | ${hex_mask}
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${hex_value}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 110 | 20

| VPP drops packets based on IPv4 TCP dst ports
| | [Documentation] | Create classify table on VPP, add destination TCP port
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 20 | 110
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 20 | 80
| | ${hex_mask}= | Compute Classify Hex Mask | ${ip_version} | TCP | destination
| | ${hex_value}= | Compute Classify Hex Value | ${hex_mask} | 0 | 80
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex | ${dut1_node} | ${hex_mask}
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${hex_value}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 20 | 80
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 20 | 110

| VPP drops packets based on IPv4 TCP src + dst ports
| | [Documentation] | Create classify table on VPP, add source and destination
| | ...             | TCP port of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 110 | 25
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | ${hex_mask}= | Compute Classify Hex Mask | ${ip_version} | TCP
| | ...                                      | source + destination
| | ${hex_value}= | Compute Classify Hex Value | ${hex_mask} | 80 | 20
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex | ${dut1_node} | ${hex_mask}
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${hex_value}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 110 | 25

| VPP drops packets based on IPv4 UDP src ports
| | [Documentation] | Create classify table on VPP, add source UDP port
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 110 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | ${hex_mask}= | Compute Classify Hex Mask | ${ip_version} | UDP | source
| | ${hex_value}= | Compute Classify Hex Value | ${hex_mask} | 80 | 0
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex | ${dut1_node} | ${hex_mask}
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${hex_value}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 110 | 20

| VPP drops packets based on IPv4 UDP dst ports
| | [Documentation] | Create classify table on VPP, add destination UDP port
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 20 | 110
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 20 | 80
| | ${hex_mask}= | Compute Classify Hex Mask | ${ip_version} | UDP | destination
| | ${hex_value}= | Compute Classify Hex Value | ${hex_mask} | 0 | 80
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex | ${dut1_node} | ${hex_mask}
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${hex_value}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 20 | 80
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 20 | 110

| VPP drops packets based on IPv4 UDP src + dst ports
| | [Documentation] | Create classify table on VPP, add source and destination
| | ...             | UDP port of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 110 | 25
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | ${hex_mask}= | Compute Classify Hex Mask | ${ip_version} | UDP
| | ...                                      | source + destination
| | ${hex_value}= | Compute Classify Hex Value | ${hex_mask} | 80 | 20
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex | ${dut1_node} | ${hex_mask}
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | ${hex_value}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | And Send TCP or UDP packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 110 | 25

| VPP drops packets based on MAC src addr
| | [Documentation] | Create classify table on VPP, add source MAC address
| | ...             | of traffic into table and setup 'deny' traffic
| | ...             | and check if traffic is dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table L2 | ${dut1_node} | src
| | And Vpp Configures Classify Session L2
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | src | ${tg_to_dut1_mac}
| | Then Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${l2_table} | ${table_index}
| | And Send packet from Port to Port should failed | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
