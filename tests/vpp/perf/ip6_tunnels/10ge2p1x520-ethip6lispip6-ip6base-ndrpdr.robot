# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | NDRPDR
| ... | NIC_Intel-X520-DA2 | IP6FWD | ENCAP | LISP | IP6UNRLAY | IP6OVRLAY
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
| Test Template | Local Template
| ...
| Documentation | *RFC6830: Pkt throughput Lisp test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv6-LISP-IPv6 on DUT1-DUT2,\
| ... | Eth-IPv6 on TG-DUTn for IPv6 routing over LISPoIPv6 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv6\
| ... | routing and static routes. LISPoIPv6 tunnel is configured between\
| ... | DUT1 and DUT2. DUT1 and DUT2 tested with 2p10GE NIC X520 Niantic\
| ... | by Intel.
| ... | *[Ver] TG verification:* TG finds and reports throughput NDR (Non Drop\
| ... | Rate) with zero packet loss tolerance or throughput PDR (Partial Drop\
| ... | Rate) with non-zero packet loss tolerance (LT) expressed in percentage\
| ... | of packets transmitted. NDR and PDR are discovered for different\
| ... | Ethernet L2 frame sizes using MLRsearch library.\
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Variables ***
# X520-DA2 bandwidth limit
| ${s_limit} | ${10000000000}
# LISP overhead.
| ${overhead} | 8
# Traffic profile:
| ${traffic_profile} | trex-sl-3n-ethip6-ip6src253

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT runs IPv6 LISP remote static mappings and whitelist\
| | ... | filters config.\
| | ... | Each DUT uses ${phy_cores} physical core(s) for worker threads.
| | ... | [Ver] Measure NDR and PDR values using MLRsearch algorithm.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - Framesize in Bytes in integer or string (IMIX_v4_1).
| | ... |   Type: integer, string
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${framesize} | ${phy_cores} | ${rxq}=${None}
| | ...
| | Set Test Variable | ${framesize}
| | Set Test Variable | ${min_rate} | ${10000}
| | ...
| | Given Add worker threads and rxqueues to all DUTs | ${phy_cores} | ${rxq}
| | And Add PCI devices to all DUTs
| | ${max_rate} | ${jumbo} = | Get Max Rate And Jumbo And Handle Multi Seg
| | ... | ${s_limit} | ${framesize} | overhead=${overhead}
| | And Apply startup configuration on all VPP DUTs
| | When Initialize LISP IPv6 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip6} | ${dut1_to_tg_ip6} | ${dut2_to_dut1_ip6}
| | ... | ${dut2_to_tg_ip6} | ${prefix6}
| | And Configure LISP topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ... | ${dut1_ip6_static_adjacency} | ${dut2_ip6_static_adjacency}
| | Then Find NDR and PDR intervals using optimized search
| | ... | ${framesize} | ${traffic_profile} | ${min_rate} | ${max_rate}

*** Test Cases ***
| tc01-78B-1c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 78B | 1C
| | framesize=${78} | phy_cores=${1}

| tc02-78B-2c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 78B | 2C
| | framesize=${78} | phy_cores=${2}

| tc03-78B-4c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 78B | 4C
| | framesize=${78} | phy_cores=${4}

| tc04-1518B-1c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 1518B | 1C
| | framesize=${1518} | phy_cores=${1}

| tc05-1518B-2c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 1518B | 2C
| | framesize=${1518} | phy_cores=${2}

| tc06-1518B-4c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 1518B | 4C
| | framesize=${1518} | phy_cores=${4}

| tc07-9000B-1c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 9000B | 1C
| | framesize=${9000} | phy_cores=${1}

| tc08-9000B-2c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 9000B | 2C
| | framesize=${9000} | phy_cores=${2}

| tc09-9000B-4c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | 9000B | 4C
| | framesize=${9000} | phy_cores=${4}

| tc10-IMIX-1c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | IMIX | 1C
| | framesize=IMIX_v4_1 | phy_cores=${1}

| tc11-IMIX-2c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | IMIX | 2C
| | framesize=IMIX_v4_1 | phy_cores=${2}

| tc12-IMIX-4c-ethip6lispip6-ip6base-ndrpdr
| | [Tags] | IMIX | 4C
| | framesize=IMIX_v4_1 | phy_cores=${4}
