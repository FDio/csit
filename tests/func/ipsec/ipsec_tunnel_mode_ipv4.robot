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
| Resource | resources/libraries/robot/ipsec.robot
| Library | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
| ...        | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Func Test Setup
| ...        | AND          | Setup Topology for IPv4 IPsec testing
| Test Teardown | Run Keywords | VPP IPsec Show | ${dut_node}
| ...           | AND          | Func Test Teardown
#| Test Setup | Run Keywords | Setup all DUTs before test
#| ...        | AND          | Setup all TGs before traffic script
#| ...        | AND          | Setup Topology for IPv4 IPsec testing
#| Test Teardown | Run Keywords | VPP IPsec Show | ${dut_node}
#| ...           | AND          | Show Packet Trace on All DUTs | ${nodes}
#| ...           | AND          | Show Vpp Errors on All DUTs
#| ...           | AND          | Show Vpp Trace Dump on All DUTs
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
| TC01: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA1-96 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA1-96 in tunnel mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC02: VPP process ESP packet in Tunnel Mode with AES-CBC-192 encryption and SHA1-96 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-192 and integrity algorithm SHA1-96 in tunnel mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | [Tags] | SKIP_PATCH
| | ${encr_alg}= | Crypto Alg AES CBC 192
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC03: VPP process ESP packet in Tunnel Mode with AES-CBC-256 encryption and SHA1-96 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-256 and integrity algorithm SHA1-96 in tunnel mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | [Tags] | SKIP_PATCH
| | ${encr_alg}= | Crypto Alg AES CBC 256
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC04: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA-256-128 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA-256-128 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | [Tags] | SKIP_PATCH
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 256 128
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC05: VPP process ESP packet in Tunnel Mode with AES-CBC-192 encryption and SHA-256-128 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-192 and integrity algorithm SHA-256-128 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ${encr_alg}= | Crypto Alg AES CBC 192
| | ${auth_alg}= | Integ Alg SHA 256 128
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC06: VPP process ESP packet in Tunnel Mode with AES-CBC-256 encryption and SHA-256-128 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-256 and integrity algorithm SHA-256-128 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | [Tags] | SKIP_PATCH
| | ${encr_alg}= | Crypto Alg AES CBC 256
| | ${auth_alg}= | Integ Alg SHA 256 128
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC07: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA-384-192 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA-384-192 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | [Tags] | SKIP_PATCH
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 384 192
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC08: VPP process ESP packet in Tunnel Mode with AES-CBC-192 encryption and SHA-384-192 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-192 and integrity algorithm SHA-384-192 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | [Tags] | SKIP_PATCH
| | ${encr_alg}= | Crypto Alg AES CBC 192
| | ${auth_alg}= | Integ Alg SHA 384 192
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC09: VPP process ESP packet in Tunnel Mode with AES-CBC-256 encryption and SHA-384-192 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-256 and integrity algorithm SHA-384-192 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ${encr_alg}= | Crypto Alg AES CBC 256
| | ${auth_alg}= | Integ Alg SHA 384 192
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC10: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA-512-256 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA-512-256 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | [Tags] | SKIP_PATCH
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 512 256
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC11: VPP process ESP packet in Tunnel Mode with AES-CBC-192 encryption and SHA-512-256 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-192 and integrity algorithm SHA-512-256 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | [Tags] | SKIP_PATCH
| | ${encr_alg}= | Crypto Alg AES CBC 192
| | ${auth_alg}= | Integ Alg SHA 512 256
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC12: VPP process ESP packet in Tunnel Mode with AES-CBC-256 encryption and SHA-512-256 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-256 and integrity algorithm SHA-512-256 in tunnel\
| | ... | mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ${encr_alg}= | Crypto Alg AES CBC 256
| | ${auth_alg}= | Integ Alg SHA 512 256
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC13: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA1-96 integrity - different encryption alogrithms used
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA1-96 in tunnel mode.
| | ... | [Ver] Send an ESP packet encrypted by encryption key different from\
| | ... | encryption key stored on VPP node from TG to VPP node and expect no\
| | ... | response to be received on TG.
| | ... | [Ref] RFC4303.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | ${encr_key2}= | And Get Second Random String | ${encr_alg} | Crypto
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key2} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC14: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA1-96 integrity - different integrity alogrithms used
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA1-96 in tunnel mode.
| | ... | [Ver] Send an ESP packet authenticated by integrity key different\
| | ... | from integrity key stored on VPP node from TG to VPP node and expect\
| | ... | no response to be received on TG.
| | ... | [Ref] RFC4303.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | ${auth_key2}= | And Get Second Random String | ${auth_alg} | Integ
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key2} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC15: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA1-96 integrity - different encryption and integrity alogrithms used
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA1-96 in tunnel mode.
| | ... | [Ver] Send an ESP packet authenticated by integrity key and encrypted\
| | ... | by encryption key different from integrity and encryption keys stored\
| | ... | on VPP node from TG to VPP node and expect no response to be received\
| | ... | on TG.
| | ... | [Ref] RFC4303.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | ${encr_key2}= | And Get Second Random String | ${encr_alg} | Crypto
| | ${auth_key2}= | And Get Second Random String | ${auth_alg} | Integ
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key2} | ${auth_alg} | ${auth_key2} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC16: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA1-96 integrity with update SA keys
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA1-96 in tunnel\
| | ... | mode. Then update SA keys - use new keys.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node before\
| | ... | and after SA keys update.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}
| | ${new_encr_key}= | Given Get Second Random String | ${encr_alg} | Crypto
| | ${new_auth_key}= | And Get Second Random String | ${auth_alg} | Integ
| | When VPP Update IPsec SA Keys | ${dut_node} | ${l_sa_id} | ${r_sa_id}
| | ... | ${new_encr_key} | ${new_auth_key}
| | Then Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${new_encr_key} | ${auth_alg} | ${new_auth_key}
| | ... | ${tg_spi} | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC17: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA1-96 integrity with update SA keys - different encryption alogrithms used
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA1-96 in tunnel
| | ... | mode. Then update SA keys - use new keys.
| | ... | [Ver] Send an ESP packet encrypted by encryption key different from\
| | ... | encryption key stored on VPP node from TG to VPP node and expect no\
| | ... | response to be received on TG before and after SA keys update.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | ${encr_key2}= | And Get Second Random String | ${encr_alg} | Crypto
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key2} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}
| | ${new_encr_key}= | Given Get Second Random String | ${encr_alg} | Crypto
| | ${new_auth_key}= | And Get Second Random String | ${auth_alg} | Integ
| | When VPP Update IPsec SA Keys | ${dut_node} | ${l_sa_id} | ${r_sa_id}
| | ... | ${new_encr_key} | ${new_auth_key}
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key2} | ${auth_alg} | ${new_auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC18: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA1-96 integrity with update SA keys - different integrity alogrithms used
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA1-96 in tunnel\
| | ... | mode. Then update SA keys - use new keys.
| | ... | [Ver] Send an ESP packet authenticated by integrity key different\
| | ... | from integrity key stored on VPP node from TG to VPP node and expect\
| | ... | no response to be received on TG before and after SA keys update.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | ${auth_key2}= | And Get Second Random String | ${auth_alg} | Integ
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key2} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}
| | ${new_encr_key}= | Given Get Second Random String | ${encr_alg} | Crypto
| | ${new_auth_key}= | And Get Second Random String | ${auth_alg} | Integ
| | When VPP Update IPsec SA Keys | ${dut_node} | ${l_sa_id} | ${r_sa_id}
| | ... | ${new_encr_key} | ${new_auth_key}
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${new_encr_key} | ${auth_alg} | ${auth_key2} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

| TC19: VPP process ESP packet in Tunnel Mode with AES-CBC-128 encryption and SHA1-96 integrity with update SA keys - different encryption and integrity alogrithms used
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with encryption\
| | ... | algorithm AES-CBC-128 and integrity algorithm SHA1-96 in tunnel\
| | ... | mode. Then update SA keys - use new keys.
| | ... | [Ver] Send an ESP packet authenticated by integrity key and encrypted\
| | ... | by encryption key different from integrity and encryption keys stored\
| | ... | on VPP node from TG to VPP node and expect no response to be received\
| | ... | on TG before and after SA keys update.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut_node} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | ${encr_key2}= | And Get Second Random String | ${encr_alg} | Crypto
| | ${auth_key2}= | And Get Second Random String | ${auth_alg} | Integ
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key2} | ${auth_alg} | ${auth_key2} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}
| | ${new_encr_key}= | Given Get Second Random String | ${encr_alg} | Crypto
| | ${new_auth_key}= | And Get Second Random String | ${auth_alg} | Integ
| | When VPP Update IPsec SA Keys | ${dut_node} | ${l_sa_id} | ${r_sa_id}
| | ... | ${new_encr_key} | ${new_auth_key}
| | Then Run Keyword And Expect Error | ESP packet Rx timeout
| | ... | Send And Receive IPsec Packet | ${tg_node} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key2} | ${auth_alg} | ${auth_key2} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip}
| | ... | ${dut_tun_ip}

*** Keywords ***
| Get Second Random String
| | [Arguments] | ${req_alg} | ${req_type}
| | ${req_key_len}= | Run Keyword | Get ${req_type} Alg Key Len | ${req_alg}
| | ${key}= | Set Variable If | '${req_type}' == 'Crypto' | ${encr_key}
| | ...                       | '${req_type}' == 'Integ' | ${auth_key}
| | :FOR | ${index} | IN RANGE | 100
| | | ${req_key}= | Generate Random String | ${req_key_len}
| | | Return From Keyword If | '${req_key}' != '${key}' | ${req_key}
