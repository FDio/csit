# Copyright (c) 2022 Cisco and/or its affiliates.
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
| ... | NIC_Intel-X710 | ETH | L2BDMACLRN | BASE | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4-l2bdbasemaclrn
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | telemetry
|
| Test Template | Local Template
|
| Documentation | **L2 bridge-domain test cases**
| ... |
| ... | - **[Top] Network Topologies:** TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... |
| ... | - **[Enc] Packet Encapsulations:** Eth-IPv4 for L2 switching of IPv4. \
| ... | Both apply to all links.
| ... |
| ... | - **[Cfg] DUT configuration:** DUT1 is configured with L2 \
| ... | cross-connect switching.
| ... |
| ... | - **[Ver] TG verification:** Test IPv4 packets with IP protocol=61 \
| ... | are sent in both directions by TG on links to DUT1; on receive TG. \
| ... | verifies packets for correctness and their IPv4 src-addr, \
| ... | dst-addr and MAC addresses.
| ... |
| ... | - **[Ref] Applicable standard specifications:** RFC792

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
# Telemetry
| ${telemetry_profile}= | vppctl_test_teardown

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | - **[Ver]** Make TG send IPv4 packets in both directions between two \
| | ... | of its interfaces to be switched by DUT to and from docker; verify \
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
| | And Initialize L2 bridge domain
| | Then Send IPv4 bidirectionally and verify received packets
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]

*** Test Cases ***
| 64B-0c-ethip4-l2bdbasemaclrn-scapy
| | [Tags] | 64B | 0C
| | frame_size=${64} | phy_cores=${0}
