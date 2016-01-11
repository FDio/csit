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
| Library | resources/libraries/python/IPv6Util.py
| Library | resources/libraries/python/IPv6Setup.py
| Library | resources/libraries/python/TrafficScriptExecutor.py
| Library | resources.libraries.python.topology.Topology
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/counters.robot
| Documentation | IPv6 keywords

*** Keywords ***
| Ipv6 icmp echo
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${src_node} | ${dst_node} | ${nodes_addr}
| | ${link}= | Get first active connecting link between node "${src_node}" and "${dst_node}"
| | ${src_port}= | Get Interface By Link Name | ${src_node} | ${link}
| | ${dst_port}= | Get Interface By Link Name | ${dst_node} | ${link}
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port} | ${src_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${src_node} | ${args}
| | Vpp dump stats | ${dst_node}
| | ${ipv6_counter}= | Vpp get interface ipv6 counter | ${dst_node} | ${dst_port}
| | Should Be Equal | ${ipv6_counter} | ${2} | #ICMPv6 neighbor advertisment + ICMPv6 echo request

| Ipv6 icmp echo sweep
| | [Documentation] | Type of the src_node must be TG and dst_node must be DUT
| | [Arguments] | ${src_node} | ${dst_node} | ${nodes_addr}
| | ${link}= | Get first active connecting link between node "${src_node}" and "${dst_node}"
| | ${src_port}= | Get Interface By Link Name | ${src_node} | ${link}
| | ${dst_port}= | Get Interface By Link Name | ${dst_node} | ${link}
| | ${src_ip}= | Get Node Port Ipv6 Address | ${src_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dst_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${src_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${dst_node} | ${dst_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port} | ${src_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| # TODO: end_size is currently minimum MTU size for IPv6 minus IPv6 and ICMPv6
| # echo header size, MTU info is not in VAT sw_interface_dump output
| | ${args}= | Set Variable | ${args} --start_size 0 --end_size 1232 --step 1
| | Run Traffic Script On Node | ipv6_sweep_ping.py | ${src_node} | ${args} | ${20}

| Ipv6 tg to dut1 egress
| | [Documentation] | Send traffic from TG to first DUT egress interface
| | [Arguments] | ${tg_node} | ${first_dut} | ${nodes_addr}
| | ${link}= | Get first active connecting link between node "${tg_node}" and "${first_dut}"
| | ${src_port}= | Get Interface By Link Name | ${tg_node} | ${link}
| | ${first_hop_port}= | Get Interface By Link Name | ${first_dut} | ${link}
| | ${dst_port}= | Get first egress interface on "${first_dut}" for link with "${tg_node}"
| | ${src_ip}= | Get Node Port Ipv6 Address | ${tg_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${first_dut} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${first_dut} | ${first_hop_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port} | ${src_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}


| Ipv6 tg to dut2 via dut1
| | [Documentation] | Send traffic from TG to second DUT through first DUT
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | ${link1}= | Get first active connecting link between node "${tg_node}" and "${first_dut}"
| | ${src_port}= | Get Interface By Link Name | ${tg_node} | ${link1}
| | ${first_hop_port}= | Get Interface By Link Name | ${first_dut} | ${link1}
| | ${link2}= | Get first active connecting link between node "${first_dut}" and "${second_dut}"
| | ${dst_port}= | Get Interface By Link Name | ${second_dut} | ${link2}
| | ${src_ip}= | Get Node Port Ipv6 Address | ${tg_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${second_dut} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${first_dut} | ${first_hop_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port} | ${src_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}

| Ipv6 tg to dut2 egress via dut1
| | [Documentation] | Send traffic from TG to second DUT egress interface through first DUT
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | ${link}= | Get first active connecting link between node "${tg_node}" and "${first_dut}"
| | ${src_port}= | Get Interface By Link Name | ${tg_node} | ${link}
| | ${first_hop_port}= | Get Interface By Link Name | ${first_dut} | ${link}
| | ${dst_port}= | Get first egress interface on "${first_dut}" for link with "${second_dut}"
| | ${src_ip}= | Get Node Port Ipv6 Address | ${tg_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${second_dut} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${first_dut} | ${first_hop_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port} | ${src_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | icmpv6_echo.py | ${tg_node} | ${args}

| Ipv6 tg to tg routed
| | [Documentation] | Send traffic from one TG port to another through DUT nodes
| | ...             | and send reply back, also verify hop limit processing
| | [Arguments] | ${tg_node} | ${first_dut} | ${second_dut} | ${nodes_addr}
| | ${link1}= | Get first active connecting link between node "${tg_node}" and "${first_dut}"
| | ${src_port}= | Get Interface By Link Name | ${tg_node} | ${link1}
| | ${src_nh_port}= | Get Interface By Link Name | ${first_dut} | ${link1}
| | ${link2}= | Get first active connecting link between node "${tg_node}" and "${second_dut}"
| | ${dst_port}= | Get Interface By Link Name | ${tg_node} | ${link2}
| | ${dst_nh_port}= | Get Interface By Link Name | ${second_dut} | ${link2}
| | ${src_ip}= | Get Node Port Ipv6 Address | ${tg_node} | ${src_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${tg_node} | ${dst_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_port}
| | ${dst_mac}= | Get Interface Mac | ${tg_node} | ${dst_port}
| | ${src_nh_mac}= | Get Interface Mac | ${first_dut} | ${src_nh_port}
| | ${dst_nh_mac}= | Get Interface Mac | ${second_dut} | ${dst_nh_port}
| | ${args}= | Traffic Script Gen Arg | ${src_port} | ${dst_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Set Variable | ${args} --src_nh_mac ${src_nh_mac} --dst_nh_mac ${dst_nh_mac} --h_num 2
| | Run Traffic Script On Node | icmpv6_echo_req_resp.py | ${tg_node} | ${args}

| Ipv6 neighbor solicitation
| | [Documentation] | Send IPv6 neighbor solicitation from TG to DUT
| | [Arguments] | ${tg_node} | ${dut_node} | ${nodes_addr}
| | ${link}= | Get first active connecting link between node "${tg_node}" and "${dut_node}"
| | ${tg_port}= | Get Interface By Link Name | ${tg_node} | ${link}
| | ${dut_port}= | Get Interface By Link Name | ${dut_node} | ${link}
| | ${src_ip}= | Get Node Port Ipv6 Address | ${tg_node} | ${tg_port} | ${nodes_addr}
| | ${dst_ip}= | Get Node Port Ipv6 Address | ${dut_node} | ${dut_port} | ${nodes_addr}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${tg_port}
| | ${dst_mac}= | Get Interface Mac | ${dut_node} | ${dut_port}
| | ${args}= | Traffic Script Gen Arg | ${tg_port} | ${tg_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | ipv6_ns.py | ${tg_node} | ${args}

| Setup ipv6 to all dut in topology
| | [Documentation] | Setup IPv6 address on all DUTs
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Setup all DUTs before test
| | Nodes Setup Ipv6 Addresses | ${nodes} | ${nodes_addr}

| Clear ipv6 on all dut in topology
| | [Documentation] | Remove IPv6 address on all DUTs
| | [Arguments] | ${nodes} | ${nodes_addr}
| | Nodes Clear Ipv6 Addresses | ${nodes} | ${nodes_addr}

| Vpp nodes ra supress link layer
| | [Documentation] | Supress ICMPv6 router advertisement message for link scope address
| | [Arguments] | ${nodes}
| | Vpp All Ra Supress Link Layer | ${nodes}

| Vpp nodes setup ipv6 routing
| | [Documentation] | Setup routing on all VPP nodes required for IPv6 tests
| | [Arguments] | ${nodes} | ${nodes_addr}
| | ${link_tg_dut1}= | Get first active connecting link between node "${nodes['TG']}" and "${nodes['DUT1']}"
| | ${link_tg_dut2}= | Get first active connecting link between node "${nodes['TG']}" and "${nodes['DUT2']}"
| | ${link_dut1_dut2}= | Get first active connecting link between node "${nodes['DUT1']}" and "${nodes['DUT2']}"
| | ${dut1_if}= | Get Interface By Link Name | ${nodes['DUT1']} | ${link_dut1_dut2}
| | ${dut2_if}= | Get Interface By Link Name | ${nodes['DUT2']} | ${link_dut1_dut2}
| | Vpp Ipv6 Route Add | ${nodes['DUT1']} | ${link_tg_dut2} | ${dut1_if} | ${nodes_addr}
| | Vpp Ipv6 Route Add | ${nodes['DUT2']} | ${link_tg_dut1} | ${dut2_if} | ${nodes_addr}
