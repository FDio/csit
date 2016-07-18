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

"""IPv6 keywords"""

*** Settings ***
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.topology.Topology
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/counters.robot
| Documentation | IPv6 keywords

*** Keywords ***
| Ipv6 icmp echo
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${tg_node} | ${dut_node} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${dut_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}
| | Vpp dump stats | ${dst_node}
| | ${ipv6_counter}= | Vpp get interface ipv6 counter | ${dst_node} | ${dst_port}
| | Should Be Equal | ${ipv6_counter} | ${2} | #ICMPv6 neighbor advertisement + ICMPv6 echo request

| Ipv6 icmp echo sweep
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${src_node} | ${dst_node} | ${start_size} | ${end_size}
| | ...         | ${step} | ${nodes_addr}
| | Append Nodes | ${src_node} | ${dst_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Set Variable
| | ...      | ${args} --start_size ${start_size} --end_size ${end_size} --step ${step}
| | Run Traffic Script On Node | ipv6_sweep_ping.py | ${src_node} | ${args}

| Ipv6 tg to dut1 egress
| | [Documentation] | Send traffic from TG to first DUT egress interface
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${first_dut} | ${second_dut}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hop_port} | ${hop_node}= | First Ingress Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${hop_node} | ${hop_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}


| Ipv6 tg to dut2 via dut1
| | [Documentation] | Send traffic from TG to second DUT through first DUT
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${first_dut} | ${second_dut}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hop_port} | ${hop_node}= | First Ingress Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${hop_node} | ${hop_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}

| Ipv6 tg to dut2 egress via dut1
| | [Documentation] | Send traffic from TG to second DUT egress interface through first DUT
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${first_dut} | ${second_dut} | ${tg_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hop_port} | ${hop_node}= | First Ingress Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${hop_node} | ${hop_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}

| Ipv6 tg to tg routed
| | [Documentation] | Send traffic from one TG port to another through DUT nodes
| | ...             | and send reply back, also verify hop limit processing
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${first_dut} | ${second_dut} | ${tg_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_nh_port} | ${src_nh_node}= | First Ingress Interface
| | ${dst_nh_port} | ${dst_nh_node}= | Last Egress Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${src_node} | ${dst_port}
| | ${src_nh_mac}= | Get Interface Mac | ${src_nh_node} | ${src_nh_port}
| | ${dst_nh_mac}= | Get Interface Mac | ${dst_nh_node} | ${dst_nh_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${dst_port_name}= | Get interface name | ${dst_node} | ${dst_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${dst_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Catenate | ${args} | --src_nh_mac ${src_nh_mac}
| |          | ...      | --dst_nh_mac ${dst_nh_mac} | --h_num 2
| | Run Traffic Script On Node | icmpv6_echo_req_resp.py | ${tg_node} | ${args}

| Ipv6 neighbor solicitation
| | [Documentation] | Send IPv6 neighbor solicitation from TG to DUT
| | [Arguments] | ${tg_node} | ${dut_node} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${dut_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | ipv6_ns.py | ${src_node} | ${args}

| Setup ipv6 to all dut in topology
| | [Documentation] | Setup IPv6 address on all DUTs
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Setup all DUTs before test
| | ${interfaces}= | Nodes Set Ipv6 Addresses | ${nodes} | ${nodes_addr}
| | :FOR | ${interface} | IN | @{interfaces}
| | | Set Interface State | @{interface} | up | if_type=name
| | All Vpp Interfaces Ready Wait | ${nodes}

| Clear ipv6 on all dut in topology
| | [Documentation] | Remove IPv6 address on all DUTs
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Nodes Clear Ipv6 Addresses | ${nodes} | ${nodes_addr}

| Vpp nodes ra suppress link layer
| | [Documentation] | Suppress ICMPv6 router advertisement message for link scope address
| | [Arguments] | ${nodes}
| | Vpp All Ra Suppress Link Layer | ${nodes}

| Vpp nodes setup ipv6 routing
| | [Documentation] | Setup routing on all VPP nodes required for IPv6 tests
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Append Nodes | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${tg}= | Set Variable | ${nodes['TG']}
| | ${dut1_if} | ${dut1}= | First Interface
| | ${dut2_if} | ${dut2}= | Last Interface
| | ${dut1_if_addr}= | Get Node Port Ipv6 Address | ${dut1} | ${dut1_if} | ${nodes_addr}
| | ${dut2_if_addr}= | Get Node Port Ipv6 Address | ${dut2} | ${dut2_if} | ${nodes_addr}
| | @{tg_dut1_links}= | Get active links connecting "${tg}" and "${dut1}"
| | @{tg_dut2_links}= | Get active links connecting "${tg}" and "${dut2}"
| | :FOR | ${link} | IN | @{tg_dut1_links}
| | | ${net}= | Get Link Address | ${link} | ${nodes_addr}
| | | ${prefix}= | Get Link Prefix | ${link} | ${nodes_addr}
| | | Vpp Route Add | ${dut2} | ${net} | ${prefix} | ${dut1_if_addr} | ${dut2_if}
| | :FOR | ${link} | IN | @{tg_dut2_links}
| | | ${net}= | Get Link Address | ${link} | ${nodes_addr}
| | | ${prefix}= | Get Link Prefix | ${link} | ${nodes_addr}
| | | Vpp Route Add | ${dut1} | ${net} | ${prefix} | ${dut2_if_addr} | ${dut1_if}
