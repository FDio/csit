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
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Show packet trace on all DUTs | ${nodes}
| ...           | AND          | Vpp Show Errors | ${nodes['DUT1']}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *Source RPF check on IPv4 test cases*
| ...
| ... | *[Top] Network Topologies:* TG - DUT1 - DUT2 - TG
| ... |        with one link between the nodes.
| ... | *[Cfg] DUT configuration:* DUT2 is configured with L2 Cross connect.
| ... |        DUT1 is configured with IP source check on link to TG,
| ... | *[Ver] TG verification:*Test ICMP Echo Request packets are sent
| ... |        in one direction by TG on link to DUT1 and received on TG link
| ... |        to DUT2. On receive TG verifies if packets which source address
| ... |        is not in routes are dropped.

*** Variables ***
| ${dut1_to_tg_ip}= | 192.168.1.1
| ${dut1_to_tg_ip_GW}= | 192.168.1.2
| ${dut1_to_dut2_ip}= | 192.168.2.1
| ${dut1_to_dut2_ip_GW}= | 192.168.2.2
| ${test_dst_ip}= | 32.0.0.1
| ${pass_test_src_ip}= | 16.0.0.1
| ${drop_test_src_ip}= | 24.0.0.1
| ${prefix_length}= | 24

*** Test Cases ***
| TC01: VPP source RPF check on IPv4 src-addr
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG
| | ... | [Cfg] On DUT1 setup IP source check.
| | ... | [Ver] Make TG verify matching packets which source address
| | ... | is not in routes are dropped.
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
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2} | resolve_attempts=${NONE}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip_GW}
| | ... | ${tg_to_dut1_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${pass_test_src_ip} | ${prefix_length}
| | ... | ${dut1_to_tg_ip_GW} | ${dut1_to_tg} | resolve_attempts=${NONE}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${pass_test_src_ip} | ${test_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${drop_test_src_ip} | ${test_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | ${dut1_to_tg_name}= | Get Interface Name | ${dut1_node} | ${dut1_to_tg}
| | When VPP IP Source Check Setup | ${dut1_node} | ${dut1_to_tg_name}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${pass_test_src_ip} | ${test_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${dut1_to_tg_ip_GW} | ${test_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}
| | And Send packet from Port to Port should failed | ${tg_node}
| | ... | ${drop_test_src_ip} | ${test_dst_ip} | ${tg_to_dut1}
| | ... | ${tg_to_dut1_mac} | ${dut1_to_tg_mac} | ${tg_to_dut2}
| | ... | ${dut1_to_dut2_mac} | ${tg_to_dut2_mac}

| TC02: VPP pass traffic on non-enabled RPF interface
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG
| | ... | [Cfg] On DUT1 setup IP source check.
| | ... | [Ver] Make TG verify matching packets on non-enabled RPF interface
| | ... | are passed.
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
| | ... | ${dut1_to_dut2_ip_GW} | ${dut1_to_dut2} | resolve_attempts=${NONE}
| | And Add Arp On Dut
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip_GW}
| | ... | ${tg_to_dut1_mac}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${pass_test_src_ip} | ${prefix_length}
| | ... | ${dut1_to_tg_ip_GW} | ${dut1_to_tg} | resolve_attempts=${NONE}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | ${dut1_to_tg_name}= | Get Interface Name | ${dut1_node} | ${dut1_to_tg}
| | When VPP IP Source Check Setup | ${dut1_node} | ${dut1_to_tg_name}
| | Then Send Packet And Check Headers | ${tg_node}
| | ... | ${test_dst_ip} | ${pass_test_src_ip} | ${tg_to_dut2}
| | ... | ${tg_to_dut2_mac} | ${dut1_to_dut2_mac} | ${tg_to_dut1}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
| | And Send Packet And Check Headers | ${tg_node}
| | ... | ${test_dst_ip} | ${dut1_to_tg_ip_GW} | ${tg_to_dut2}
| | ... | ${tg_to_dut2_mac} | ${dut1_to_dut2_mac} | ${tg_to_dut1}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
