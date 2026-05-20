# Copyright (c) 2026 Cisco and/or its affiliates.
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
| ... | RXQ_SIZE_0 | TXQ_SIZE_0 | UDP | QUIC | VPERF
| ... | 1CLIENT | 1STREAM | HOSTSTACK | 1280B | eth-ip4quicbase-vperf
|
| Suite Setup | Setup suite topology interfaces with no TG | vperf
| Suite Teardown | Tear down suite | hoststack
| Test Setup | Setup test
| Test Teardown | Tear down test
|
| Test Template | Local template
|
| Documentation | **Vperf client -> Vperf server QUIC goodput.**
| ... |
| ... | - **[Top] Network Topologies:** DUT-DUT 2-node topology \
| ... | with single link between nodes.
| ... |
| ... | - **[Enc] Packet Encapsulations:** Eth-IPv4-UDP-QUIC
| ... |
| ... | - **[Cfg] DUT configuration:** vperf_server on DUT2, \
| ... | vperf_client on DUT1 using the VPP app socket API (VCL) with QUIC.
| ... |
| ... | - **[Ref] Applicable standard specifications:**

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so | quic_plugin.so
| ... | quic_quicly_plugin.so | crypto_openssl_plugin.so
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${smt_used}= | ${False}
| ${overhead}= | ${0}
| ${dpdk_enable_tcp_udp_checksum}= | ${True}
| ${dpdk_no_tx_checksum_offload}= | ${False}
| ${quic_perf_config}= | ${True}
| ${frame_size}= | ${1518}
| ${crypto_type}= | ${None}
| ${bytes}= | 61440000000

*** Keywords ***
| Local template
| | [Arguments] | ${phy_cores}
| |
| | Set VPP Hoststack Attributes | phy_cores=${phy_cores}
| | ... | rxd=${512} | sess_evt_q_length=${100000}
| | Set Vperf Server Attributes
| | ... | cfg_vpp_feature=quic | protocol=quic
| | ... | vcl_config=vcl_vperf.conf
| | Set Vperf Client Attributes
| | ... | cfg_vpp_feature=quic | protocol=quic
| | ... | vcl_config=vcl_vperf.conf
| | ... | bytes=${bytes}
| | ${defer_fail}= | Get Test Results From Hoststack Vperf
| | Run Keyword If | ${defer_fail}==True | FAIL
| | ... | Defered Failure From Hoststack Vperf Program

*** Test Cases ***
| 1280B-1c-eth-ip4quicbase-vperf-bps
| | [Tags] | 1C
| | phy_cores=${1}
