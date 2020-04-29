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
| ... | NIC_Virtual | ETH | IP6FWD | FEATURE | SRv6 | SRv6_1SID | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip6ip6-ip6base-srv6enc1sid
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local Template
|
| Documentation | *Segment routing over IPv6 dataplane with one SID\
| ... | (SRH not inserted) test suite.*
|
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 configure physical interface IPv6\
| ... | addresses, static ARP record, route and IPv6 forwarding over SRv6\
| ... | with one SID - Segment Routing Header not inserted.
| ... | *[Ver] TG verification:* ETH-IP6 packet is sent from TG to DUT1 in one\
| ... | direction. Packet is received and verified for correctness on TG. Then\
| ... | ETH-IP6-IP6 packet is sent from TG in opposite direction. Packet is\
| ... | received and verified for correctness on TG.
| ... | *[Ref] Applicable standard specifications:* SRv6 Network Programming -\
| ... | draft 3.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${40}
# SIDs
| ${dut1_sid1}= | 2002:1::
| ${dut1_sid2}= | 2003:2::
| ${dut1_bsid}= | 2002:1::1
| ${dut2_sid1}= | 2002:2::
| ${dut2_sid2}= | 2003:1::
| ${sid_prefix}= | ${64}
# IP settings
| ${tg_if1_ip6_subnet}= | 2001:1::
| ${tg_if2_ip6_subnet}= | 2001:2::
| ${dst_addr_nr}= | ${1}
| ${dut1_if1_ip6}= | 2001:1::1
| ${dut1_if2_ip6}= | 2001:3::1
| ${dut2_if1_ip6}= | 2001:3::2
| ${dut2_if2_ip6}= | 2001:2::1
| ${prefix}= | ${64}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT1 is configured with IPv6 routing and static route,\
| | ... | SR policy and steering policy for one direction and one SR\
| | ... | behaviour (function) - End.DX6 - for other direction.
| | ... | [Ver] Make TG send IPv6 packets routed over DUT1 interfaces.\
| | ... | Make TG verify IPv6 packets are correct.
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
| | And Initialize SRv6 encapsulation with '1' x SID 'with' decapsulation
| | Then Send IPv6 Packet and verify SRv6 encapsulation in received packet
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${DUT1_${int}2_mac}[0] | ${tg_if1_ip6_subnet}2 | ${tg_if2_ip6_subnet}2
| | ... | ${dut1_sid1} | ${dut1_sid2} | ${dut2_sid2} | ${dut2_sid1}

*** Test Cases ***
| tc01-78B-ethip6ip6-ip6base-srv6enc1sid-dev
| | [Tags] | 78B
| | frame_size=${78} | phy_cores=${0}
