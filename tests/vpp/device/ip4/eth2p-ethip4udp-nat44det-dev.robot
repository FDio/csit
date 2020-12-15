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
| Resource | resources/libraries/robot/ip/nat.robot
| Resource | resources/libraries/robot/shared/traffic.robot
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | ETH | IP4FWD | FEATURE | NAT44 | NAT44_DETERMINISTIC
| ... | BASE | UDP | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4udp-nat44det-dev
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | det44
|
| Test Template | Local Template
|
| Documentation | *NAT44 deterministic mode test cases*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP for IPv4 routing.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and
| ... | one static IPv4 /${dest_mask} route entries.
| ... | DUT1 is tested with ${nic_name}.\
| ... | *[Ver] TG verification:* Eth-IPv4-UDP packet is sent from TG to DUT1 in\
| ... | one direction. Packet is received and verified for correctness on TG.\
| ... | Then Eth-IPv4-UDP packet is sent from TG in opposite direction. Packet\
| ... | is received and verified for correctness on TG.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC768, RFC3022,
| ... | RFC4787.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | det44_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
# IP addresing
| ${tg_if1_ip4}= | 10.0.0.2
| ${tg_if1_mask}= | ${20}
| ${tg_if2_ip4}= | 12.0.0.2
| ${tg_if2_mask}= | ${20}
| ${dut1_if1_ip4}= | 10.0.0.1
| ${dut1_if1_mask}= | ${20}
| ${dut1_if2_ip4}= | 12.0.0.1
| ${dut1_if2_mask}= | ${20}
| ${dest_net}= | 30.0.0.0
| ${dest_mask}= | ${24}
# proto layer settings
| ${protocol}= | UDP
| ${src_port_in}= | 1024
| ${dst_port}= | 8080
# NAT settings
| ${nat_mode}= | deterministic
| ${in_net}= | 20.0.0.0
| ${in_mask}= | ${32}
| ${out_net}= | 200.0.0.0
| ${out_mask}= | ${32}

*** Keywords ***
| Local Template
| |
| | [Documentation]
| | ... | [Cfg] DUT runs NAT44 ${nat_mode} configuration.
| | ... | [Ver] Make TG send IPv4 packet routed over DUT1 interfaces.\
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
| | Given Set Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | ... | ${lock_file}=${lock_file_path}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize IPv4 forwarding for NAT44 in circular topology
| | And Initialize NAT44 deterministic mode in circular topology
| | Then Send TCP or UDP packet and verify network address translations
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0] | ${DUT1_vf1_mac}[0]
| | ... | ${DUT1_vf2_mac}[0] | ${in_net} | ${out_net} | ${dest_net}
| | ... | ${protocol} | ${src_port_in} | ${dst_port}

*** Test Cases ***
| 64B-ethip4udp-nat44det-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
