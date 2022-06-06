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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
|
| Documentation | GTPU keywords.

*** Keywords ***
| Initialize IP4 forwarding with GTPU tunnel in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Create GTPU tunnel on both DUT nodes, setup IPv4 adresses
| | ... | with /30 prefix on DUT1-DUT2 link, and set routing on both DUT nodes
| | ... | with prefix /24 and next hop of neighbour DUT interface. Gtpu offload
| | ... | rx will be enabled on both DUT nodes if offload is set to true.
| |
| | ... | *Arguments:*
| | ... | - offload - False or True. Type: bool
| |
| | [Arguments] | ${offload}=${False}
| |
| | VPP Interface Set IP Address | ${dut1} | ${DUT1_${int}1}[0]
| | ... | 10.10.10.1 | 24
| | VPP Interface Set IP Address | ${dut1} | ${DUT1_${int}2}[0]
| | ... | 1.1.1.2 | 30
| | VPP Interface Set IP Address | ${dut2} | ${DUT2_${int}1}[0]
| | ... | 1.1.1.1 | 30
| | VPP Interface Set IP Address | ${dut2} | ${DUT2_${int}2}[0]
| | ... | 20.20.20.1 | 24
| |
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 10.10.10.2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 1.1.1.1 | ${DUT2_${int}1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 1.1.1.2 | ${DUT1_${int}2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}2}[0] | 20.20.20.2 | ${TG_pf2_mac}[0]
| |
| | ${dut1_tunnel_if_index}= | Create GTPU Tunnel Interface | ${dut1}
| | ... | source_ip=1.1.1.2 | destination_ip=1.1.1.1 | teid=${10}
| | ${dut2_tunnel_if_index}= | Create GTPU Tunnel Interface | ${dut2}
| | ... | source_ip=1.1.1.1 | destination_ip=1.1.1.2 | teid=${10}
| |
| | Set Interface State | ${dut1} | ${dut1_tunnel_if_index} | up
| | Set Interface State | ${dut2} | ${dut2_tunnel_if_index} | up
| |
| | VPP Interface Set IP Address | ${dut1} | ${dut1_tunnel_if_index}
| | ... | 10.10.1.2 | 24
| | VPP Interface Set IP Address | ${dut2} | ${dut2_tunnel_if_index}
| | ... | 10.10.1.1 | 24
| |
| | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | gateway=1.1.1.2
| | ... | interface=${dut1_tunnel_if_index}
| | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | gateway=1.1.1.1
| | ... | interface=${dut2_tunnel_if_index}
| |
| | Vpp Get Ice | ${dut1}
| | Vpp Get DDP | ${dut1}
| | Vpp Set Flow | ${dut1} | ${DUT1_${int}2}[0]
| |
| | Run keyword if | ${offload} == ${True}
| | ... | Vpp Enable GTPU Offload rx
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut1_tunnel_if_index}
| | Run keyword if | ${offload} == ${True}
| | ... | Vpp Enable GTPU Offload rx
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut2_tunnel_if_index}
