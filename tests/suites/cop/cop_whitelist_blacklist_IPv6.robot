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
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Variables  | resources/libraries/python/IPv6NodesAddr.py | ${nodes}
| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
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
| ... | MAC addresses are checked.

*** Variables ***
| ${tg_node}= | ${nodes['TG']}
| ${dut1_node}= | ${nodes['DUT1']}
| ${dut2_node}= | ${nodes['DUT2']}

| ${dut1_if1_ip}= | 3ffe:62::1
| ${dut1_if2_ip}= | 3ffe:63::1
| ${dut1_if1_ip_GW}= | 3ffe:62::2
| ${dut1_if2_ip_GW}= | 3ffe:63::2

| ${dut2_if1_ip}= | 3ffe:72::1
| ${dut2_if2_ip}= | 3ffe:73::1

| ${test_dst_ip}= | 3ffe:64::1
| ${test_src_ip}= | 3ffe:61::1

| ${cop_dut_ip}= | 3ffe:61::

| ${ip_prefix}= | 64

| ${nodes_ipv6_addresses}= | ${nodes_ipv6_addr}

| ${fib_table_number}= | 1

*** Test Cases ***
| VPP permits packets based on IPv6 src addr
| | [Documentation] | COP Whitelist test with basic setup.
| | Given Path for 3-node testing is set
| | ... | ${tg_node} | ${dut1_node} | ${dut2_node} | ${tg_node}
| | And Interfaces in 3-node path are up
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | And VPP Set IF IPv6 Addr
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_if1_ip} | ${ip_prefix}
| | And VPP Set IF IPv6 Addr
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_if2_ip} | ${ip_prefix}
| | And VPP Set IF IPv6 Addr
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_if1_ip} | ${ip_prefix}
| | And VPP Set IF IPv6 Addr
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_if2_ip} | ${ip_prefix}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_if1_ip_GW} | ${tg_if1_mac}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | And Vpp Route Add | ${dut1_node}
| | ... | ${test_dst_ip} | ${ip_prefix} | ${dut1_if2_ip_GW} | ${dut1_to_dut2}
| | And Vpp All Ra Suppress Link Layer | ${nodes}
| | And Add fib table | ${dut1_node} | ${cop_dut_ip} | ${ip_prefix} |
| | ... | ${fib_table_number} | local
| | When COP Add whitelist Entry | ${dut1_node} | ${dut1_to_tg} | ip6 |
| | ... | ${fib_table_number}
| | And COP interface enable or disable | ${dut1_node} | ${dut1_to_tg} | enable
| | Then Send Packet And Check Headers | ${tg_node} |
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} |
| | ... | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}


| VPP drops packets based on IPv6 src addr
| | [Documentation] | COP blacklist test with basic setup.
| | Given Path for 3-node testing is set
| | ... | ${tg_node} | ${dut1_node} | ${dut2_node} | ${tg_node}
| | And Interfaces in 3-node path are up
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | And VPP Set IF IPv6 Addr
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_if1_ip} | ${ip_prefix}
| | And VPP Set IF IPv6 Addr
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_if2_ip} | ${ip_prefix}
| | And VPP Set IF IPv6 Addr
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_if1_ip} | ${ip_prefix}
| | And VPP Set IF IPv6 Addr
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_if2_ip} | ${ip_prefix}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_if1_ip_GW} | ${tg_if1_mac}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}
| | And Vpp Route Add | ${dut1_node}
| | ... | ${test_dst_ip} | ${ip_prefix} | ${dut1_if2_ip_GW} | ${dut1_to_dut2}
| | And Vpp All Ra Suppress Link Layer | ${nodes}
| | And Add fib table | ${dut1_node}
| | ... | ${cop_dut_ip} | ${ip_prefix} | ${fib_table_number} | drop
| | When COP Add whitelist Entry
| | ... | ${dut1_node} | ${dut1_to_tg} | ip6 | ${fib_table_number}
| | And COP interface enable or disable | ${dut1_node} | ${dut1_to_tg} | enable
| | Then Send packet from Port to Port should failed | ${tg_node} |
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} |
| | ... | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
