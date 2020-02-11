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
| Library  | resources.libraries.python.HoststackUtil
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/hoststack/hoststack.robot
|
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| ... | NIC_Intel-X710 | DRV_VFIO_PCI | UDP | QUIC | VPPECHO
| ... | HOSTSTACK | eth-ip4udpquic-vppecho
|
| Suite Setup | Setup suite single link no tg
| Suite Teardown | Tear down suite
| Test Setup | Setup test
| Test Teardown | Tear down test
|
| Test Template | Local template
|
| Documentation | *QUIC Unidirectional Echo Client -> Echo Server throughput.
|
| ... | *[Top] Network Topologies:* DUT-DUT 2-node topology
| ... | with single link between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP-QUIC
| ... | *[Cfg] DUT configuration:*
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | quic_plugin.so
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}
| ${frame_size}= | ${9000}
| ${crypto_type}= | ${None}

*** Keywords ***
| Local template
| | [Arguments] | ${phy_cores} | ${clients} |  ${streams} | ${bytes}
| |
| | Set VPP Hoststack Attributes | phy_cores=${phy_cores}
| | Set VPP Echo Server Attributes | cfg_vpp_feature=quic | nclients=${clients}
| | ... | quic_streams=${streams} | rx_bytes=${bytes}
| | Set VPP Echo Client Attributes | cfg_vpp_feature=quic | nclients=${clients}
| | ... | quic_streams=${streams} | tx_bytes=${bytes}
| | ${no_results}= | Get Test Results From Hoststack VPP Echo Test
| | Run Keyword If | ${no_results}==True | FAIL
| | ... | No Test Results From External Hoststack Apps

*** Test Cases ***
| tc01-1cl1s-9000B-1c-eth-ip4udpquic-vppecho-bps
| | [Tags] | 1C | 1CLIENT | 1STREAM
| | phy_cores=${1} | clients=${1} | streams=${1} | bytes=10G

| tc02-1cl10s-9000B-1c-eth-ip4udpquic-vppecho-bps
| | [Tags] | 1C | 1CLIENT | 10STREAM
| | phy_cores=${1} | clients=${1} | streams=${10} | bytes=1G

| tc03-10cl1s-9000B-1c-eth-ip4udpquic-vppecho-bps
| | [Tags] | 1C | 10CLIENT | 1STREAM
| | phy_cores=${1} | clients=${10} | streams=${1} | bytes=1G

| tc04-10cl10s-9000B-1c-eth-ip4udpquic-vppecho-bps
| | [Tags] | 1C | 10CLIENT | 10STREAM
| | phy_cores=${1} | clients=${10} | streams=${10} | bytes=100M
