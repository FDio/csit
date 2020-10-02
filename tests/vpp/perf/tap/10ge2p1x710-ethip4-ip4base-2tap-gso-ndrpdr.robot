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
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | NDRPDR
| ... | NIC_Intel-X710 | IP4FWD | BASE | IP4BASE | DRV_TAPV2
| ... | RXQ_SIZE_0 | TXQ_SIZE_0 | GSO_TRUE
| ... | l2bdbasemaclrn-2tapv2gso
|
| Suite Setup | Setup suite topology interfaces
| Suite Teardown | Tear down suite | iperf3
| Test Setup | Setup test
| Test Teardown | Tear down test | namespace
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
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${osi_layer}= | L3
| ${overhead}= | ${0}
| ${enable_gso}= | ${True}
# iPerf3 client settings:
| ${iperf_client_bind}= | 10.10.10.1
| ${iperf_client_bind_mask}= | 24
| ${iperf_client_interface}= | tap0
| ${iperf_client_udp}= | ${False}
# iPerf3 server settings:
| ${iperf_server_bind}= | 1.1.1.1
| ${iperf_server_bind_mask}= | 24
| ${iperf_server_interface}= | tap1
# Traffic profile:
| ${traffic_profile}= | iperf3-ethip4udp

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT1 is configured with VPP L2 bridge-domain with MAC learning\
| | ... | enabled.
| | ... | [Ver] Measure NDR and PDR values using MLRsearch algorithm.\
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
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize L2 bridge domain
| | Then Traffic should pass with maximum rate on iPerf3

*** Test Cases ***
| 64000B-1c-ethip4-ip4base-2tap-gso-ndrpdr
| | [Tags] | 64000B | 1C
| | frame_size=${64000} | phy_cores=${1}
