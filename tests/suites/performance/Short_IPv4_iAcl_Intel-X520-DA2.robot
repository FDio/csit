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
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']} | WITH NAME | dut1_v4
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT2']} | WITH NAME | dut2_v4
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_SHORT
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L3 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keyword | Remove startup configuration of VPP from all DUTs
| Documentation | Minimal throughput acceptance test cases

*** Test Cases ***
| 1core VPP passes 64B frames through IPv4 forwarding with iAcl at 2x 3.5Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 64B frames through IPv4 forwarding
| | ... | at 2x 3.5Mpps in 3-node topology with iAcl.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 3.5mpps
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv4 forwarding initialized in a 3-node circular topology
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip4 | ${table_index}
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut2} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 10.10.10.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip4 | ${table_index}
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv4

| 1core VPP passes 1518B frames through IPv4 forwarding with iAcl at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 1518B frames through IPv4 forwarding
| | ... | at 2x 812,743pps (2x 10Gbps) in 3-node topology with iAcl.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv4 forwarding initialized in a 3-node circular topology
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip4 | ${table_index}
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut2} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 10.10.10.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip4 | ${table_index}
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv4

| 1core VPP passes 9000B frames through IPv4 forwarding with iAcl at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 9000B frames through IPv4 forwarding
| | ... | at 2x 138,580pps (2x 10Gbps) in 3-node topology with iAcl.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv4 forwarding initialized in a 3-node circular topology
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip4 | ${table_index}
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut2} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 10.10.10.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip4 | ${table_index}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 2core VPP with rxqueues 1 passes 64B frames through IPv4 forwarding with iAcl at 2x 5.8Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 64B frames through IPv4 forwarding
| | ... | at 2x 5.8Mpps in 3-node topology with iAcl.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 5.8mpps
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv4 forwarding initialized in a 3-node circular topology
| | ${table_index} | ${skip_n} | ${match_n}= | When Vpp Create Classify Table
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip4 | ${table_index}
| | ${table_index} | ${skip_n} | ${match_n}= | When Vpp Create Classify Table
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut2} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 10.10.10.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip4 | ${table_index}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 2core VPP with rxqueues 1 passes 1518B frames through IPv4 forwarding with iAcl at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 1518B frames through IPv4 forwarding
| | ... | at 2x 812,743pps (2x 10Gbps) in 3-node topology with iAcl.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv4 forwarding initialized in a 3-node circular topology
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip4 | ${table_index}
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut2} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 10.10.10.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip4 | ${table_index}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 2core VPP with rxqueues 1 passes 9000B frames through IPv4 forwarding with iAcl at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 9000B frames through IPv4 forwarding
| | ... | at 2x 138,580pps (2x 10Gbps) in 3-node topology with iAcl.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv4 forwarding initialized in a 3-node circular topology
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip4 | ${table_index}
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut2} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 10.10.10.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip4 | ${table_index}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 4core VPP with rxqueues 2 passes 64B frames through IPv4 forwarding with iAcl at 2x 7.8Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rxqueues 2 should pass 64B frames through IPv4
| | ... | forwarding at 2x 7.8Mpps in 3-node topology with iAcl.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 7.8mpps
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   IPv4 forwarding initialized in a 3-node circular topology
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 4core VPP with rxqueues 2 passes 1518B frames through IPv4 forwarding with iAcl at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rxqueues 2 should pass 1518B frames through IPv4
| | ... | forwarding at 2x 812,743pps (2x 10Gbps) in 3-node topology with iAcl.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv4 forwarding initialized in a 3-node circular topology
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip4 | ${table_index}
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut2} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 10.10.10.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip4 | ${table_index}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4

| 4core VPP with rxqueues 2 passes 9000B frames through IPv4 forwarding with iAcl at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rxqueues 2 should pass 9000B frames through IPv4
| | ... | forwarding at 2x 138,580pps (2x 10Gbps) in 3-node topology with iAcl.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv4 forwarding initialized in a 3-node circular topology
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut1} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip4 | ${table_index}
| | ${table_index} | ${skip_n} | ${match_n}= | And Vpp Create Classify Table
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configure Classify Session
| | ... | ${dut2} | permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 10.10.10.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip4 | ${table_index}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-IPv4
