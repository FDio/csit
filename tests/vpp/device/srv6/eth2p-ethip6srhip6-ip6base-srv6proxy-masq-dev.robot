# Copyright (c) 2020 Cisco and/or its affiliates.
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
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | ETH | IP6FWD | FEATURE | SRv6 | SRv6_PROXY
| ... | SRv6_PROXY_MASQ | MEMIF | DOCKER | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip6srhip6-ip6base-srv6proxy-masq
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | container
|
| Test Template | Local Template
|
| Documentation | *Segment routing over IPv6 dataplane with Masquerading\
| ... | SRv6 proxy test cases*
|
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv6 routing and\
| ... | static route, SR policy and steering policy for one direction and\
| ... | two SR behaviours (functions) - End and End.DX6 - for other direction.
| ... | *[Ver] TG verification:* ETH-IP6 packet is sent from TG to DUT1. Packet\
| ... | is received on TG from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC4303.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | memif_plugin.so | srv6am_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${80}
# SIDs
| ${dut1_sid1}= | 2002:1::
| ${dut1_sid2}= | 2003:2::
| ${dut1_bsid}= | 2002:1::1
| ${dut2_sid1}= | 2002:2::
| ${dut2_sid2}= | 2003:1::
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
# Container
| ${container_engine}= | Docker
| ${container_chain_topology}= | chain_functional

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT1 is configured with IPv6 routing and static route,\
| | ... | SR policy and steering policy for one direction and\
| | ... | one SR behaviours (function) - End - for other direction.
| | ... | [Ver]
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
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
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Start containers for test | auto_scale=${False} | pinning=${False}
| | And Initialize IPv6 forwarding over SRv6 with endpoint to SR-unaware Service Function via 'masquerading' behaviour in circular topology
| | Then Send IPv6 Packet and verify SRv6 encapsulation in received packet
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${DUT1_${int}2_mac}[0] | ${tg_if1_ip6_subnet}2 | ${tg_if2_ip6_subnet}2
| | ... | ${dut1_sid1} | ${dut1_sid2} | ${dut2_sid2} | ${dut2_sid1}
| | ... | ${out_sid2_1} | ${out_sid1_1} | decap=${False}
| | ... | out_sid1_2=${out_sid1_2} | out_sid2_2=${out_sid2_2}

*** Test Cases ***
| tc01-78B-ethip6srhip6-ip6base-srv6proxy-masq-dev
| | [Tags] | 78B
| | frame_size=${78} | phy_cores=${0}
