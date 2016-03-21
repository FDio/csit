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
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']} | WITH NAME | dut1_v4
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT2']} | WITH NAME | dut2_v4
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_LONG
| Suite Setup | 3-node Performance Suite Setup | L3
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown  | Run Keyword If Test Failed | Show statistics on all DUTs
| Documentation | Throughput search suite (long running test suite based on RFC2544).

*** Test Cases ***
| Find NDR by using linear search and 64B frames through IPv4 forwarding in 3-node topology
| | ${framesize}= | Set Variable | 64
| | ${start_rate}= | Set Variable | 5000000
| | ${step_rate}= | Set Variable | 100000
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | 14880952
| | Given IPv4 forwarding initialized in a 3-node circular topology
| | Then Find NDR using linear search and pps | ${framesize} | ${start_rate} | ${step_rate}
| | ...                                       | 3-node-IPv4 | ${min_rate} | ${max_rate}

| Find NDR by using linear search and 1518B frames through IPv4 forwarding in 3-node topology
| | ${framesize}= | Set Variable | 1518
| | ${start_rate}= | Set Variable | 812743
| | ${step_rate}= | Set Variable | 10000
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | 812743
| | Given IPv4 forwarding initialized in a 3-node circular topology
| | Then Find NDR using linear search and pps | ${framesize} | ${start_rate} | ${step_rate}
| | ...                                       | 3-node-IPv4 | ${min_rate} | ${max_rate}

| Find NDR by using linear search and 9000B frames through IPv4 forwarding in 3-node topology
| | ${framesize}= | Set Variable | 9000
| | ${start_rate}= | Set Variable | 138580
| | ${step_rate}= | Set Variable | 5000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | 138580
| | Given IPv4 forwarding initialized in a 3-node circular topology
| | Then Find NDR using linear search and pps | ${framesize} | ${start_rate} | ${step_rate}
| | ...                                       | 3-node-IPv4 | ${min_rate} | ${max_rate}
