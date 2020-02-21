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
| ... | NIC_Virtual | ETH | IP6FWD | BASE | MEMIF | DOCKER | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethipv6-ip6base-eth-2memif-1dcr
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | container
|
| Test Template | Local Template
|
| Documentation | *IPv4 routing test cases with memif interface*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology with \
| ... | single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv6 for IPv6 routing on \
| ... | both links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv6 routing and \
| ... | two static IPv6 /64 route entries. Container is connected to VPP via \
| ... | Memif interface. Container is running same VPP version as running on \
| ... | DUT.
| ... | *[Ver] TG verification:* Test IPv6 packets are sent in one direction \
| ... | by TG on links to DUT1 and via container; on receive TG verifies \
| ... | packets for correctness and their IPv6 src-addr, dst-addr and \
| ... | MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | memif_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
# Container
| ${container_engine}= | Docker
| ${container_chain_topology}= | chain_functional

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send IPv6 packets in both directions between two\
| | ... | of its interfaces to be routed by DUT to and from docker; verify\
| | ... | all packets are received.
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
| | And Set interfaces in path up
| | And Set up memif interfaces on DUT node
| | ... | ${dut1} | memif-DUT1_CNF | memif-DUT1_CNF
| | ... | memif_if1=memif_if1 | memif_if2=memif_if2
| | ... | rxq=${rxq_count_int} | txq=${rxq_count_int}
| | And Add Fib Table | ${dut1} | 20 | ipv6=${True}
| | And Assign Interface To Fib Table
| | ... | ${dut1} | ${memif_if2} | 20 | ipv6=${True}
| | And Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 20 | ipv6=${True}
| | And VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 2001:1::1 | 64
| | And VPP Interface Set IP Address
| | ... | ${dut1} | ${memif_if1} | 2001:2::1 | 64
| | And VPP Interface Set IP Address
| | ... | ${dut1} | ${memif_if2} | 2001:2::2 | 64
| | And VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2001:3::1 | 64
| | ${memif_if2_key}= | Get interface by sw index | ${nodes['DUT1']}
| | ... | ${memif_if2}
| | ${memif_if2_mac}= | Get interface MAC | ${nodes['DUT1']} | ${memif_if2_key}
| | And Vpp Route Add
| | ... | ${dut1} | 2001:3::0 | 64 | gateway=2001:2::2 | interface=${memif_if1}
| | And Vpp Route Add
| | ... | ${dut1} | 2001:1::0 | 64 | gateway=2001:2::2 | interface=${memif_if2}
| | ... | vrf=20
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${memif_if1} | 2001:2::2 | ${memif_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2001:3::2 | ${TG_pf2_mac}[0]
| | Then Send packet and verify headers
| | ... | ${tg} | 2001:1::1 | 2001:3::2
| | ... | ${TG_pf1}[0] | ${TG_pf1_mac}[0] | ${DUT1_vf1_mac}[0]
| | ... | ${TG_pf2}[0] | ${DUT1_vf2_mac}[0] | ${TG_pf2_mac}[0]

*** Test Cases ***
| tc01-78B-ethipv6-ip6base-eth-2memif-1dcr-dev
| | [Tags] | 78B
| | frame_size=${78} | phy_cores=${0}
