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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/l2/l2_xconnect.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Library | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *IPv4 ARP test cases*
| ...
| ... | RFC826 ARP: Eth-IPv4 and Eth-ARP on links TG-DUT1, TG-DUT2, DUT1-DUT2:
| ... | IPv4 ARP tests use 3-node topology TG - DUT1 - DUT2 - TG with one link
| ... | between the nodes. DUT1 and DUT2 are configured with IPv4 routing and
| ... | static routes. DUT ARP functionality is tested by making TG send ICMPv4
| ... | Echo Requests towards its other interface via DUT1 and DUT2.

*** Variables ***
| ${dut1_to_tg_ip}= | 192.168.1.1
| ${dut1_to_dut2_ip}= | 192.168.2.1
| ${dut1_to_dut2_ip_GW}= | 192.168.2.2
| ${test_dst_ip}= | 32.0.0.1
| ${test_src_ip}= | 16.0.0.1
| ${prefix_length}= | 24

*** Test Cases ***
| TC01: DUT sends ARP Request for unresolved locally connected IPv4 address
| | [Documentation]
| | ... | Make TG send test packet destined to IPv4 address of its other\
| | ... | interface connected to DUT2. Make TG verify DUT2 sends ARP
| | ... | Request for locally connected TG IPv4 address.
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Configure L2XC
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | Then Send packet and verify ARP request | ${tg_node}
| | ... | ${test_src_ip} | ${dut1_to_dut2_ip_GW} | ${tg_to_dut1}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2} | ${dut1_to_dut2_mac}
| | ... | ${dut1_to_dut2_ip} | ${dut1_to_dut2_ip_GW}

| TC02: DUT sends ARP Request for route next hop IPv4 address
| | [Documentation] |
| | ... | Make TG send test packet destined to IPv4 address matching\
| | ... | static route on DUT2. Make TG verify DUT2 sends ARP Request for
| | ... | next hop of the static route.
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Configure L2XC
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix_length}
| | And Vpp Route Add
| | ... | ${dut1_node} | ${test_dst_ip} | ${prefix_length}
| | ... | gateway=${dut1_to_dut2_ip_GW} | interface=${dut1_to_dut2}
| | ... | resolve_attempts=${NONE}
| | Then Send packet and verify ARP request | ${tg_node}
| | ... | ${test_src_ip} | ${test_dst_ip} | ${tg_to_dut1}
| | ... | ${dut1_to_tg_mac} | ${tg_to_dut2} | ${dut1_to_dut2_mac}
| | ... | ${dut1_to_dut2_ip} | ${dut1_to_dut2_ip_GW}
