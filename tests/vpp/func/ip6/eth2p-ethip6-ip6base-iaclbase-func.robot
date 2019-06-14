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
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.Trace
| ...
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/l2/l2_xconnect.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| ...
| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO | SKIP_VPP_PATCH
| ...
| Test Setup | Set up functional test
| ...
| Test Teardown | Tear down functional test
| ...
| Documentation | *IPv6 routing with ingress ACL test cases*
| ...
| ... | Encapsulations: Eth-IPv6 on links TG-DUT1, TG-DUT2, DUT1-DUT2. IPv6
| ... | ingress ACL (iACL) tests use 3-node topology TG - DUT1 - DUT2 - TG with
| ... | one link between the nodes. DUT1 and DUT2 are configured with IPv6
| ... | routing and static routes. DUT1 is configured with iACL on link to TG,
| ... | iACL classification and permit action are configured on a per test
| ... | case basis. Test ICMPv6 Echo Request packets are sent in one direction
| ... | by TG on link to DUT1 and received on TG link to DUT2. On receive TG
| ... | verifies if packets are accepted, or if received verifies packet IPv6
| ... | src-addr, dst-addr and MAC addresses.

*** Variables ***
| ${dut1_to_tg_ip}= | 3ffe:62::1
| ${dut1_to_dut2_ip}= | 3ffe:63::1
| ${dut1_to_dut2_ip_GW}= | 3ffe:63::2
| ${dut2_to_dut1_ip}= | 3ffe:72::1
| ${dut2_to_tg_ip}= | 3ffe:73::1
| ${test_dst_ip}= | 3ffe:64::1
| ${test_src_ip}= | 3ffe:61::1
| ${non_drop_dst_ip}= | 3ffe:54::1
| ${non_drop_src_ip}= | 3ffe:51::1
| ${prefix_length}= | 64
| ${ip_version}= | ip6
| ${l2_table}= | l2

*** Test Cases ***
| TC01: DUT with iACL IPv6 src-addr and dst-addr accepts matching pkts
| | [Documentation]
| | ... | On DUT1 add source and destination IPv6 addresses to classify table\
| | ... | with 'permit'.
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And VPP Interface Set IP Address
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And VPP Interface Set IP Address
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And VPP Add IP Neighbor
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | gateway=${dut1_to_dut2_ip_GW} | interface=${dut1_to_dut2}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${non_drop_dst_ip} | ${prefix_length}
| | ... | gateway=${dut1_to_dut2_ip_GW} | interface=${dut1_to_dut2}
| | And Configure L2XC
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | And Vpp All Ra Suppress Link Layer | ${nodes}
| | Then Send packet and verify headers | ${tg_node}
| | ... | ${non_drop_src_ip} | ${non_drop_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | ${table_index_1} | ${skip_n_1} | ${match_n_1}=
| | ... | When Vpp Creates Classify Table L3 | ${dut1_node}
| | ... | ${ip_version} | src | ${test_src_ip}
| | ${table_index_2} | ${skip_n_2} | ${match_n_2}=
| | ... | And Vpp Creates Classify Table L3 | ${dut1_node} | ${ip_version}
| | ... | dst | ${test_dst_ip}
| | And Vpp Configures Classify Session L3
| | ... | ${dut1_node} | permit | ${table_index_1}
| | ... | ${ip_version} | src | ${test_src_ip}
| | And Vpp Configures Classify Session L3
| | ... | ${dut1_node} | permit | ${table_index_2}
| | ... | ${ip_version} | dst | ${test_dst_ip}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index_1}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index_2}
| | Then Send packet and verify headers | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers | ${tg_node}
| | ... | ${non_drop_src_ip} | ${non_drop_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}

| TC02: DUT with iACL IPv6 TCP src-ports and dst-ports accepts matching pkts
| | [Documentation]
| | ... | On DUT1 add TCP source and destination ports to classify table\
| | ... | with 'permit'.
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And VPP Interface Set IP Address
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And VPP Interface Set IP Address
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip}
| | ... | ${prefix_length}
| | And VPP Add IP Neighbor
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | gateway=${dut1_to_dut2_ip_GW} | interface=${dut1_to_dut2}
| | And Configure L2XC
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | And Vpp All Ra Suppress Link Layer | ${nodes}
| | Then Send TCP or UDP packet and verify received packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 110 | 25
| | And Send TCP or UDP packet and verify received packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | ${hex_mask}= | Compute Classify Hex Mask | ${ip_version} | TCP
| | ... | source + destination
| | ${hex_value}= | Compute Classify Hex Value | ${hex_mask} | 80 | 20
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex | ${dut1_node} | ${hex_mask}
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | permit | ${table_index} | ${hex_value}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet and verify received packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 80 | 20
| | And Send TCP or UDP packet and verify received packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | TCP | 110 | 25

| TC03: DUT with iACL IPv6 UDP src-ports and dst-ports accepts matching pkts
| | [Documentation]
| | ... | On DUT1 add UDP source and destination ports to classify table\
| | ... | with 'permit'.
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And VPP Interface Set IP Address
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And VPP Interface Set IP Address
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip}
| | ... | ${prefix_length}
| | And VPP Add IP Neighbor
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip_GW}
| | ... | ${tg_to_dut2_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | gateway=${dut1_to_dut2_ip_GW} | interface=${dut1_to_dut2}
| | And Configure L2XC
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | And Vpp All Ra Suppress Link Layer | ${nodes}
| | Then Send TCP or UDP packet and verify received packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 110 | 25
| | And Send TCP or UDP packet and verify received packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | ${hex_mask}= | Compute Classify Hex Mask | ${ip_version} | UDP
| | ... | source + destination
| | ${hex_value}= | Compute Classify Hex Value | ${hex_mask} | 80 | 20
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | When Vpp Creates Classify Table Hex | ${dut1_node} | ${hex_mask}
| | And Vpp Configures Classify Session Hex
| | ... | ${dut1_node} | permit | ${table_index} | ${hex_value}
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1_node} | ${dut1_to_tg} | ${ip_version} | ${table_index}
| | Then Send TCP or UDP packet and verify received packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 80 | 20
| | And Send TCP or UDP packet and verify received packet | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1} | ${tg_to_dut1_mac}
| | ... | ${tg_to_dut2} | ${dut1_to_tg_mac} | UDP | 110 | 25
