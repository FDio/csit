# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/performance/performance_setup.robot
| Resource | resources/libraries/robot/crypto/ipsec.robot
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | SCALE | SOAK
| ... | IP4FWD | IPSEC | IPSECHW | IPSECTUN | NIC_Intel-XL710 | TNL_1000
| ...
| Suite Setup | Set up IPSec performance test suite | L3 | Intel-XL710
| ... | HW_cryptodev
| Suite Teardown | Tear down 3-node performance topology
| ...
| Test Setup | Set up performance test
| ...
| Test Teardown | Tear down performance mrr test
| ...
| Test Template | Local Template
| ...
| Documentation | *RFC2544: Pkt throughput IPv4 IPsec tunnel mode.*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 on TG-DUTn,
| ... | Eth-IPv4-IPSec on DUT1-DUT2
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with multiple
| ... | IPsec tunnels between them. DUTs get IPv4 traffic from TG, encrypt it
| ... | and send to another DUT, where packets are decrypted and sent back to TG
| ... | *[Ver] TG verification:* Perform PLRsearch to find critical load.

*** Variables ***
# XL710-DA2 bandwidth limit ~49Gbps/2=24.5Gbps
| ${s_24.5G}= | ${24500000000}
# XL710-DA2 Mpps limit 37.5Mpps/2=18.75Mpps
| ${s_18.75Mpps}= | ${18750000}
| ${tg_if1_ip4}= | 192.168.10.2
| ${dut1_if1_ip4}= | 192.168.10.1
| ${dut1_if2_ip4}= | 172.168.1.1
| ${dut2_if1_ip4}= | 172.168.1.2
| ${dut2_if2_ip4}= | 192.168.20.1
| ${tg_if2_ip4}= | 192.168.20.2
| ${raddr_ip4}= | 20.0.0.0
| ${laddr_ip4}= | 10.0.0.0
| ${addr_range}= | ${32}
| ${overhead}= | ${58}
| ${n_tunnels}= | ${1000}
# Traffic profile:
| ${traffic_profile}= | trex-sl-3n-ethip4-ip4dst${n_tunnels}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT runs IPSec tunneling CBC-SHA1 config.\
| | ... | Each DUT uses ${phy_cores} physical core(s) for worker threads.
| | ... | [Ver] Perform PLRsearch to find critical load.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - Framesize in Bytes in integer or string (IMIX_v4_1).
| | ... | Type: integer, string
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${framesize} | ${phy_cores} | ${rxq}=${None}
| | ...
| | ${encr_alg} = | Crypto Alg AES CBC 128
| | ${auth_alg} = | Integ Alg SHA1 96
| | ...
| | Given Add worker threads and rxqueues to all DUTs | ${phy_cores} | ${rxq}
| | And Add PCI devices to all DUTs
| | ${max_rate} | ${jumbo} = | Get Max Rate And Jumbo And Handle Multi Seg
| | ... | ${s_24.5G} | ${framesize} | overhead=${overhead}
| | ... | pps_limit=${s_18.75Mpps}
| | And Add cryptodev to all DUTs | ${phy_cores}
| | And Add DPDK dev default RXD to all DUTs | 2048
| | And Add DPDK dev default TXD to all DUTs | 2048
| | And Apply startup configuration on all VPP DUTs
| | When Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Initialize IPSec in 3-node circular topology
| | And VPP IPsec Create Tunnel Interfaces
| | ... | ${dut1} | ${dut2} | ${dut1_if2_ip4} | ${dut2_if1_ip4} | ${dut1_if2}
| | ... | ${dut2_if1} | ${n_tunnels} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${laddr_ip4} | ${raddr_ip4} | ${addr_range}
| | Then Find critical load using PLRsearch
| | ... | ${framesize} | ${traffic_profile} | ${10000} | ${max_rate}

*** Test Cases ***
| tc01-64B-1c-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1-soak
| | [Tags] | 64B | 1C
| | framesize=${64} | phy_cores=${1}
