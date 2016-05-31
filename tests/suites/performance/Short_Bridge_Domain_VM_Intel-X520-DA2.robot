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
| ...        | VHOST_BRIDGE | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L2 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Remove startup configuration of VPP from all DUTs
| ...           | AND          | Qemu Teardown | ${dut1} | ${vm1} | VM1
| ...           | AND          | Qemu Teardown | ${dut2} | ${vm2} | VM2
| Documentation | Minimal throughput acceptance test cases

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2
| ${sock1}= | /tmp/sock-1-${bd_id1}
| ${sock2}= | /tmp/sock-1-${bd_id2}

*** Test Cases ***
| 1core VPP passes 64B frames through BD-VM-BD at 2x 0.1Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 64B frames through bridge domain
| | ... | interconnected via VM at 2x 0.1Mpps in 3-node topology.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.03mpps
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 1core VPP passes 1518B frames through BD-VM-BD at 2x 0.1Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 1518B frames through bridge domain
| | ... | interconnected via VM at 2x 0.1Mpps in 3-node topology.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUS_1 | SINGLE_THREAD | NDR | THIS
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.1mpps
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 1core VPP passes 9000B frames through BD-VM-BD at 2x 0.1Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 9000B frames through bridge domain
| | ... | interconnected via VM at 2x 0.1Mpps in 3-node topology.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.1mpps
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 2core VPP with rxqueues 1 passes 64B frames through bridge domain at 2x 0.1Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 64B frames through bridge domain
| | ... | at 2x 0.1Mpps in 3-node topology.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.1mpps
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 2core VPP with rxqueues 1 passes 1518B frames through bridge domain at 2x 0.1mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 1518B frames through bridge domain
| | ... | at 2x 0.1mpps in 3-node topology.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.1mpps
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 2core VPP with rxqueues 1 passes 9000B frames through bridge domain at 2x 0.1mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 9000B frames through bridge domain
| | ... | at 2x 0.1mpps in 3-node topology.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.1mpps
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 4core VPP with rxqueues 2 passes 64B frames through bridge domain at 2x 0.1mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rxqueues 2 should pass 64B frames through bridge
| | ... | domain at 2x 0.1mpps in 3-node topology.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.1mpps
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 4core VPP with rxqueues 2 passes 1518B frames through bridge domain at 2x 0.1mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rxqueues 2 should pass 1518B frames through bridge
| | ... | domain at 2x 0.1mpps in 3-node topology.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.1mpps
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge

| 4core VPP with rxqueues 2 passes 9000B frames through bridge domain at 2x 0.1mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rxqueues 2should pass 9000B frames through bridge
| | ... | domain at 2x 0.1mpps in 3-node topology.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 0.1mpps
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-bridge
