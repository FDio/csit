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
| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO | COP
| Suite Setup | Run Keywords | Setup all DUTs before test
| ...         | AND          | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Show packet trace on all DUTs | ${nodes}
| Documentation | *COP Blacklist and Whitelist Tests*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes where DUT2 has xconnect.
| ... | Test packets are sent only in one direction with COP set either as
| ... | whitelist or blacklist. Subsequently, packet's IP src/dst and
| ... | mac addresses are checked.

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
| | [Documentation] | Cop Whitelist test with basic setup
| | Given Setup Nodes And Variables
| | And Add fib table | ${dut1} | ${cop_dut_ip} | ${cop_prefix} | 1 | local
| | And Cop Add whitelist Entry | ${dut1} | ${dut1_if1} | ip4 | 1
| | And cop interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | Then Send packet from Port to Port |
| | ... | ${tg} | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}


| COP IPV4 Blacklist |
| | [Documentation] | Cop blacklist test with basic setup
| | Given Setup Nodes And Variables
| | And Add fib table | ${dut1} | ${cop_dut_ip} | ${cop_prefix} | 1 | drop
| | And Cop Add whitelist Entry | ${dut1} | ${dut1_if1} | ip4 | 1
| | And cop interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | ${status}= | run keyword and return status | Send packet from Port to Port |
| | ... | ${tg} | ${test_src_ip} | ${test_dst_ip} | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac} | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
| | Then should be equal | '${status}' | 'False'


*** Keywords ***
| Send packet from Port to Port
| | [Documentation] | Sends packet from ip (with specified mac) to ip
| | ... | (with dest mac). There has to be 4 mac addresses when using 2 node +
| | ... | xconnect ( one for each eth.
| | [Arguments] | ${tg} | ${src_ip} | ${dst_ip} | ${tx_src_port} | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac} | ${rx_dst_mac}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac |
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip} | --tx_if | ${tx_src_port} | --rx_if | ${rx_port}
| | Run Traffic Script On Node | send_icmp_check_headers.py | ${tg} | ${args}

| Setup Nodes And Variables
| | [Documentation] | Setup of test variables and setup for ONE way packet flow
| | ... | only.
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | ${tg_if1_mac}= | Get interface mac | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get interface mac | ${tg} | ${tg_if2}
| | ${dut1_if1_mac}= | Get interface mac | ${dut1} | ${dut1_if1}
| | ${dut1_if2_mac}= | Get interface mac | ${dut1} | ${dut1_if2}

| | Set Test Variable | ${tg_if1}
| | Set Test Variable | ${tg_if2}
| | Set Test Variable | ${dut1_if1}
| | Set Test Variable | ${dut1_if2}
| | Set Test Variable | ${dut2_if1}
| | Set Test Variable | ${dut2_if2}
| | Set Test Variable | ${dut1}
| | Set Test Variable | ${dut2}
| | Set Test Variable | ${tg}
| | Set Test Variable | ${tg_if1_mac}
| | Set Test Variable | ${tg_if2_mac}
| | Set Test Variable | ${dut1_if1_mac}
| | Set Test Variable | ${dut1_if2_mac}

| | Set Interface State | ${tg} | ${tg_if1} | up
| | Set Interface State | ${tg} | ${tg_if2} | up
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up

| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}

| | Set Interface Address | ${dut1} | ${dut1_if1} | ${dut1_if1_ip} | ${ip_prefix}
| | Set Interface Address | ${dut1} | ${dut1_if2} | ${dut1_if2_ip} | ${ip_prefix}

| | Setup Arp On Dut | ${dut1} | ${dut1_if1} | ${dut1_if1_ip_GW} | ${tg_if1_mac}
| | Setup Arp On Dut | ${dut1} | ${dut1_if2} | ${dut1_if2_ip_GW} | ${tg_if2_mac}

| | Vpp Route Add | ${dut1} | ${dst_ip_prefix} | ${dst_ip_prefix_length} | ${dut1_if2_ip_GW} | ${dut1_if2}