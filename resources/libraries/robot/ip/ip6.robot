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
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficScriptExecutor
| ...
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| ...
| Documentation | IPv6 keywords

*** Keywords ***
| Get interface Ipv6 addresses
| | [Documentation] | Get IPv6 address for the given interface of the node.
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
| | ... | ${node} | ${interface} | ipv6

| Suppress ICMPv6 router advertisement message
| | [Documentation] | Suppress ICMPv6 router advertisement message for link
| | ... | scope address
| | [Arguments] | ${nodes}
| | Vpp All Ra Suppress Link Layer | ${nodes}

| Configure IPv6 forwarding in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv6 addresses with /64 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv6 adresses with /96 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /64
| | ... | and next hop of neighbour DUT interface IPv6 address. Configure route
| | ... | entries for remote hosts IPv6 addresses if required.
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_ip6 - IPv6 address of TG interface1. Type: string
| | ... | - tg_if2_ip6 - IPv6 address of TG interface2. Type: string
| | ... | - dut1_if1_ip6 - IPv6 address of DUT1 interface1. Type: string
| | ... | - dut1_if2_ip6 - IPv6 address of DUT1 interface1. Type: string
| | ... | - dut2_if1_ip6 - IPv6 address of DUT2 interface1 (Optional).
| | ... | Type: string
| | ... | - dut2_if2_ip6 - IPv6 address of DUT2 interface2 (Optional).
| | ... | Type: string
| | ... | - remote_host1_ip6 - IPv6 address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip6 - IPv6 address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_ip6_prefix - IPv6 address prefix for host IPv6 addresses
| | ... | (Optional). Type: string or integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IPv6 forwarding in circular topology \
| | ... | \| 2001:1::2 \| 2001:2::2 \| 2001:1::1 \| 2001:2::1 \|
| | ... | \| Configure IPv6 forwarding in circular topology \
| | ... | \| 2001:1::2 \| 2001:2::2 \| 2001:1::1 \| 2001:2::1 \
| | ... | \| remote_host1_ip6=3ffe:5f::1 \| remote_host2_ip6=3ffe:5f::2 \
| | ... | \| remote_host_ip6_prefix=128 \|
| | ... | \| Configure IPv6 forwarding in circular topology \
| | ... | \| 2001:1::2 \| 2001:2::2 \| 2001:1::1 \| 2003:3::1 \| 2003:3::2 \
| | ... | \| 2001:2::1 \|
| | ... | \| Configure IPv6 forwarding in circular topology \
| | ... | \| 2001:1::2 \| 2001:2::2 \| 2001:1::1 \| 2003:3::1 \| 2003:3::2 \
| | ... | \| 2001:2::1 \| remote_host1_ip4=3ffe:5f::1 \
| | ... | \| remote_host2_ip4=3ffe:5f::2 \| remote_host_ip4_prefix=128 \|
| | ...
| | [Arguments] | ${tg_if1_ip6} | ${tg_if2_ip6} | ${dut1_if1_ip6}
| | ... | ${dut1_if2_ip6} | ${dut2_if1_ip6}=${NONE} | ${dut2_if2_ip6}=${NONE}
| | ... | ${remote_host1_ip6}=${NONE} | ${remote_host2_ip6}=${NONE}
| | ... | ${remote_host_ip6_prefix}=${NONE}
| | ...
| | ...
| | Configure interfaces in path up
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2_node}
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IPv6 forwarding in 3-node circular topology
| | ... | ${tg_if1_ip6} | ${tg_if2_ip6} | ${dut1_if1_ip6} | ${dut1_if2_ip6}
| | ... | ${dut2_if1_ip6} | ${dut2_if2_ip6} | ${remote_host1_ip6}
| | ... | ${remote_host2_ip6} | ${remote_host_ip6_prefix}
| | ... | ELSE
| | ... | Configure IPv6 forwarding in 2-node circular topology
| | ... | ${tg_if1_ip6} | ${tg_if2_ip6} | ${dut1_if1_ip6} | ${dut1_if2_ip6}
| | ... | remote_host1_ip6=${remote_host1_ip6}
| | ... | remote_host2_ip6=${remote_host2_ip6}
| | ... | remote_host_ip6_prefix=${remote_host_ip6_prefix}

| Configure IPv6 forwarding in 2-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces on DUT node in 2-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv6 addresses with /64 prefix on DUT-TG
| | ... | links. Configure route entries for remote hosts IPv6 addresses
| | ... | if required.
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_ip6 - IPv6 address of TG interface1. Type: string
| | ... | - tg_if2_ip6 - IPv6 address of TG interface2. Type: string
| | ... | - dut1_if1_ip6 - IPv6 address of DUT1 interface1. Type: string
| | ... | - dut1_if2_ip6 - IPv6 address of DUT1 interface1. Type: string
| | ... | - remote_host1_ip6 - IPv6 address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip6 - IPv6 address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_ip6_prefix - IPv6 address prefix for host IPv6 addresses
| | ... | (Optional). Type: string or integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IPv6 forwarding in circular topology \
| | ... | \| 2001:1::2 \| 2001:2::2 \| 2001:1::1 \| 2001:2::1 \|
| | ... | \| Configure IPv6 forwarding in circular topology \
| | ... | \| 2001:1::2 \| 2001:2::2 \| 2001:1::1 \| 2001:2::1 \
| | ... | \| remote_host1_ip6=3ffe:5f::1 \| remote_host2_ip6=3ffe:5f::2 \
| | ... | \| remote_host_ip6_prefix=128 \|
| | ...
| | [Arguments] | ${tg_if1_ip6} | ${tg_if2_ip6} | ${dut1_if1_ip6}
| | ... | ${dut1_if2_ip6} | ${remote_host1_ip6}=${NONE}
| | ... | ${remote_host2_ip6}=${NONE} | ${remote_host_ip6_prefix}=${NONE}
| | ...
| | ${dut_tg_ip6_prefix}= | Set Variable | 64
| | ...
| | VPP Add IP Neighbor
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${tg_if1_ip6} | ${tg_to_dut_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${tg_if2_ip6} | ${tg_to_dut_if2_mac}
| | ...
| | VPP Interface Set IP Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut1_if1_ip6} | ${dut_tg_ip6_prefix}
| | VPP Interface Set IP Address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut1_if2_ip6} | ${dut_tg_ip6_prefix}
| | ...
| | Run Keyword Unless | '${remote_host1_ip6}' == '${NONE}'
| | ... | Vpp Route Add | ${dut_node} | ${remote_host1_ip6}
| | ... | ${remote_host_ip6_prefix} | gateway=${tg_if1_ip6}
| | ... | interface=${dut_to_tg_if1}
| | Run Keyword Unless | '${remote_host2_ip6}' == '${NONE}'
| | ... | Vpp Route Add | ${dut_node} | ${remote_host2_ip6}
| | ... | ${remote_host_ip6_prefix} | gateway=${tg_if2_ip6}
| | ... | interface=${dut_to_tg_if2}

| Configure IPv6 forwarding in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv6 addresses with /64 prefix on DUT-TG links.
| | ... | Configure IPv6 adresses with /96 prefix on DUT1-DUT2 link and set
| | ... | routing on both DUT nodes with prefix /64 and next hop of neighbour
| | ... | DUT interface IPv6 address. Configure route entries for remote hosts
| | ... | IPv6 addresses if required.
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_ip6 - IPv6 address of TG interface1. Type: string
| | ... | - tg_if2_ip6 - IPv6 address of TG interface2. Type: string
| | ... | - dut1_if1_ip6 - IPv6 address of DUT1 interface1. Type: string
| | ... | - dut1_if2_ip6 - IPv6 address of DUT1 interface1. Type: string
| | ... | - dut2_if1_ip6 - IPv6 address of DUT2 interface1 Type: string
| | ... | - dut2_if2_ip6 - IPv6 address of DUT2 interface2 Type: string
| | ... | - remote_host1_ip6 - IPv6 address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip6 - IPv6 address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_ip6_prefix - IPv6 address prefix for host IPv6 addresses
| | ... | (Optional). Type: string or integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IPv6 forwarding in circular topology \
| | ... | \| 2001:1::2 \| 2001:2::2 \| 2001:1::1 \| 2003:3::1 \| 2003:3::2 \
| | ... | \| 2001:2::1 \|
| | ... | \| Configure IPv6 forwarding in circular topology \
| | ... | \| 2001:1::2 \| 2001:2::2 \| 2001:1::1 \| 2003:3::1 \| 2003:3::2 \
| | ... | \| 2001:2::1 \| remote_host1_ip4=3ffe:5f::1 \
| | ... | \| remote_host2_ip4=3ffe:5f::2 \| remote_host_ip4_prefix=128 \|
| | ...
| | [Arguments] | ${tg_if1_ip6} | ${tg_if2_ip6} | ${dut1_if1_ip6}
| | ... | ${dut1_if2_ip6} | ${dut2_if1_ip6} | ${dut2_if2_ip6}
| | ... | ${remote_host1_ip6}=${NONE} | ${remote_host2_ip6}=${NONE}
| | ... | ${remote_host_ip6_prefix}=${NONE}
| | ...
| | ${dut_tg_ip6_prefix}= | Set Variable | 64
| | ${dut_link_ip6_prefix}= | Set Variable | 96
| | ...
| | VPP Add IP Neighbor
| | ... | ${dut1_node} | ${dut1_to_tg} | ${tg_if1_ip6} | ${tg_to_dut1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut2_if1_ip6} | ${dut2_to_dut1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut1_if2_ip6} | ${dut1_to_dut2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2_node} | ${dut2_to_tg} | ${tg_if2_ip6} | ${tg_to_dut2_mac}
| | ...
| | VPP Interface Set IP Address
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_if1_ip6} | ${dut_tg_ip6_prefix}
| | VPP Interface Set IP Address | ${dut1_node}
| | ... | ${dut1_to_dut2} | ${dut1_if2_ip6} | ${dut_link_ip6_prefix}
| | VPP Interface Set IP Address | ${dut2_node}
| | ... | ${dut2_to_dut1} | ${dut2_if1_ip6} | ${dut_link_ip6_prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_if2_ip6} | ${dut_tg_ip6_prefix}
| | ...
| | Vpp Route Add | ${dut1_node} | ${tg_if2_ip6} | ${dut_tg_ip6_prefix}
| | ... | gateway=${dut2_if1_ip6} | interface=${dut1_to_dut2}
| | Vpp Route Add | ${dut2_node} | ${tg_if1_ip6} | ${dut_tg_ip6_prefix}
| | ... | gateway=${dut1_if2_ip6} | interface=${dut2_to_dut1}
| | ...
| | Run Keyword Unless | '${remote_host1_ip6}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1_node} | ${remote_host1_ip6}
| | ... | ${remote_host_ip6_prefix} | gateway=${tg_if1_ip6}
| | ... | interface=${dut1_to_tg}
| | Run Keyword Unless | '${remote_host2_ip6}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1_node} | ${remote_host2_ip6}
| | ... | ${remote_host_ip6_prefix} | gateway=${dut2_if1_ip6}
| | ... | interface=${dut1_to_dut2}
| | Run Keyword Unless | '${remote_host1_ip6}' == '${NONE}'
| | ... | Vpp Route Add | ${dut2_node} | ${remote_host1_ip6}
| | ... | ${remote_host_ip6_prefix} | gateway=${dut1_if2_ip6}
| | ... | interface=${dut2_to_dut1}
| | Run Keyword Unless | '${remote_host2_ip6}' == '${NONE}'
| | ... | Vpp Route Add | ${dut2_node} | ${remote_host2_ip6}
| | ... | ${remote_host_ip6_prefix} | gateway=${tg_if2_ip6}
| | ... | interface=${dut2_to_tg}
