# Copyright (c) 2023 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/shared/default.robot
|
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | NDRPDR
| ... | NIC_Intel-X710 | SRv6 | IP6FWD | FEATURE | SRv6_PROXY
| ... | SRv6_PROXY_MASQ | MEMIF | DOCKER | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip6srhip6-ip6base-srv6proxy-masq
|
| Suite Setup | Setup suite topology interfaces | performance
| Suite Teardown | Tear down suite | performance
| Test Setup | Setup test | performance
| Test Teardown | Tear down test | performance | srv6 | container
|
| Test Template | Local Template
|
| Documentation | **Packet throughput Segment routing over IPv6 dataplane with \
| ... | Masquerading SRv6 proxy test cases**
| ... |
| ... | - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular \
| ... | topology with single links between nodes.
| ... |
| ... | - **[Enc] Packet Encapsulations:** Eth-IPv6-SRH-IPv6 on DUT1-DUT2, \
| ... | DUTn-CNT and DUTn->TG, Eth-IPv6 on TG->DUTn for IPv6 routing over SRv6.
| ... |
| ... | - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv6 \
| ... | routing and static route, SR policy and steering policy for one \
| ... | direction and one SR behaviour (function) - End.AM - for other \
| ... | direction. DUT1 and DUT2 are tested with ${nic_name}.
| ... |
| ... | - **[Ver] TG verification:** TG finds and reports throughput NDR (Non \
| ... | Drop Rate) with zero packet loss tolerance and throughput PDR \
| ... | (Partial Drop Rate) with non-zero packet loss tolerance (LT) \
| ... | expressed in percentage of packets transmitted. NDR and PDR are \
| ... | discovered for different Ethernet L2 frame sizes using MLRsearch \
| ... | library.
| ... | Test packets are generated by TG on \
| ... | links to DUTs. TG traffic profile contains two L3 flow-groups \
| ... | (flow-group per direction, 253 flows per flow-group) with \
| ... | all packets containing Ethernet header,IPv6 header with static \
| ... | payload. \
| ... | MAC addresses are matching MAC addresses of the TG node interfaces.
| ... |
| ... | - **[Ref] Applicable standard specifications:** SRv6 Network \
| ... | Programming - draft 3.and Segment Routing for Service Chaining \
| ... | - internet draft 01.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so | memif_plugin.so
| ... | srv6am_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${osi_layer}= | L3
| ${overhead}= | ${96}
# SIDs
| ${dut1_sid1}= | 2002:1::
| ${dut1_sid2}= | 2003:2::
| ${dut1_bsid}= | 2002:1::1
| ${dut2_sid1}= | 2002:2::
| ${dut2_sid2}= | 2003:1::
| ${dut2_bsid}= | 2003:1::1
| ${out_sid1_1}= | 2002:3::
| ${out_sid1_2}= | 2002:4::
| ${out_sid2_1}= | 2003:3::
| ${out_sid2_2}= | 2003:4::
| ${sid_prefix}= | ${64}
# IP settings
| ${tg_if1_ip6_subnet}= | 2001:1::
| ${tg_if2_ip6_subnet}= | 2001:2::
| ${dst_addr_nr}= | ${1}
| ${dut1_if1_ip6}= | 2001:1::1
| ${dut1_if2_ip6}= | 2001:3::1
| ${dut1-memif-1-if1_ip6}= | 3001:1::1
| ${dut1-memif-1-if2_ip6}= | 3001:1::2
| ${dut1_nh}= | 4002::
| ${dut2_if1_ip6}= | 2001:3::2
| ${dut2_if2_ip6}= | 2001:2::1
| ${dut2-memif-1-if1_ip6}= | 3002:1::1
| ${dut2-memif-1-if2_ip6}= | 3002:1::2
| ${dut2_nh}= | 4001::
| ${prefix}= | ${64}
| ${mem_prefix}= | ${128}
# Traffic profile:
| ${traffic_profile}= | trex-stl-ethip6-ip6src253
# Container
| ${container_engine}= | Docker
| ${container_chain_topology}= | chain

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | - **[Cfg]** DUT1 and DUT2 are configured with IPv6 routing \
| | ... | and static route, SR policy and steering policy for one direction \
| | ... | and SR behaviour (function) - End.AM - for other direction. \
| | ... | Each DUT uses ${phy_cores} physical core(s) for worker threads.
| | ... | - **[Ver]** Measure NDR and PDR values using MLRsearch algorithm.
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer or string (IMIX_v4_1).
| | ... | Type: integer, string
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| |
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| |
| | Set Test Variable | \${frame_size}
| |
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Start containers for test | nf_chains=${1} | nf_nodes=${1}
| | And Initialize SRv6 with 'masquerading' SR-unaware Service Function
| | Then Find NDR and PDR intervals using optimized search

*** Test Cases ***
| 78B-1c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 78B | 1C
| | frame_size=${78} | phy_cores=${1}

| 78B-2c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 78B | 2C
| | frame_size=${78} | phy_cores=${2}

| 78B-4c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 78B | 4C
| | frame_size=${78} | phy_cores=${4}

| 1518B-1c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 1518B | 1C
| | frame_size=${1518} | phy_cores=${1}

| 1518B-2c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 1518B | 2C
| | frame_size=${1518} | phy_cores=${2}

| 1518B-4c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 1518B | 4C
| | frame_size=${1518} | phy_cores=${4}

| 9000B-1c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 9000B | 1C
| | frame_size=${9000} | phy_cores=${1}

| 9000B-2c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 9000B | 2C
| | frame_size=${9000} | phy_cores=${2}

| 9000B-4c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | 9000B | 4C
| | frame_size=${9000} | phy_cores=${4}

| IMIX-1c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | IMIX | 1C
| | frame_size=IMIX_v4_1 | phy_cores=${1}

| IMIX-2c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | IMIX | 2C
| | frame_size=IMIX_v4_1 | phy_cores=${2}

| IMIX-4c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
| | [Tags] | IMIX | 4C
| | frame_size=IMIX_v4_1 | phy_cores=${4}