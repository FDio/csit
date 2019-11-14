
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
| ... | NIC_Virtual | ETH | L2BDMACLRN | FEATURE | ACL | ACL_STATELESS
| ... | IACL | MACIP_ACL_10
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | macipacl
| ...
| Test Template | Local Template
| ...
| Documentation | *L2BD MACIP ACL test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 on TG-DUT1 (if1) link.
| ... | [Cfg] Configure bridge on DUT1 both interfaces to TG\
| ... | and configure L2 MACIP ACLs on ingress interface.
| ... | [Ver] Send simple UDP packet from one TG interface to the DUT1,\
| ... | and verify UDP header in received packet.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | acl_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}
| ${osi_layer}= | L2
# ACL test setup
| ${acl_action}= | permit
| ${no_hit_aces_number}= | 10
# starting points for non-hitting ACLs
| ${src_ip_start}= | 30.30.30.1
| ${ip_step}= | ${1}
| ${src_mac_start}= | 00:00:00:00:00:00
| ${src_mac_step}= | ${1000}
| ${src_mac_mask}= | 00:00:00:00:00:00
| ${tg_stream1_mac}= | 00:00:00:00:00:00
| ${tg_stream2_mac}= | 00:00:00:00:00:00
| ${tg_mac_mask}= | ff:ff:ff:ff:c0:00
| ${tg_stream1_subnet}= | 10.10.10.0/24
| ${tg_stream2_subnet}= | 20.20.20.0/24

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure Bridge Domain and apply MACIP ACL.
| | ...
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| | ...
| | Set Test Variable | \${frame_size}
| | Set Test Variable | ${src_mac_start} | ${tg_if1_mac}
| | Set Test Variable | ${tg_stream1_mac} | ${tg_if1_mac}
| | Set Test Variable | ${tg_stream2_mac} | ${tg_if2_mac}
| | ...
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize L2 bridge domain with MACIP ACLs
| | Then Send packet and verify headers | ${tg}
| | ... | 10.10.10.2 | 20.20.20.2
| | ... | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${tg_if2} | ${tg_if1_mac} | ${dut1_if1_mac}

*** Test Cases ***
| tc01-64B-1c-eth-l2bdbasemaclrn-macip-iacl-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}

