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
| Variables | resources/test_data/lisp/lisp.py
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | IP4FWD | LISPGPE_IP6o4 | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4lispgpe-ip6base
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local Template
|
| Documentation | *ip4-lispgpe-ip6 encapsulation test cases*
|
| ... | *[Top] Network Topologies:* TG(if1)-DUT1-TG(if2) 2-node\
| ... | circular topology with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISPGPE-IPv6-ICMPv6\
| ... | on DUT1-TG(if2),Eth-IPv6-ICMPv6 on TG-DUTn for IPv6\
| ... | routing over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and TG(if2) are configured\
| ... | with IPv6 routing and static routes. LISPoIPv4 tunnel is\
| ... | configured between DUT1 and TG(if2).
| ... | *[Ver] TG verification:* Test ICMPv6 Echo Request packets\
| ... | are sent in if1 by TG on links to DUT1; on receive\
| ... | TG verifies packets for correctness and their IPv6 src-addr,\
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${54}
| ${ot_mode}= | 6to4
| ${is_gpe}= | ${1}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure LISPGPE\
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
| | And Configure topology for IPv6 LISPoIP4 testing
| | And Vpp All RA Suppress Link Layer | ${nodes}
| | And Configure LISP in 2-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip6o4_eid}
| | ... | ${dut1_ip6o4_static_adjacency} | ${is_gpe}
| | Then Send packet and verify LISPoTunnel encap
| | ... | ${tg} | ${tg_if1_ip6} | ${dst_ip6}
| | ... | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
| | ... | ${src_rloc4} | ${dst_rloc4} | ${ot_mode}

*** Test Cases ***
| tc01-62B-ethip4lispgpe-ip6base-dev
| | [Tags] | 62B
| | frame_size=${62} | phy_cores=${0}
