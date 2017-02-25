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
#| Resource | resources/libraries/robot/interfaces.robot
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPv6Util

*** Keywords ***
| Setup VRF on DUT
| | [Documentation]
| | ... | The keyword sets a FIB table on a DUT, assigns two interfaces to it,\
| | ... | adds two ARP items and a route, see example.
| | ...
| | ... | *Arguments*
| | ... | - node - DUT node. Type: dictionary
| | ... | - table - FIB table ID. Type: integer
| | ... | - route_interface - Destination interface to be assigned to FIB.\
| | ... | Type: string
| | ... | - route_gateway_ip - Route gateway IP address. Type: string
| | ... | - route_gateway_mac - Route gateway MAC address. Type string
| | ... | - route_dst_ip - Route destination IP. Type: string
| | ... | - vrf_src_if - Source interface to be assigned to FIB. Type: string
| | ... | - src_if_ip - IP address of the source interface. Type: string
| | ... | - src_if_mac - MAC address of the source interface. Type: string
| | ... | - prefix_len - Prefix length. Type: int
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
| | ... | via ${route_gateway_ip} sw_if_index ${route_interface_idx} multipath
| | ...
| | Assign Interface To Fib Table
| | ... | ${node} | ${route_interface} | ${table}
| | Assign Interface To Fib Table
| | ... | ${node} | ${vrf_src_if} | ${table}
| | ...
| | Add IP Neighbor | ${node} | ${vrf_src_if}
| | ... | ${src_if_ip} | ${src_if_mac}
| | Add IP Neighbor | ${node} | ${route_interface}
| | ... | ${route_gateway_ip} | ${route_gateway_mac}
| | ...
| | Vpp Route Add | ${node} | ${route_dst_ip} | ${prefix_len}
| | ... | ${route_gateway_ip} | ${route_interface} | vrf=${table}
