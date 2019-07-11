# Copyright (c) 2019 Cisco and/or its affiliates.
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
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | IP4FWD | IPSEC | IPSECSW | IPSECTUN | IP4BASE
| ... | AES_256_GCM | AES
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
| ...
| Test Template | Local Template
| ...
| Documentation | *IPv4 IPsec tunnel mode test suite.*
| ...
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 create loopback interface, configure\
| ... | loopback an physical interface IPv4 addresses, static ARP record, route\
| ... | and IPsec manual keyed connection in tunnel mode.
| ... | *[Ver] TG verification:* ESP packet is sent from TG to DUT1. ESP packet\
| ... | is received on TG from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC4303.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | crypto_ia32_plugin.so
| ... | crypto_ipsecmb_plugin.so | crypto_openssl_plugin.so
| ${nic_name}= | virtual
| ${overhead}= | ${54}
| ${tg_spi}= | ${1000}
| ${dut_spi}= | ${1001}
| ${ESP_PROTO}= | ${50}
| ${tg_if_ip4}= | 192.168.100.2
| ${dut_if_ip4}= | 192.168.100.3
| ${tg_lo_ip4}= | 192.168.3.3
| ${dut_lo_ip4}= | 192.168.4.4
| ${ip4_plen}= | ${24}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES_256_GCM in tunnel mode.
| | ...
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| | ...
| | Set Test Variable | \${frame_size}
| | ...
| | # These are enums (not strings) so they cannot be in Variables table.
| | ${encr_alg}= | Crypto Alg AES GCM 256
| | ${auth_alg}= | Set Variable | ${NONE}
| | ${ipsec_proto}= | IPsec Proto ESP
| | ...
| | Given Add worker threads and rxqueues to all DUTs | ${phy_cores} | ${rxq}
| | And Add PCI devices to all DUTs
| | And Set Max Rate And Jumbo And Handle Multi Seg
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Configure topology for IPv4 IPsec testing
| | ${encr_key}= | ${integ_key}= |
| | ... | Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut1} | ${dut1_if1} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg} | ${tg_if1} | ${dut1_if1_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

*** Test Cases ***
| tc01-110B-eth2p-ethip4ipsec1tnlsw-ip4base-policy-aes-256-gcm-dev
| | [Tags] | 110B
| | frame_size=${110} | phy_cores=${0}
