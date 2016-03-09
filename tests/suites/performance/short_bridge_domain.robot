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
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/performance.robot
| Resource | resources/libraries/robot/counters.robot
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.NodePath
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_SHORT
| Suite Setup | 3-node Performance Suite Setup
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown  | Run Keyword If Test Failed | Show statistics on all DUTs

*** Test Cases ***
| 1core VPP passes 64B frames through bridge domain at 3.5mpps in 3-node topology
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 3.5mpps | 64 | 3-node-bridge

| 1core VPP passes 1518B frames through bridge domain at 10gbps in 3-node topology
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 10gbps | 1518 | 3-node-bridge

| 1core VPP passes 9000B frames through bridge domain at 10gbps in 3-node topology
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 10gbps | 9000 | 3-node-bridge

*** Keywords ***

| 3-node Performance Suite Setup
| | 3-node circular Topology Variables Setup
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ...                          | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | ...                          | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | ...                          | L2

| 3-node Performance Suite Teardown
| | Teardown traffic generator | ${tg}

| L2 bridge domain initialized in a 3-node circular topology
| | Vpp l2bd forwarding setup | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Vpp l2bd forwarding setup | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Traffic should pass with no loss
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | Send traffic on | ${tg} | ${duration}
| | ...             | ${rate} | ${framesize} | ${topology_type}
| | No traffic loss occured

| Show statistics on all DUTs
| | Sleep | 10 | Waiting for statistics to be collected
| | Vpp show stats | ${dut1}
| | Vpp show stats | ${dut2}
