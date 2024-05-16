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
| Library | String
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPsecUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.IPv6Util
|
| Documentation | IPsec keywords.

*** Keywords ***
| Generate keys for IPSec
| | [Documentation] | Generate keys for IPsec.
| |
| | ... | *Arguments:*
| | ... | - crypto_alg - Encryption algorithm. Type: enum
| | ... | - integ_alg - Integrity algorithm. Type: enum
| |
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - encr_key - Encryption key. Type: string
| | ... | - auth_key - Integrity key. Type: string
| |
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128 \|
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96 \|
| | ... | \| Generate keys for IPSec \| ${encr_alg} \| ${auth_alg} \|
| |
| | [Arguments] | ${crypto_alg} | ${integ_alg}
| |
| | ${encr_key_len}= | Get Crypto Alg Key Len | ${crypto_alg}
| | ${encr_key}= | Generate Random String | ${encr_key_len}
| | ${auth_key_len}= | Get Integ Alg Key Len | ${integ_alg}
| | ${auth_key}= | Generate Random String | ${auth_key_len}
| | Set Test Variable | ${encr_key}
| | Set Test Variable | ${auth_key}

| Configure topology for IPv4 IPsec testing
| | [Documentation] | Setup topology for IPv4 IPsec testing.
| |
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - dut_tun_ip - DUT tunnel IP address. Type: string
| | ... | - dut_src_ip - DUT source IP address. Type: string
| | ... | - tg_tun_ip - TG tunnel IP address. Type: string
| | ... | - tg_src_ip - TG source IP address. Type: string
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv4 IPsec testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut_if1_ip4} | ${ip4_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut_if2_ip4} | ${ip4_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${tg_if1_ip4} | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tg_if2_ip4} | ${TG_pf2_mac}[0]
| | Vpp Route Add
| | ... | ${dut1} | ${tg_host_ip4} | ${ip4_plen} | gateway=${tg_if1_ip4}
| | ... | interface=${DUT1_${int}1}[0] | strict=${False}
| | Set Test Variable | ${dut_tun_ip} | ${dut_if1_ip4}
| | Set Test Variable | ${tg_tun_ip} | ${tg_if1_ip4}
| | Set Test Variable | ${tg_src_ip} | ${tg_host_ip4}
| | Set Test Variable | ${tg_dst_ip} | ${tg_if2_ip4}

| Configure topology for IPv6 IPsec testing
| | [Documentation] | Setup topology fo IPv6 IPsec testing.
| |
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - dut_tun_ip - DUT tunnel IP address. Type: string
| | ... | - dut_src_ip - DUT source IP address. Type: string
| | ... | - tg_tun_ip - TG tunnel IP address. Type: string
| | ... | - tg_src_ip - TG source IP address. Type: string
| |
| | ... | *Example:*
| | ... | \| Configure topology for IPv6 IPsec testing \|
| |
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut_if1_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut_if2_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${tg_if1_ip6} | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tg_if2_ip6} | ${TG_pf2_mac}[0]
| | Vpp Interfaces RA Suppress On All Nodes | ${nodes}
| | Vpp Route Add
| | ... | ${dut1} | ${tg_host_ip6} | ${ip6_plen_rt} | gateway=${tg_if1_ip6}
| | ... | interface=${DUT1_${int}1}[0]
| | Set Test Variable | ${dut_tun_ip} | ${dut_if1_ip6}
| | Set Test Variable | ${tg_tun_ip} | ${tg_if1_ip6}
| | Set Test Variable | ${tg_src_ip} | ${tg_host_ip6}
| | Set Test Variable | ${tg_dst_ip} | ${tg_if2_ip6}

| Configure manual keyed connection for IPSec
| | [Documentation] | Setup IPsec manual keyed connection on VPP node.
| |
| | ... | *Arguments:*
| | ... | - node - VPP node to setup IPsec on. Type: dictionary
| | ... | - interface - Interface to enable IPsec on. Type: string
| | ... | - crypto_alg - Encrytion algorithm. Type: enum
| | ... | - crypto_key - Encryption key. Type: string
| | ... | - integ_alg - Integrity algorithm. Type: enum
| | ... | - integ_key - Integrity key. Type: string
| | ... | - l_spi - Local SPI. Type: integer
| | ... | - r_spi - Remote SPI. Type: integer
| | ... | - l_ip - Local IP address. Type: string
| | ... | - r_ip - Remote IP address. Type: string
| | ... | - l_tunnel - Local tunnel IP address (optional). Type: string
| | ... | - r_tunnel - Remote tunnel IP address (optional). Type: string
| |
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - l_sa_id
| | ... | - r_sa_id
| |
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128 \|
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96 \|
| | ... | \| Configure manual keyed connection for IPSec \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| ${encr_alg} \| sixteenbytes_key \
| | ... | \| ${auth_alg} \| twentybytessecretkey \| ${1000} \| ${1001} \
| | ... | \| 192.168.4.4 \| 192.168.3.3 \| 192.168.100.3 \| 192.168.100.2 \|
| |
| | [Arguments] | ${node} | ${interface} | ${crypto_alg} | ${crypto_key}
| | ... | ${integ_alg} | ${integ_key} | ${l_spi} | ${r_spi} | ${l_ip}
| | ... | ${r_ip} | ${l_tunnel}=${None} | ${r_tunnel}=${None}
| | ... | ${is_ipv6}=${FALSE}
| |
| | Set Test Variable | ${l_sa_id} | ${10}
| | Set Test Variable | ${r_sa_id} | ${20}
| | ${spd_id}= | Set Variable | ${1}
| | ${p_hi}= | Set Variable | ${100}
| | ${p_lo}= | Set Variable | ${10}
| | VPP IPsec Add SAD Entry | ${node} | ${l_sa_id} | ${l_spi} | ${crypto_alg}
| | ... | ${crypto_key} | ${integ_alg} | ${integ_key}
| | ... | ${l_tunnel} | ${r_tunnel}
| | VPP IPsec Add SAD Entry | ${node} | ${r_sa_id} | ${r_spi} | ${crypto_alg}
| | ... | ${crypto_key} | ${integ_alg} | ${integ_key}
| | ... | ${r_tunnel} | ${l_tunnel}
| | VPP IPsec Add SPD | ${node} | ${spd_id}
| | VPP IPsec SPD Add If | ${node} | ${spd_id} | ${interface}
| | VPP IPsec Add SPD Entry | ${node} | ${spd_id} | ${p_hi} | BYPASS
| | ... | inbound=${TRUE} | proto=ESP | is_ipv6=${is_ipv6}
| | ... | laddr_range=${tg_tun_ip} | raddr_range=${dut_tun_ip}
| | VPP IPsec Add SPD Entry | ${node} | ${spd_id} | ${p_hi} | BYPASS
| | ... | inbound=${FALSE} | proto=ESP | is_ipv6=${is_ipv6}
| | ... | laddr_range=${dut_tun_ip} | raddr_range=${tg_tun_ip}
| | VPP IPsec Add SPD Entry | ${node} | ${spd_id} | ${p_lo} | PROTECT
| | ... | sa_id=${r_sa_id} | laddr_range=${l_ip}
| | ... | raddr_range=${r_ip} | inbound=${TRUE}
| | VPP IPsec Add SPD Entry | ${node} | ${spd_id} | ${p_lo} | PROTECT
| | ... | sa_id=${l_sa_id} | laddr_range=${l_ip}
| | ... | raddr_range=${r_ip} | inbound=${FALSE}

| Initialize IPSec in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on VPP
| | ... | interfaces towards TG. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. Set routing for decrypted traffic on both DUT nodes
| | ... | with prefix /8 and next hop of neighbour TG interface IPv4 address.
| |
| | Set interfaces in path up
| | ${memif_1_varname} = | Set Variable | DUT1-memif-1-if2
| | ${memif_1_swindex} = | Set Variable | ${${memif_1_varname}}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${memif_1_swindex} | ${dut1_if1_ip4} | 24
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${memif_1_swindex} | ${tg_if1_ip4} | ${TG_pf1_mac}[0]
| | Vpp Route Add | ${dut1} | ${laddr_ip4} | 8 | gateway=${tg_if1_ip4}
| | ... | interface=${memif_1_swindex}
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | Return From Keyword If | "${dut2_status}" != "PASS"
| | ${memif_2_varname} = | Set Variable | DUT2-memif-1-if2
| | ${memif_2_swindex} = | Set Variable | ${${memif_2_varname}}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${memif_2_swindex} | ${dut2_if2_ip4} | 24
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${memif_2_swindex} | ${tg_if2_ip4} | ${TG_pf2_mac}[0]
| | Vpp Route Add | ${dut2} | ${raddr_ip4} | 8 | gateway=${tg_if2_ip4}
| | ... | interface=${memif_2_swindex}

| Initialize IPSec in 3-node circular container topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG and
| | ... | DUT1-DUT2 links. Set routing for encrypted traffic on both DUT nodes
| | ... | with prefix /8 and next hop of neighbour DUT or TG interface IPv4
| | ... | address.
| |
| | Set interfaces in path up on DUT | DUT1
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_if1_ip4} | 24
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${tg_if1_ip4} | ${TG_pf1_mac}[0]
| | Vpp Route Add
| | ... | ${dut1} | ${laddr_ip4} | 8 | gateway=${tg_if1_ip4}
| | ... | interface=${DUT1_${int}1}[0]

| Enable IPSec Async Mode on all VPP DUTs
| | [Documentation]
| | ... | Set IPsec async mode on for all DUT nodes.
| |
| | FOR | ${dut} | IN | @{duts}
| | | VPP Ipsec Set Async Mode | ${nodes['${dut}']}
| | END

| Set Data Plane And Feature Plane Workers for IPsec on all VPP DUTs
| | [Documentation]
| | ... | Disable crypto work for specified data plane CPU cores
| | ... | on all DUT nodes (leaving feature plane workers enabled).
| | ... | Set Round Robin interface RX placement on data plane CPU cores
| | ... | on all DUT nodes (leaving feature plane workers disabled).
| |
| | VPP Round Robin Rx Placement on all DUTs
| | ... | ${nodes} | prefix=${EMPTY} | use_dp_cores=${False}
#| | VPP IPSec Crypto SW Scheduler Set Worker on all DUTs
#| | ... | ${nodes} | crypto_enable=${False}

| Enable SPD flow cache IPv4 Inbound
| | [Documentation]
| | ... | Enable IPv4 Inbound SPD flow cache in VPP configuration file.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | ${dut}.Add IPsec SPD Flow cache IPv4 Inbound | on
| | | Run Keyword | ${dut}.Add IPsec SPD Fast Path IPv4 Inbound | on
| | END

| Enable SPD flow cache IPv4 Outbound
| | [Documentation]
| | ... | Enable IPv4 Outbound SPD flow cache in VPP configuration file.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | ${dut}.Add IPsec SPD Flow cache IPv4 Outbound | on
| | | Run Keyword | ${dut}.Add IPsec SPD Fast Path IPv4 Outbound | on
| | END

| Enable IPsec SPD Fast Path IPv4 Inbound and Outbound
| | [Documentation]
| | ... | Enable IPsec SPD fast path IPv4 Inbound and outbound in VPP
| | ... | configuration file.
| |
| | ... | *Arguments:*
| | ... | - value - The number buckets for spd fast path. Type: int
| |
| | [Arguments] | ${value}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | ${dut}.Add IPsec SPD Flow Cache IPv4 Outbound | off
| | | Run Keyword | ${dut}.Add IPsec SPD Flow Cache IPv4 Inbound | off
| | | Run Keyword | ${dut}.Add IPsec SPD Fast Path IPv4 Outbound | on
| | | Run Keyword | ${dut}.Add IPsec SPD Fast Path IPv4 Inbound | on
| | | Run Keyword | ${dut}.Add IPsec SPD Fast Path Num Buckets | ${value}
| | END
