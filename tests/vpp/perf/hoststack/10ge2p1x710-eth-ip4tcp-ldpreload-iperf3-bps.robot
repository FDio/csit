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
| ... | TCP | NIC_Intel-X710 | DRV_VFIO_PCI | HOSTSTACK
| ... | LDPRELOAD | IPERF3 | eth-ip4tcp-ldpreload-iperf3
|
| Suite Setup | Setup suite single link no tg
| Suite Teardown | Tear down suite | hoststack
| Test Setup | Setup test
| Test Teardown | Tear down test
|
| Test Template | Local template
|
| Documentation | *Iperf3 client -> Iperf3 server throughput.
|
| ... | *[Top] Network Topologies:* DUT-DUT 2-node topology
| ... | with single link between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-TCP
| ... | *[Cfg] DUT configuration:*
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}
| ${frame_size}= | ${9000}
| ${crypto_type}= | ${None}

*** Keywords ***
| Local template
| | [Arguments] | ${phy_cores} | ${clients} | ${streams}
| |
| | Set Test Variable | ${dpdk_no_tx_checksum_offload} | ${False}
| | Set VPP Hoststack Attributes | phy_cores=${phy_cores}
| | Set Iperf3 Client Attributes | parallel=${streams}
| | ${no_results}= | Get Test Results From Hoststack Iperf3 Test
| | Run Keyword If | ${no_results}==True | FAIL
| | ... | No Test Results From Iperf3 client

*** Test Cases ***
| tc01-1cl1s-9000B-1c-eth-ip4tcp-ldpreload-iperf3-bps
| | [Tags] | 1C | 1CLIENT | 1STREAM
| | phy_cores=${1} | clients=${1} | streams=${1}

| tc02-1cl10s-9000B-1c-eth-ip4tcp-ldpreload-iperf3-bps
| | [Tags] | 1C | 1CLIENT | 10STREAM
| | phy_cores=${1} | clients=${1} | streams=${10}
