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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/cop.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Variables  | resources/libraries/python/IPv4NodeAddress.py | ${nodes}
| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO | COP
| Suite Setup | Run Keywords | Setup all DUTs before test
| ...         | AND          | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Show packet trace on all DUTs | ${nodes}
| Documentation | *COP Blacklist and Whitelist Tests*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes where DUT2 has xconnect.
| ... | Test packets are sent only in one direction with COP set either as
| ... | whitelist or blacklist. Subsequently, packet's IP src/dst and
| ... | mac addresses are checked.

*** Variables ***
| ${TG}= | ${nodes['TG']}
| ${DUT1}= | ${nodes['DUT1']}
| ${DUT2}= | ${nodes['DUT2']}

| ${dut1_if1_ip}= | 192.168.1.1
| ${dut1_if2_ip}= | 192.168.2.1
| ${dut1_if1_ip_GW}= | 192.168.1.2
| ${dut1_if2_ip_GW}= | 192.168.2.2

| ${test_dst_ip}= | 32.0.0.1
| ${test_src_ip}= | 16.0.0.1

| ${cop_dut_ip}= | 16.0.0.0

| ${ip_prefix}= | 24
| ${nodes_ipv4_addresses}= | ${nodes_ipv4_addr}

| ${fib_table_number}= | 1

*** Test Cases ***
| VPP permits packets based on IPv4 src addr
| | [Documentation] | Cop Whitelist test with basic setup
| | Given Setup Nodes And Variables | ${TG} | ${DUT1} | ${DUT2}
| | And L2 setup xconnect on DUT | ${DUT2} | ${dut2_if1} | ${dut2_if2}
| | And Set IPv4 Interface Addresses | ${DUT1}
| | And Set ARP on Nodes | ${DUT1}
| | And Vpp Route Add | ${DUT1} | ${test_dst_ip} | ${ip_prefix} |
| | ... | ${dut1_if2_ip_GW} | ${dut1_if2}
| | And Add fib table | ${DUT1} | ${cop_dut_ip} | ${ip_prefix} |
| | ... | ${fib_table_number} | local
| | When Cop Add whitelist Entry | ${DUT1} | ${dut1_if1} | ip4 |
| | ... | ${fib_table_number}
| | And Cop interface enable or disable | ${DUT1} | ${dut1_if1} | enable
| | Then Send Packet And Check Headers |
| | ... | ${TG} | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} |
| | ... | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}


| VPP drops packets based on IPv4 src addr
| | [Documentation] | Cop blacklist test with basic setup
| | Given Setup Nodes And Variables | ${TG} | ${DUT1} | ${DUT2}
| | And L2 setup xconnect on DUT | ${DUT2} | ${dut2_if1} | ${dut2_if2}
| | And Set IPv4 Interface Addresses | ${DUT1}
| | And Set ARP on Nodes | ${DUT1}
| | And Vpp Route Add | ${DUT1} | ${test_dst_ip} | ${ip_prefix} |
| | ... | ${dut1_if2_ip_GW} | ${dut1_if2}
| | And Add fib table | ${DUT1} | ${cop_dut_ip} | ${ip_prefix} |
| | ... | ${fib_table_number} | drop
| | When Cop Add whitelist Entry | ${DUT1} | ${dut1_if1} | ip4 |
| | ... | ${fib_table_number}
| | And Cop interface enable or disable | ${DUT1} | ${dut1_if1} | enable
| | Then Send packet from Port to Port should failed |
| | ... | ${TG} | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} |
| | ... | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
