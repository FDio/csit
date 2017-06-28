# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/performance/performance_setup.robot
| Resource | resources/libraries/robot/overlay/lisp_static_adjacency.robot
| Variables | resources/test_data/lisp/performance/lisp_static_adjacency.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | NDRPDRDISC
| ... | NIC_Intel-X520-DA2 | IP4FWD | ENCAP | LISP | IP6UNRLAY | IP4OVRLAY
| ...
| Suite Setup | Set up 3-node performance topology with DUT's NIC model
| ... | L3 | Intel-X520-DA2
| Suite Teardown | Tear down 3-node performance topology
| ...
| Test Setup | Set up performance test
| ...
| Test Teardown | Tear down performance discovery test | ${min_rate}pps
| ... | ${framesize} | ${traffic_profile}
| ...
| Documentation | *RFC6830: Pkt throughput Lisp test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv6 on DUT1-DUT2 and\
| ... | Eth-IPv4 on TG-DUTn for IPv4 routing over LISPoIPv6 tunnel.\
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4\
| ... | routing and static routes. LISPoIPv6 tunnel is configured\
| ... | between DUT1 and DUT2. DUT1 and DUT2 tested with 2p10GE NIC X520\
| ... | Niantic by Intel.
| ... | *[Ver] TG verification:* TG finds and reports throughput NDR (Non Drop\
| ... | Rate) with zero packet loss tolerance or throughput PDR (Partial Drop\
| ... | Rate) with non-zero packet loss tolerance (LT) expressed in percentage\
| ... | of packets transmitted. NDR and PDR are discovered for different\
| ... | Ethernet L2 frame sizes using either binary search or linear search\
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Variables ***
# X520-DA2 bandwidth limit
| ${s_limit} | ${10000000000}
# Traffic profile:
| ${traffic_profile} | trex-sl-3n-ethip4-ip4src253

*** Test Cases ***
| tc01-64B-1t1c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 64 Byte frames using binary search start\
| | ... | at 10GE linerate, step 100kpps.
| | [Tags] | 64B | 1T1C | STHREAD | NDRDISC
| | ${framesize}= | Set Variable | ${64}
| | ${min_rate}= | Set Variable | ${100000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc02-64B-1t1c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 64 Byte frames using binary search start\
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
| | [Tags] | 64B | 1T1C | STHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${64}
| | ${min_rate}= | Set Variable | ${100000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}

| tc03-1460B-1t1c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 1460 Byte frames using binary search start\
| | ... | at 10GE linerate, step 100kpps.
| | [Tags] | 1460B | 1T1C | STHREAD | NDRDISC
| | ${framesize}= | Set Variable | ${1460}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc04-1460B-1t1c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 1460 Byte frames using binary search start\
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
| | [Tags] | 1460B | 1T1C | STHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${1460}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}

| tc05-9000B-1t1c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 9000 Byte frames using binary search start\
| | ... | at 10GE linerate, step 5kpps.
| | [Tags] | 9000B | 1T1C | STHREAD | NDRDISC
| | ${framesize}= | Set Variable | ${9000}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc06-9000B-1t1c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 1 thread, 1 phy core, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 9000 Byte frames using binary search start\
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
| | [Tags] | 9000B | 1T1C | STHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${9000}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}

| tc07-64B-2t2c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 2 threads, 2 phy cores, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 64 Byte frames using binary search start\
| | ... | at 10GE linerate, step 100kpps.
| | [Tags] | 64B | 2T2C | MTHREAD | NDRDISC
| | ${framesize}= | Set Variable | ${64}
| | ${min_rate}= | Set Variable | ${100000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc08-64B-2t2c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 2 threads, 2 phy cores, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 64 Byte frames using binary search start\
| | ... | at 10GE linerate, step 100kpps.
| | [Tags] | 64B | 2T2C | MTHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${64}
| | ${min_rate}= | Set Variable | ${100000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}

| tc09-1460B-2t2c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 2 threads, 2 phy cores, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 1460 Byte frames using binary search start\
| | ... | at 10GE linerate, step 10kpps.
| | [Tags] | 1460B | 2T2C | MTHREAD | NDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${1460}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc10-1460B-2t2c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 2 threads, 2 phy cores, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 1460 Byte frames using binary search start\
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
| | [Tags] | 1460B | 2T2C | MTHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${1460}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}

| tc11-9000B-2t2c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 2 threads, 2 phy cores, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 9000 Byte frames using binary search start\
| | ... | at 10GE linerate, step 5kpps.
| | [Tags] | 9000B | 2T2C | MTHREAD | NDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${9000}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc12-9000B-2t2c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 2 threads, 2 phy cores, 1 receive queue per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 9000 Byte frames using binary search start\
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
| | [Tags] | 9000B | 2T2C | MTHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${9000}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}

| tc13-64B-4t4c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 4 threads, 4 phy cores, 2 receive queues per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 64 Byte frames using binary search start\
| | ... | at 10GE linerate, step 100kpps.
| | [Tags] | 64B | 4T4C | MTHREAD | NDRDISC
| | ${framesize}= | Set Variable | ${64}
| | ${min_rate}= | Set Variable | ${100000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc14-64B-4t4c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 4 threads, 4 phy cores, 2 receive queues per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 64 Byte frames using binary search start\
| | ... | at 10GE linerate, step 100kpps, LT=0.5%.
| | [Tags] | 64B | 4T4C | MTHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${64}
| | ${min_rate}= | Set Variable | ${100000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}

| tc15-1460B-4t4c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 4 threads, 4 phy cores, 2 receive queues per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 1460 Byte frames using binary search start\
| | ... | at 10GE linerate, step 10kpps.
| | [Tags] | 1460B | 4T4C | MTHREAD | NDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${1460}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc16-1460B-4t4c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 4 threads, 4 phy cores, 2 receive queues per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 1460 Byte frames using binary search start\
| | ... | at 10GE linerate, step 10kpps, LT=0.5%.
| | [Tags] | 1460B | 4T4C | MTHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${1460}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}

| tc17-9000B-4t4c-ethip4lispip6-ip4base-ndrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 4 threads, 4 phy cores, 2 receive queues per NIC\
| | ... | port.
| | ... | [Ver] Find NDR for 9000 Byte frames using binary search start\
| | ... | at 10GE linerate, step 5kpps.
| | [Tags] | 9000B | 4T4C | MTHREAD | NDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${9000}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

| tc18-9000B-4t4c-ethip4lispip6-ip4base-pdrdisc
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config with 4 threads, 4 phy cores, 2 receive queues per NIC\
| | ... | port.
| | ... | [Ver] Find PDR for 9000 Byte frames using binary search start\
| | ... | at 10GE linerate, step 5kpps, LT=0.5%.
| | [Tags] | 9000B | 4T4C | MTHREAD | PDRDISC | SKIP_PATCH
| | ${framesize}= | Set Variable | ${9000}
| | ${min_rate}= | Set Variable | ${10000}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${framesize + 48}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4o6} | ${dut1_to_tg_ip4o6} | ${dut2_to_dut1_ip4o6}
| | ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6} | ${dut_prefix4o6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| | ... | ${dut1_ip4o6_static_adjacency} | ${dut2_ip4o6_static_adjacency}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}
