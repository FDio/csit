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
| | Set interfaces in path up
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_if1_ip4} | 32
| | ${next_index}= | VPP Add Node Next
| | ... | ${dut1} | geneve4-input | ethernet-input
| | FOR | ${tunnel} | IN | @{geneve_tunnels}
| | | ${tunnel_sw_index}= | Add Geneve Tunnel
| | | ... | ${dut1} | ${tunnel.local} | ${tunnel.remote} | ${tunnel.vni}
| | | ... | l3_mode=${True} | next_index=${next_index}
| | | ${tunnel_if_key}= | Get Interface By SW Index
| | | ... | ${dut1} | ${tunnel_sw_index}
| | | Set Interface State
| | | ... | ${dut1} | ${tunnel_if_key} | up
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${tunnel_if_key} | ${tunnel.if_ip} | 32
| | | VPP Add IP Neighbor
| | | ... | ${dut1} | ${tunnel_if_key} | ${tunnel.remote} | ${TG_pf2_mac}[0]
| | | Vpp Route Add
| | | ... | ${dut1} | ${tunnel.dst_ip} | ${tunnel.ip_mask}
| | | ... | gateway=${tunnel.remote} | interface=${tunnel_if_key}
| | | VPP Add IP Neighbor
| | | ... | ${dut1} | ${DUT1_${int}1}[0] | ${tunnel.src_ip} | ${TG_pf1_mac}[0]
| | END
