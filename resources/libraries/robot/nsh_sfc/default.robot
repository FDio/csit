# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.SFC.SFCTest
| Library | Collections

*** Keywords ***
| Setup DUT nodes for '${type}' functional testing
| | [Documentation] | Configure and Start the SFC functional test
| | ... | on the DUT node.
| | ${testtype}= | Convert to String | ${type}
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_to_dut_if1} | ${tg_node}= | First Interface
| | ${tg_to_dut_if2} | ${tg_node}= | Last Interface
| | ${dut_to_tg_if1} | ${dut_node}= | First Ingress Interface
| | ${dut_to_tg_if2} | ${dut_node}= | Last Egress Interface
| | ${tg_to_dut_if1_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut_if1}
| | ${tg_to_dut_if2_mac}= | Get interface mac | ${tg_node} | ${tg_to_dut_if2}
| | ${dut_to_tg_if1_mac}= | Get interface mac | ${dut_node} | ${dut_to_tg_if1}
| | ${dut_to_tg_if2_mac}= | Get interface mac | ${dut_node} | ${dut_to_tg_if2}
| | Set Suite Variable | ${tg_to_dut_if1}
| | Set Suite Variable | ${tg_to_dut_if2}
| | Set Suite Variable | ${dut_to_tg_if1}
| | Set Suite Variable | ${dut_to_tg_if2}
| | Set Suite Variable | ${tg_to_dut_if1_mac}
| | Set Suite Variable | ${tg_to_dut_if2_mac}
| | Set Suite Variable | ${dut_to_tg_if1_mac}
| | Set Suite Variable | ${dut_to_tg_if2_mac}
| | Set Suite Variable | ${tg_node}
| | Set Suite Variable | ${dut_node}
| | Set Interface State | ${tg_node} | ${tg_to_dut_if1} | 'up'
| | Set Interface State | ${tg_node} | ${tg_to_dut_if2} | 'up'
| | Set Interface Ethernet MTU | ${tg_node} | ${tg_to_dut_if1} | 9000
| | Set Interface Ethernet MTU | ${tg_node} | ${tg_to_dut_if2} | 9000
| | Config and Start SFC test | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${dut_to_tg_if2} | ${tg_to_dut_if1_mac} | ${tg_to_dut_if2_mac}
| | ... | ${testtype}


| Node "${from_node}" interface "${from_port}" send "${size}" Bytes packet to node "${to_node}" interface "${to_port}" for "${type}" test
| | [Documentation] | At the first start the tcpdump on the TG node,
| | ... | then build the packet with the scapy and send the packet to the
| | ... | DUT node, DUT node will receive the packet on the ingress interface
| | ... | DUT will loopback packet to the TG after processed. TG will use
| | ... | the tcpdump to capture the packet and check the packet is correct.
| | ${src_ip}= | Set Variable If | "${type}" == "Classifier" | 10.10.12.101 | 192.168.50.72
| | ${dst_ip}= | Set Variable If | "${type}" == "Classifier" | 10.10.12.100 | 192.168.50.76
| | ${src_mac}= | Get interface mac | ${from_node} | ${from_port}
| | ${dst_mac}= | Get interface mac | ${to_node} | ${to_port}
| | ${tx_port_name}= | Get interface name | ${from_node} | ${from_port}
| | ${rx_port_name}= | Get interface name | ${from_node} | ${tg_to_dut_if2}
| | ${timeout}= | Set Variable | 10
| | ${frame_size}= | Convert To Integer | ${size}
| | ${args}= | Traffic Script Gen Arg | ${rx_port_name} | ${tx_port_name}
| |          | ...      | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Catenate | ${args} | --framesize ${frame_size}
| |          | ...      | --timeout ${timeout} | --testtype "${type}"
| | Run Keyword If | "${type}" == "Classifier" | Run Traffic Script On Node
| | | | | ... | send_tcp_for_classifier_test.py | ${from_node} | ${args}
| | ... | ELSE IF | "${type}" == "Proxy Inbound" | Run Traffic Script On Node
| | | | | ... | send_vxlangpe_nsh_for_proxy_test.py | ${from_node} | ${args}
| | ... | ELSE IF | "${type}" == "Proxy Outbound" | Run Traffic Script On Node
| | | | | ... | send_vxlan_for_proxy_test.py | ${from_node} | ${args}
| | ... | ELSE | Run Traffic Script On Node | send_vxlangpe_nsh_for_sff_test.py
| | | | | ... | ${from_node} | ${args}
