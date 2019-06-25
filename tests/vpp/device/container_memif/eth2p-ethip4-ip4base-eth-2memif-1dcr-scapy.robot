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
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | ETH | IP4FWD | BASE | MEMIF | DOCKER
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | container
| ...
| Documentation | *IPv4 routing test cases with memif interface*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology with \
| ... | single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for IPv4 routing on \
| ... | both links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and \
| ... | two static IPv4 /24 route entries. Container is connected to VPP via \
| ... | Memif interface. Container is running same VPP version as running on \
| ... | DUT.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in \
| ... | one direction by TG on links to DUT1 and via container; on receive TG \
| ... | verifies packets for correctness and their IPv4 src-addr, dst-addr and \
| ... | MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | memif_plugin.so
| ${nic_name}= | virtual
| ${overhead}= | ${0}
| ${rxq_count_int}= | 1
# Container
| ${container_engine}= | Docker
| ${container_chain_topology}= | chain_functional

*** Test Cases ***
| tc01-eth2p-ethip4-ip4base-eth-2memif-1dcr-scapy
| | [Documentation]
| | ... | [Cfg] Configure two VRFs to route IPv4 traffic through two memif\
| | ... | interfaces. Both interfaces are configured with IP addresses from\
| | ... | the same network.
| | ...
| | Set Test Variable | ${frame_size} | ${64}
| | ...
| | Given Add PCI devices to all DUTs
| | And Set Max Rate And Jumbo And Handle Multi Seg
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Start containers for device test
| | And Initialize IPv4 routing with memif pairs
| | Then Send packet and verify headers
| | ... | ${tg} | 10.10.10.1 | 20.20.20.1
| | ... | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
