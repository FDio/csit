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
| Resource | resources/libraries/robot/shared/default.robot
|
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | MRR
| ... | NIC_Intel-X710 | IP4FWD | BASE | IP4BASE | DRV_TAPV2
| ... | RXQ_SIZE_0 | TXQ_SIZE_0 | GSO_TRUE
| ... | ethip4-ip4base-2tap-gso

| Suite Setup | Setup suite topology interfaces
| Suite Teardown | Tear down suite
| Test Setup | Setup test
| Test Teardown | Tear down test | iPerf3 | namespace
|
| Test Template | Local Template
|
| Documentation | *RFC2544: Pkt throughput L2BD test cases with vhost and vpp
| ... | link bonding*
|
| ... | *[Top] Network Topologies:* DUT1 1-node topology without physical links.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP for L2 switching of IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with VPP L2 bridge-domain\
| ... | with MAC learning enabled.
| ... | *[Ver] TG verification:* iPerf3 client/server is used for Packet\
| ... | generation and verification.
| ... | *[Ref] Applicable standard specifications:* RFC2544.

*** Variables ***
| @{plugins_to_enable}= | ping_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | Intel-X710
| ${nic_driver}= | tap
| ${nic_rxq_size}= | 4096
| ${nic_txq_size}= | 4096
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${osi_layer}= | L3
| ${overhead}= | ${0}
| ${enable_gso}= | ${True}
# iPerf3 client settings:
| ${iperf_client_bind}= | 1.1.1.1
| ${iperf_client_bind_gw}= | 1.1.1.2
| ${iperf_client_bind_mask}= | 30
| ${iperf_client_interface}= | tap0
| ${iperf_client_udp}= | ${False}
# iPerf3 server settings:
| ${iperf_server_bind}= | 2.2.2.2
| ${iperf_server_bind_gw}= | 2.2.2.1
| ${iperf_server_bind_mask}= | 30
| ${iperf_server_interface}= | tap1

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT1 is configured with VPP L2 bridge-domain with MAC learning\
| | ... | enabled.
| | ... | [Ver] Measure MaxReceivedRate for ${frame_size}B frames\
| | ... | using burst trials throughput test.\
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer, string
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| |
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| |
| | Set Test Variable | \${frame_size}
| |
| | Given Set Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 1.1.1.2 | 30
| | And VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2.2.2.1 | 30
| | Then Traffic should pass with maximum rate on iPerf3

*** Test Cases ***
#| 128KB-1c-ethip4-ip4base-2tap-gso-mrr
#| | [Tags] | 128KB | 1C
#| | frame_size=${128000} | phy_cores=${1}

#| 128KB-2c-ethip4-ip4base-2tap-gso-mrr
#| | [Tags] | 128KB | 2C
#| | frame_size=${128000} | phy_cores=${2}

| 128KB-4c-ethip4-ip4base-2tap-gso-mrr
| | [Tags] | 128KB | 4C
| | frame_size=${128000} | phy_cores=${4}
