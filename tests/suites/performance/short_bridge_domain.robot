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
| Suite Setup | 3-node Performance Suite Setup | L2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown  | Run Keyword If Test Failed | Show statistics on all DUTs

*** Test Cases ***
| 1core VPP passes 64B frames through bridge domain at 3.5mpps in 3-node topology
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 3.5mpps
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate} | ${framesize} | 3-node-bridge

| 1core VPP passes 1518B frames through bridge domain at 10gbps in 3-node topology
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 10gbps
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate} | ${framesize} | 3-node-bridge

| 1core VPP passes 9000B frames through bridge domain at 10gbps in 3-node topology
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 10gbps
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate} | ${framesize} | 3-node-bridge
