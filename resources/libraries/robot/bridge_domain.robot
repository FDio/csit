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
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.NodePath

*** Keywords ***
| Vpp l2bd forwarding
| | [Documentation] | Forward packet from first to second TG interface via VPP
| | ...             | L2 bridge domain
| | [Arguments] | ${tg_node} | ${vpp_node}
| | Append Nodes | ${tg_node} | ${vpp_node} | ${tg_node}
| | Compute Path | ${FALSE}
| | ${src_if} | ${tmp}= | First Interface
| | ${dst_if} | ${tmp}= | Last Interface
| | ${bd_if1} | ${tmp}= | First Ingress Interface
| | ${bd_if2} | ${tmp}= | Last Egress Interface
| | Vpp Add L2 Bridge Domain | ${vpp_node} | ${1} | ${bd_if1} | ${bd_if2}
| | Sleep | 5 | # Wait some time after interface is set up
| | Send and receive traffic | ${tg_node} | ${src_if} | ${dst_if}

| Vpp l2bd circular
| | [Documentation] | Forward packet from first to second TG interface via first
| | ...             | and second VPP L2 bridge domains
| | [Arguments] | ${tg} | ${dut1} | ${dut2} | ${learn}=${TRUE}
| | Append Nodes | ${tg} | ${dut1} | ${dut2} | ${tg}
| | Compute Path
| | ${src_if} | ${tmp}= | Next Interface
| | ${dut1_if1} | ${tmp}= | Next Interface
| | ${dut1_if2} | ${tmp}= | Next Interface
| | ${dut2_if1} | ${tmp}= | Next Interface
| | ${dut2_if2} | ${tmp}= | Next Interface
| | ${dst_if} | ${tmp}= | Next Interface
| | ${mac}= | Get Interface Mac | ${tg} | ${src_if}
| | Vpp Add L2 Bridge Domain | ${dut1} | ${1} | ${dut1_if1} | ${dut1_if2} | ${learn}
| | Vpp Add L2 Bridge Domain | ${dut2} | ${1} | ${dut2_if1} | ${dut2_if2} | ${learn}
| | Run Keyword If | ${learn} == ${FALSE}
| | ... | Vpp Add L2fib Entry | ${dut1} | ${mac} | ${dut1_if2} | ${1}
| | Run Keyword If | ${learn} == ${FALSE}
| | ... | Vpp Add L2fib Entry | ${dut2} | ${mac} | ${dut2_if2} | ${1}
| | Sleep | 5 | # Wait some time after interface is set up
| | Send and receive traffic | ${tg} | ${src_if} | ${dst_if}

| Send and receive traffic
| | [Documentation] | Send traffic from source interface to destination interface
| | [Arguments] | ${tg_node} | ${src_int} | ${dst_int}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_int}
| | ${dst_mac}= | Get Interface Mac | ${tg_node} | ${dst_int}
| | ${src_ip}= | Set Variable | 192.168.100.1
| | ${dst_ip}= | Set Variable | 192.168.100.2
| | ${args}= | Traffic Script Gen Arg | ${dst_int} | ${src_int} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | send_ip_icmp.py | ${tg_node} | ${args}
