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
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/cop.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Variables  | resources/libraries/python/IPv4NodeAddress.py | ${nodes}
| Force Tags | COP
| Suite Setup | Run Keywords | Setup all DUTs before test
| ...         | AND          | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Show packet trace on all DUTs | ${nodes}

*** Variables ***
${dut1_if1_ip}              192.168.1.1
${dut1_if2_ip}              192.168.2.1
${dut1_if1_ip_GW}           192.168.1.2
${dut1_if2_ip_GW}           192.168.2.2


${dst_ip_prefix}            32.0.0.0
${dst_ip_prefix_length}     8
${test_dst_ip}              32.0.0.1
${test_src_ip}              16.0.0.1


${cop_dut_ip}               16.0.0.0
${cop_prefix}               16

${ip_prefix}                24
${nodes_ipv4_addresses}     ${nodes_ipv4_addr}
*** Test Cases ***
| COP IPV4 Whitelist |
| | [Setup] | Basic Setup For Traffic
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${hops}= | Set Variable | ${1}
| | ${tg_if2} | ${tg}= | Last Interface
| | ${src_mac}= | Get interface mac | ${tg} | ${tg_if1}
| | ${dst_mac}= | Get interface mac | ${dut1} | ${dut1_if1}
| | Add fib table | ${dut1} | ${cop_dut_ip} | ${cop_prefix} | 1 | local
| | cop whitelist enable or disable | ${dut1} | ${dut1_if1} | ip4 | 1
| | cop interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | Node interface can route to node interface hops away using IPv4 | ${tg} | ${tg_if1} | ${src_mac} | ${test_src_ip} | ${dst_mac} | ${test_dst_ip} | ${tg_if2}


#| COP IPV4 Blacklist |
#| | [Setup] | Basic Setup For Traffic
#| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
#| | Compute Path
#| | ${tg_if1} | ${tg}= | Next Interface
#| | ${dut1_if1} | ${dut1}= | Next Interface
#| | ${dut1_if2} | ${dut1}= | Next Interface
#| | ${hops}= | Set Variable | ${1}
#| | ${tg_if2} | ${tg}= | Last Interface
#| | Add fib table | ${dut1} | ${cop_dut_ip} | ${cop_prefix} | 1 | drop
#| | cop whitelist enable or disable | ${dut1} | ${dut1_if1} | ip4 | 1
#| | cop interface enable or disable | ${dut1} | ${dut1_if1} | enable
#| | ${status}= | run keyword and return status | Node interface can route to node interface hops away using IPv4 | ${tg} | ${tg_if1} | ${tg} | ${tg_if2} | ${hops}
#| | should be equal | '${status}' | 'False'
#

*** Keywords ***
| Node interface can route to node interface hops away using IPv4
| | [Arguments] | ${tg} | ${tx_src_port} | ${tx_src_mac} | ${tx_src_ip} | ${tx_dst_mac} | ${tx_dst_ip} | ${rx_port}
| | ${src_ip}= | Set Variable | ${test_src_ip}
| | ${dst_ip}= | Set Variable | ${test_dst_ip}
| | ${args}= | Catenate | --src_mac | ${tx_src_mac} | --dst_mac | ${tx_dst_mac} | --src_ip | ${tx_src_ip} | --dst_ip | ${tx_dst_ip} | --tx_if | ${tx_src_port} | --rx_if | ${rx_port}
| | Run Traffic Script On Node | send_ip_icmp.py | ${tg} | ${args}

| Basic Setup For Traffic
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | ${mac_tg_if1}= | Get interface mac | ${tg} | ${tg_if1}
| | ${mac_tg_if2}= | Get interface mac | ${tg} | ${tg_if2}

| | Set Interface State | ${tg} | ${tg_if1} | up
| | Set Interface State | ${tg} | ${tg_if2} | up
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up

| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}

| | Set Interface Address | ${dut1} | ${dut1_if1} | ${dut1_if1_ip} | ${ip_prefix}
| | Set Interface Address | ${dut1} | ${dut1_if2} | ${dut1_if2_ip} | ${ip_prefix}

| | Setup Arp On Dut | ${dut1} | ${dut1_if1} | ${dut1_if1_ip_GW} | ${mac_tg_if1}
| | Setup Arp On Dut | ${dut1} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${mac_tg_if2}

| | Vpp Route Add | ${dut1} | ${dst_ip_prefix} | ${dst_ip_prefix_length} | ${dut1_if2_ip_GW} | ${dut1_if2}