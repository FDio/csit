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
| ... | NIC_Virtual | IP4FWD | IPSEC | IPSECSW | IPSECTPT | IP4BASE
| ... | AES_128_CBC | HMAC_SHA_512 | HMAC | AES | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4ipsec1tptsw-ip4base-policy-aes-128-cbc-sha-512-256
|
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local Template
|
| Documentation | *IPv4 IPsec transport mode test suite.*
|
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 create loopback interface, configure\
| ... | loopback an physical interface IPv4 addresses, static ARP record, route\
| ... | and IPsec manual keyed connection in transport mode.
| ... | *[Ver] TG verification:* ESP packet is sent from TG to DUT1. ESP packet\
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
| ${overhead}= | ${54}
| ${tg_spi}= | ${1000}
| ${dut_spi}= | ${1001}
| ${ESP_PROTO}= | ${50}
| ${tg_if1_ip4}= | 192.168.100.2
| ${tg_if2_ip4}= | 192.168.4.4
| ${dut_if1_ip4}= | 192.168.100.3
| ${dut_if2_ip4}= | 192.168.4.3
| ${tg_host_ip4}= | 192.168.3.3
| ${ip4_plen}= | ${24}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES_128_CBC and integrity algorithm HMAC_SHA_512 in\
| | ... | transport mode.
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
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 512 256
| |
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Configure topology for IPv4 IPsec testing
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut1} | ${dut1_if1} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${tg_dst_ip} | ${tg_src_ip}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg} | ${tg_if1} | ${tg_if2} | ${dut1_if1_mac} | ${dut1_if2_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${tg_dst_ip}

*** Test Cases ***
| tc01-110B-ethip4ipsec1tptsw-ip4base-policy-aes-128-cbc-sha-512-256-dev
| | [Tags] | 110B
| | frame_size=${110} | phy_cores=${0}
