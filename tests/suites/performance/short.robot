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
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/counters.robot
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.NodePath
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| Suite Setup | 3-node Performance Suite Setup
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown  | Run Keyword If Test Failed | Show statistics on all DUTs

*** Test Cases ***
| 2core VPP passes 64B frames through L2 cross connect at 3.5mpps in 3-node topology
| | Given L2 xconnect initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 3.5mpps | 64 | 3-node-xconnect

| 2core VPP passes 1518B frames through L2 cross connect at 10gbps in 3-node topology
| | Given L2 xconnect initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 10gbps | 1518 | 3-node-xconnect

| 2core VPP passes 9000B frames through L2 cross connect at 10gbps in 3-node topology
| | Given L2 xconnect initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 10gbps | 9000 | 3-node-xconnect

| 2core VPP passes 64B frames through bridge domain at 3.5mpps in 3-node topology
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 3.5mpps | 64 | 3-node-bridge

| 2core VPP passes 1518B frames through bridge domain at 10gbps in 3-node topology
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 10gbps | 1518 | 3-node-bridge

| 2core VPP passes 9000B frames through bridge domain at 10gbps in 3-node topology
| | Given L2 bridge domain initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | 10 | 10gbps | 9000 | 3-node-bridge

#| VPP passes 64B frames through IPv4 forwarding at 3.5mpps in 3-node topology
#| | Given IPv4 forwarding initialized in a 3-node topology
#| | Then Traffic should pass with no loss | 10 | 3.5mpps | 64 | 3-node-IPv4

#| VPP passes 1518B frames through IPv4 forwarding at 100% in 3-node topology
#| | Given IPv4 forwarding initialized in a 3-node topology
#| | Then Traffic should pass with no loss | 10 | 100 | 1518 | 3-node-IPv4

#| VPP passes 9000B frames through IPv4 forwarding at 100% in 3-node topology
#| | Given IPv4 forwarding initialized in a 3-node topology
#| | Then Traffic should pass with no loss | 10 | 100 | 9000 | 3-node-IPv4


*** Keywords ***

| 3-node Topology Variables Setup
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...          | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}
| | Set Suite Variable | ${dut2}
| | Set Suite Variable | ${dut2_if1}
| | Set Suite Variable | ${dut2_if2}

| 3-node Performance Suite Setup
| | 3-node Topology Variables Setup
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2} | L2

| 3-node Performance Suite Teardown
| | Teardown traffic generator | ${tg}

| IPv4 forwarding initialized in a 3-node topology
| | Setup nodes for IPv4 testing

| L2 bridge domain initialized in a 3-node circular topology
| | Vpp l2bd forwarding setup | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Vpp l2bd forwarding setup | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Sleep | 10 | Wait for interfaces initialization

| L2 xconnect initialized in a 3-node circular topology
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Sleep | 10 | Wait for interfaces initialization

| Traffic should pass with no loss
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | Send traffic on | ${nodes} | ${duration}
| | ...             | ${rate} | ${framesize} | ${topology_type}
| | No traffic loss occured

| Show statistics on all DUTs
| | Sleep | 10 | Waiting for statistics to be collected
| | Vpp show stats | ${dut1}
| | Vpp show stats | ${dut2}
