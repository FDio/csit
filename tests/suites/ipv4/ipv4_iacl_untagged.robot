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
| Resource | resources/libraries/robot/l2_traffic.robot
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Show packet trace on all DUTs | ${nodes}
| ...           | AND          | Vpp Show Errors | ${nodes['DUT1']}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *IPv4 routing with ingress ACL test cases*
| ...
| ... | Encapsulations: Eth-IPv4 on links TG-DUT1, TG-DUT2, DUT1-DUT2. IPv4
| ... | ingress ACL (iACL) tests use 3-node topology TG - DUT1 - DUT2 - TG with
| ... | one link between the nodes. DUT1 and DUT2 are configured with IPv4
| ... | routing and static routes. DUT1 is configured with iACL on link to TG,
| ... | iACL classification and permit/deny action are configured on a per test
| ... | case basis. Test ICMPv4 Echo Request packets are sent in one direction
| ... | by TG on link to DUT1 and received on TG link to DUT2. On receive TG
| ... | verifies if packets are dropped, or if received verifies packet IPv4
| ... | src-addr, dst-addr and MAC addresses.

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
| TC01: DUT with iACL IPv4 src-addr drops matching pkts
| | [Documentation]
| | ... | On DUT1 add source IPv4 address to classify table with 'deny'.\
| | ... | Make TG verify matching packets are dropped.
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

| TC02: DUT with iACL IPv4 dst-addr drops matching pkts
| | [Documentation]
| | ... | On DUT1 add destination IPv4 address to classify table with 'deny'.\
| | ... | Make TG verify matching packets are dropped.
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

| TC03: DUT with iACL IPv4 src-addr and dst-addr drops matching pkts
| | [Documentation]
| | ... | On DUT1 add source and destination IPv4 addresses to classify table\
| | ... | with 'deny'. Make TG verify matching packets are dropped.
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

| TC04: DUT with iACL IPv4 protocol set to TCP drops matching pkts
| | [Documentation]
| | ... | On DUT1 add protocol mask and TCP protocol (0x06) to classify table\
| | ... | with 'deny'. Make TG verify matching packets are dropped.
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

| TC05: DUT with iACL IPv4 protocol set to UDP drops matching pkts
| | [Documentation]
| | ... | On DUT1 add protocol mask and UDP protocol (0x11) to classify table\
| | ... | with 'deny'. Make TG verify matching packets are dropped.
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

| TC06: DUT with iACL IPv4 TCP src-ports drops matching pkts
| | [Documentation]
| | ... | On DUT1 add TCP source ports to classify table with 'deny'.\
| | ... | Make TG verify matching packets are dropped.
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

| TC07: DUT with iACL IPv4 TCP dst-ports drops matching pkts
| | [Documentation]
| | ... | On DUT1 add TCP destination ports to classify table with 'deny'.\
| | ... | Make TG verify matching packets are dropped.
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

| TC08: DUT with iACL IPv4 TCP src-ports and dst-ports drops matching pkts
| | [Documentation]
| | ... | On DUT1 add TCP source and destination ports to classify table\
| | ... | with 'deny'. Make TG verify matching packets are dropped.
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

| TC09: DUT with iACL IPv4 UDP src-ports drops matching pkts
| | [Documentation]
| | ... | On DUT1 add UDP source ports to classify table with 'deny'.\
| | ... | Make TG verify matching packets are dropped.
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

| TC10: DUT with iACL IPv4 UDP dst-ports drops matching pkts
| | [Documentation]
| | ... | On DUT1 add TCP destination ports to classify table with 'deny'.\
| | ... | Make TG verify matching packets are dropped.
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

| TC11: DUT with iACL IPv4 UDP src-ports and dst-ports drops matching pkts
| | [Documentation]
| | ... | On DUT1 add UDP source and destination ports to classify table\
| | ... | with 'deny'. Make TG verify matching packets are dropped.
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

| TC12: DUT with iACL MAC src-addr drops matching pkts
| | [Documentation]
| | ... | On DUT1 add source MAC address to classify table with 'deny'.\
| | ... | Make TG verify matching packets are dropped.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And L2 setup xconnect on DUT
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_tg}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send and receive ICMP Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table L2 | ${dut1_node} | src
| | And Vpp Configures Classify Session L2
| | ... | ${dut1_node} | deny | ${table_index} | ${skip_n} | ${match_n}
| | ... | src | ${tg_to_dut1_mac}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${l2_table} | ${table_index}
| | Then Send and receive ICMP Packet should failed
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
