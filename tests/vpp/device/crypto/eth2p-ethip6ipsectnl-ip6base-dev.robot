# Copyright (c) 2016 Cisco and/or its affiliates.
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
| ... | FUNCTEST | IP6FWD | IPSEC | IPSEC_TNL | IP6BASE
| ...
| Suite Setup | Setup suite | ${nic_name}
| ...
| Test Setup | Setup test | vpp_device
| Test Teardown | Tear down test | packet_trace
| ...
| Documentation | *IPv6 IPsec tunnel mode test suite.*
| ...
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 create loopback interface, configure
| ... | loopback an physical interface IPv6 addresses, static ARP record, route
| ... | and IPsec manual keyed connection in tunnel mode.
| ... | *[Ver] TG verification:* ESP packet is sent from TG to DUT1. ESP packet
| ... | is received on TG from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC4303.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | crypto_ia32_plugin.so
| ... | crypto_ipsecmb_plugin.so | crypto_openssl_plugin.so
| ${nic_name}= | virtual
| ${tg_spi}= | ${1000}
| ${dut_spi}= | ${1001}
| ${ESP_PROTO}= | ${50}
| ${tg_if_ip6}= | 3ffe:5f::1
| ${dut_if_ip6}= | 3ffe:5f::2
| ${tg_lo_ip6}= | 3ffe:60::3
| ${dut_lo_ip6}= | 3ffe:60::4
| ${ip6_plen}= | ${64}
| ${ip6_plen_rt}= | ${128}

*** Test Cases ***
| tc01-eth2p-ethip6ipsectnl-ip6base-device-aes-128-cbc-sha-256-128
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA-256-128 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ...
| | Given Add PCI devices to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Configure topology for IPv6 IPsec testing
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 256 128
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip} | is_ipv6=${TRUE}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| tc02-eth2p-ethip6ipsectnl-ip6base-device-aes-256-cbc-sha-256-128
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-256 and integrity algorithm SHA-256-128 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ...
| | Given Add PCI devices to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Configure topology for IPv6 IPsec testing
| | ${encr_alg}= | Crypto Alg AES CBC 256
| | ${auth_alg}= | Integ Alg SHA 256 128
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip} | is_ipv6=${TRUE}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| tc03-eth2p-ethip6ipsectnl-ip6base-device-aes-128-cbc-sha-512-256
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA-512-256 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ...
| | Given Add PCI devices to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Configure topology for IPv6 IPsec testing
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 512 256
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip} | is_ipv6=${TRUE}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| tc04-eth2p-ethip6ipsectnl-ip6base-device-aes-256-cbc-sha-512-256
| | [Documentation]
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-256 and integrity algorithm SHA-512-256 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ...
| | Given Add PCI devices to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Configure topology for IPv6 IPsec testing
| | ${encr_alg}= | Crypto Alg AES CBC 256
| | ${auth_alg}= | Integ Alg SHA 512 256
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip} | is_ipv6=${TRUE}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}
