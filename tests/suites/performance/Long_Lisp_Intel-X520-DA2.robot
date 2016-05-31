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
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']}
| ...     | WITH NAME | dut1_v4
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT2']}
| ...     | WITH NAME | dut2_v4
# import additional Lisp settings from resource file
| Variables | tests/suites/performance/resources/lisp_static_mapping.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_LONG
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup
| ... | L3
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keyword | Remove startup configuration of VPP from all DUTs
| Documentation | *Throughput search suite (based on RFC2544).*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG, with one link
| ... | between nodes. Traffic profile contain 2 Lisp L3 streams (1 stream per
| ... | direction). Packets contain Ethernet header, IPv4 header,
| ... | IP protocol=61, IPv6 header, Lisp header and random payload.
| ... | Ethernet header MAC addresses are matching MAC addresses of the TG node.

*** Test Cases ***
| Find NDR by using RFC2544 binary search and 64B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 64B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 1480B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 1480B frames by using
| | ... | binary search with threshold 10,000pps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 1480B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 1480B frames by using
| | ... | binary search with threshold 10,000pps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 9000B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 9000B frames by using
| | ... | binary search with threshold 5,000pps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 9000B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 9000B frames by using
| | ... | binary search with threshold of 5,000pps. Loss acceptance is set to
| | ... | 0.5 percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 64B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 64B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 64B frames by
| | ... | using binary search with threshold 0.1Mpps. Loss acceptance is set to
| | ... | 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 1480B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 1480B frames by
| | ... | using binary search with threshold 10,000pps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 1480B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 1480B frames by
| | ... | using binary search with threshold 10,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 9000B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 9000B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 64B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 64B
| | ... | frames by using binary search with threshold 0.1Mpps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 64B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate
| | ... | for 64B frames by using binary search with threshold 0.1Mpps.
| | ... | Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 1480B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 1480B
| | ... | frames by using binary search with threshold 10,000pps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 1480B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate
| | ... | for 1480B frames by using binary search with threshold 10,000pps.
| | ... | Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 linear search and 9000B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 9000B
| | ... | frames by using binary search with threshold 5,000pps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 linear search and 9000B frames through IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate for 9000B
| | ... | frames by using binary search with threshold 5,000pps. Loss
| | ... | acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ...  | ${dut2_to_tg_ip4} | ${prefix4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ...  | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 78B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 78B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 78B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 78B frames by using
| | ... | binary search with threshold 0.1Mpps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 1480B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 1480B frames by using
| | ... | binary search with threshold 10,000pps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 1480B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 1480B frames by using
| | ... | binary search with threshold 10,000pps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 9000B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 9000B frames by using
| | ... | binary search with threshold 5,000pps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 9000B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 9000B frames by using
| | ... | binary search with threshold of 5,000pps. Loss acceptance is set to
| | ... | 0.5 percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 78B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 78B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 78B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 78B frames by
| | ... | using binary search with threshold 10,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 1480B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 1480B frames by
| | ... | using binary search with threshold 10,000pps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 1480B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 1480B frames by
| | ... | using binary search with threshold 10,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 9000B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 9000B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 78B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 78B
| | ... | frames by using binary search with threshold 0.1Mpps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 78B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate for 78B
| | ... | frames by using binary search with threshold 0.1Mpps. Loss acceptance
| | ... | is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 1480B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 1480B
| | ... | frames by using binary search with threshold 10,000pps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 1480B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate
| | ... | for 1480B frames by using binary search with threshold 10,000pps.
| | ... | Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1480
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1480B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 linear search and 9000B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 9000B
| | ... | frames by using linear search starting at 138,580pps, stepping down
| | ... | with step of 5,000pps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 linear search and 9000B frames through IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate for 9000B
| | ... | frames by using binary search with threshold 5,000pps. Loss
| | ... | acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ...  | ${dut2_to_tg_ip6} | ${prefix6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ...  | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 64B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 64B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 1460B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 1460B frames by using
| | ... | binary search with threshold 10,000pps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 1460B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 1460B frames by using
| | ... | binary search with threshold 10,000pps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 9000B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 9000B frames by using
| | ... | binary search with threshold 5,000pps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 9000B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 9000B frames by using
| | ... | binary search with threshold of 5,000pps. Loss acceptance is set to
| | ... | 0.5 percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 64B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 64B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 64B frames by
| | ... | using binary search with threshold 0.1Mpps. Loss acceptance is set to
| | ... | 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 1460B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 1460B frames by
| | ... | using binary search with threshold 10,000pps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 1460B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 1460B frames by
| | ... | using binary search with threshold 10,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 9000B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 9000B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 64B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 64B
| | ... | frames by using binary search with threshold 0.1Mpps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 64B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate for 64B
| | ... | frames by using binary search with threshold 0.1Mpps. Loss acceptance
| | ... | is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 1460B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 1460B
| | ... | frames by using binary search with threshold 10,000pps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 1460B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate
| | ... | for 1460B frames by using binary search with threshold 10,000pps.
| | ... | Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 linear search and 9000B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 9000B
| | ... | frames by using binary search with threshold 5,000pps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 linear search and 9000B frames through IPv4 over IPv6 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate
| | ... | for 9000B frames by using binary search with threshold 5,000pps.
| | ... | Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv4oIPv6
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ...  | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ...  | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv4
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 78B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 78B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 78B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 78B frames by using
| | ... | binary search with threshold 0.1Mpps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv6IPv4
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 1460B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 1460B frames by using
| | ... | binary search with threshold 10,000pps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 1460B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 1460B frames by using
| | ... | binary search with threshold 10,000pps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 9000B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 9000B frames by using
| | ... | binary search with threshold 5,000pps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 9000B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 9000B frames by using
| | ... | binary search with threshold of 5,000pps. Loss acceptance is set to
| | ... | 0.5 percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 78B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 78B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 78B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 78B frames by
| | ... | using binary search with threshold 10,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 1460B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 1460B frames by
| | ... | using binary search with threshold 10,000pps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 1460B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 1460B frames by
| | ... | using binary search with threshold 10,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 9000B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rxqueues 1 by using RFC2544 binary search and 9000B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rxqueues '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 78B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 78B
| | ... | frames by using binary search with threshold 0.1Mpps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 78B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate for 78B
| | ... | frames by using binary search with threshold 0.1Mpps. Loss acceptance
| | ... | is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 78
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_78B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 1460B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 1460B
| | ... | frames by using binary search with threshold 10,000pps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 binary search and 1460B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate
| | ... | for 1460B frames by using binary search with threshold 10,000pps.
| | ... | Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_1460B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rxqueues 2 by using RFC2544 linear search and 9000B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with non drop rate for 9000B
| | ... | frames by using linear search starting at 138,580pps, stepping down
| | ... | with step of 5,000pps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rxqueues 2 by using RFC2544 linear search and 9000B frames through IPv6 over IPv4 forwarding in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rxqueues 2 with partial drop rate
| | ... | for 9000B frames by using binary search with threshold 5,000pps.
| | ... | Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv6oIPv4
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_iph_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rxqueues '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
| | ...  | ${dut1_to_dut2_ip6o4} | ${dut1_to_tg_ip6o4} | ${dut2_to_dut1_ip6o4}
| | ...  | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4} | ${dut_prefix6o4}
| | And  Set up Lisp topology
| | ...  | ${dut1} | ${dut1_if2} | ${NONE}
| | ...  | ${dut2} | ${dut2_if1} | ${NONE}
| | ...  | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| | ...  | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-IPv6
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}
