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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/ipv4.robot
| Suite Setup | Run Keywords | Setup all DUTs before test
| ...         | AND          | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| ...         | AND          | Setup DUT nodes for IPv4 testing
| Test Setup | Clear interface counters on all vpp nodes in topology | ${nodes}

*** Test Cases ***

| VPP replies to ICMPv4 echo request
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${0}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4

| TG can route to DUT egress interface
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hops}= | Set Variable | ${0}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4

| TG can route to DUT2 through DUT1
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${1}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4

| TG can route to DUT2 egress interface through DUT1
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Egress Interface
| | ${hops}= | Set Variable | ${1}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4

| TG can route to TG through DUT1 and DUT2
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | ${hops}= | Set Variable | ${2}
| | Node "${src_node}" interface "${src_port}" can route to node "${dst_node}" interface "${dst_port}" ${hops} hops away using IPv4
| | ${port} | ${node}= | Next Interface
| | ${port} | ${node}= | Next Interface
| | ${exp_counter_val}= | Set Variable | ${1}
| | Vpp dump stats table | ${node}
| | Check ipv4 interface counter | ${node} | ${port} | ${exp_counter_val}
| | ${port} | ${node}= | Next Interface
| | Check ipv4 interface counter | ${node} | ${port} | ${exp_counter_val}
| | ${port} | ${node}= | Next Interface
| | Vpp dump stats table | ${node}
| | Check ipv4 interface counter | ${node} | ${port} | ${exp_counter_val}
| | ${port} | ${node}= | Next Interface
| | Check ipv4 interface counter | ${node} | ${port} | ${exp_counter_val}

| VPP can process ICMP echo request from min to max packet size with 1B increment
| | Ipv4 icmp echo sweep | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                  | ${nodes['TG']['interfaces']['port3']['name']}
| | ...                  | ${nodes['DUT1']['interfaces']['port1']['name']}

| VPP responds to ARP request
| | Send ARP request and validate response | ${nodes['TG']} | ${nodes['DUT1']}
