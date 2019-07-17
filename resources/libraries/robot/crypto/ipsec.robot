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
| Library | String
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPsecUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.IPv6Util
| ...
| Documentation | IPsec keywords.

*** Keywords ***
| Generate keys for IPSec
| | [Documentation] | Generate keys for IPsec.
| | ...
| | ... | *Arguments:*
| | ... | - crypto_alg - Encryption algorithm. Type: enum
| | ... | - integ_alg - Integrity algorithm. Type: enum
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - encr_key - Encryption key. Type: string
| | ... | - auth_key - Integrity key. Type: string
| | ...
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128 \|
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96 \|
| | ... | \| Generate keys for IPSec \| ${encr_alg} \| ${auth_alg} \|
| | ...
| | [Arguments] | ${crypto_alg} | ${integ_alg}
| | ...
| | ${encr_key_len}= | Get Crypto Alg Key Len | ${crypto_alg}
| | ${encr_key}= | Generate Random String | ${encr_key_len}
| | ${auth_key_len}= | Get Integ Alg Key Len | ${integ_alg}
| | ${auth_key}= | Generate Random String | ${auth_key_len}
| | Set Test Variable | ${encr_key}
| | Set Test Variable | ${auth_key}

| Configure path for IPSec test
| | [Documentation] | Setup path for IPsec testing TG<-->DUT1.
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - dut_lo - DUT loopback interface. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Configure path for IPSec test \|
| | ...
| | ${dut1_lo1}= | Vpp Create Loopback | ${dut1}
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_lo1} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Set Test Variable | ${dut1_lo1}

| Configure topology for IPv4 IPsec testing
| | [Documentation] | Setup topology for IPv4 IPsec testing.
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - dut_tun_ip - DUT tunnel IP address. Type: string
| | ... | - dut_src_ip - DUT source IP address. Type: string
| | ... | - tg_tun_ip - TG tunnel IP address. Type: string
| | ... | - tg_src_ip - TG source IP address. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Configure topology for IPv4 IPsec testing \|
| | ...
| | Configure path for IPSec test
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut_if_ip4} | ${ip4_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_lo1} | ${dut_lo_ip4} | ${ip4_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${tg_if_ip4} | ${tg_if1_mac}
| | Vpp Route Add
| | ... | ${dut1} | ${tg_lo_ip4} | ${ip4_plen} | gateway=${tg_if_ip4}
| | ... | interface=${dut1_if1}
| | Set Test Variable | ${dut_tun_ip} | ${dut_if_ip4}
| | Set Test Variable | ${dut_src_ip} | ${dut_lo_ip4}
| | Set Test Variable | ${tg_tun_ip} | ${tg_if_ip4}
| | Set Test Variable | ${tg_src_ip} | ${tg_lo_ip4}

| Configure topology for IPv6 IPsec testing
| | [Documentation] | Setup topology fo IPv6 IPsec testing.
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - dut_tun_ip - DUT tunnel IP address. Type: string
| | ... | - dut_src_ip - DUT source IP address. Type: string
| | ... | - tg_tun_ip - TG tunnel IP address. Type: string
| | ... | - tg_src_ip - TG source IP address. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Configure topology for IPv6 IPsec testing \|
| | ...
| | Configure path for IPSec test
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut_if_ip6} | ${ip6_plen}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_lo1} | ${dut_lo_ip6} | ${ip6_plen}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${tg_if_ip6} | ${tg_if1_mac}
| | Vpp All RA Suppress Link Layer | ${nodes}
| | Vpp Route Add
| | ... | ${dut1} | ${tg_lo_ip6} | ${ip6_plen_rt} | gateway=${tg_if_ip6}
| | ... | interface=${dut1_if1}
| | Set Test Variable | ${dut_tun_ip} | ${dut_if_ip6}
| | Set Test Variable | ${dut_src_ip} | ${dut_lo_ip6}
| | Set Test Variable | ${tg_tun_ip} | ${tg_if_ip6}
| | Set Test Variable | ${tg_src_ip} | ${tg_lo_ip6}

| Configure manual keyed connection for IPSec
| | [Documentation] | Setup IPsec manual keyed connection on VPP node.
| | ...
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
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - l_sa_id
| | ... | - r_sa_id
| | ...
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128 \|
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96 \|
| | ... | \| Configure manual keyed connection for IPSec \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| ${encr_alg} \| sixteenbytes_key \
| | ... | \| ${auth_alg} \| twentybytessecretkey \| ${1000} \| ${1001} \
| | ... | \| 192.168.4.4 \| 192.168.3.3 \| 192.168.100.3 \| 192.168.100.2 \|
| | ...
| | [Arguments] | ${node} | ${interface} | ${crypto_alg} | ${crypto_key}
| | ... | ${integ_alg} | ${integ_key} | ${l_spi} | ${r_spi} | ${l_ip}
| | ... | ${r_ip} | ${l_tunnel}=${None} | ${r_tunnel}=${None}
| | ... | ${is_ipv6}=${FALSE}
| | ...
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
| | ${action}= | Policy Action Bypass
| | VPP IPsec Policy Add | ${node} | ${spd_id} | ${p_hi} | ${action}
| | ... | inbound=${TRUE} | proto=${ESP_PROTO} | is_ipv6=${is_ipv6}
| | ... | laddr_range=${tg_tun_ip} | raddr_range=${dut_tun_ip}
| | VPP IPsec Policy Add | ${node} | ${spd_id} | ${p_hi} | ${action}
| | ... | inbound=${FALSE} | proto=${ESP_PROTO} | is_ipv6=${is_ipv6}
| | ... | laddr_range=${dut_tun_ip} | raddr_range=${tg_tun_ip}
| | ${action}= | Policy Action Protect
| | VPP IPsec Policy Add | ${node} | ${spd_id} | ${p_lo} | ${action}
| | ... | sa_id=${r_sa_id} | laddr_range=${l_ip}
| | ... | raddr_range=${r_ip} | inbound=${TRUE}
| | VPP IPsec Policy Add | ${node} | ${spd_id} | ${p_lo} | ${action}
| | ... | sa_id=${l_sa_id} | laddr_range=${l_ip}
| | ... | raddr_range=${r_ip} | inbound=${FALSE}

| Initialize IPSec in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG and
| | ... | DUT1-DUT2 links. Set routing for encrypted traffic on both DUT nodes
| | ... | with prefix /8 and next hop of neighbour DUT or TG interface IPv4
| | ... | address.
| | ...
| | Set interfaces in path up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1}
| | ... | ${dut1_if1_ip4} | 24
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if2}
| | ... | ${dut2_if2_ip4} | 24
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | ${tg_if1_ip4} | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | ${tg_if2_ip4} | ${tg_if2_mac}
| | Vpp Route Add | ${dut1} | ${laddr_ip4} | 8 | gateway=${tg_if1_ip4}
| | ... | interface=${dut1_if1}
| | Vpp Route Add | ${dut2} | ${raddr_ip4} | 8 | gateway=${tg_if2_ip4}
| | ... | interface=${dut2_if2}

| Initialize IPSec in 3-node circular container topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG and
| | ... | DUT1-DUT2 links. Set routing for encrypted traffic on both DUT nodes
| | ... | with prefix /8 and next hop of neighbour DUT or TG interface IPv4
| | ... | address.
| | ...
| | Set interfaces in path up on DUT | DUT1
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | ${dut1_if1_ip4} | 24
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | ${tg_if1_ip4} | ${tg_if1_mac}
| | Vpp Route Add | ${dut1} | ${laddr_ip4} | 8 | gateway=${tg_if1_ip4}
| | ... | interface=${dut1_if1}
