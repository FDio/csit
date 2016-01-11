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
| Library | resources/libraries/python/IPv4Util.py
| Variables | resources/libraries/python/IPv4NodeAddress.py

*** Keywords ***

| Setup IPv4 adresses on all nodes in topology
| | [Documentation] | Setup IPv4 address on all DUTs and TG in topology
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Nodes setup IPv4 addresses | ${nodes} | ${nodes_addr}

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

| Setup nodes for IPv4 testing
| | Interfaces needed for IPv4 testing are in "up" state
| | Setup IPv4 adresses on all nodes in topology | ${nodes} | ${nodes_ipv4_addr}
| | Routes are set up for IPv4 testing

| TG interface "${tg_port}" can route to node "${node}" interface "${port}" "${hops}" hops away using IPv4
| | Node "${nodes['TG']}" interface "${tg_port}" can route to node "${node}" interface "${port}" "${hops}" hops away using IPv4

| Node "${from_node}" interface "${from_port}" can route to node "${to_node}" interface "${to_port}" "${hops}" hops away using IPv4
| | After ping is sent from node "${from_node}" interface "${from_port}" with destination IPv4 address of node "${to_node}" interface "${to_port}" a ping response arrives and TTL is decreased by "${hops}"
