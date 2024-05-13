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
| ... | NIC_Intel-X710 | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0 | UDP | QUIC | VPPECHO
| ... | 1CLIENT | 1STREAM | HOSTSTACK | 1280B | eth-ip4udpquicbase-vppecho
|
| Suite Setup | Setup suite topology interfaces with no TG | vppecho
| Suite Teardown | Tear down suite
| Test Setup | Setup test
| Test Teardown | Tear down test
|
| Test Template | Local template
|
| Documentation | **QUIC Unidirectional Echo Client -> Echo Server goodput.**
| ... |
| ... | - **[Top] Network Topologies:** DUT-DUT 2-node topology \
| ... | with single link between nodes.
| ... |
| ... | - **[Enc] Packet Encapsulations:** Eth-IPv4-UDP-QUIC
| ... |
| ... | - **[Cfg] DUT configuration:**
| ... |
| ... | - **[Ref] Applicable standard specifications:**

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so | quic_plugin.so | crypto_openssl_plugin.so
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
| ${frame_size}= | ${1518}
| ${crypto_type}= | ${None}
| ${bytes}= | 5G

*** Keywords ***
| Local template
| | [Arguments] | ${phy_cores}
| |
| | Set VPP Hoststack Attributes | phy_cores=${phy_cores}
| | Set VPP Echo Server Attributes | cfg_vpp_feature=quic | rx_bytes=${bytes}
| | Set VPP Echo Client Attributes | cfg_vpp_feature=quic | tx_bytes=${bytes}
| | ${defer_fail}= | Get Test Results From Hoststack VPP Echo Test
| | Run Keyword If | ${defer_fail}==True | FAIL
| | ... | Defered Failure From Hoststack VPP Echo Test Program

*** Test Cases ***
| 1280B-1c-eth-ip4udpquicbase-vppecho-bps
| | [Tags] | 1C
| | phy_cores=${1}
