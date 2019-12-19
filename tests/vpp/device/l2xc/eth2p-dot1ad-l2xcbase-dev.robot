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
| Resource | resources/libraries/robot/l2/tagging.robot
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | ETH | L2XCFWD | BASE | DOT1AD | DRV_VFIO_PCI
|
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local Template
|
| Documentation | *L2XC with 802.1ad test cases*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 for L2 xconnect.
| ... | 802.1ad tagging is applied on link between DUT1 interfaces and its \
| ... | subinterface with inner 4B vlan tag (id=100) and \
| ... | outer 4B vlan tag (id=200).
| ... | *[Cfg] DUT configuration:* DUT1 are configured with L2 cross-connect.
| ... | *[Ver] TG verification:* TG send Eth-IPv4 packets on both \
| ... | directions, on receive TG verifies packets for correctness and their \
| ... | IPv4 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${osi_layer}= | L2
| ${overhead}= | ${8}
| ${subid}= | 10
| ${outer_vlan_id}= |
| ${inner_vlan_id}= |
| ${type_subif}= | two_tags
| ${tag_rewrite}= | pop-2

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send IPv4 packets in both directions between two \
| | ... | of its interfaces to be switched by DUT to and from TG; verify \
| | ... | all packets are received.
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integeri. Type: integer
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
| | And Apply Startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | When Initialize VLAN sub-interfaces in circular topology
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id}
| | ... | ${type_subif}
| | And Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut1} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Configure L2XC
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_2}
| | And Configure L2XC
| | ... | ${dut1} | ${dut1_if2} | ${subif_index_1}
| | Then Send IPv4 bidirectionally and verify received packets
| | ... | ${tg} | ${tg_if1} | ${tg_if2}

*** Test Cases ***
| tc01-64B-eth-dot1ad-l2xcbase-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
