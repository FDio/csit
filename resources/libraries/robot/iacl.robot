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
| Documentation | Keywords for iACL tests
| Resource | resources/libraries/robot/default.robot
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath

*** Keywords ***
| Node path computed for 3-node topology
| | [Arguments] | ${tg_node} | ${dut1_node} | ${dut2_node} | ${tg_node}
| | [Documentation] | *Create interface variables for 3-node topology.*
| | ...
| | ... | *Arguments:*
| | ... | - ${tg_node} - Node attached to the path. Type: dictionary
| | ... | - ${dut1_node} - Node attached to the path. Type: dictionary
| | ... | - ${dut2_node} - Node attached to the path. Type: dictionary
| | ...
| | ... | _Set testcase variables for nodes and interfaces._
| | ... | - ${tg_node} - Variable for node in path. Type: dictionary
| | ... | - ${dut1_node} - Variable for node in path. Type: dictionary
| | ... | - ${dut2_node} - Variable for node in path. Type: dictionary
| | ... | - ${tg_if1} - First interface of TG node. Type: str
| | ... | - ${tg_if2} - Second interface of TG node. Type: str
| | ... | - ${dut1_if1} - First interface of first DUT node. Type: str
| | ... | - ${dut1_if2} - Second interface of first DUT node. Type: str
| | ... | - ${dut2_if1} - First interface of second DUT node. Type: str
| | ... | - ${dut2_if2} - Second interface of second DUT node. Type: str
| | ... | - ${tg_if1_mac} - MAC address of TG interface (1st).
| | ... | - ${tg_if2_mac} - MAC address of TG interface (2nd).
| | ... | - ${dut1_if1_mac} - MAC address of DUT1 interface (1st).
| | ... | - ${dut1_if2_mac} - MAC address of DUT1 interface (2nd).
| | ...
| | Append Nodes | ${tg1_node} | ${dut1_node} | ${dut2_node} | ${tg2_node}
| | Compute Path
| | ${tg_if1} | ${tg_node}= | Next Interface
| | ${dut1_if1} | ${dut1_node}= | Next Interface
| | ${dut1_if2} | ${dut1_node}= | Next Interface
| | ${dut2_if1} | ${dut2_node}= | Next Interface
| | ${dut2_if2} | ${dut2_node}= | Next Interface
| | ${tg_if2} | ${tg_node}= | Next Interface
| | ${tg_if1_mac}= | Get interface mac | ${tg_node} | ${tg_if1}
| | ${tg_if2_mac}= | Get interface mac | ${tg_node} | ${tg_if2}
| | ${dut1_if1_mac}= | Get interface mac | ${dut1_node} | ${dut1_if1}
| | ${dut1_if2_mac}= | Get interface mac | ${dut1_node} | ${dut1_if2}
| | Set Test Variable | ${tg_node}
| | Set Test Variable | ${tg_if1}
| | Set Test Variable | ${tg_if2}
| | Set Test Variable | ${dut1_node}
| | Set Test Variable | ${dut1_if1}
| | Set Test Variable | ${dut1_if2}
| | Set Test Variable | ${dut2_node}
| | Set Test Variable | ${dut2_if1}
| | Set Test Variable | ${dut2_if2}
| | Set Test Variable | ${tg_if1_mac}
| | Set Test Variable | ${tg_if2_mac}
| | Set Test Variable | ${dut1_if1_mac}
| | Set Test Variable | ${dut1_if2_mac}

| Interfaces in path are up
| | [Documentation] | *Set UP state on interfaces in path on nodes.*
| | ...
| | Set Interface State | ${tg_node} | ${tg_if1} | up
| | Set Interface State | ${tg_node} | ${tg_if2} | up
| | Set Interface State | ${dut1_node} | ${dut1_if1} | up
| | Set Interface State | ${dut1_node} | ${dut1_if2} | up
| | Set Interface State | ${dut2_node} | ${dut2_if1} | up
| | Set Interface State | ${dut2_node} | ${dut2_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Vpp Node Interfaces Ready Wait | ${dut2}

| IPv4 Addresses set on the node interfaces
| | [Arguments] | ${dut_node} | ${int1} | ${ip_addr1} | ${int2} | ${ip_addr2}
| | ...         | ${prefix_length}
| | [Documentation] | Setup IPv4 adresses on the node interfaces
| | ...
| | ... | *Arguments*
| | ... | - ${dut_node} - VPP node.
| | ... | - ${int1} - First node interface.
| | ... | - ${ip_addr1} - First IP address.
| | ... | - ${int2} - Second node interface.
| | ... | - ${ip_addr2} - Second IP address.
| | ... | - ${prefix_length} - IP prefix length.
| | ...
| | ... | *Example*
| | ... | \| IPv4 Addresses set on the node interfaces \
| | ... | \| ${dut1_node} \| ${dut1_if1} \| ${dut1_if1_ip} \
| | ... | \| ${dut1_if2} \| ${dut1_if2_ip} \| ${prefix_length} \|
| | ...
| | Set Interface Address | ${dut_node} | ${int1} | ${ip_addr1}
| | ...                   | ${prefix_length}
| | Set Interface Address | ${dut_node} | ${int2} | ${ip_addr2}
| | ...                   | ${prefix_length}

| IPv6 Addresses set on the node interfaces
| | [Arguments] | ${dut_node} | ${int1} | ${ip_addr1} | ${int2} | ${ip_addr2}
| | ...         | ${prefix_length}
| | [Documentation] | Setup IPv6 adresses on the node interfaces
| | ...
| | ... | *Arguments*
| | ... | - ${dut_node} - VPP node.
| | ... | - ${int1} - First node interface.
| | ... | - ${ip_addr1} - First IP address.
| | ... | - ${int2} - Second node interface.
| | ... | - ${ip_addr2} - Second IP address.
| | ... | - ${prefix_length} - IP prefix length.
| | ...
| | ... | *Example*
| | ... | \| IPv6 Addresses set on the node interfaces \
| | ... | \| ${dut1_node} \| ${dut1_if1} \| ${dut1_if1_ip} \
| | ... | \| ${dut1_if2} \| ${dut1_if2_ip} \| ${prefix_length} \|
| | ...
| | Vpp Set If Ipv6 Addr | ${dut_node} | ${int1} | ${ip_addr1} | ${prefix_length}
| | Vpp Set If Ipv6 Addr | ${dut_node} | ${int2} | ${ip_addr2} | ${prefix_length}

| Send ICMP packet should failed
| | [Arguments] | ${tg_node} | ${tg_rx} | ${tg_tx} | ${tg_tx_mac}
| | ...         | ${dut_int_mac} | ${src_ip} | ${dst_ip}
| | [Documentation] | Send packet from TG and should be dropped on DUT
| | ...
| | ... | *Arguments*
| | ... | - ${tg_node} - Traffic Generator (TG) node.
| | ... | - ${tg_rx} - TG node interface that receives traffic.
| | ... | - ${tg_tx} - TG node interface that sends traffic.
| | ... | - ${tg_tx_mac} - Source MAC address.
| | ... | - ${dut_int_mac} - Next node interface MAC address.
| | ... | - ${src_ip} - Source IP address.
| | ... | - ${dst_ip} - Destination IP address.
| | ...
| | ... | *Example*
| | ... | \| Send ICMP packet should failed \
| | ... | \| ${tg_node} \| ${tg_if2} \| ${tg_if1} \| ${tg_if1_mac} \
| | ... | \| ${dut1_if1_mac} \| ${test_src_ip} \| ${test_dst_ip} \|
| | ...
| | ${args}= | Traffic Script Gen Arg | ${tg_rx} | ${tg_tx} | ${tg_tx_mac}
| | ... | ${dut_int_mac} | ${src_ip} | ${dst_ip}
| | Run Keyword And Expect Error | Traffic script execution failed
| | ... | Run Traffic Script On Node | send_ip_icmp.py | ${tg_node} | ${args}


| Send ICMPv6 packet should failed
| | [Arguments] | ${tg_node} | ${tg_rx} | ${tg_tx} | ${tg_tx_mac}
| | ...         | ${dut_int_mac} | ${src_ip} | ${dst_ip}
| | [Documentation] | Send packet from TG and should be dropped on DUT
| | ...
| | ... | *Arguments*
| | ... | - ${tg_node} - Traffic Generator (TG) node.
| | ... | - ${tg_rx} - TG node interface that receives traffic.
| | ... | - ${tg_tx} - TG node interface that sends traffic.
| | ... | - ${tg_tx_mac} - Source MAC address.
| | ... | - ${dut_int_mac} - Next node interface MAC address.
| | ... | - ${src_ip} - Source IP address.
| | ... | - ${dst_ip} - Destination IP address.
| | ...
| | ... | *Example*
| | ... | \| Send ICMPv6 packet should failed \
| | ... | \| ${tg_node} \| ${tg_if2} \| ${tg_if1} \| ${tg_if1_mac} \
| | ... | \| ${dut1_if1_mac} \| ${test_src_ip} \| ${test_dst_ip} \|
| | ...
| | ${args}= | Traffic Script Gen Arg | ${tg_rx} | ${tg_tx} | ${tg_tx_mac}
| | ... | ${dut_int_mac} | ${src_ip} | ${dst_ip}
| | Run Keyword And Expect Error | Traffic script execution failed
| | ... | Run Traffic Script On Node | send_ip6_icmp.py | ${tg_node} | ${args}
