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
| Variables | resources/libraries/python/topology.py
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.TGSetup
| Library | resources.libraries.python.SFC.Classifier
| Library | Collections

*** Keywords ***
| Setup DUT nodes for Classifier functional testing
| | [Documentation] | Start the l2fwd with M worker threads without SMT
| | ... | and rxqueues N and B (yes or no) jumbo frames in all DUTs.
| | ...
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | Set Suite Variable | ${src_node}
| | Set Suite Variable | ${src_port}
| | Set Suite Variable | ${dst_node}
| | Set Suite Variable | ${dst_port}
| | ${adj_mac}= | Get interface mac | ${src_node} | ${src_port}
| | Configure and Start Classifier functional test | ${dst_node} | ${dst_port} | ${adj_mac}

| Node "${from_node}" interface "${from_port}" send ${frame_size} Bytes TCP packet to node "${to_node}" interface "${to_port}"
| | ${src_ip}= | 10.10.12.101
| | ${dst_ip}= | 10.10.12.100
| | ${src_mac}= | Get interface mac | ${from_node} | ${from_port}
| | ${dst_mac}= | Get interface mac | ${to_node} | ${to_port}
| | ${from_port_name}= | Get interface name | ${from_node} | ${from_port}
| | ${to_port_name}= | Get interface name | ${to_node} | ${to_port}
| | ${args}= | Traffic Script Gen Arg | ${from_port_name} | ${from_port_name} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Catenate | ${args} | --framesize ${frame_size}
| | Run Traffic Script On Node | send_tcp_for_classifier_test.py | ${from_node} | ${args}
