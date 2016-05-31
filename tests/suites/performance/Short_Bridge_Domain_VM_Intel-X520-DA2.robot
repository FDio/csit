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
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_SHORT
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L2 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Remove startup configuration of VPP from all DUTs
| ...           | AND          | Stop and Clear QEMU | ${dut1} | ${vm1}
| ...           | AND          | Stop and Clear QEMU | ${dut2} | ${vm2}
| Documentation | Minimal throughput acceptance test cases

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2
| ${sock1}= | /tmp/sock-1-1
| ${sock2}= | /tmp/sock-1-2

*** Test Cases ***
| 1core VPP passes 64B frames through L2 bridge domain interconnected via VM at 2x 3.2Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 64B frames through bridge domain
| | ... | interconnected via VM at 2x 3.2Mpps in 3-node topology.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR | VPP-BRIDGEVM-VPP
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 3.2mpps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | And   ${vm1}= | VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...   | ${dut1} | ${sock1} | ${sock2}
| | And   ${vm2}= | VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...   | ${dut2} | ${sock1} | ${sock2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge


