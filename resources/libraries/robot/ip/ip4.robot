# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.IPv4Util.IPv4Util
| Library | resources.libraries.python.IPv4Setup.IPv4Setup
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.TrafficScriptExecutor
| ...
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| ...
| Variables | resources/libraries/python/IPv4NodeAddress.py | ${nodes}
| ...
| Documentation | IPv4 keywords

*** Keywords ***
| Show IP FIB On All DUTs
| | [Documentation] | Show IP FIB on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | VPP Show IP Table | ${nodes['${dut}']}

| Get interface Ipv4 addresses
| | [Documentation] | Get IPv4 address for the given interface of the node.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node data. Type: dictionary
| | ... | - interface - Name of the interface on the VPP node. Type: string
| | ...
| | [Arguments] | ${node} | ${interface}
| | ...
| | [Return] | ${ip_data}
| | ...
| | ${ip_data}= | VPP get interface ip addresses
| | ... | ${node} | ${interface} | ipv4

| Configure IP addresses on interfaces
| | [Documentation] | Iterates through @{args} list and set IP interface address
| | ... | for every (${dut_node}, ${interface}, ${address},
| | ... | ${prefix}) tuple.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where IP address should be set to.
| | ... | Type: dictionary
| | ... | - interface - Interface name. Type: string
| | ... | - address - IP address. Type: string
| | ... | - prefix - Prefix length. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IP addresses on interfaces \
| | ... | \| ${dut1_node} \| ${dut1_to_dut2} \| 192.168.1.1 \| 24 \|
| | ... | \| ... \| ${dut1_node} \| ${dut1_to_tg} \| 192.168.2.1 \| 24 \|
| | ...
| | [Arguments] | @{args}
| | :FOR | ${dut_node} | ${interface} | ${address} | ${prefix} | IN | @{args}
| | | VPP Interface Set IP Address | ${dut_node} | ${interface} | ${address}
| | | ... | ${prefix}

| Send ICMP echo request and verify answer
| | [Documentation] | Run traffic script that waits for ICMP reply and ignores
| | ... | all other packets.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node where run traffic script. Type: dictionary
| | ... | - tg_interface - TG interface where send ICMP echo request.
| | ... | Type: string
| | ... | - dst_mac - Destination MAC address. Type: string
| | ... | - src_mac - Source MAC address. Type: string
| | ... | - dst_ip - Destination IP address. Type: string
| | ... | - src_ip - Source IP address. Type: string
| | ... | - timeout - Wait timeout in seconds (Default: 10). Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send ICMP echo request and verify answer \
| | ... | \| ${nodes['TG']} \| eth2 \
| | ... | \| 08:00:27:46:2b:4c \| 08:00:27:66:b8:57 \
| | ... | \| 192.168.23.10 \| 192.168.23.1 \| 10 \|
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface}
| | ... | ${dst_mac} | ${src_mac} | ${dst_ip} | ${src_ip} | ${timeout}=${10}
| | ...
| | ${tg_interface_name}= | Get interface name | ${tg_node} | ${tg_interface}
| | ${args}= | Catenate | --rx_if ${tg_interface_name}
| | ... | --tx_if ${tg_interface_name} | --dst_mac ${dst_mac}
| | ... | --src_mac ${src_mac} | --dst_ip ${dst_ip} | --src_ip ${src_ip}
| | ... | --timeout ${timeout}
| | Run Traffic Script On Node | send_icmp_wait_for_reply.py
| | ... | ${tg_node} | ${args}

| Configure IPv4 forwarding in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address. Configure route
| | ... | entries for remote hosts IPv4 addresses if required.
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_ip4 - IP address of TG interface1. Type: string
| | ... | - tg_if2_ip4 - IP address of TG interface2. Type: string
| | ... | - dut1_if1_ip4 - IP address of DUT1 interface1. Type: string
| | ... | - dut1_if2_ip4 - IP address of DUT1 interface1. Type: string
| | ... | - dut2_if1_ip4 - IP address of DUT2 interface1 (Optional).
| | ... | Type: string
| | ... | - dut2_if2_ip4 - IP address of DUT2 interface2 (Optional).
| | ... | Type: string
| | ... | - remote_host1_ip4 - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip4 - IP address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_ip4_prefix - IP address prefix for host IP addresses
| | ... | (Optional). Type: string or integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IPv4 forwarding in circular topology \
| | ... | \| 10.10.10.2 \| 20.20.20.2 \| 10.10.10.1 \| 20.20.20.1 \|
| | ... | \| Configure IPv4 forwarding in circular topology \
| | ... | \| 10.10.10.2 \| 20.20.20.2 \| 10.10.10.1 \| 20.20.20.1 \
| | ... | \| remote_host1_ip4=192.168.0.1 \| remote_host2_ip4=192.168.0.2 \
| | ... | \| remote_host_ip4_prefix=32 \|
| | ... | \| Configure IPv4 forwarding in circular topology \
| | ... | \| 10.10.10.2 \| 20.20.20.2 \| 10.10.10.1 \| 1.1.1.1 \| 1.1.1.2 \
| | ... | \| 20.20.20.1 \|
| | ... | \| Configure IPv4 forwarding in circular topology \
| | ... | \| 10.10.10.2 \| 20.20.20.2 \| 10.10.10.1 \| 1.1.1.1 \| 1.1.1.2 \
| | ... | \| 20.20.20.1 \| remote_host1_ip4=192.168.0.1 \
| | ... | \| remote_host2_ip4=192.168.0.2 \| remote_host_ip4_prefix=32 \|
| | ...
| | [Arguments] | ${tg_if1_ip4} | ${tg_if2_ip4} | ${dut1_if1_ip4}
| | ... | ${dut1_if2_ip4} | ${dut2_if1_ip4}=${NONE} | ${dut2_if2_ip4}=${NONE}
| | ... | ${remote_host1_ip4}=${NONE} | ${remote_host2_ip4}=${NONE}
| | ... | ${remote_host_ip4_prefix}=${NONE}
| | ...
| | Configure interfaces in path up
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2_node}
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IPv4 forwarding in 3-node circular topology
| | ... | ${tg_if1_ip4} | ${tg_if2_ip4} | ${dut1_if1_ip4} | ${dut1_if2_ip4}
| | ... | ${dut2_if1_ip4} | ${dut2_if2_ip4} | ${remote_host1_ip4}
| | ... | ${remote_host2_ip4} | ${remote_host_ip4_prefix}
| | ... | ELSE
| | ... | Configure IPv4 forwarding in 2-node circular topology
| | ... | ${tg_if1_ip4} | ${tg_if2_ip4} | ${dut1_if1_ip4} | ${dut1_if2_ip4}
| | ... | remote_host1_ip4=${remote_host1_ip4}
| | ... | remote_host2_ip4=${remote_host2_ip4}
| | ... | remote_host_ip4_prefix=${remote_host_ip4_prefix}

| Configure IPv4 forwarding in 2-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces on DUT node in 2-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. Configure route entries for remote hosts IPv4 addresses
| | ... | if required.
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_ip4 - IP address of TG interface1. Type: string
| | ... | - tg_if2_ip4 - IP address of TG interface2. Type: string
| | ... | - dut1_if1_ip4 - IP address of DUT1 interface1. Type: string
| | ... | - dut1_if2_ip4 - IP address of DUT1 interface1. Type: string
| | ... | - remote_host1_ip4 - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip4 - IP address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_ip4_prefix - IP address prefix for host IP addresses
| | ... | (Optional). Type: string or integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IPv4 forwarding in circular topology \
| | ... | \| 10.10.10.2 \| 20.20.20.2 \| 10.10.10.1 \| 20.20.20.1 \|
| | ... | \| Configure IPv4 forwarding in circular topology \
| | ... | \| 10.10.10.2 \| 20.20.20.2 \| 10.10.10.1 \| 20.20.20.1 \
| | ... | \| 192.168.0.1 \| 192.168.0.2 \| 32 \|
| | ...
| | [Arguments] | ${tg_if1_ip4} | ${tg_if2_ip4} | ${dut1_if1_ip4}
| | ... | ${dut1_if2_ip4} | ${remote_host1_ip4}=${NONE}
| | ... | ${remote_host2_ip4}=${NONE} | ${remote_host_ip4_prefix}=${NONE}
| | ...
| | ${dut_tg_ip4_prefix}= | Set Variable | 24
| | ...
| | VPP Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1} | ${tg_if1_ip4}
| | ... | ${tg_to_dut_if1_mac}
| | VPP Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${tg_if2_ip4}
| | ... | ${tg_to_dut_if2_mac}
| | ...
| | Configure IP addresses on interfaces | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${dut1_if1_ip4} | ${dut_tg_ip4_prefix}
| | Configure IP addresses on interfaces | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${dut1_if2_ip4} | ${dut_tg_ip4_prefix}
| | ...
| | Run Keyword Unless | '${remote_host1_ip4}' == '${NONE}'
| | ... | Vpp Route Add | ${dut_node} | ${remote_host1_ip4}
| | ... | ${remote_host_ip4_prefix} | gateway=${tg_if1_ip4}
| | ... | interface=${dut_to_tg_if1}
| | Run Keyword Unless | '${remote_host2_ip4}' == '${NONE}'
| | ... | Vpp Route Add | ${dut_node} | ${remote_host2_ip4}
| | ... | ${remote_host_ip4_prefix} | gateway=${tg_if2_ip4}
| | ... | interface=${dut_to_tg_if2}

| Configure IPv4 forwarding in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG links.
| | ... | Configure IPv4 adresses with /30 prefix on DUT1-DUT2 link and set
| | ... | routing on both DUT nodes with prefix /24 and next hop of neighbour
| | ... | DUT interface IPv4 address. Configure route entries for remote hosts
| | ... | IPv4 addresses if required.
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_ip4 - IP address of TG interface1. Type: string
| | ... | - tg_if2_ip4 - IP address of TG interface2. Type: string
| | ... | - dut1_if1_ip4 - IP address of DUT1 interface1. Type: string
| | ... | - dut1_if2_ip4 - IP address of DUT1 interface1. Type: string
| | ... | - dut2_if1_ip4 - IP address of DUT2 interface1. Type: string
| | ... | - dut2_if2_ip4 - IP address of DUT2 interface2. Type: string
| | ... | - remote_host1_ip4 - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip4 - IP address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_ip4_prefix - IP address prefix for host IP addresses
| | ... | (Optional). Type: string or integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IPv4 forwarding in circular topology \
| | ... | \| 10.10.10.2 \| 20.20.20.2 \| 10.10.10.1 \| 1.1.1.1 \| 1.1.1.2 \
| | ... | \| 20.20.20.1 \|
| | ... | \| Configure IPv4 forwarding in circular topology \
| | ... | \| 10.10.10.2 \| 20.20.20.2 \| 10.10.10.1 \| 1.1.1.1 \| 1.1.1.2 \
| | ... | \| 20.20.20.1 \| 192.168.0.1 \| 192.168.0.2 \| 32 \|
| | ...
| | [Arguments] | ${tg_if1_ip4} | ${tg_if2_ip4} | ${dut1_if1_ip4}
| | ... | ${dut1_if2_ip4} | ${dut2_if1_ip4} | ${dut2_if2_ip4}
| | ... | ${remote_host1_ip4}=${NONE} | ${remote_host2_ip4}=${NONE}
| | ... | ${remote_host_ip4_prefix}=${NONE}
| | ...
| | ${dut_tg_ip4_prefix}= | Set Variable | 24
| | ${dut_link_ip4_prefix}= | Set Variable | 30
| | ...
| | VPP Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg_if1_ip4}
| | ... | ${tg_to_dut1_mac}
| | VPP Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_if1_ip4}
| | ... | ${dut2_to_dut1_mac}
| | VPP Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_if2_ip4}
| | ... | ${dut1_to_dut2_mac}
| | VPP Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg_if2_ip4}
| | ... | ${tg_to_dut2_mac}
| | ...
| | Configure IP addresses on interfaces | ${dut1_node} | ${dut1_to_tg}
| | ... | ${dut1_if1_ip4} | ${dut_tg_ip4_prefix}
| | Configure IP addresses on interfaces | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${dut1_if2_ip4} | ${dut_link_ip4_prefix}
| | Configure IP addresses on interfaces | ${dut2_node} | ${dut2_to_dut1}
| | ... | ${dut2_if1_ip4} | ${dut_link_ip4_prefix}
| | Configure IP addresses on interfaces | ${dut2_node} | ${dut2_to_tg}
| | ... | ${dut2_if2_ip4} | ${dut_tg_ip4_prefix}
| | ...
| | Vpp Route Add | ${dut1_node} | ${tg_if2_ip4} | ${dut_tg_ip4_prefix}
| | ... | gateway=${dut2_if1_ip4} | interface=${dut1_to_dut2}
| | Vpp Route Add | ${dut2_node} | ${tg_if1_ip4} | ${dut_tg_ip4_prefix}
| | ... | gateway=${dut1_if2_ip4} | interface=${dut2_to_dut1}
| | ...
| | Run Keyword Unless | '${remote_host1_ip4}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1_node} | ${remote_host1_ip4}
| | ... | ${remote_host_ip4_prefix} | gateway=${tg_if1_ip4}
| | ... | interface=${dut1_to_tg}
| | Run Keyword Unless | '${remote_host2_ip4}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1_node} | ${remote_host2_ip4}
| | ... | ${remote_host_ip4_prefix} | gateway=${dut2_if1_ip4}
| | ... | interface=${dut1_to_dut2}
| | Run Keyword Unless | '${remote_host1_ip4}' == '${NONE}'
| | ... | Vpp Route Add | ${dut2_node} | ${remote_host1_ip4}
| | ... | ${remote_host_ip4_prefix} | gateway=${dut1_if2_ip4}
| | ... | interface=${dut2_to_dut1}
| | Run Keyword Unless | '${remote_host2_ip4}' == '${NONE}'
| | ... | Vpp Route Add | ${dut2_node} | ${remote_host2_ip4}
| | ... | ${remote_host_ip4_prefix} | gateway=${tg_if2_ip4}
| | ... | interface=${dut2_to_tg}
