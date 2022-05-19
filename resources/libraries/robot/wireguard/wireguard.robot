# Copyright (c) 2022 Intel and/or its affiliates.
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
| Library | resources.libraries.python.WireGuardUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.IPv6Util
|
| Documentation | Wireguard keywords.

*** Keywords ***
| Generate keys for WireGuard
| | [Documentation] | Generate a pair of keys for WireGuard
| |
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - private_key - wireguard Private key. Type: bytes
| | ... | - pub_key - wireguard public key. Type: bytes
| |
| | ... | *Example:*
| | ... | \| ${private_key} | ${pub_key} |
| | ... | \| Generate Wireguard Privatekey and Pubkey \|
| |
| | ${private_key} | ${pub_key} | Generate Wireguard Privatekey and Pubkey
| | Set Test Variable | ${private_key}
| | Set Test Variable | ${pub_key}

| Initialize WireGuard in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on VPP
| | ... | interfaces towards TG. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. Set routing for decrypted traffic on both DUT nodes
| | ... | with prefix /8 and next hop of neighbour TG interface IPv4 address.
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_if1_ip4} | 24
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${dut2_if2_ip4} | 24
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${tg_if1_ip4} | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${tg_if2_ip4} | ${TG_pf2_mac}[0]
| | Vpp Route Add | ${dut1} | ${laddr_ip4} | 8 | gateway=${tg_if1_ip4}
| | ... | interface=${DUT1_${int}1}[0]
| | Vpp Route Add | ${dut2} | ${raddr_ip4} | 8 | gateway=${tg_if2_ip4}
| | ... | interface=${DUT2_${int}2}[0]
