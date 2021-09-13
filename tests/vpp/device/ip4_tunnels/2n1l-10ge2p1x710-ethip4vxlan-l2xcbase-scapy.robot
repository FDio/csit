# Copyright (c) 2021 Cisco and/or its affiliates.
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
| ... | NIC_Intel-X710 | L2XCBASE | ENCAP | VXLAN | L2OVRLAY | IP4UNRLAY
| ... | RXQ_SIZE_0 | TXQ_SIZE_0 | DRV_VFIO_PCI
| ... | ethip4vxlan-l2xcbase
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | telemetry
|
| Test Template | Local Template
|
| Documentation | *L2XC with VXLANoIPv4 test cases*
|
| ... | *[Top] Network topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on\
| ... | TG-DUT.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with L2 cross-connect.\
| ... | VXLAN tunnels are configured on links betwen TG and DUT.
| ... | *[Ver] TG verification:* Test Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 packet is\
| ... | sent by TG on link to DUT1; on receive TG verifies packets for\
| ... | correctness and their IPv4 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC7348.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${50}
# Telemetry
| ${telemetry_profile}= | vpp_test_teardown

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send VXLAN encapsulated Ethernet frame; verify\
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
| | And Initialize layer ip4vxlan
| | And Initialize L2 cross connect
| | Then Send VXLAN encapsulated packet and verify received packet
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]
| | ... | ${TG_pf1_mac}[0] | ${DUT1_vf1_mac}[0]
| | ... | 172.17.0.2 | 172.16.0.1 | ${0} | 172.26.0.1 | 172.27.0.2 | ${0}

*** Test Cases ***
| 64B-0c-ethip4vxlan-l2xcbase-scapy
| | [Tags] | 64B | 0C
| | frame_size=${64} | phy_cores=${0}
