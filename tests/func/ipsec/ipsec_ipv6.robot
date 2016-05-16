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
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Setup Topology for IPv6 IPsec testing
| Test Teardown | Run Keywords | VPP IPsec Show | ${dut}
| ...           | AND          | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *IPv6 IPsec test suite.*
| ...
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Cfg] DUT configuration:* On DUT1 create loopback interface, configure\
| ... | loopback an physical interface IPv6 addresses, static ARP record, route\
| ... | and IPsec manual keyed connection.
| ... | *[Ver] TG verification:* ESP packet is sent from TG to DUT1. ESP packet\
| ... | is received on TG from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC4303.

*** Variables ***
| ${tg_spi}= | ${1000}
| ${dut_spi}= | ${1001}

*** Test Cases ***
| TC01: VPP process ESP packet in Tunnel Mode with AES-CBC encrytion and SHA1-96 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with AES-CBC\
| | ... | encrytion and SHA1-96 integrity in tunnel mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_src_ip} | ${tg_src_ip}
| | ... | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send and Receive IPsec Packet | ${tg} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_src_ip} | ${dut_src_ip} | ${tg_tun_ip} | ${dut_tun_ip}

| TC02: VPP process ESP packet in Transport Mode with AES-CBC encrytion and SHA1-96 integrity
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC4303.
| | ... | [Cfg] On DUT1 configure IPsec manual keyed connection with AES-CBC\
| | ... | encrytion and SHA1-96 integrity in transport mode.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut} | ${dut_if} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${dut_tun_ip} | ${tg_tun_ip}
| | Then Send and Receive IPsec Packet | ${tg} | ${tg_if} | ${dut_if_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_tun_ip} | ${dut_tun_ip}
