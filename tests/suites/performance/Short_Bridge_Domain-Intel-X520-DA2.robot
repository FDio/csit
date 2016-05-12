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
| Library | resources.libraries.python.NodePath
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_SHORT
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L2 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keyword | Show statistics on all DUTs
| Documentation | Minimal throughput acceptance test cases

*** Test Cases ***
| 1core VPP passes 64B frames through bridge domain at 2x 3.2Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 64B frames through bridge domain
| | ... | at 2x 3.2Mpps in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 3.2mpps
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 1core VPP passes 1518B frames through bridge domain at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 1518B frames through bridge domain
| | ... | at 2x 812,743pps (2x 10Gbps) in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 1core VPP passes 9000B frames through bridge domain at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 9000B frames through bridge domain
| | ... | at 2x 138,580pps (2x 10Gbps) in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 2core VPP with rss 1 passes 64B frames through bridge domain at 2x 6.9Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 64B frames through bridge domain
| | ... | at 2x 6.9Mpps in 3-node topology
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 6.9mpps
| | Given Setup '2' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 2core VPP with rss 1 passes 1518B frames through bridge domain at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 1518B frames through bridge domain
| | ... | at 2x 812,743pps (2x 10Gbps) in 3-node topology
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Setup '2' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 2core VPP with rss 1 passes 9000B frames through bridge domain at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 9000B frames through bridge domain
| | ... | at 2x 138,580pps (2x 10Gbps) in 3-node topology
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Setup '2' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 4core VPP with rss 2 passes 64B frames through bridge domain at 2x 7.4Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rss 2 should pass 64B frames through bridge
| | ... | domain at 2x7.4Mpps in 3-node topology
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 7.4mpps
| | Given Setup '4' worker threads and rss '2' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 4core VPP with rss 2 passes 1518B frames through bridge domain at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rss 2 should pass 1518B frames through bridge
| | ... | domain at 2x 812,743pps (2x 10Gbps) in 3-node topology
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Setup '4' worker threads and rss '2' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 4core VPP with rss 2 passes 9000B frames through bridge domain at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rss 2should pass 9000B frames through bridge
| | ... | domain at 2x 138,580pps (2x 10Gbps) in 3-node topology
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Setup '4' worker threads and rss '2' without HTT on all DUTs
| | AND   L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge
