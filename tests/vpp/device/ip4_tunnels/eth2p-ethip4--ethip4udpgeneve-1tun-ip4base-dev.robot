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
| Resource | resources/libraries/robot/ip/geneve.robot
| Resource | resources/libraries/robot/shared/traffic.robot
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | ETH | IP4FWD | IP4BASE | UDP | ENCAP | GENEVE
| ... | GENEVE_L3MODE | GENEVE4_1TUN | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4--ethip4udpgeneve-1tun-ip4base
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | geneve4
|
| Test Template | Local Template
|
| Documentation | *L2BD with GENEVE L3 mode test cases*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 between TG-if1 and DUT1-if1 and\
| ... | Eth-IPv4-UDP-GENEVE-Eth-IPv4 between DUT1-if2 and TG-if2 for IPv4\
| ... | routing over GENEVE tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing over\
| ... | GENEVE tunnel and 4 static IPv4 /24 route entries.\
| ... | DUT1 is tested with ${nic_name}.
| ... | *[Ver] TG verification:* Test Eth-IPv4 packet is sent by TG-if1 on link\
| ... | to DUT1-if1; on receive by TG-if2 the encapsulated packet is verified\
| ... | for correctness and its outer and inner IPv4 and MAC addresses, UDP\
| ... | ports and GENEVE vni and protocol number. Then test\
| ... | Eth-IPv4-UDP-GENEVE-Eth-IPv4 packet is sent by TG-if2 on link to\
| ... | DUT1-if2; on receive by TG-if1 decapsulated packet is verified for\
| ... | correctness and its IPv4 and MAC addresses
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC768, RFC8926.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | geneve_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
# IP settings
| ${dut1_if1_ip4}= | 20.0.0.1
| ${dut1_if2_ip4}= | 30.0.0.1
| ${tg_if1_ip4}= | 20.0.0.2
| ${tg_if2_ip4}= | 30.0.0.2
# GENEVE settings
| ${gen_mode}= | L3
| ${n_tunnels}= | ${1}
| &{gen_tunnel}=
| ... | local=1.1.1.2 | remote=1.1.1.1 | vni=${1}
| ... | src_ip=10.128.1.0 | dst_ip=10.0.1.0 | ip_mask=${24} | if_ip=11.0.1.2

*** Keywords ***
| Local Template
| |
| | [Documentation]
| | ... | [Cfg] DUT runs GENEVE ${gen_mode} mode configuration.
| | ... | Each DUT uses ${phy_cores} physical core(s) for worker threads.
| | ... | [Ver] Measure NDR and PDR values using MLRsearch algorithm.\
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
| | ... | lock_path=${lock_dir}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize GENEVE L3 mode in circular topology
| | Then Send IP packet and verify GENEVE encapsulation in received packets
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]
| | ... | ${DUT1_vf1_mac}[0] | ${DUT1_vf2_mac}[0]
| | ... | ${gen_tunnel}[local] | ${gen_tunnel}[remote] | ${gen_tunnel}[vni]
| | ... | ${gen_tunnel}[src_ip] | ${gen_tunnel}[dst_ip]
| | And Show Geneve Tunnel Data | ${nodes['DUT1']}

*** Test Cases ***
| 64B-ethip4--ethip4udpgeneve-1tun-ip4base-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
