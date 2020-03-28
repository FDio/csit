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
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | IP4FWD | IPSEC | IPSECSW | IPSECINT | IP6BASE
| ... | AES_128_CBC | HMAC_SHA_512 | HMAC | AES | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip6ipsec1tnlsw-ip6base-int-aes128cbc-hmac512sha
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local Template
|
| Documentation | *IPv6 IPsec tunnel mode test suite.*
|
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 create loopback interface, configure\
| ... | loopback an physical interface IPv6 addresses, static ARP record, route\
| ... | and IPsec manual keyed connection in tunnel mode.
| ... | *[Ver] TG verification:* ETH-IP6 packet is sent from TG to DUT1. Packet\
| ... | is received on TG from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC4303.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | crypto_native_plugin.so
| ... | crypto_ipsecmb_plugin.so | crypto_openssl_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${80}
| ${tg_if1_ip6}= | 3ffe:5f::1
| ${dut1_if1_ip6}= | 3ffe:5f::2
| ${tun_if1_ip6}= | 3ffe:60::1
| ${tun_if2_ip6}= | 3ffe:61::2
| ${raddr_ip6}= | 2001::
| ${laddr_ip6}= | 1001::
| ${addr_range}= | ${96}
| ${n_tunnels}= | ${1}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec tunnel interface with encryption\
| | ... | algorithm AES_128_CBC and integrity algorithm HMAC_SHA_512 in tunnel\
| | ... | mode.
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
| | # These are enums (not strings) so they cannot be in Variables table.
| | ${encr_alg} = | Crypto Alg AES CBC 128
| | ${auth_alg} = | Integ Alg SHA 512 256
| |
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize IPSec in 2-node circular topology
| | ${encr_key} | ${auth_key} | ${dut_spi} | ${tg_spi} =
| | ... | And VPP IPsec Create Tunnel Interfaces
| | ... | ${nodes} | ${tun_if1_ip6} | ${tun_if2_ip6} | ${DUT1_${int}2}[0]
| | ... | ${TG_pf2}[0] | ${n_tunnels} | ${encr_alg} | ${auth_alg}
| | ... | ${laddr_ip6} | ${raddr_ip6} | ${addr_range}
| | Then Send IP Packet and verify ESP encapsulation in received packet
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${DUT1_${int}2_mac}[0] | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${laddr_ip6} | ${raddr_ip6}
| | ... | ${tun_if1_ip6} | ${tun_if2_ip6}

*** Test Cases ***
| tc01-158B-ethip6ipsec1tnlsw-ip6base-int-aes-128-cbc-sha-512-256-dev
| | [Tags] | 158B
| | frame_size=${158} | phy_cores=${0}
