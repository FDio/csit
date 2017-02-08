# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.honeycomb.Routing.RoutingKeywords
| Library | resources.libraries.python.Trace.Trace
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/routing.robot
| Suite Setup | Vpp nodes ra suppress link layer | ${nodes}
| Test Setup | Clear Packet Trace on All DUTs | ${nodes}
| Suite Teardown | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Documentation | *Honeycomb routing test suite.*
| Force Tags | Honeycomb_sanity | honeycomb_test

*** Test Cases ***
| TC01: Single hop IPv4 route
| | [Teardown] | Honeycomb routing test teardown | ${node} | table1
| | Given Setup interfaces and neighbors for IPv4 routing test
| | When Honeycomb configures routing table
| | ... | ${node} | table1 | ipv4 | ${table1} | ${1}
| | Then Routing data from Honeycomb should contain
| | ... | ${node} | table1 | ipv4 | ${table1_oper}
| | And Verify Route IPv4 | ${nodes['TG']}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}

| TC02: Multi hop IPv4 route
| | [Teardown] | Honeycomb routing test teardown | ${node} | table2
| | Given Setup interfaces and neighbors for IPv4 routing test
| | And Honeycomb adds interface ipv4 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${next_hop1} | ${next_hop_mac1}
| | And Honeycomb adds interface ipv4 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${next_hop2} | ${next_hop_mac2}
| | When Honeycomb configures routing table
| | ... | ${node} | table2 | ipv4 | ${table2} | ${1}
| | Then Routing data from Honeycomb should contain
| | ... | ${node} | table2 | ipv4 | ${table2_oper}
| | And Verify multipath Route | ${nodes['TG']}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${dut_to_tg_if2_mac} | ${next_hop_mac1} | ${next_hop_mac2}

| TC03: Special hop - blackhole IPv4 route
| | [Teardown] | Honeycomb routing test teardown | ${node} | table3
| | Given Setup interfaces and neighbors for IPv4 routing test
| | When Honeycomb configures routing table
| | ... | ${node} | table3 | ipv4 | ${table3} | ${1} | special=${TRUE}
| | Then Routing data from Honeycomb should contain
| | ... | ${node} | table3 | ipv4 | ${table3_oper}
| | And Run keyword and Expect Error | ICMP echo Rx timeout
| | ... | Verify Route IPv4 | ${nodes['TG']}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}

| TC04: Single hop IPv6 route
| | [Teardown] | Honeycomb routing test teardown | ${node} | table4
| | Given Setup interfaces and neighbors for IPv6 routing test
| | When Honeycomb configures routing table
| | ... | ${node} | table4 | ipv6 | ${table4} | ${1}
| | Then Routing data from Honeycomb should contain
| | ... | ${node} | table4 | ipv6 | ${table4_oper}
| | And Verify Route IPv6 | ${nodes['TG']}
| | ... | ${src_ip} | ${next_hop}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}

| TC05: Multi hop IPv6 route
| | [Teardown] | Honeycomb routing test teardown | ${node} | table5
| | Given Setup interfaces and neighbors for IPv6 routing test
| | And Honeycomb adds interface ipv6 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${next_hop1} | ${next_hop_mac1}
| | And Honeycomb adds interface ipv6 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${next_hop2} | ${next_hop_mac2}
| | When Honeycomb configures routing table
| | ... | ${node} | table5 | ipv6 | ${table5} | ${1}
| | Then Routing data from Honeycomb should contain
| | ... | ${node} | table5 | ipv6 | ${table5_oper}
| | And Verify multipath Route | ${nodes['TG']}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${dut_to_tg_if2_mac} | ${next_hop_mac1} | ${next_hop_mac2}

| TC06: Special hop - blackhole IPv6 route
| | [Teardown] | Honeycomb routing test teardown | ${node} | table6
| | Given Setup interfaces and neighbors for IPv6 routing test
| | When Honeycomb configures routing table
| | ... | ${node} | table6 | ipv6 | ${table6} | ${1} | special=${TRUE}
| | Then Routing data from Honeycomb should contain
| | ... | ${node} | table6 | ipv6 | ${table6_oper}
| | And Run keyword and Expect Error | ICMP echo Rx timeout
| | ... | Verify Route IPv6 | ${nodes['TG']}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}

*** Keywords ***
| Setup interfaces and neighbors for IPv4 routing test
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Import Variables | resources/test_data/honeycomb/routing.py
| | ... | ${nodes['DUT1']} | ipv4 | ${dut_to_tg_if2}
| | Honeycomb sets interface vrf ID
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${1} | ipv4
| | Honeycomb sets interface vrf ID
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${1} | ipv4
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_len}
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_len}
| | Honeycomb adds interface ipv4 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_ip} | ${tg_to_dut_if1_mac}
| | Honeycomb adds interface ipv4 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${next_hop} | ${tg_to_dut_if2_mac}

| Setup interfaces and neighbors for IPv6 routing test
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Import Variables | resources/test_data/honeycomb/routing.py
| | ... | ${nodes['DUT1']} | ipv6 | ${dut_to_tg_if2}
| | Honeycomb sets interface vrf ID
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${1} | ipv6
| | Honeycomb sets interface vrf ID
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${1} | ipv6
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb sets interface ipv6 address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_len}
| | Honeycomb sets interface ipv6 address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_len}
| | Honeycomb adds interface ipv6 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_ip} | ${tg_to_dut_if1_mac}
| | Honeycomb adds interface ipv6 neighbor | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${next_hop} | ${tg_to_dut_if2_mac}

| Honeycomb routing test teardown
| | [arguments] | ${node} | ${routing_table}
| | Show Packet Trace on All DUTs | ${nodes}
| | Log routing configuration from VAT | ${node}
| | Honeycomb removes routing configuration | ${node} | ${routing_table}
