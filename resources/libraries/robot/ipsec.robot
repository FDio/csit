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
| Resource | resources/libraries/robot/default.robot
| Library | resources.libraries.python.IPsecUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.IPv4Util
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.Routing
| Library | String
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']}
| ...     | WITH NAME | dut1_v4
| Documentation | *IPsec keywords.*

*** Variables ***
| ${ESP_PROTO}= | ${50}
| ${tg_if_ip4}= | 192.168.100.2
| ${dut_if_ip4}= | 192.168.100.3
| ${tg_lo_ip4}= | 192.168.3.3
| ${dut_lo_ip4}= | 192.168.4.4
| ${ip4_plen}= | ${24}

*** Keywords ***
| IPsec Generate Keys
| | [Documentation] | Generate keys for IPsec.
| | ...
| | ... | *Arguments:*
| | ... | - ${crypto_alg} - Encryption algorithm. Type: enum
| | ... | - ${integ_alg} - Integrity algorithm. Type: enum
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${encr_key} - Encryption key. Type: string
| | ... | - ${auth_key} - Integrity key. Type: string
| | ...
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96
| | ... | \| IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | [Arguments] | ${crypto_alg} | ${integ_alg}
| | ${encr_key_len}= | Get Crypto Alg Key Len | ${crypto_alg}
| | ${encr_key}= | Generate Random String | ${encr_key_len}
| | ${auth_key_len}= | Get Integ Alg Key Len | ${integ_alg}
| | ${auth_key}= | Generate Random String | ${auth_key_len}
| | Set Test Variable | ${encr_key}
| | Set Test Variable | ${auth_key}

| Setup Path for IPsec testing
| | [Documentation] | Setup path for IPsec testing TG<-->DUT1.
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${tg} - TG node. Type: dictionary
| | ... | - ${tg_if} - TG interface connected to DUT. Type: string
| | ... | - ${tg_if_mac} - TG interface MAC. Type: string
| | ... | - ${dut} - DUT node. Type: dictionary
| | ... | - ${dut_if} - DUT interface connected to TG. Type: string
| | ... | - ${dut_if_mac} - DUT interface MAC. Type: string
| | ... | - ${dut_lo} - DUT loopback interface. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Setup Path for IPsec testing
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${tg_if} | ${tg}= | Next Interface
| | ${dut_if} | ${dut}= | Next Interface
| | ${dut_if_mac}= | Get Interface Mac | ${dut} | ${dut_if}
| | ${tg_if_mac}= | Get Interface Mac | ${tg} | ${tg_if}
| | ${dut_lo}= | Vpp Create Loopback | ${dut}
| | Set Interface State | ${tg} | ${tg_if} | up
| | Set Interface State | ${dut} | ${dut_if} | up
| | Set Interface State | ${dut} | ${dut_lo} | up
| | Vpp Node Interfaces Ready Wait | ${dut}
| | Set Test Variable | ${tg}
| | Set Test Variable | ${tg_if}
| | Set Test Variable | ${tg_if_mac}
| | Set Test Variable | ${dut}
| | Set Test Variable | ${dut_if}
| | Set Test Variable | ${dut_if_mac}
| | Set Test Variable | ${dut_lo}

| Setup Topology for IPv4 IPsec testing
| | [Documentation] | Setup topology fo IPv4 IPsec testing.
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${dut_tun_ip} - DUT tunnel IP address. Type: string
| | ... | - ${dut_src_ip} - DUT source IP address. Type: string
| | ... | - ${tg_tun_ip} - TG tunnel IP address. Type: string
| | ... | - ${tg_src_ip} - TG source IP address. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Setup Topology for IPsec testing
| | Setup Path for IPsec testing
| | Set Interface Address | ${dut} | ${dut_if} | ${dut_if_ip4} | ${ip4_plen}
| | Set Interface Address | ${dut} | ${dut_lo} | ${dut_lo_ip4} | ${ip4_plen}
| | dut1_v4.Set Arp | ${dut_if} | ${tg_if_ip4} | ${tg_if_mac}
| | Vpp Route Add | ${dut} | ${tg_lo_ip4} | ${24} | ${tg_if_ip4} | ${dut_if}
| | Set Test Variable | ${dut_tun_ip} | ${dut_if_ip4}
| | Set Test Variable | ${dut_src_ip} | ${dut_lo_ip4}
| | Set Test Variable | ${tg_tun_ip} | ${tg_if_ip4}
| | Set Test Variable | ${tg_src_ip} | ${tg_lo_ip4}

| VPP Setup IPsec Manual Keyed Connection
| | [Documentation] | todo
| | ...
| | ... | *Arguments:*
| | ... | - ${node} - VPP node to setup IPsec on. Type: dictionary
| | ... | - ${interface} - Interface to enable IPsec on. Type: string
| | ... | - ${crypto_alg} - Encrytion algorithm. Type: enum
| | ... | - ${crypto_key} - Encryption key. Type: string
| | ... | - ${integ_alg} - Integrity algorithm. Type: enum
| | ... | - ${integ_key} - Integrity key. Type: string
| | ... | - ${l_spi} - Local SPI. Type: integer
| | ... | - ${r_spi} - Remote SPI. Type: integer
| | ... | - ${l_ip} - Local IP address. Type: string
| | ... | - ${r_ip} - Remote IP address. Type: string
| | ... | - ${l_tunnel} - Local tunnel IP address (optional). Type: string
| | ... | - ${r_tunnel} - Remote tunnel IP address (optional). Type: string
| | ...
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96
| | ... | \| Setup IPsec Manual Keyed Connection \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| ${encr_alg} \| sixteenbytes_key \
| | ... | \| ${auth_alg} \| twentybytessecretkey \| ${1000} \| ${1001} \
| | ... | \| 192.168.4.4 \| 192.168.3.3 \| 192.168.100.3 \| 192.168.100.2
| | [Arguments] | ${node} | ${interface} | ${crypto_alg} | ${crypto_key}
| | ...         | ${integ_alg} | ${integ_key} | ${l_spi} | ${r_spi} | ${l_ip}
| | ...         | ${r_ip} | ${l_tunnel}=${None} | ${r_tunnel}=${None}
| | ${l_sa_id}= | Set Variable | ${10}
| | ${r_sa_id}= | Set Variable | ${20}
| | ${spd_id}= | Set Variable | ${1}
| | ${p_hi}= | Set Variable | ${100}
| | ${p_lo}= | Set Variable | ${10}
| | VPP IPsec Add SAD Entry | ${node} | ${l_sa_id} | ${l_spi} | ${crypto_alg}
| | ...                     | ${crypto_key} | ${integ_alg} | ${integ_key}
| | ...                     | ${l_tunnel} | ${r_tunnel}
| | VPP IPsec Add SAD Entry | ${node} | ${r_sa_id} | ${r_spi} | ${crypto_alg}
| | ...                     | ${crypto_key} | ${integ_alg} | ${integ_key}
| | ...                     | ${r_tunnel} | ${l_tunnel}
| | VPP IPsec Add SPD | ${node} | ${spd_id}
| | VPP IPsec SPD Add If | ${node} | ${spd_id} | ${interface}
| | ${action}= | Policy Action Bypass
| | VPP IPsec SPD Add Entry | ${node} | ${spd_id} | ${p_hi} | ${action}
| | ...                     | inbound=${TRUE} | proto=${ESP_PROTO}
| | VPP IPsec SPD Add Entry | ${node} | ${spd_id} | ${p_hi} | ${action}
| | ...                     | inbound=${FALSE} | proto=${ESP_PROTO}
| | ${action}= | Policy Action Protect
| | VPP IPsec SPD Add Entry | ${node} | ${spd_id} | ${p_lo} | ${action}
| | ...                     | sa_id=${r_sa_id} | laddr_range=${l_ip}
| | ...                     | raddr_range=${r_ip} | inbound=${TRUE}
| | VPP IPsec SPD Add Entry | ${node} | ${spd_id} | ${p_lo} | ${action}
| | ...                     | sa_id=${l_sa_id} | laddr_range=${l_ip}
| | ...                     | raddr_range=${r_ip} | inbound=${FALSE}

| Send and Receive IPsec Packet
| | [Documentation] | todo
| | ...
| | ... | *Arguments:*
| | ... | - ${node} - TG node. Type: dictionary
| | ... | - ${interface} - TG Interface. Type: string
| | ... | - ${dst_mac} - Destination MAC. Type: string
| | ... | - ${crypto_alg} - Encrytion algorithm. Type: enum
| | ... | - ${crypto_key} - Encryption key. Type: string
| | ... | - ${integ_alg} - Integrity algorithm. Type: enum
| | ... | - ${integ_key} - Integrity key. Type: string
| | ... | - ${l_spi} - Local SPI. Type: integer
| | ... | - ${r_spi} - Remote SPI. Type: integer
| | ... | - ${l_ip} - Local IP address. Type: string
| | ... | - ${r_ip} - Remote IP address. Type: string
| | ... | - ${l_tunnel} - Local tunnel IP address (optional). Type: string
| | ... | - ${r_tunnel} - Remote tunnel IP address (optional). Type: string
| | ...
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96
| | ... | \| Send and Receive IPsec Packet \| ${nodes['TG']} \| eth1 \
| | ... | \| 52:54:00:d4:d8:22 \| ${encr_alg} \| sixteenbytes_key \
| | ... | \| ${auth_alg} \| twentybytessecretkey \| ${1001} \| ${1000} \
| | ... | \| 192.168.3.3 \| 192.168.4.4 \| 192.168.100.2 \| 192.168.100.3
| | [Arguments] | ${node} | ${interface} | ${dst_mac} | ${crypto_alg}
| | ...         | ${crypto_key} | ${integ_alg} | ${integ_key} | ${l_spi}
| | ...         | ${r_spi} | ${l_ip} | ${r_ip} | ${l_tunnel}=${None}
| | ...         | ${r_tunnel}=${None}
| | ${src_mac}= | Get Interface Mac | ${node} | ${interface}
| | ${args}= | Traffic Script Gen Arg | ${interface} | ${interface} | ${src_mac}
| | ...      | ${dst_mac} | ${l_ip} | ${r_ip}
| | ${crypto_alg_str}= | Get Crypto Alg Scapy Name | ${crypto_alg}
| | ${integ_alg_str}= | Get Integ Alg Scapy Name | ${integ_alg}
| | ${args}= | Set Variable | ${args} --crypto_alg ${crypto_alg_str}
| | ${args}= | Set Variable | ${args} --crypto_key ${crypto_key}
| | ${args}= | Set Variable | ${args} --integ_alg ${integ_alg_str}
| | ${args}= | Set Variable | ${args} --integ_key ${integ_key}
| | ${args}= | Set Variable | ${args} --l_spi ${l_spi} --r_spi ${r_spi}
| | ${args}= | Set Variable If | "${l_tunnel}" == "${None}" | ${args} | ${args} --src_tun ${l_tunnel}
| | ${args}= | Set Variable If | "${r_tunnel}" == "${None}" | ${args} | ${args} --dst_tun ${r_tunnel}
| | Run Traffic Script On Node | ipsec.py | ${node} | ${args}
