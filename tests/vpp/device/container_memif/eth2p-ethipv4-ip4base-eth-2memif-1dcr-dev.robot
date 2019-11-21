# Copyright (c) 2019 Cisco and/or its affiliates.
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
| ... | NIC_Virtual | ETH | IP4FWD | BASE | MEMIF | DOCKER | DRV_VFIO_PCI
|
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | container
|
| Test Template | Local Template
|
| Documentation | *IPv4 routing test cases with memif interface*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology with \
| ... | single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 for IPv4 routing on both links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and \
| ... | two static IPv4 /24 route entries. Container is connected to VPP via \
| ... | Memif interface. Container is running same VPP version as running on \
| ... | DUT.
| ... | *[Ver] TG verification:* Test IPv4 packets with IP protocol=61 are \
| ... | sent in one direction by TG on links to DUT1 and via container; on \
| ... | receive TG verifies packets for correctness and their IPv4 src-addr, \
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | memif_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}
# Container
| ${container_engine}= | Docker
| ${container_chain_topology}= | chain_functional

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send IPv4 packet in both directions between two\
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
| | And Initialize IPv4 routing with memif pairs
| | Then Send packet and verify headers
| | ... | ${tg} | 10.10.10.1 | 20.20.20.1
| | ... | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}

*** Test Cases ***
| tc01-64B-ethipv4-ip4base-eth-2memif-1dcr-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
