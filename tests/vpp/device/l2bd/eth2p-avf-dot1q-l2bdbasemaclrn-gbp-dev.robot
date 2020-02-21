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
| ... | NIC_Virtual | DOT1Q | L2BDMACLRN | BASE | DRV_AVF | GBP
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | avf-dot1q-l2bdbasemaclrn-gbp
|
| Suite Setup | Setup suite topology interfaces | scapy
| Suite Teardown | Tear down suite
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local template
|
| Documentation | *L2BD with IEEE 802.1Q and GBP test cases*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Dot1q-IPv4 for L2 switching of IPv4. \
| ... | IEEE 802.1Q tagging is applied on both links TG-DUT1 .
| ... | *[Cfg] DUT configuration:* DUT1 is configured with:\
| ... | 2 VLAN subinterfaces (VID 200 and 300),\
| ... | 1 L2 BD with the 2 VLAN subinterfaces and a BVI,\
| ... | 1 GBP L3 RD,\
| ... | 1 GBP L2 BD with the L2 BD,\
| ... | 1 GBP EPG EPG-1 with sclass 100, the GBP L2 BD and L3 RD,\
| ... | 2 GBP external EP in EPG-1,\
| ... | 2 external subnets with sclass 200 and 300,\
| ... | Contracts allowing full communications between the 2 external subnets.\
| ... | DUT1 tested with ${nic_name} with VF enabled.
| ... | *[Ver] TG verification:* Test IPv4 packets are sent in one direction \
| ... | by TG on link to DUT1; on receive TG verifies packets for correctness \
| ... | and drops as applicable.
| ... | *[Ref] Applicable standard specifications:* IEEE 802.1q.

*** Variables ***
| @{plugins_to_enable}= | avf_plugin.so | gbp_plugin.so | acl_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | avf
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 1
| ${overhead}= | ${4}

*** Keywords ***
| Local template
| | [Documentation]
| | ... | [Ver] Make TG send IPv4 packet in one direction between two\
| | ... | of its interfaces to be switched by DUT to and from docker.\
| | ... | Make TG verify IPv4 packet is correct.
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
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize layer dot1q
| | And Initialize GBP routing domains
| | Then Send packet and verify headers
| | ... | ${tg} | 10.10.10.2 | 20.20.20.2
| | ... | ${TG_pf1}[0] | ${TG_pf1_mac}[0] | ba:dc:00:ff:ee:01
| | ... | ${TG_pf2}[0] | ba:dc:00:ff:ee:01 | ${TG_pf2_mac}[0]
| | ... | traffic_script=send_ip_check_headers

*** Test Cases ***
| tc01-64B-avf-dot1q-l2bdbasemaclrn-gbp-dev
| | [Tags] | 64B | 1C
| | frame_size=${64} | phy_cores=${0}
