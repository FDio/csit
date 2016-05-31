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
| Variables | resources/test_data/lisp/performance/lisp_static_mapping.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_LONG
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup
| ... | L3
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keyword | Remove startup configuration of VPP from all DUTs
| Documentation | *RFC6830: Pkt throughput Lisp test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2,
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel;
| ... | Eth-IPv6-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for
| ... | IPv6 routing over LISPoIPv6 tunnel; Eth-IPv6-LISP-IPv4-ICMPv4 on
| ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv6
| ... | tunnel; Eth-IPv4-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on
| ... | TG-DUTn for IPv6 routing over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4 (IPv6)
| ... | routing and static routes. LISPoIPv4 (oIPv6) tunnel is configured
| ... | between DUT1 and DUT2. DUT1 and DUT2 tested with 2p10GE NIC X520 Niantic
| ... | by Intel.
| ... | *[Ver] TG verification:* TG finds and reports throughput NDR (Non Drop
| ... | Rate) with zero packet loss tolerance or throughput PDR (Partial Drop
| ... | Rate) with non-zero packet loss tolerance (LT) expressed in percentage
| ... | of packets transmitted. NDR and PDR are discovered for different
| ... | Ethernet L2 frame sizes using either binary search or linear search
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: 64B NDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC02: 64B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC03: 1480B NDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1480 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC04: 1480B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1480 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC05: 9000B NDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC06: 9000B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC07: 64B NDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC08: 64B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC09: 1480B NDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1480 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC10: 1480B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1480 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC11: 9000B NDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC12: 9000B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC13: 64B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC14: 64B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC15: 1480B NDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1480 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC16: 1480B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1480 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC17: 9000B NDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC18: 9000B PDR binary search - DUT IPv4 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv4 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC19: 78B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC20: 78B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC21: 1460B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1460B}
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

| TC22: 1460B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
| | [Tags] | 1_THREAD_NOHTT_RXQUEUES_1 | SINGLE_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1460B}
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

| TC23: 9000B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC24: 9000B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC24: 78B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC25: 78B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC26: 1460B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1460B}
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

| TC27: 1460B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
| | [Tags] | 2_THREAD_NOHTT_RXQUEUES_1 | MULTI_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1460B}
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

| TC28: 9000B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC29: 9000B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC30: 78B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC31: 78B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC32: 1460B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | NDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1460B}
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

| TC32: 1460B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
| | [Tags] | 4_THREAD_NOHTT_RXQUEUES_2 | MULTI_THREAD | PDR | LISP_IPv6
| | ${framesize}= | Set Variable | 1460
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_lisp_linerate_pps_1460B}
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

| TC33: 9000B NDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC34: 9000B PDR binary search - DUT IPv6 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC35: 64B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC36: 64B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC37: 1460B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC38: 1460B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC39: 9000B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC40: 9000B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC41: 64B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC42: 64B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC43: 1460B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC44: 1460B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC45: 9000B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC46: 9000B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC47: 64B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC48: 64B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 64 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC49: 1460B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC50: 1460B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC51: 9000B NDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC52: 9000B PDR binary search - DUT IPv4 over LISPoIPv6 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC53: 78B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC54: 78B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC55: 1460B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC56: 1460B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC57: 9000B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC58: 9000B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 1thread 1core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC59: 78B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC60: 78B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC61: 1460B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC62: 1460B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC63: 9000B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC64: 9000B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 2thread 2core 1rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 2 thread, 2 phy core, 1 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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

| TC65: 78B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps.
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

| TC66: 78B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 78 Byte frames using binary search start
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
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

| TC66: 1460B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps.
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

| TC67: 1460B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 1460 Byte frames using binary search start
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
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

| TC68: 9000B NDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find NDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps.
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

| TC69: 9000B PDR binary search - DUT IPv6 over LISPoIPv4 tunnel - 4thread 4core 2rxq
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist \
| | ... | filters config with 4 thread, 4 phy core, 2 receive queue per NIC
| | ... | port. [Ver] Find PDR for 9000 Byte frames using binary search start
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
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
