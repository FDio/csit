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
| Resource | resources/libraries/robot/crypto/ipsec.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | IP4FWD | IPSEC | IPSEC_TNL | IP4BASE
| ...
| Test Setup | Set up IPSec SW device functional test | IPv4
| ...
| Test Teardown | Tear down VPP device test
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
| ${tg_spi}= | ${1000}
| ${dut_spi}= | ${1001}
| ${ESP_PROTO}= | ${50}
| ${tg_if_ip4}= | 192.168.100.2
| ${dut_if_ip4}= | 192.168.100.3
| ${tg_lo_ip4}= | 192.168.3.3
| ${dut_lo_ip4}= | 192.168.4.4
| ${ip4_plen}= | ${24}

*** Test Cases ***
| tc01-eth2p-ethip4ipsectnl-ip4base-device-aes-128-cbc-sha-256-128
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA-256-128 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 256 128
| | Given Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | When Configure manual keyed connection for IPSec
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| tc02-eth2p-ethip4ipsectnl-ip4base-device-aes-256-cbc-sha-256-128
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-256 and integrity algorithm SHA-256-128 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 256
| | ${auth_alg}= | Integ Alg SHA 256 128
| | Given Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | When Configure manual keyed connection for IPSec
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| tc03-eth2p-ethip4ipsectnl-ip4base-device-aes-128-cbc-sha-512-256
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA-512-256 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 512 256
| | Given Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | When Configure manual keyed connection for IPSec
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| tc04-eth2p-ethip4ipsectnl-ip4base-device-aes-256-cbc-sha-512-256
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-256 and integrity algorithm SHA-512-256 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 256
| | ${auth_alg}= | Integ Alg SHA 512 256
| | Given Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | When Configure manual keyed connection for IPSec
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}
