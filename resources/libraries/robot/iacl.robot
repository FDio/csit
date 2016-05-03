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
| Documentation | Keywords for VLAN tests
| Resource | resources/libraries/robot/default.robot
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.IPv4Util.IPv4Util


*** Keywords ***
| Node path computed for 3-node topology
| | [Arguments] | ${TG} | ${DUT1} | ${DUT2} | ${TG}
| | [Documentation] | *Create interface variables for 3-node topology.*
| | ...
| | ... | *Arguments:*
| | ... | - ${TG} - Node attached to the path. Type: dictionary
| | ... | - ${DUT1} - Node attached to the path. Type: dictionary
| | ... | - ${DUT2} - Node attached to the path. Type: dictionary
| | ...
| | ... | _Set testcase variables for nodes and interfaces._
| | ... | - ${tg} - Variable for node in path. Type: dictionary
| | ... | - ${dut1} - Variable for node in path. Type: dictionary
| | ... | - ${dut2} - Variable for node in path. Type: dictionary
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
| | Append Nodes | ${TG} | ${DUT1} | ${DUT2} | ${TG}
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
| | Set Test Variable | ${tg}
| | Set Test Variable | ${tg_if1}
| | Set Test Variable | ${tg_if2}
| | Set Test Variable | ${dut1}
| | Set Test Variable | ${dut1_if1}
| | Set Test Variable | ${dut1_if2}
| | Set Test Variable | ${dut2}
| | Set Test Variable | ${dut2_if1}
| | Set Test Variable | ${dut2_if2}
| | Set Test Variable | ${tg_if1_mac}
| | Set Test Variable | ${tg_if2_mac}
| | Set Test Variable | ${dut1_if1_mac}
| | Set Test Variable | ${dut1_if2_mac}

| Interfaces in path are up
| | [Documentation] | *Set UP state on interfaces in path on nodes.*
| | ...
| | Set Interface State | ${tg} | ${tg_if1} | up
| | Set Interface State | ${tg} | ${tg_if2} | up
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Vpp Node Interfaces Ready Wait | ${dut2}

| IPv4 Addresses set on the node interfaces
| | [Arguments] | ${DUT} | ${INT1} | ${IP_ADDR1} | ${INT2} | ${IP_ADDR2}
| | ...         | ${PREFIX_LENGTH}
| | [Documentation] | Setup IPv4 adresses on the node interfaces
| | Set Interface Address | ${DUT} | ${INT1} | ${IP_ADDR1} | ${PREFIX_LENGTH}
| | Set Interface Address | ${DUT} | ${INT2} | ${IP_ADDR2} | ${PREFIX_LENGTH}

| IPv6 Addresses set on the node interfaces
| | [Arguments] | ${DUT} | ${INT1} | ${IP_ADDR1} | ${INT2} | ${IP_ADDR2}
| | ...         | ${PREFIX_LENGTH}
| | [Documentation] | Setup IPv6 adresses on the node interfaces
| | Vpp Set If Ipv6 Addr | ${DUT} | ${INT1} | ${IP_ADDR1} | ${PREFIX_LENGTH}
| | Vpp Set If Ipv6 Addr | ${DUT} | ${INT2} | ${IP_ADDR2} | ${PREFIX_LENGTH}

| Send ICMP packet should failed
| | [Arguments] | ${TG} | ${TG_RX} | ${TG_TX} | ${TG_TX_MAC} | ${DUT_INT_MAC}
| | ...         | ${SRC_IP} | ${DST_IP}
| | [Documentation] | Send packet from TG and should be dropped on DUT
| | ${args}= | Traffic Script Gen Arg | ${TG_RX} | ${TG_TX} | ${TG_TX_MAC}
| | ... | ${DUT_INT_MAC} | ${SRC_IP} | ${DST_IP}
| | ${status}= | Run Keyword And Return Status | Run Traffic Script On Node |
| | ... | send_ip_icmp.py | ${TG} | ${args}
| | Should Not Be True | ${status}

| Send ICMPv6 packet should failed
| | [Arguments] | ${TG} | ${TG_RX} | ${TG_TX} | ${TG_TX_MAC} | ${DUT_INT_MAC}
| | ...         | ${SRC_IP} | ${DST_IP}
| | [Documentation] | Send packet from TG and should be dropped on DUT
| | ${args}= | Traffic Script Gen Arg | ${TG_RX} | ${TG_TX} | ${TG_TX_MAC}
| | ... | ${DUT_INT_MAC} | ${SRC_IP} | ${DST_IP}
| | ${status}= | Run Keyword And Return Status | Run Traffic Script On Node |
| | ... | send_ip6_icmp.py | ${TG} | ${args}
| | Should Not Be True | ${status}