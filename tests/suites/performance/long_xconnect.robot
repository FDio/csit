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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_LONG
| Suite Setup | 3-node Performance Suite Setup | L2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Show statistics on all DUTs
| ...           | AND          | Reset startup configuration of VPP on all DUTs
| Documentation | Throughput search suite (long running test suite based on RFC2544).

*** Test Cases ***
| Find NDR by using linear search and 64B frames through L2 cross connect in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | # Variables
| | ${framesize}= | Set Variable | 64
| | ${start_rate}= | Set Variable | 4800000
| | ${step_rate}= | Set Variable | 100000
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | 14880952
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 xconnect initialized in a 3-node circular topology
| | # Linear search
| | Then Find NDR using linear search and pps | ${framesize} | ${start_rate}
| | ...                                       | ${step_rate} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}


| Find NDR by using linear search and 1518B frames through L2 cross connect in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | # Variables
| | ${framesize}= | Set Variable | 1518
| | ${start_rate}= | Set Variable | 812743
| | ${step_rate}= | Set Variable | 10000
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | 812743
| | # VPP setup
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 xconnect initialized in a 3-node circular topology
| | # Linear search
| | Then Find NDR using linear search and pps | ${framesize} | ${start_rate}
| | ...                                       | ${step_rate} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}

| Find NDR by using linear search and 9000B frames through L2 cross connect in 3-node topology
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD
| | # Variables
| | ${framesize}= | Set Variable | 9000
| | ${start_rate}= | Set Variable | 138580
| | ${step_rate}= | Set Variable | 5000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | 138580
| | # VPP setup
| | Given Setup '1' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 xconnect initialized in a 3-node circular topology
| | # Linear search
| | Then Find NDR using linear search and pps | ${framesize} | ${start_rate}
| | ...                                       | ${step_rate} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}

| Find NDR with 2 cores and rss 1 by using linear search and 64B frames through L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 64B frames by using
| | ... | linear search starting at 8.2Mpps, stepping down with step of 0.1Mpps
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD
| | # Variables
| | ${framesize}= | Set Variable | 64
| | ${start_rate}= | Set Variable | 12000000
| | ${step_rate}= | Set Variable | 100000
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | 14880952
| | # VPP setup
| | Given Setup '2' worker threads and rss '1' without HTT on all DUTs
| | AND   L2 xconnect initialized in a 3-node circular topology
| | # Linear search
| | Then Find NDR using linear search and pps | ${framesize} | ${start_rate}
| | ...                                       | ${step_rate} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}

| Find NDR with 4 cores and rss 2 by using linear search and 64B frames through L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with non drop rate for 64B
| | ... | frames by using linear search starting at 8.2Mpps, stepping down
| | ... | with step of 0.1Mpps
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD
| | # Variables
| | ${framesize}= | Set Variable | 64
| | ${start_rate}= | Set Variable | 12200000
| | ${step_rate}= | Set Variable | 100000
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | 14880952
| | # VPP setup
| | Given Setup '4' worker threads and rss '2' without HTT on all DUTs
| | AND   L2 xconnect initialized in a 3-node circular topology
| | # Linear search
| | Then Find NDR using linear search and pps | ${framesize} | ${start_rate}
| | ...                                       | ${step_rate} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}

