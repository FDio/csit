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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficScriptExecutor
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Documentation | IPv6 keywords

*** Keywords ***
| Send IPv6 icmp echo request to DUT1 ingress inteface and verify answer
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${tg_node} | ${dut_node} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${dut_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port}
| | ... | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port}
| | ... | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name}
| | ... | ${src_mac}
| | ... | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}
| | Vpp Dump Stats Table | ${dst_node}
| | ${ipv6_counter}= | Vpp Get Ipv6 Interface Counter | ${dst_node}
| | ... | ${dst_port}
| | Should Be Equal | ${ipv6_counter} | ${2}
| | ... | #ICMPv6 neighbor advertisement + ICMPv6 echo request

| Execute IPv6 ICMP echo sweep
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${src_node} | ${dst_node} | ${start_size} | ${end_size}
| | ... | ${step} | ${nodes_addr}
| | Append Nodes | ${src_node} | ${dst_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port}
| | ... | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port}
| | ... | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name}
| | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Set Variable
| | ... | ${args} --start_size ${start_size} --end_size ${end_size}
| | ... | --step ${step}
| | Run Traffic Script On Node | ipv6_sweep_ping.py | ${src_node} | ${args}
| | ... | timeout=${180}

| Send IPv6 ICMP echo request to DUT1 egress interface and verify answer
| | [Documentation] | Send traffic from TG to first DUT egress interface
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${first_dut} | ${second_dut}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hop_port} | ${hop_node}= | First Ingress Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port}
| | ... | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port}
| | ... | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${hop_node} | ${hop_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name}
| | ... | ${src_mac}
| | ... | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}


| Send IPv6 ICMP echo request to DUT2 via DUT1 and verify answer
| | [Documentation] | Send traffic from TG to second DUT through first DUT
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${first_dut} | ${second_dut}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hop_port} | ${hop_node}= | First Ingress Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port}
| | ... | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port}
| | ... | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${hop_node} | ${hop_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name}
| | ... | ${src_mac}
| | ... | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}

| Send IPv6 ICMP echo request to DUT2 egress interface via DUT1 and verify answer
| | [Documentation] | Send traffic from TG to second DUT egress interface
| | ... | through first DUT
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${first_dut} | ${second_dut} | ${tg_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hop_port} | ${hop_node}= | First Ingress Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port}
| | ... | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port}
| | ... | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${hop_node} | ${hop_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name}
| | ... | ${src_mac}
| | ... | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}

| Ipv6 tg to tg routed
| | [Documentation] | Send traffic from one TG port to another through DUT nodes
| | ... | and send reply back, also verify hop limit processing
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${first_dut} | ${second_dut} | ${tg_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_nh_port} | ${src_nh_node}= | First Ingress Interface
| | ${dst_nh_port} | ${dst_nh_node}= | Last Egress Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port}
| | ... | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port}
| | ... | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${src_node} | ${dst_port}
| | ${src_nh_mac}= | Get Interface Mac | ${src_nh_node} | ${src_nh_port}
| | ${dst_nh_mac}= | Get Interface Mac | ${dst_nh_node} | ${dst_nh_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${dst_port_name}= | Get interface name | ${dst_node} | ${dst_port}
| | ${args}= | Traffic Script Gen Arg | ${dst_port_name} | ${src_port_name}
| | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Catenate | ${args} | --src_nh_mac ${src_nh_mac}
| | ... | --dst_nh_mac ${dst_nh_mac} | --h_num 2
| | Run Traffic Script On Node | icmpv6_echo_req_resp.py | ${tg_node} | ${args}

| Send IPv6 neighbor solicitation and verify answer
| | [Documentation] | Send IPv6 neighbor solicitation from TG to DUT
| | [Arguments] | ${tg_node} | ${dut_node} | ${nodes_addr}
| | Append Nodes | ${tg_node} | ${dut_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port}
| | ... | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port}
| | ... | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name}
| | ... | ${src_mac}
| | ... | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | ipv6_ns.py | ${src_node} | ${args}

| Configure IPv6 on all DUTs in topology
| | [Documentation] | Setup IPv6 address on all DUTs
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Configure all DUTs before test
| | ${interfaces}= | Nodes Set Ipv6 Addresses | ${nodes} | ${nodes_addr}
| | :FOR | ${interface} | IN | @{interfaces}
| | | Set Interface State | @{interface} | up | if_type=name
| | All Vpp Interfaces Ready Wait | ${nodes}

| Suppress ICMPv6 router advertisement message
| | [Documentation] | Suppress ICMPv6 router advertisement message for link
| | ... | scope address
| | [Arguments] | ${nodes}
| | Vpp All Ra Suppress Link Layer | ${nodes}

| Configure IPv6 routing on all DUTs
| | [Documentation] | Setup routing on all VPP nodes required for IPv6 tests
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Append Nodes | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${tg}= | Set Variable | ${nodes['TG']}
| | ${dut1_if} | ${dut1}= | First Interface
| | ${dut2_if} | ${dut2}= | Last Interface
| | ${dut1_if_addr}= | Get Node Port Ipv6 Address | ${dut1} | ${dut1_if}
| | ... | ${nodes_addr}
| | ${dut2_if_addr}= | Get Node Port Ipv6 Address | ${dut2} | ${dut2_if}
| | ... | ${nodes_addr}
| | @{tg_dut1_links}= | Get active links connecting "${tg}" and "${dut1}"
| | @{tg_dut2_links}= | Get active links connecting "${tg}" and "${dut2}"
| | :FOR | ${link} | IN | @{tg_dut1_links}
| | | ${net}= | Get Link Address | ${link} | ${nodes_addr}
| | | ${prefix}= | Get Link Prefix | ${link} | ${nodes_addr}
| | | Vpp Route Add | ${dut2} | ${net} | ${prefix} | ${dut1_if_addr}
| | | ... | ${dut2_if}
| | :FOR | ${link} | IN | @{tg_dut2_links}
| | | ${net}= | Get Link Address | ${link} | ${nodes_addr}
| | | ${prefix}= | Get Link Prefix | ${link} | ${nodes_addr}
| | | Vpp Route Add | ${dut1} | ${net} | ${prefix} | ${dut2_if_addr}
| | | ... | ${dut1_if}

| Initialize IPv6 forwarding in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| | ...
| | [Arguments] | ${tg_if1_ip6} | ${tg_if2_ip6} | ${dut1_if1_ip6}
| | ... | ${dut1_if2_ip6} | ${dut2_if1_ip6}=${NONE} | ${dut2_if2_ip6}=${NONE}
| | ... | ${remote_host1_ip6}=${NONE} | ${remote_host2_ip6}=${NONE}
| | ... | ${remote_host_ip6_prefix}=${NONE}
| | ...
| | ${dut_tg_ip6_prefix}= | Set Variable | 64
| | ${dut_link_ip6_prefix}= | Set Variable | 96
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2_node}
| | ...
| | Set interfaces in path up
| | ...
| | ${dut1}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut1_node} | ${dut_node}
| | ${dut2}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut2_node}
| | ${tg_if1}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut1_to_tg} | ${dut_to_tg_if1}
| | ${tg_if2}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut2_to_tg} | ${dut_to_tg_if2}
| | ${tg_if1_mac}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${tg_to_dut1_mac} | ${tg_to_dut_if1_mac}
| | ${tg_if2_mac}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${tg_to_dut2_mac} | ${tg_to_dut_if2_mac}
| | ${dut1_if1}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut1_to_tg} | ${dut_to_tg_if1}
| | ${dut1_if2}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut1_to_dut2} | ${dut_to_tg_if2}
| | ${dut1_if2_mac}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut1_to_dut2_mac}
| | ${dut2_if1}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut2_to_dut1}
| | ${dut2_if2}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut2_to_tg}
| | ${dut2_if1_mac}= | Set Variable If | '${dut2_status}' == 'PASS'
| | ... | ${dut2_to_dut1_mac}
| | ...
| | Add IP neighbor | ${dut1} | ${dut1_if1} | ${tg_if1_ip6} | ${tg_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add IP neighbor | ${dut1} | ${dut1_if2} | ${dut2_if1_ip6}
| | ... | ${dut2_if1_mac}
| | ... | ELSE
| | ... | Add IP neighbor | ${dut1} | ${dut1_if2} | ${tg_if2_ip6}
| | ... | ${tg_if2_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add IP neighbor | ${dut2} | ${dut2_if1} | ${dut1_if2_ip6}
| | ... | ${dut1_if2_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add IP neighbor | ${dut2} | ${dut2_if2} | ${tg_if2_ip6}
| | ... | ${tg_if2_mac}
| | ...
| | VPP set If IPv6 addr | ${dut1} | ${dut1_if1} | ${dut1_if1_ip6}
| | ... | ${dut_tg_ip6_prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP set If IPv6 addr | ${dut1} | ${dut1_if2} | ${dut1_if2_ip6}
| | ... | ${dut_link_ip6_prefix}
| | ... | ELSE
| | ... | VPP set If IPv6 addr | ${dut1} | ${dut1_if2} | ${dut1_if2_ip6}
| | ... | ${dut_tg_ip6_prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP set If IPv6 addr | ${dut2} | ${dut2_if1} | ${dut2_if1_ip6}
| | ... | ${dut_link_ip6_prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP set If IPv6 addr | ${dut2} | ${dut2_if2} | ${dut2_if2_ip6}
| | ... | ${dut_tg_ip6_prefix}
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${tg_if2_ip6} | ${dut_tg_ip6_prefix}
| | ... | ${dut2_if1_ip6} | ${dut1_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${tg_if1_ip6} | ${dut_tg_ip6_prefix}
| | ... | ${dut1_if2_ip6} | ${dut2_if1}
| | ...
| | Run Keyword Unless | '${remote_host1_ip6}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip6}
| | ... | ${remote_host_ip6_prefix} | ${tg_if1_ip6} | ${dut1_if1}
| | Run Keyword Unless
| | ... | '${remote_host2_ip6}' == '${NONE}' or '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${remote_host2_ip6}
| | ... | ${remote_host_ip6_prefix} | ${tg_if2_ip6} | ${dut1_if2}
| | Run Keyword Unless
| | ... | '${remote_host2_ip6}' == '${NONE}' or '${dut2_status}' == 'FAIL'
| | ... | Vpp Route Add | ${dut1} | ${remote_host2_ip6}
| | ... | ${remote_host_ip6_prefix} | ${dut2_if1_ip6} | ${dut1_if2}
| | Run Keyword Unless
| | ... | '${remote_host1_ip6}' == '${NONE}' or '${dut2_status}' == 'FAIL'
| | ... | Vpp Route Add | ${dut2} | ${remote_host1_ip6}
| | ... | ${remote_host_ip6_prefix} | ${dut1_if2_ip6} | ${dut2_if1}
| | Run Keyword Unless
| | ... | '${remote_host2_ip6}' == '${NONE}' or '${dut2_status}' == 'FAIL'
| | ... | Vpp Route Add | ${dut2} | ${remote_host2_ip6}
| | ... | ${remote_host_ip6_prefix} | ${tg_if2_ip6} | ${dut2_if2}
