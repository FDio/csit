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
| ... | NIC_Intel-X710 | ETH | IP4FWD | FEATURE | IACLDST | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4-ip4base-iacldstbase
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | telemetry | classify
|
| Test Template | Local Template
|
| Documentation | **IPv4 iAcl whitelist test cases**
| ... |
| ... | - **[Top] Network Topologies:** TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... |
| ... | - **[Enc] Packet Encapsulations:** Eth-IPv4 on all links.
| ... |
| ... | - **[Cfg] DUT configuration:** DUT1 is configured with IPv4 routing \
| ... | and static routes. IPv4 iAcl security whitelist is applied on DUT1 \
| ... | ingress interface from TG.
| ... |
| ... | - **[Ver] TG verification:** Test IPv4 packets are sent in one \
| ... | direction by TG on link to DUT1; on receive TG verifies packets for \
| ... | correctness and drops as applicable.
| ... |
| ... | - **[Ref] Applicable standard specifications:**

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
| | ... | - **[Ver]** Make TG send IPv4 on its interface to DUT1; \
| | ... | verify received IPv4 pkts are correct.
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
| | And Initialize IPv4 forwarding in circular topology
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst | 255.255.255.255
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip4 | ${table_idx}
| | Then Send packet and verify headers
| | ... | ${tg} | 10.10.10.2 | 20.20.20.2
| | ... | ${TG_pf1}[0] | ${TG_pf1_mac}[0] | ${DUT1_vf1_mac}[0]
| | ... | ${TG_pf2}[0] | ${DUT1_vf2_mac}[0] | ${TG_pf2_mac}[0]

*** Test Cases ***
| 64B-0c-ethip4-ip4base-iacldstbase-scapy
| | [Tags] | 64B | 0C
| | frame_size=${64} | phy_cores=${0}
