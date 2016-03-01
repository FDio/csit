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
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/performance.robot
| Resource | resources/libraries/robot/counters.robot
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']} | WITH NAME | dut1_v4
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT2']} | WITH NAME | dut2_v4
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| Suite Setup | 3-node Performance Suite Setup
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown  | Run Keyword If Test Failed | Show statistics on all DUTs

*** Test Cases ***
| 2core VPP passes 64B frames through IPv4 forwarding at 3.5mpps in 3-node topology
| | Given IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 3.5mpps | 64 | 3-node-IPv4

| 2core VPP passes 1518B frames through IPv4 forwarding at 10gbps in 3-node topology
| | Given IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 10gbps | 1518 | 3-node-IPv4

| 2core VPP passes 9000B frames through IPv4 forwarding at 10gbps in 3-node topology
| | Given IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 10gbps | 9000 | 3-node-IPv4

*** Keywords ***

| 3-node Performance Suite Setup
| | 3-node circular Topology Variables Setup
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ...                          | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | ...                          | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | ...                          | L3

| 3-node Performance Suite Teardown
| | Teardown traffic generator | ${tg}

| IPv4 forwarding initialized in a 3-node circular topology
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if1_mac}= | Get Interface MAC | ${dut1} | ${dut1_if1}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut1_if1}
| | ${dut2_if2_mac}= | Get Interface MAC | ${dut2} | ${dut1_if2}
| | dut1_v4.set_arp | ${dut1_if1} | 10.10.10.2 | ${tg1_if1_mac}
| | dut1_v4.set_arp | ${dut1_if2} | 1.1.1.2 | ${dut2_if1_mac}
| | dut2_v4.set_arp | ${dut2_if1} | 1.1.1.1 | ${dut1_if2_mac}
| | dut2_v4.set_arp | ${dut2_if2} | 20.20.20.2 | ${tg1_if2_mac}
| | dut1_v4.set_ip | ${dut1_if1} | 10.10.10.1 | 24
| | dut1_v4.set_ip | ${dut1_if2} | 1.1.1.1 | 30
| | dut2_v4.set_ip | ${dut2_if1} | 1.1.1.2 | 30
| | dut2_v4.set_ip | ${dut2_if2} | 20.20.20.1 | 24
| | dut1_v4.set_route | 20.20.20.0 | 24 | 1.1.1.2 | ${dut1_if2}
| | dut2_v4.set_route | 10.10.10.0 | 24 | 1.1.1.1 | ${dut2_if1}

| Traffic should pass with no loss
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | Send traffic on | ${nodes} | ${duration}
| | ...             | ${rate} | ${framesize} | ${topology_type}
| | No traffic loss occured

| Show statistics on all DUTs
| | Sleep | 10 | Waiting for statistics to be collected
| | Vpp show stats | ${dut1}
| | Vpp show stats | ${dut2}
