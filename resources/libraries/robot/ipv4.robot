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
| Library | resources.libraries.python.IPv4Util
| Library | resources.libraries.python.TrafficScriptExecutor
| Variables | resources/libraries/python/IPv4NodeAddress.py

*** Keywords ***

| Setup IPv4 adresses on all DUT nodes in topology
| | [Documentation] | Setup IPv4 address on all DUTs in topology
| | [Arguments] | ${nodes} | ${nodes_addr}
| | DUT Nodes setup IPv4 addresses | ${nodes} | ${nodes_addr}

| Interfaces needed for IPv4 testing are in "${state}" state
| | Node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port1']['name']}" is in "${state}" state
| | Node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port3']['name']}" is in "${state}" state
| | Node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port1']['name']}" is in "${state}" state
| | Node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port3']['name']}" is in "${state}" state

| Routes are set up for IPv4 testing
| | ${gateway} = | Get IPv4 address of node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port3']['name']}"
| | ${subnet} = | Get IPv4 subnet of node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port1']['name']}"
| | ${prefix_length} = | Get IPv4 address prefix of node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port1']['name']}"
| | Node "${nodes['DUT1']}" routes to IPv4 network "${subnet}" with prefix length "${prefix_length}" using interface "${nodes['DUT1']['interfaces']['port3']['name']}" via "${gateway}"
| | ${gateway} = | Get IPv4 address of node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port3']['name']}"
| | ${subnet} = | Get IPv4 subnet of node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port1']['name']}"
| | ${prefix_length} = | Get IPv4 address prefix of node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port1']['name']}"
| | Node "${nodes['DUT2']}" routes to IPv4 network "${subnet}" with prefix length "${prefix_length}" using interface "${nodes['DUT2']['interfaces']['port3']['name']}" via "${gateway}"

| Setup DUT nodes for IPv4 testing
| | Interfaces needed for IPv4 testing are in "up" state
| | Setup IPv4 adresses on all DUT nodes in topology | ${nodes} | ${nodes_ipv4_addr}
| | Setup ARP on all DUTs | ${nodes}
| | Routes are set up for IPv4 testing

| Setup nodes for IPv4 testing
| | Interfaces needed for IPv4 testing are in "up" state
| | Setup IPv4 adresses on all DUT nodes in topology | ${nodes} | ${nodes_ipv4_addr}
| | Setup ARP on all DUTs | ${nodes}
| | Routes are set up for IPv4 testing
| | Sleep | 10

| TG interface "${tg_port}" can route to node "${node}" interface "${port}" "${hops}" hops away using IPv4
| | Node "${nodes['TG']}" interface "${tg_port}" can route to node "${node}" interface "${port}" "${hops}" hops away using IPv4

| Node "${from_node}" interface "${from_port}" can route to node "${to_node}" interface "${to_port}" "${hops}" hops away using IPv4
| | After ping is sent in topology "${nodes}" from node "${from_node}" interface "${from_port}" with destination IPv4 address of node "${to_node}" interface "${to_port}" a ping response arrives and TTL is decreased by "${hops}"

| Ipv4 icmp echo sweep
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${src_node} | ${dst_node} | ${src_port} | ${dst_port}
| | ${src_ip}= | Get IPv4 address of node "${src_node}" interface "${src_port}"
| | ${dst_ip}= | Get IPv4 address of node "${dst_node}" interface "${dst_port}"
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port} | ${src_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| # TODO: end_size is currently minimum MTU size for Ethernet minus IPv4 and
| # ICMP echo header size (1500 - 20 - 8),
| # MTU info is not in VAT sw_interface_dump output
| | ${args}= | Set Variable | ${args} --start_size 0 --end_size 1472 --step 1
| | Run Traffic Script On Node | ipv4_sweep_ping.py | ${src_node} | ${args}

| Send ARP request and validate response
| | [Arguments] | ${tg_node} | ${vpp_node}
| | ${link_name}= | Get first active connecting link between node "${tg_node}" and "${vpp_node}"
| | ${src_if}= | Get interface by link name | ${tg_node} | ${link_name}
| | ${dst_if}= | Get interface by link name | ${vpp_node} | ${link_name}
| | ${src_ip}= | Get IPv4 address of node "${tg_node}" interface "${src_if}"
| | ${dst_ip}= | Get IPv4 address of node "${vpp_node}" interface "${dst_if}"
| | ${src_mac}= | Get node link mac | ${tg_node} | ${link_name}
| | ${dst_mac}= | Get node link mac | ${vpp_node} | ${link_name}
| | ${args}= | Traffic Script Gen Arg | ${src_if} | ${src_if} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | arp_request.py | ${tg_node} | ${args}

