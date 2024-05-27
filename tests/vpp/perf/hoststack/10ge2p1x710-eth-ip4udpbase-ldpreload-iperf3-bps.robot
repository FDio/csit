# Copyright (c) 2024 Cisco and/or its affiliates.
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
| Library  | resources.libraries.python.HoststackUtil
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/hoststack/hoststack.robot
|
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| ... | UDP | NIC_Intel-X710 | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0 | HOSTSTACK
| ... | LDPRELOAD | IPERF3 | 1CLIENT | 1STREAM | 1460B
| ... | eth-ip4udpbase-ldpreload-iperf3
|
| Suite Setup | Setup suite topology interfaces with no TG | iPerf3
| Suite Teardown | Tear down suite | hoststack
| Test Setup | Setup test
| Test Teardown | Tear down test
|
| Test Template | Local template
|
| Documentation | **Iperf3 client -> Iperf3 server goodput.**
| ... |
| ... | - **[Top] Network Topologies:** DUT-DUT 2-node topology \
| ... | with single link between nodes.
| ... |
| ... | - **[Enc] Packet Encapsulations:** Eth-IPv4-UDP
| ... |
| ... | - **[Cfg] DUT configuration:**
| ... |
| ... | - **[Ref] Applicable standard specifications:**

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
| ${dpdk_no_tx_checksum_offload}= | ${False}
| ${frame_size}= | ${1518}
| ${crypto_type}= | ${None}
| ${iperf3_packet_length}= | ${1460}

*** Keywords ***
| Local template
| | [Arguments] | ${phy_cores}
| |
| | Set VPP Hoststack Attributes | phy_cores=${phy_cores}
| | ${bandwidth} = | Get From Dictionary
| | ... | ${NIC_NAME_TO_BPS_LIMIT} | ${nic_name}
| | Set Iperf3 Client Attributes | udp=${True} | bandwidth=${bandwidth}
| | ... | length=${iperf3_packet_length}
| | ${defer_fail}= | Get Test Results From Hoststack Iperf3 Test
| | Run Keyword If | ${defer_fail}==True | FAIL
| | ... | Defered Failure From Hoststack Iperf3 Test Program

*** Test Cases ***
| 1460B-1c-eth-ip4udpbase-ldpreload-iperf3-bps
| | [Tags] | 1C
| | phy_cores=${1}
