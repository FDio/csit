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
| ... | NIC_Virtual | IP4FWD | IPSEC | IPSECSW | IPSECINT | IP4BASE
| ... | AES_128_GCM | AES | DRV_VFIO_PCI
|
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local Template
|
| Documentation | *IPv4 IPsec tunnel mode test suite.*
|
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 create loopback interface, configure\
| ... | loopback an physical interface IPv4 addresses, static ARP record, route\
| ... | and IPsec manual keyed connection in tunnel mode.
| ... | *[Ver] TG verification:* ETH-IP4 packet is sent from TG to DUT1. Packet\
| ... | is received on TG from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC4303.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | crypto_native_plugin.so
| ... | crypto_ipsecmb_plugin.so | crypto_openssl_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${54}
| ${tg_spi}= | ${1000}
| ${dut_spi}= | ${1001}
| ${ESP_PROTO}= | ${50}
| ${tg_if1_ip4}= | 192.168.10.2
| ${tg_if2_ip4}= | 192.168.20.2
| ${dut_if1_ip4}= | 192.168.10.1
| ${dut_if2_ip4}= | 192.168.20.1
| ${dut1_if1_ip4}= | 192.168.10.1
| ${dut1_if2_ip4}= | 192.168.20.1
| ${tg_host_ip4}= | 192.168.3.3
| ${raddr_ip4}= | 20.0.0.0
| ${laddr_ip4}= | 10.0.0.0
| ${tun_dut1_if2}= | 200.0.0.2
| ${tun_tg_if2}= | 100.0.0.1
| ${r_ip4}= | 20.0.0.1
| ${l_ip4}= | 10.0.0.1
| ${ip4_plen}= | ${24}
| ${addr_range}= | ${24}
| ${n_tunnels}= | ${1}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES_128_CBC and integrity algorithm HMAC_SHA_512 in tunnel\
| | ... | mode.
|
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| |
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| |
| | Set Test Variable | \${frame_size}
|
| | # These are enums (not strings) so they cannot be in Variables table.
| | ${encr_alg} = | Crypto Alg AES GCM 128
| | ${auth_alg} = | Set Variable | ${NONE}
| | ${ipsec_proto} = | IPsec Proto ESP
|
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize IPSec in 2-node circular topology
| | And VPP IPsec Create Tunnel Interfaces on 2node
| | ... | ${nodes} | ${tun_tg_if2} | ${tun_dut1_if2} | ${dut1_if2}
| | ... | ${tg_if2} | ${n_tunnels} | ${encr_alg} | ${auth_alg}
| | ... | ${laddr_ip4} | ${raddr_ip4} | ${addr_range}
| | Then Send packet and verify headers
| | ... | ${tg} | ${lip4} | ${rip4}
| | ... | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}

*** Test Cases ***
| tc01-110B-ethip4ipsec1tnlsw-ip4base-policy-aes-128-cbc-sha-512-256-dev
| | [Tags] | 110B
| | frame_size=${110} | phy_cores=${0}
