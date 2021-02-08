# Copyright (c) 2021 Cisco and/or its affiliates.
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
| | VPP GENEVE Add Multiple Tunnels
| | ... | ${dut1} | &{gen_tunnel} | ${n_tunnels} | ${DUT1_${int}1}[0]
| | ... | ${DUT1_${int}2}[0] | ${tg_if1_ip4} | ${tg_if2_ip4}
| | ... | ${TG_pf2_mac}[0] | ${next_index}
| |
| | All VPP Interfaces Ready Wait | ${nodes} | retries=${60}
