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
| ... | NIC_Intel-X710 | IP4FWD | IPSEC | IPSECSW | IPSECINT | IP4BASE
| ... | AES_128_CBC | HMAC_SHA_512 | HMAC | AES | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4ipsec1tnlsw-ip4base-int-aes128cbc-hmac512sha
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | telemetry | ipsec_sa
|
| Test Template | Local Template
|
| Documentation | **IPv4 IPsec tunnel mode test suite.**
| ... |
| ... | - **[Top] Network topologies:** TG-DUT1 2-node topology with one link \
| ... | between nodes.
| ... |
| ... | - **[Cfg] DUT configuration:** On DUT1 create loopback interface, \
| ... | configure loopback an physical interface IPv4 addresses, static ARP \
| ... | irecord, route and IPsec manual keyed connection in tunnel mode.
| ... |
| ... | - **[Ver] TG verification:** ETH-IP4 packet is sent from TG to DUT1. \
| ... | Packet is received on TG from DUT1.
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
| ${overhead}= | ${90}
| ${tg_if1_ip4}= | 192.168.10.2
| ${dut1_if1_ip4}= | 192.168.10.1
| ${tun_if1_ip4}= | 100.0.0.1
| ${tun_if2_ip4}= | 200.0.0.2
| ${raddr_ip4}= | 20.0.0.0
| ${laddr_ip4}= | 10.0.0.0
| ${addr_range}= | ${24}
| ${n_tunnels}= | ${1}
# Telemetry
| ${telemetry_profile}= | vppctl_test_teardown

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | - **[Cfg]** On DUT1 configure IPsec tunnel interface with encryption \
| | ... | algorithm AES_128_CBC and integrity algorithm HMAC_SHA_512 in \
| | ... | tunnel mode.
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
| | And Initialize IPSec in 2-node circular topology
| | ${encr_keys} | ${auth_keys} | ${dut_spi} | ${tg_spi} =
| | ... | And VPP IPsec Create Tunnel Interfaces
| | ... | ${nodes} | ${tun_if1_ip4} | ${tun_if2_ip4} | ${DUT1_${int}2}[0]
| | ... | ${TG_pf2}[0] | ${n_tunnels} | ${encr_alg} | ${auth_alg}
| | ... | ${laddr_ip4} | ${raddr_ip4} | ${addr_range} | return_keys=${True}
| | Then Send IP Packet and verify ESP encapsulation in received packet
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${DUT1_${int}2_mac}[0] | ${encr_alg} | ${encr_keys}[0] | ${auth_alg}
| | ... | ${auth_keys}[0] | ${dut_spi} | ${tg_spi} | ${laddr_ip4} | ${raddr_ip4}
| | ... | ${tun_if1_ip4} | ${tun_if2_ip4}

*** Test Cases ***
| 64B-0c-ethip4ipsec1tnlsw-ip4base-int-aes128cbc-hmac512sha-scapy
| | [Tags] | 64B | 0C
| | frame_size=${64} | phy_cores=${0}
