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
| ... | NIC_Virtual | ETH | L2BDMACLRN | FEATURE | ACL | ACL_STATELESS
| ... | IACL | ACL1 | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethipv4-l2bdmaclrn-iacl1sl
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | acl | packet_trace
|
| Test Template | Local Template
|
| Documentation | *L2BD test cases with ACL*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 on all links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with L2 bridge domain\
| ... | and MAC learning enabled.Required ACL rules are applied to input\
| ... | paths of both DUT1 intefaces.\
| ... | *[Ver] TG verification:* Test IPv4 packets are sent in one direction \
| ... | by TG on link to DUT1; on receive TG verifies packets for correctness \
| ... | and drops as applicable.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | acl_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
# ACL test setup
| ${acl_action}= | permit
| ${acl_apply_type}= | input
| ${no_hit_aces_number}= | 1
# starting points for non-hitting ACLs
| ${src_ip_start}= | 30.30.30.1
| ${dst_ip_start}= | 40.40.40.1
| ${ip_step}= | ${1}
| ${sport_start}= | ${1000}
| ${dport_start}= | ${1000}
| ${port_step}= | ${1}
| ${trex_stream1_subnet}= | 10.10.10.0/24
| ${trex_stream2_subnet}= | 20.20.20.0/24

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT runs L2BD config with ACLs.
| | ... | [Ver] Make TG send IPv4 packet in one direction between two\
| | ... | of its interfaces to be switched by DUT to and from docker.\
| | ... | Make TG verify IPv4 packet is correct.
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
| | And Apply Startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize L2 bridge domain with IPv4 ACLs in circular topology
| | Then Send packet and verify headers
| | ... | ${tg} | 10.10.10.2 | 20.20.20.2
| | ... | ${TG_pf1}[0] | ${TG_pf1_mac}[0] | ${TG_pf2_mac}[0]
| | ... | ${TG_pf2}[0] | ${TG_pf1_mac}[0] | ${TG_pf2_mac}[0]

*** Test Cases ***
| 64B-ethipv4-l2bdmaclrn-iacl1sl-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
