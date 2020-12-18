# Copyright (c) 2020 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.GeneveUtil
|
| Documentation | Keywords for GENEVE tunnels in VPP.

*** Keywords ***
| Initialize GENEVE L3 mode in circular topology
| | [Documentation] | Initialization of GENEVE L3 mode on DUT1.
| |
| | [Arguments] | ${with_bypass}=${False}
| |
| | Set interfaces in path up
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_if1_ip4} | 24
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${tg_if1_ip4} | ${TG_pf1_mac}[0]
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut1_if2_ip4} | 24
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tg_if2_ip4} | ${TG_pf2_mac}[0]
| | ${next_index}= | VPP Add Graph Node Next
| | ... | ${dut1} | geneve4-input | ethernet-input
| |
| | ${src_ip_int} = | IP To Int | ${gen_tunnel.src_ip}
| | ${dst_ip_int} = | IP To Int | ${gen_tunnel.dst_ip}
| | ${if_ip_int} = | IP To Int | ${gen_tunnel.if_ip}
| |
| | FOR | ${nr} | IN RANGE | 0 | ${n_tunnels}
| | | ${src_ip} = | Int To IP | ${${src_ip_int} + ${nr} * 256}
| | | ${dst_ip} = | Int To IP | ${${dst_ip_int} + ${nr} * 256}
| | | ${if_ip} = | Int To IP | ${${if_ip_int} + ${nr} * 256}
| | | Vpp Route Add
| | | ... | ${dut1} | ${src_ip} | ${gen_tunnel.ip_mask}
| | | ... | gateway=${tg_if1_ip4} | interface=${DUT1_${int}1}[0]
| | | ${tunnel_sw_index}= | Add Geneve Tunnel
| | | ... | ${dut1} | ${gen_tunnel.local} | ${gen_tunnel.remote}
| | | ... | ${${gen_tunnel.vni} + ${nr}} | l3_mode=${True}
| | | ... | next_index=${next_index}
| | | ${tunnel_if_key}= | Get Interface By SW Index
| | | ... | ${dut1} | ${tunnel_sw_index}
| | | ${tunnel_if_mac}= | Get Interface MAC
| | | ... | ${dut1} | ${tunnel_if_key}
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${tunnel_if_key} | ${if_ip} | 24
| | | VPP Add IP Neighbor
| | | ... | ${dut1} | ${tunnel_if_key} | ${dut1_if2_ip4} | ${DUT1_vf2_mac}[0]
| | | Vpp Route Add
| | | ... | ${dut1} | ${dst_ip} | ${gen_tunnel.ip_mask} | interface=${tunnel_if_key}
#| | | ... | gateway=${tg_if2_ip4} | interface=${tunnel_if_key}
#| | | ... | gateway=${dut1_if2_ip4} | interface=${tunnel_if_key}
| | | Vpp Route Add
| | | ... | ${dut1} | ${gen_tunnel.remote} | 32
| | | ... | gateway=${tg_if2_ip4} | interface=${DUT1_${int}2}[0]
| | | VPP Add IP Neighbor
| | | ... | ${dut1} | ${tunnel_if_key} | ${gen_tunnel.local} | ${tunnel_if_mac}
| | | Vpp Route Add
| | | ... | ${dut1} | ${gen_tunnel.local} | 32 | gateway=${if_ip}
| | | Set Interface State
| | | ... | ${dut1} | ${tunnel_if_key} | up
| | END
| | All VPP Interfaces Ready Wait | ${nodes} | retries=${60}
