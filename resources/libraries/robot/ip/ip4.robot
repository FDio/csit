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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Library | resources.libraries.python.IPv4Util.IPv4Util
| Library | resources.libraries.python.IPv4Setup.IPv4Setup
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.InterfaceUtil
| Variables | resources/libraries/python/IPv4NodeAddress.py | ${nodes}

*** Keywords ***

| Show IP FIB On All DUTs
| | [Documentation] | Show IP FIB on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | VPP Show IP Table | ${nodes['${dut}']}

| Configure IPv4 addresses on all DUTs
| | [Documentation] | Setup IPv4 address on all DUTs in topology
| | [Arguments] | ${nodes} | ${nodes_addr}
| | ${interfaces}= | VPP nodes set ipv4 addresses | ${nodes} | ${nodes_addr}
| | :FOR | ${interface} | IN | @{interfaces}
| | | Set Interface State | @{interface} | up | if_type=name

| Configure routes for IPv4 test
| | [Documentation] | Setup routing on all VPP nodes required for IPv4 tests
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Append Nodes | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${tg}= | Set Variable | ${nodes['TG']}
| | ${dut1_if} | ${dut1}= | First Interface
| | ${dut2_if} | ${dut2}= | Last Interface
| | ${dut1_if_addr}= | Get IPv4 address of node "${dut1}" interface "${dut1_if}" from "${nodes_addr}"
| | ${dut2_if_addr}= | Get IPv4 address of node "${dut2}" interface "${dut2_if}" from "${nodes_addr}"
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

| Configure DUT nodes for IPv4 testing
| | Configure IPv4 addresses on all DUTs | ${nodes} | ${nodes_ipv4_addr}
| | Setup ARP on all DUTs | ${nodes} | ${nodes_ipv4_addr}
| | Configure routes for IPv4 test | ${nodes} | ${nodes_ipv4_addr}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Route traffic from interface '${from_port}' on node '${from_node}' to interface '${to_port}' on node '${to_node}' '${hops}' hops away using IPv4
| | ${src_ip}= | Get IPv4 address of node "${from_node}" interface "${from_port}" from "${nodes_ipv4_addr}"
| | ${dst_ip}= | Get IPv4 address of node "${to_node}" interface "${to_port}" from "${nodes_ipv4_addr}"
| | ${src_mac}= | Get interface mac | ${from_node} | ${from_port}
| | ${dst_mac}= | Get interface mac | ${to_node} | ${to_port}
| | ${is_dst_tg}= | Is TG node | ${to_node}
| | ${adj_node} | ${adj_int}= | Get adjacent node and interface | ${nodes} | ${from_node} | ${from_port}
| | ${from_port_name}= | Get interface name | ${from_node} | ${from_port}
| | ${to_port_name}= | Get interface name | ${to_node} | ${to_port}
| | ${adj_int_mac}= | Get interface MAC | ${adj_node} | ${adj_int}
| | ${args}= | Traffic Script Gen Arg | ${to_port_name} | ${from_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Catenate | ${args} | --hops ${hops} | --first_hop_mac ${adj_int_mac}
| |          | ...      | --is_dst_tg ${is_dst_tg}
| | Run Traffic Script On Node | ipv4_ping_ttl_check.py | ${from_node} | ${args}

| Execute IPv4 ICMP echo sweep
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${src_node} | ${dst_node} | ${start_size} | ${end_size} | ${step}
| | Append Nodes | ${src_node} | ${dst_node}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${src_ip}= | Get IPv4 address of node "${src_node}" interface "${src_port}" from "${nodes_ipv4_addr}"
| | ${dst_ip}= | Get IPv4 address of node "${dst_node}" interface "${dst_port}" from "${nodes_ipv4_addr}"
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${src_port_name}= | Get interface name | ${src_node} | ${src_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port_name} | ${src_port_name}
| |          | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Set Variable
| | ... | ${args} --start_size ${start_size} --end_size ${end_size} --step ${step}
| | Run Traffic Script On Node | ipv4_sweep_ping.py | ${src_node} | ${args}
| | ... | timeout=${180}

| Send ARP request and verify response
| | [Arguments] | ${tg_node} | ${vpp_node}
| | ${link_name}= | Get first active connecting link between node "${tg_node}" and "${vpp_node}"
| | ${src_if}= | Get interface by link name | ${tg_node} | ${link_name}
| | ${dst_if}= | Get interface by link name | ${vpp_node} | ${link_name}
| | ${src_ip}= | Get IPv4 address of node "${tg_node}" interface "${src_if}" from "${nodes_ipv4_addr}"
| | ${dst_ip}= | Get IPv4 address of node "${vpp_node}" interface "${dst_if}" from "${nodes_ipv4_addr}"
| | ${src_mac}= | Get node link mac | ${tg_node} | ${link_name}
| | ${dst_mac}= | Get node link mac | ${vpp_node} | ${link_name}
| | ${src_if_name}= | Get interface name | ${tg_node} | ${src_if}
| | ${args}= | Traffic Script Gen Arg | ${src_if_name} | ${src_if_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | arp_request.py | ${tg_node} | ${args}

| Configure IP addresses on interfaces
| | [Documentation] | Iterates through @{args} list and Set Interface Address
| | ... | for every (${dut_node}, ${interface}, ${address},
| | ... | ${prefix}) tuple.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - Node where IP address should be set to.
| | ... | Type: dictionary
| | ... | - ${interface} - Interface name. Type: string
| | ... | - ${address} - IP address. Type: string
| | ... | - ${prefix} - Prefix length. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IP addresses on interfaces \
| | ... | \| ${dut1_node} \| ${dut1_to_dut2} \| 192.168.1.1 \| 24 \|
| | ... | \| ... \| ${dut1_node} \| ${dut1_to_tg} \| 192.168.2.1 \| 24 \|
| | ...
| | [Arguments] | @{args}
| | :FOR | ${dut_node} | ${interface} | ${address} | ${prefix} | IN | @{args}
| | | Set Interface Address | ${dut_node} | ${interface} | ${address}
| | | ... | ${prefix}

| Send ICMP echo request and verify answer
| | [Documentation] | Run traffic script that waits for ICMP reply and ignores
| | ... | all other packets.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node where run traffic script. Type: dictionary
| | ... | - tg_interface - TG interface where send ICMP echo request.
| | ... | Type: string
| | ... | - dst_mac - Destination MAC address. Type: string
| | ... | - src_mac - Source MAC address. Type: string
| | ... | - dst_ip - Destination IP address. Type: string
| | ... | - src_ip - Source IP address. Type: string
| | ... | - timeout - Wait timeout in seconds (Default: 10). Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send ICMP echo request and verify answer \
| | ... | \| ${nodes['TG']} \| eth2 \
| | ... | \| 08:00:27:46:2b:4c \| 08:00:27:66:b8:57 \
| | ... | \| 192.168.23.10 \| 192.168.23.1 \| 10 \|
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface}
| | ... | ${dst_mac} | ${src_mac} | ${dst_ip} | ${src_ip} | ${timeout}=${10}
| | ...
| | ${tg_interface_name}= | Get interface name | ${tg_node} | ${tg_interface}
| | ${args}= | Catenate | --rx_if | ${tg_interface_name}
| | ... | --tx_if | ${tg_interface_name} | --dst_mac | ${dst_mac}
| | ... | --src_mac | ${src_mac} | --dst_ip | ${dst_ip} | --src_ip | ${src_ip}
| | ... | --timeout | ${timeout}
| | Run Traffic Script On Node | send_icmp_wait_for_reply.py
| | ... | ${tg_node} | ${args}

| Initialize IPv4 forwarding in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| | ...
| | [Arguments] | ${tg_if1_ip4} | ${tg_if2_ip4} | ${dut1_if1_ip4}
| | ... | ${dut1_if2_ip4} | ${dut2_if1_ip4}=${NONE} | ${dut2_if2_ip4}=${NONE}
| | ... | ${remote_host1_ip4}=${NONE} | ${remote_host2_ip4}=${NONE}
| | ...
| | ${dut_tg_ip4_prefix}= | Set Variable | 24
| | ${dut_link_ip4_prefix}= | Set Variable | 30
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
| | Add arp on dut | ${dut1} | ${dut1_if1} | ${tg_if1_ip4} | ${tg_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add arp on dut | ${dut1} | ${dut1_if2} | ${dut2_if1_ip4}
| | ... | ${dut2_if1_mac}
| | ... | ELSE
| | ... | Add arp on dut | ${dut1} | ${dut1_if2} | ${tg_if2_ip4} | ${tg_if2_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add arp on dut | ${dut2} | ${dut2_if1} | ${dut1_if2_ip4}
| | ... | ${dut1_if2_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add arp on dut | ${dut2} | ${dut2_if2} | ${tg_if2_ip4} | ${tg_if2_mac}
| | ...
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | ${dut1_if1_ip4} | ${dut_tg_ip4_prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | ${dut1_if2_ip4} | ${dut_link_ip4_prefix}
| | ... | ELSE
| | ... | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | ${dut1_if2_ip4} | ${dut_tg_ip4_prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1}
| | ... | ${dut2_if1_ip4} | ${dut_link_ip4_prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2}
| | ... | ${dut2_if2_ip4} | ${dut_tg_ip4_prefix}
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${tg_if2_ip4} | ${dut_tg_ip4_prefix}
| | ... | ${dut2_if1_ip4} | ${dut1_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${tg_if1_ip4} | ${dut_tg_ip4_prefix}
| | ... | ${dut1_if2_ip4} | ${dut2_if1}
| | ...
| | Run Keyword Unless | '${remote_host1_ip4}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip4} | ${dut_tg_ip4_prefix}
| | ... | ${tg_if1_ip4} | ${dut1_if1}
| | Run Keyword Unless
| | ... | '${remote_host2_ip4}' == '${NONE}' or '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${remote_host2_ip4} | ${dut_tg_ip4_prefix}
| | ... | ${tg_if2_ip4} | ${dut1_if2}
| | Run Keyword Unless
| | ... | '${remote_host2_ip4}' == '${NONE}' or '${dut2_status}' == 'FAIL'
| | ... | Vpp Route Add | ${dut1} | ${remote_host2_ip4} | ${dut_tg_ip4_prefix}
| | ... | ${dut2_if1_ip4} | ${dut1_if2}
| | Run Keyword Unless
| | ... | '${remote_host1_ip4}' == '${NONE}' or '${dut2_status}' == 'FAIL'
| | ... | Vpp Route Add | ${dut2} | ${remote_host1_ip4} | ${dut_tg_ip4_prefix}
| | ... | ${dut1_if2_ip4} | ${dut2_if1}
| | Run Keyword Unless
| | ... | '${remote_host2_ip4}' == '${NONE}' or '${dut2_status}' == 'FAIL'
| | ... | Vpp Route Add | ${dut2} | ${remote_host2_ip4} | ${dut_tg_ip4_prefix}
| | ... | ${tg_if2_ip4} | ${dut2_if2}
