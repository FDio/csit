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
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| ... | TCP | NIC_Intel-X710 | DRV_VFIO_PCI | IPERF3_LDPRELOAD
|
| Suite Setup | Setup suite single link no tg
| Suite Teardown | Tear down suite
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
| ${frame_size}= | IMIX_v4_1
| ${crypto_type}= | ${None}

*** Keywords ***
| Local template
| | [Arguments] | ${phy_cores} | ${parallel} | ${time}
| |
| | Set VPP Hoststack Attributes | phy_cores=${phy_cores}
| | Set Iperf3 Client Attributes | parallel=${parallel} | time=${time}
| | ${no_results}= | Get Test Results From Hoststack Iperf3 Test
| | Run Keyword If | ${no_results}==True | FAIL
| | ... | No Test Results From Iperf3 client

*** Test Cases ***
| tc01-IMIX-1c-eth-ip4tcp-ldpreload-iperf3p1-ndrpdr
| | [Documentation]
| | ... | Measure Throughput using iperf3 client & server.
| | ...
| | [Tags] | 1C | IPERF3_P1
| | phy_cores=1 |  parallel=1 | time=60 |

| tc02-IMIX-1c-eth-ip4tcp-ldpreload-iperf3p8-ndrpdr
| | [Documentation]
| | ... | Measure Throughput using iperf3 client & server.
| | ...
| | [Tags] | 1C | IPERF3_P8
| | phy_cores=1 | parallel=8 | time=60 |

| tc03-IMIX-2c-eth-ip4tcp-ldpreload-iperf3p8-ndrpdr
| | [Documentation]
| | ... | Measure Throughput using iperf3 client & server.
| | ...
| | [Tags] | 2C | IPERF3_P8
| | phy_cores=2 | parallel=8 | time=60 |

| tc04-IMIX-4c-eth-ip4tcp-ldpreload-iperf3p8-ndrpdr
| | [Documentation]
| | ... | Measure Throughput using iperf3 client & server.
| | ...
| | [Tags] | 4C | IPERF3_P8
| | phy_cores=4 | parallel=8 | time=60 |
