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
| ... | NIC_Intel-X710 | ETH | L2BD | BASE | 2TAP | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4-l2bdbasemaclrn-eth-2tap
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test | namespace
| Test Teardown | Tear down test | packet_trace | telemetry | namespace
| ... | linux_bridge
|
| Test Template | Local Template
|
| Documentation | **Tap Interface Traffic Tests**
| ... |
| ... | - **[Top] Network Topologies:** TG=DUT1 2-node topology with two links \
| ... | between nodes.
| ... |
| ... | - **[Enc] Packet Encapsulations:** Eth-IPv4 for L2 switching of \
| ... | IPv4.
| ... |
| ... | - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 \
| ... | bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG) \
| ... | are set depending on test case; Namespaces (NM) \
| ... | are set on DUT1 with attached linux-TAP.
| ... |
| ... | - **[Ver] TG verification:** Test IPv4 packets with IP protocol=61 \
| ... | are sent by TG on link to DUT1; On receipt TG verifies packets \
| ... | for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.
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
| ${bid_TAP}= | tapBr
# Telemetry
| ${telemetry_profile}= | vppctl_test_teardown

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | - **[Ver]** Packet sent from TG is passed through all L2BD and \
| | ... | received back on TG. Then src_ip, dst_ip and MAC are checked.
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
| | ${int2}= | And Add Tap Interface | ${dut1} | tap1
| | And Set Interface State | ${dut1} | ${int1} | up
| | And Set Interface State | ${dut1} | ${int2} | up
| | And Create L2 BD | ${dut1} | 19 | learn=${TRUE}
| | And Create L2 BD | ${dut1} | 20 | learn=${TRUE}
| | And Linux Add Bridge | ${dut1} | ${bid_TAP} | tap0 | tap1
| | And Add interface to bridge domain | ${dut1} | ${int1} | 20 | 0
| | And Add interface to bridge domain | ${dut1} | ${DUT1_${int}1}[0] | 20 | 0
| | And Add interface to bridge domain | ${dut1} | ${int2} | 19 | 0
| | And Add interface to bridge domain | ${dut1} | ${DUT1_${int}2}[0] | 19 | 0
| | Then Send IP packet and verify received packet
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]

*** Test Cases ***
| 64B-0c-ethip4-l2bdbasemaclrn-eth-2tap-scapy
| | [Tags] | 64B | 0C
| | frame_size=${64} | phy_cores=${0}
