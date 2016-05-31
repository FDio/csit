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
| Resource | resources/libraries/robot/lisp/lisp_static_mapping.robot
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']} | WITH NAME | dut1_v4
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT2']} | WITH NAME | dut2_v4
# import additional Lisp settings from resource file
| Variables | tests/suites/performance/resources/lisp_static_mapping.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_SHORT
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L3 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keyword | Remove startup configuration of VPP from all DUTs
| Documentation | TODO

*** Test Cases ***
| 1core Lisp VPP passes 64B frames through IPv4 forwarding at 2x 3.5Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 64B frames through IPv4 forwarding
| | ... | at 2x 3.5Mpps in 3-node topology.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 3.5mpps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...   | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...   | ${dut2_to_tg_ip4} | ${prefix4}
| | When  Set up Lisp topology
| | ...   | ${dut1} | ${dut1_if2} | ${NONE}
| | ...   | ${dut2} | ${dut2_if1} | ${NONE}
| | ...   | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...   | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv4

| 1core Lisp VPP passes 78B frames through IPv6 forwarding at 2x 2.9Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 78B frames through IPv6 forwarding
| | ... | at 2x2.9Mpps in 3-node topology.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 78
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 2.9mpps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...   | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...   | ${dut2_to_tg_ip6} | ${prefix6}
| | When  Set up Lisp topology
| | ...   | ${dut1} | ${dut1_if2} | ${NONE}
| | ...   | ${dut2} | ${dut2_if1} | ${NONE}
| | ...   | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...   | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 1core Lisp VPP passes 64B frames through IPv4 over IPv6 forwarding at 2x 3.5Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 64B frames through IPv4 forwarding
| | ... | at 2x 3.5Mpps in 3-node topology.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 3.5mpps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...   | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...   | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | When  Set up Lisp topology
| | ...   | ${dut1} | ${dut1_if2} | ${NONE}
| | ...   | ${dut2} | ${dut2_if1} | ${NONE}
| | ...   | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...   | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv4

| 1core Lisp VPP passes 78B frames through IPv6 over IPv4 forwarding at 2x 2.9Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 78B frames through IPv6 forwarding
| | ... | at 2x2.9Mpps in 3-node topology.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 78
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 2.9mpps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...   | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...   | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | When  Set up Lisp topology
| | ...   | ${dut1} | ${dut1_if2} | ${NONE}
| | ...   | ${dut2} | ${dut2_if1} | ${NONE}
| | ...   | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...   | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6
