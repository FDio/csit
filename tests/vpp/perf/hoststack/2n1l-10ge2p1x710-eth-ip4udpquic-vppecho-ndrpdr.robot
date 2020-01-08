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
| ... | NIC_Intel-X710 | DRV_VFIO_PCI | QUIC | QUIC_NOCRYPTO
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
| ${frame_size}= | IMIX_v4_1
| ${crypto_type}= | ${None}

*** Keywords ***
| Local template
| | [Arguments] | ${nclients} | ${quic_streams} | ${num_bytes}
| |
| | Set VPP Echo Server Attributes | cfg_vpp_feature=quic | nclients=${nclients}
| | ... | quic_streams=${quic_streams} | rx_bytes=${num_bytes}
| | Set VPP Echo Client Attributes | cfg_vpp_feature=quic | nclients=${nclients}
| | ... | quic_streams=${quic_streams} | tx_bytes=${num_bytes}
| | ${no_results}= | Get Test Results From Hoststack VPP Echo Test
| | Run Keyword If | ${no_results}==True | FAIL
| | ... | No Test Results From External Hoststack Apps

*** Test Cases ***
| tc01-IMIX-1c-eth-ip4udpquic-vppecho1q1s-ndrpdr
| | [Documentation]
| | ... | Measure Throughput using VPP Echo Client & Server
| | ...
| | [Tags] | 1C | QUIC_NCLIENTS_1Q1S
| | nclients=1 | quic_streams=1 | num_bytes=100M

| tc02-IMIX-1c-eth-ip4udpquic-vppecho1q10s-ndrpdr
| | [Documentation]
| | ... | Measure Throughput using VPP Echo Client & Server
| | ...
| | [Tags] | 1C | QUIC_NCLIENTS_1Q10S
| | nclients=1 | quic_streams=10 | num_bytes=100M

| tc03-IMIX-1c-eth-ip4udpquic-vppecho10q1s-ndrpdr
| | [Documentation]
| | ... | Measure Throughput using VPP Echo Client & Server
| | ...
| | [Tags] | 1C | QUIC_NCLIENTS_10Q1S
| | nclients=10 | quic_streams=1 | num_bytes=100M

| tc04-IMIX-1c-eth-ip4udpquic-vppecho10q10s-ndrpdr
| | [Documentation]
| | ... | Measure Throughput using VPP Echo Client & Server
| | ...
| | [Tags] | 1C | QUIC_NCLIENTS_10Q10S
| | nclients=10 | quic_streams=10 | num_bytes=100M
