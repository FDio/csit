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
| Initialize GENEVE L2 mode in circular topology
| | [Documentation] | Initialization of GENEVE L2 mode on DUT1.
| |
| | Create L2 BD | ${dut1} | ${bd_id}
| | Add interface to bridge domain | ${dut1} | ${DUT1_${int}1}[0] | ${bd_id}
| | FOR | ${tunnel} | IN | @{geneve_tunnels}
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tunnel.local} | 32
| | | VPP Add IP Neighbor
| | | ... | ${dut2} | ${DUT2_${int}1}[0] | ${tunnel.remote} | ${TG_pf2_mac}[0]
| | | ${tunnel_sw_index}= | Add Geneve Tunnel
| | | ... | ${dut1} | ${tunnel.local} | ${tunnel.remote} | ${tunnel.vni}
| | | ${tunnel_if_key}= | Get Interface By SW Index
| | | ... | ${dut1} | ${tunnel_sw_index}
| | | Add Interface To Bridge Domain | ${dut1} | ${tunnel_if_key} | ${bd_id}
| | | VPP Add L2FIB Entry
| | | ... | ${dut1} | ${tunnel.dst_mac} | ${tunnel_if_key} | ${bd_id}
| | END
