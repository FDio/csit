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
| Resource | resources/libraries/robot/performance.robot
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']} | WITH NAME | dut1_v4
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT2']} | WITH NAME | dut2_v4
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_SHORT
| Suite Setup | 3-node Performance Suite Setup | L3
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Show statistics on all DUTs
| ...           | AND          | Reset startup configuration of VPP on all DUTs
| Documentation | Minimal throughput acceptance test suite

*** Test Cases ***
| 1core VPP passes 64B frames through IPv4 forwarding at 3.5mpps in 3-node topology
| | [Documentation] | 1core VPP should pass 64B frames through IPv4
| | ...             | forwarding at 3.5mpps in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 3.5mpps
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 1core VPP passes 1518B frames through IPv4 forwarding at 10gbps in 3-node topology
| | [Documentation] | 1core VPP should pass 1518B frames through IPv4
| | ...             | forwarding at 10gbps in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 10gbps
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 1core VPP passes 9000B frames through IPv4 forwarding at 10gbps in 3-node topology
| | [Documentation] | 1core VPP should pass 9000B frames through IPv4
| | ...             | forwarding at 10gbps in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 10gbps
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 2core VPP with rss 1 passes 64B frames through IPv4 forwarding at 8.3mpps in 3-node topology
| | [Documentation] | 2core VPP with rss 1 should pass 64B frames through
| | ...             | IPv4 forwarding at 8.3mpps in 3-node topology
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 8.3mpps
| | Given Setup '2' worker threads and rss '1' without HTT on all DUTs
| | AND   IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 4core VPP with rss 2 passes 64B frames through IPv4 forwarding at 9.2mpps in 3-node topology
| | [Documentation] | 4core VPP with rss 2 should pass 64B frames through
| | ...             | IPv4 forwarding at 9.0mpps in 3-node topology
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 9.0mpps
| | Given Setup '2' worker threads and rss '1' without HTT on all DUTs
| | AND   IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4
