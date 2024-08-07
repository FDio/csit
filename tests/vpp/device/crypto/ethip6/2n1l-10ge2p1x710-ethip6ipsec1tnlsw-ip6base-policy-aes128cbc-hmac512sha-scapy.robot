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
| Resource | resources/libraries/robot/shared/default.robot
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Intel-X710 | IP6FWD | IPSEC | IPSECSW | IPSECTUN | IP6BASE
| ... | AES_128_CBC | HMAC_SHA_512 | HMAC | AES | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip6ipsec1tnlsw-ip6base-policy-aes128cbc-hmac512sha
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | telemetry | ipsec_sa
|
| Test Template | Local Template
|
| Documentation | **IPv6 IPsec tunnel mode test suite.**
| ... |
| ... | - **[Top] Network topologies:** TG-DUT1 2-node topology with one link \
| ... | between nodes.
| ... |
| ... | - **[Cfg] DUT configuration:** On DUT1 create loopback interface, \
| ... | configure loopback an physical interface IPv6 addresses, static ARP \
| ... | record, route and IPsec manual keyed connection in tunnel mode.
| ... |
| ... | - **[Ver] TG verification:** ESP packet is sent from TG to DUT1. ESP \
| ... | packet is received on TG from DUT1.
| ... |
| ... | - **[Ref] Applicable standard specifications:** RFC4303.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so
| ... | crypto_native_plugin.so | crypto_ipsecmb_plugin.so
| ... | crypto_openssl_plugin.so
| ${crypto_type}= | ${None}
| ${encr_alg}= | AES CBC 128
| ${auth_alg}= | SHA 512 256
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${54}
| ${tg_spi}= | ${1000}
| ${dut_spi}= | ${1001}
| ${tg_if1_ip6}= | 3ffe:5f::1
| ${tg_if2_ip6}= | 3ffe:60::4
| ${dut_if1_ip6}= | 3ffe:5f::2
| ${dut_if2_ip6}= | 3ffe:60::3
| ${tg_host_ip6}= | 3ffe:61::3
| ${ip6_plen}= | ${64}
| ${ip6_plen_rt}= | ${128}
# Telemetry
| ${telemetry_profile}= | vppctl_test_teardown

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | - **[Cfg]** On DUT1 configure IPsec manual keyed connection with \
| | ... | encryption algorithm AES_128_CBC and integrity algorithm \
| | ... | HMAC_SHA_512 in tunnel mode.
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
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
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Configure topology for IPv6 IPsec testing
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${tg_dst_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip} | is_ipv6=${TRUE}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]
| | ... | ${DUT1_vf1_mac}[0] | ${DUT1_vf2_mac}[0]
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${tg_dst_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

*** Test Cases ***
| 78B-0c-ethip6ipsec1tnlsw-ip6base-policy-aes128cbc-hmac512sha-scapy
| | [Tags] | 78B | 0C
| | frame_size=${78} | phy_cores=${0}
