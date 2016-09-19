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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.LispUtil
| Library | resources.libraries.python.IPsecUtil
| Library | String
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/lisp/lispgpe.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/ipv6_lispgpe_ipv6/ipv6_lispgpe_ipv6.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | EXPECTED_FAILING | LISP
| ...
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| ...           | AND          | VPP Show Errors | ${nodes['DUT1']}
| ...           | AND          | VPP Show Errors | ${nodes['DUT2']}
| ...
| Documentation | *IPv6 - ip6-ipsec-lispgpe-ip6 - main fib, vrf (gpe_vni-to-vrf), lisp2lisp*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:*
| ... |
| ... | *[Cfg] DUT configuration:*
| ... |
| ... |
| ... | *[Ver] TG verification:*
| ... |
| ... |
| ... |
| ... | *[Ref] Applicable standard specifications:* RFC6830.


#IPv6 - ip6-ipsec-lispgpe-ip6 - main fib, vrf (gpe_vni-to-vrf), lisp2lisp
*** Variables ***
| ${dut2_spi}= | ${1000}
| ${dut1_spi}= | ${1001}
| ${ESP_PROTO}= | ${50}

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using physical interfaces
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - phy2lisp \
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on received
| | ... | packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Interfaces in 3-node path are up
| | IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip6} | ${prefix6}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip6} | ${prefix6}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip6} | ${prefix6}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip6} | ${prefix6}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip6} | ${tg_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip6} | ${tg_to_dut2_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip6} | ${dut2_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip6} | ${dut1_to_dut2_mac}
#| | Vpp Route Add | ${dut1_node} | ${tg2_ip6} | 64 | ${dut2_to_dut1_ip6} | ${dut1_to_dut2}
#| | Vpp Route Add | ${dut2_node} | ${tg1_ip6} | 64 | ${dut1_to_dut2_ip6} | ${dut2_to_dut1}
| | IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut1_spi} | ${dut2_spi} | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6}
| | VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut2_spi} | ${dut1_spi} | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6}
| | Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ... | ${dut1_to_dut2_ip6_static_adjacency}
| | ... | ${dut2_to_dut1_ip6_static_adjacency}
| | Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip6} | ${tg2_ip6}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip6} | ${tg1_ip6}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC02: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using physical interfaces and VRF is enabled
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - vrf, phy2lisp \
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on received
| | ... | packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Setup VRF on DUT | ${dut1_node} | ${dut1_fib_table} | ${dut1_to_dut2}
| | ... | ${dut2_to_dut1_ip6} | ${dut2_to_dut1_mac} | ${tg2_ip6} | ${dut1_to_tg}
| | ... | ${tg1_ip6} | ${tg_to_dut1_mac} | ${prefix6}
| | And Setup VRF on DUT | ${dut2_node} | ${dut2_fib_table} | ${dut2_to_dut1}
| | ... | ${dut1_to_dut2_ip6} | ${dut1_to_dut2_mac} | ${tg1_ip6} | ${dut2_to_tg}
| | ... | ${tg2_ip6} | ${tg_to_dut2_mac} | ${prefix6}
| | IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip6} | ${prefix6}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip6} | ${prefix6}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip6} | ${prefix6}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip6} | ${prefix6}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip6} | ${tg_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip6} | ${tg_to_dut2_mac}
#| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip6} | ${dut2_to_dut1_mac}
#| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip6} | ${dut1_to_dut2_mac}
| | IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut1_spi} | ${dut2_spi} | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6}
| | VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut2_spi} | ${dut1_spi} | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6}
| | Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ... | ${dut1_to_dut2_ip6_static_adjacency}
| | ... | ${dut2_to_dut1_ip6_static_adjacency}
| | Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip6} | ${tg2_ip6}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip6} | ${tg1_ip6}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

*** Keywords ***
| Setup VRF on DUT
| | [Documentation]
| | ... | The keyword sets a FIB table on a DUT, assigns two interfaces to it,\
| | ... | adds two ARP items and a route, see example.
| | ...
| | ... | *Example:*
| | ... | Three-node topology:
| | ... | TG_if1 - DUT1_if1-DUT1_if2 - DUT2_if1-DUT2_if2 - TG_if2
| | ... | Create one VRF on each DUT:
| | ... | \| Setup VRF on DUT \| ${dut1_node} \| ${dut1_fib_table} \
| | ... | \| ${dut1_to_dut2} \| ${dut2_to_dut1_ip4} \| ${dut2_to_dut1_mac} \
| | ... | \| ${tg2_ip4} \| ${dut1_to_tg} \| ${tg1_ip4} \| ${tg_to_dut1_mac} \
| | ... | \| 24 \|
| | ... | \| Setup VRF on DUT \| ${dut2_node} \| ${dut2_fib_table} \
| | ... | \| ${dut2_to_dut1} \| ${dut1_to_dut2_ip4} \| ${dut1_to_dut2_mac} \
| | ... | \| ${tg1_ip4} \| ${dut2_to_tg} \| ${tg2_ip4} \| ${tg_to_dut2_mac} \
| | ... | \| 24 \|
| | ...
| | [Arguments]
| | ... | ${node} | ${table} | ${route_interface} | ${route_gateway_ip}
| | ... | ${route_gateway_mac} | ${route_dst_ip} | ${vrf_src_if} | ${src_if_ip}
| | ... | ${src_if_mac} | ${prefix_len}
| | ...
| | ${route_interface_idx}= | Get Interface SW Index
| | ... | ${node} | ${route_interface}
| | ...
| | Add fib table | ${node}
| | ... | ${route_dst_ip} | ${prefix_len} | ${table}
| | ... | via ${route_gateway_ip} sw_if_index ${route_interface_idx} multipath
| | ...
| | Assign Interface To Fib Table
| | ... | ${node} | ${route_interface} | ${table}
| | Assign Interface To Fib Table
| | ... | ${node} | ${vrf_src_if} | ${table}
| | ...
| | Add Arp On Dut | ${node} | ${vrf_src_if}
| | ... | ${src_if_ip} | ${src_if_mac} | vrf=${table}
| | Add Arp On Dut | ${node} | ${route_interface}
| | ... | ${route_gateway_ip} | ${route_gateway_mac} | vrf=${table}
| | ...
| | Vpp Route Add | ${node} | ${route_dst_ip} | ${prefix_len}
| | ... | ${route_gateway_ip} | ${route_interface} | vrf=${table}

| IPsec Generate Keys
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
| | ... | \| IPsec Generate Keys \| ${encr_alg} \| ${auth_alg} \|
| | [Arguments] | ${crypto_alg} | ${integ_alg}
| | ${encr_key_len}= | Get Crypto Alg Key Len | ${crypto_alg}
| | ${encr_key}= | Generate Random String | ${encr_key_len}
| | ${auth_key_len}= | Get Integ Alg Key Len | ${integ_alg}
| | ${auth_key}= | Generate Random String | ${auth_key_len}
| | Set Test Variable | ${encr_key}
| | Set Test Variable | ${auth_key}

| VPP Setup IPsec Manual Keyed Connection
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
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128 \|
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96 \|
| | ... | \| VPP Setup IPsec Manual Keyed Connection \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| ${encr_alg} \| sixteenbytes_key \
| | ... | \| ${auth_alg} \| twentybytessecretkey \| ${1000} \| ${1001} \
| | ... | \| 192.168.4.4 \| 192.168.3.3 \| 192.168.100.3 \| 192.168.100.2 \|
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