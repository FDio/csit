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
| ... | NIC_Virtual | ETH | IP4FWD | BASE | IP4BASE | 1TAP | NAMESPACE
| ... | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethicmpv4-ip4base-eth-1tap-namespace
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test | namespace
| Test Teardown | Tear down test | packet_trace | namespace
|
| Test Template | Local Template
|
| Documentation | *Tap Interface Traffic Tests*
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG)
| ... | are set depending on test case; Namespaces (NM)
| ... | are set on DUT1 with attached linux-TAP.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets
| ... | are sent by TG on link to DUT1; On receipt TG verifies packets
| ... | for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
| ${tap1_VPP_ip}= | 16.0.10.1
| ${tap1_NM_ip}= | 16.0.10.2
| ${tap1_NM_mac}= | 02:00:00:00:00:02
| ${dut_ip_address}= | 192.168.0.1
| ${tg_ip_address}= | 192.168.0.2
| ${tg_ip_address_GW}= | 192.168.0.0
| ${prefix}= | 24

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure two interface addresses with IPv4 of which\
| | ... | one is TAP interface (dut_to_tg_if and TAP) and one is linux-TAP in\
| | ... | namespace.
| | ... | [Ver] Packet sent from TG gets to the destination and ICMP-reply is\
| | ... | received on TG.
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
| | ${int1}= | And Add Tap Interface | ${dut1} | tap0
| | And VPP Interface Set IP Address
| | ... | ${dut1} | ${int1} | ${tap1_VPP_ip} | ${prefix}
| | And VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut_ip_address} | ${prefix}
| | And Set Interface State | ${dut1} | ${int1} | up
| | And Create Namespace | ${dut1} | nmspace1
| | And Attach Interface To Namespace | ${dut1} | nmspace1 | tap0
| | And Set Linux Interface MAC
| | ... | ${dut1} | tap0 | ${tap1_NM_mac} | nmspace1
| | And Set Linux Interface IP
| | ... | ${dut1} | tap0 | ${tap1_NM_ip} | ${prefix} | nmspace1
| | And VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${tg_ip_address} | ${TG_pf1_mac}[0]
| | And VPP Add IP Neighbor
| | ... | ${dut1} | ${int1} | ${tap1_NM_ip} | ${tap1_NM_mac}
| | And Add Linux Route
| | ... | ${dut1} | ${tg_ip_address_GW} | ${prefix} | ${tap1_VPP_ip} | nmspace1
| | Then Send ICMP echo request and verify answer
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_vf1_mac}[0] | ${TG_pf1_mac}[0]
| | ... | ${tap1_NM_ip} | ${tg_ip_address}

*** Test Cases ***
| tc01-64B-ethicmpv4-ip4base-eth-1tap-namespace-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
