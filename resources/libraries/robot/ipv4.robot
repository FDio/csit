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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/counters.robot
| Library | resources.libraries.python.IPv4Util.IPv4Util
| Library | resources.libraries.python.IPv4Setup.IPv4Setup
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.InterfaceUtil
| Variables | resources/libraries/python/IPv4NodeAddress.py | ${nodes}

*** Keywords ***

| Setup IPv4 adresses on all DUT nodes in topology
| | [Documentation] | Setup IPv4 address on all DUTs in topology
| | [Arguments] | ${nodes} | ${nodes_addr}
| | ${interfaces}= | VPP nodes set ipv4 addresses | ${nodes} | ${nodes_addr}
| | :FOR | ${interface} | IN | @{interfaces}
| | | Set Interface State | @{interface} | up

| Routes are set up for IPv4 testing
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

| Setup DUT nodes for IPv4 testing
| | Setup IPv4 adresses on all DUT nodes in topology | ${nodes} | ${nodes_ipv4_addr}
| | Setup ARP on all DUTs | ${nodes} | ${nodes_ipv4_addr}
| | Routes are set up for IPv4 testing | ${nodes} | ${nodes_ipv4_addr}
| | All Vpp Interfaces Ready Wait | ${nodes}

| TG interface "${tg_port}" can route to node "${node}" interface "${port}" "${hops}" hops away using IPv4
| | Node "${nodes['TG']}" interface "${tg_port}" can route to node "${node}" interface "${port}" "${hops}" hops away using IPv4

| Node "${from_node}" interface "${from_port}" can route to node "${to_node}" interface "${to_port}" ${hops} hops away using IPv4
| | ${src_ip}= | Get IPv4 address of node "${from_node}" interface "${from_port}" from "${nodes_ipv4_addr}"
| | ${dst_ip}= | Get IPv4 address of node "${to_node}" interface "${to_port}" from "${nodes_ipv4_addr}"
| | ${src_mac}= | Get interface mac | ${from_node} | ${from_port}
| | ${dst_mac}= | Get interface mac | ${to_node} | ${to_port}
| | ${is_dst_tg}= | Is TG node | ${to_node}
| | ${adj_node} | ${adj_int}= | Get adjacent node and interface | ${nodes} | ${from_node} | ${from_port}
| | ${args}= | Traffic Script Gen Arg | ${to_port} | ${from_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Catenate | ${args} | --hops ${hops} | --first_hop_mac ${adj_int['mac_address']}
| |          | ...      | --is_dst_tg ${is_dst_tg}
| | Run Traffic Script On Node | ipv4_ping_ttl_check.py | ${from_node} | ${args}

| Ipv4 icmp echo sweep
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${src_node} | ${dst_node} | ${src_port} | ${dst_port}
| | ${src_ip}= | Get IPv4 address of node "${src_node}" interface "${src_port}" from "${nodes_ipv4_addr}"
| | ${dst_ip}= | Get IPv4 address of node "${dst_node}" interface "${dst_port}" from "${nodes_ipv4_addr}"
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port} | ${src_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| # TODO: end_size is currently minimum MTU size for Ethernet minus IPv4 and
| # ICMP echo header size (1500 - 20 - 8),
| # MTU info is not in VAT sw_interface_dump output
| | ${args}= | Set Variable | ${args} --start_size 1 --end_size 1472 --step 1
| | Run Traffic Script On Node | ipv4_sweep_ping.py | ${src_node} | ${args}

| Send ARP request and validate response
| | [Arguments] | ${tg_node} | ${vpp_node}
| | ${link_name}= | Get first active connecting link between node "${tg_node}" and "${vpp_node}"
| | ${src_if}= | Get interface by link name | ${tg_node} | ${link_name}
| | ${dst_if}= | Get interface by link name | ${vpp_node} | ${link_name}
| | ${src_ip}= | Get IPv4 address of node "${tg_node}" interface "${src_if}" from "${nodes_ipv4_addr}"
| | ${dst_ip}= | Get IPv4 address of node "${vpp_node}" interface "${dst_if}" from "${nodes_ipv4_addr}"
| | ${src_mac}= | Get node link mac | ${tg_node} | ${link_name}
| | ${dst_mac}= | Get node link mac | ${vpp_node} | ${link_name}
| | ${args}= | Traffic Script Gen Arg | ${src_if} | ${src_if} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | arp_request.py | ${tg_node} | ${args}

