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
| Library | resources.libraries.python.SFC.PerformanceTest
| Library | Collections

*** Keywords ***
| Setup DUT nodes for '${type}' functional testing
| | [Documentation] | Configure and Start the SFC functional test
| | ... | on the DUT node.
| | ${testtype}= | Convert to String | ${type}
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${src_port} | ${src_node}= | First Interface
| | ${dst_port} | ${dst_node}= | Last Interface
| | Set Suite Variable | ${src_node}
| | Set Suite Variable | ${src_port}
| | Set Suite Variable | ${dst_node}
| | Set Suite Variable | ${dst_port}
| | Set Interface State | ${src_node} | ${src_port} | 'up'
| | Set Interface Ethernet MTU | ${src_node} | ${src_port} | 9000
| | ${adj_mac}= | Get interface mac | ${src_node} | ${src_port}
| | Config and Start SFC test | ${dst_node} | ${dst_port}
| | ... | ${adj_mac} | ${testtype}

| Node "${from_node}" interface "${from_port}" send "${size}" Bytes packet to node "${to_node}" interface "${to_port}" for "${type}" test
| | [Documentation] | At the first start the tcpdump on the TG node,
| | ... | then build the packet with the scapy and send the packet to the
| | ... | DUT node, DUT node will receive the packet on the ingress interface
| | ... | DUT will loopback packet to the TG after processed. TG will use
| | ... | the tcpdump to capture the packet and check the packet is correct.
| | ${filter_dst_ip}= | Set Variable | 192.168.50.71
| | Start the tcpdump on the Node | ${from_node} | ${from_port} | ${filter_dst_ip}
| | ${src_ip}= | Set Variable If | "${type}" == "Classifier" | 10.10.12.101 | 192.168.50.72
| | ${dst_ip}= | Set Variable If | "${type}" == "Classifier" | 10.10.12.100 | 192.168.50.76
| | ${src_mac}= | Get interface mac | ${from_node} | ${from_port}
| | ${dst_mac}= | Get interface mac | ${to_node} | ${to_port}
| | ${from_port_name}= | Get interface name | ${from_node} | ${from_port}
| | ${to_port_name}= | Get interface name | ${to_node} | ${to_port}
| | ${timeout}= | Set Variable | 10
| | ${frame_size}= | Convert To Integer | ${size}
| | ${args}= | Traffic Script Gen Arg | ${from_port_name} | ${from_port_name}
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

| Start NSH SFC "${type}" performance test in a 3-node circular topology
| | [Documentation] | Configure and Start the SFC performance test
| | ... | on the DUT node.
| | ${testtype}= | Convert to String | ${type}
| | ${dut1_to_tg_mac}= | Get interface mac | ${tg} | ${tg_if1}
| | ${dut1_to_dut2_mac}= | Get interface mac | ${dut2} | ${dut2_if1}
| | ${dut2_to_tg_mac}= | Get interface mac | ${tg} | ${tg_if2}
| | ${dut2_to_dut1_mac}= | Get interface mac | ${dut1} | ${dut1_if2}
| | Start performance test on DUT | ${dut1} | ${dut1_if1}
| | ... | ${dut1_if2} | ${dut1_to_tg_mac} | ${dut2_to_tg_mac} | ${testtype} | "DUT1"
| | Start performance test on DUT | ${dut2} | ${dut2_if1}
| | ... | ${dut2_if2} | ${dut1_to_tg_mac} | ${dut2_to_tg_mac} | ${testtype} | "DUT2"
