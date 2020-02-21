# Copyright (c) 2020 Cisco and/or its affiliates.
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
|
| Documentation | IPv6 keywords

*** Keywords ***
| Initialize IPv6 forwarding in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup neighbor
| | ... | on all VPP interfaces. Setup IPv6 addresses with /64 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv6 adresses with /64 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /64
| | ... | and next hop of neighbour DUT interface IPv4 address.
| |
| | ... | *Arguments:*
| | ... | - remote_host1_ip - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip - IP address of remote host2 (Optional).
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv6 forwarding in circular topology \
| | ... | \| 3ffe:5f::1 \| 3ffe:5f::2 \|
| |
| | [Arguments] | ${remote_host1_ip}=${NONE} | ${remote_host2_ip}=${NONE}
| |
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| |
| | Set interfaces in path up
| |
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 2001:1::2 | ${TG_pf1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2001:3::1 | ${DUT2_${int}1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 2001:3::2 | ${DUT1_${int}2_mac}[0]
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}2}[0]
| | ... | ELSE | Set Variable | ${DUT1_${int}2}[0]
| | VPP Add IP Neighbor
| | ... | ${dut} | ${dut_if2} | 2001:2::2 | ${TG_pf2_mac}[0]
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 2001:1::1 | 64
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2001:3::1 | 64
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 2001:3::2 | 64
| | VPP Interface Set IP Address
| | ... | ${dut} | ${dut_if2} | 2001:2::1 | 64
| |
| | Vpp All Ra Suppress Link Layer | ${nodes}
| |
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 2001:2::0 | 64 | gateway=2001:3::2
| | ... | interface=${DUT1_${int}2}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 2001:1::0 | 64 | gateway=2001:3::1
| | ... | interface=${DUT2_${int}1}[0]
| |
| | Run Keyword Unless | '${remote_host1_ip}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip} | 128
| | ... | gateway=2001:1::2 | interface=${DUT1_${int}1}[0]
| | Run Keyword Unless | '${remote_host2_ip}' == '${NONE}'
| | ... | Vpp Route Add | ${dut} | ${remote_host2_ip} | 128
| | ... | gateway=2001:2::2 | interface=${dut_if2}
| | Run Keyword Unless | '${remote_host1_ip}' == '${NONE}'
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip} | 128
| | ... | gateway=2001:3::2 | interface=${DUT1_${int}2}[0]
| | Run Keyword Unless | '${remote_host2_ip}' == '${NONE}'
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${remote_host2_ip} | 128
| | ... | gateway=2001:3::1 | interface=${DUT2_${int}1}[0]

| Initialize IPv6 forwarding with scaling in circular topology
| | [Documentation]
| | ... | Custom setup of IPv6 topology with scalability of ip routes on all
| | ... | DUT nodes in 2-node / 3-node circular topology
| |
| | ... | *Arguments:*
| | ... | - count - IP route count. Type: integer
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv6 forwarding with scaling in circular \
| | ... | topology \| 100000 \|
| |
| | [Arguments] | ${count}
| |
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| |
| | Set interfaces in path up
| |
| | ${prefix}= | Set Variable | 64
| | ${host_prefix}= | Set Variable | 128
| | VPP Interface Set IP Address
| | .. | ${dut1} | ${DUT1_${int}1}[0] | 2001:3::1 | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2001:4::1 | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 2001:4::2 | ${prefix}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}2}[0]
| | ... | ELSE | Set Variable | ${DUT1_${int}2}[0]
| | VPP Interface Set IP Address
| | ... | ${dut} | ${dut_if2} | 2001:5::1 | ${prefix}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 2001:3::2 | ${TG_pf1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2001:4::2 | ${DUT2_${int}1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 2001:4::1 | ${DUT1_${int}2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut} | ${dut_if2} | 2001:5::2 | ${TG_pf2_mac}[0]
| | Vpp Route Add | ${dut1} | 2001:1::0 | ${host_prefix} | gateway=2001:3::2
| | ... | interface=${DUT1_${int}1}[0] | count=${count}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 2001:2::0 | ${host_prefix}
| | ... | gateway=2001:4::2 | interface=${DUT1_${int}2}[0] | count=${count}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 2001:1::0 | ${host_prefix}
| | ... | gateway=2001:4::1 | interface=${DUT2_${int}1}[0] | count=${count}
| | Vpp Route Add | ${dut} | 2001:2::0 | ${host_prefix} | gateway=2001:5::2
| | ... | interface=${dut_if2} | count=${count}

| Initialize IPv6 forwarding with vhost in 2-node circular topology
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on \
| | ... | VPP node. Set UP state of all VPP interfaces in path. Create \
| | ... | nf_nodes+1 FIB tables on DUT with multipath routing. Assign each \
| | ... | Virtual interface to FIB table with Physical interface or Virtual \
| | ... | interface on both nodes. Setup IPv6 addresses with /64 prefix on \
| | ... | DUT-TG links. Set routing on DUT nodes in all FIB tables with \
| | ... | prefix /64 and next hop of neighbour IPv6 address. Setup neighbours \
| | ... | on all VPP interfaces.
| |
| | ... | *Arguments:*
| | ... | - nf_nodes - Number of guest VMs. Type: integer
| |
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /var/run/vpp/sock-${VM_ID}-1
| | ... | - /var/run/vpp/sock-${VM_ID}-2
| |
| | ... | *Example:*
| |
| | ... | \| IPv6 forwarding with Vhost-User initialized in a 2-node circular\
| | ... | topology \| 1 \|
| |
| | [Arguments] | ${nf_nodes}=${1}
| |
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | Set interfaces in path up
| | ${prefix}= | Set Variable | 64
| | ${fib_table_1}= | Set Variable | ${101}
| | ${fib_table_2}= | Evaluate | ${fib_table_1}+${nf_nodes}
| | Add Fib Table | ${dut1} | ${fib_table_1} | ipv6=${True}
| | Add Fib Table | ${dut1} | ${fib_table_2} | ipv6=${True}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${fib_table_1}
| | ... | ipv6=${True}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${fib_table_2}
| | ... | ipv6=${True}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 2001:100::1
| | ... | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2001:200::1
| | ... | ${prefix}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0]} | 2001:100::2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2001:200::2 | ${TG_pf2_mac}[0]
| | Vpp Route Add | ${dut1} | 2001:1::0 | 64 | gateway=2001:100::2
| | ... | interface=${dut1_if1} | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 2001:2::0 | 64 | gateway=2001:200::2
| | ... | interface=${dut1_if2} | vrf=${fib_table_2}
| | FOR | ${number} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${fib_table_1}= | Evaluate | ${100}+${number}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1}+${1}
| | | Configure vhost interfaces | ${dut1}
| | | ... | /var/run/vpp/sock-${number}-1 | /var/run/vpp/sock-${number}-2
| | | ... | dut1-vhost-${number}-if1 | dut1-vhost-${number}-if2
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if1} | up
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if2} | up
| | | Add Fib Table | ${dut1} | ${fib_table_1} | ipv6=${True}
| | | Add Fib Table | ${dut1} | ${fib_table_2} | ipv6=${True}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | ${fib_table_1} | ipv6=${True}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | ${fib_table_2} | ipv6=${True}
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${dut1-vhost-${number}-if1} | 1:1::2 | 64
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${dut1-vhost-${number}-if2} | 1:2::2 | 64
| | | Vpp Route Add | ${dut1} | 2001:2::0 | 64 | gateway=1:1::1
| | | ... | interface=${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Vpp Route Add | ${dut1} | 2001:1::0 | 64 | gateway=1:2::1
| | | ... | interface=${dut1-vhost-${number}-if2} | vrf=${fib_table_2}
| | END

| Initialize IPv6 forwarding with VLAN dot1q sub-interfaces in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. In case of 3-node topology create VLAN
| | ... | sub-interfaces between DUTs. In case of 2-node topology create VLAN
| | ... | sub-interface on dut1-if2 interface. Get the interface MAC addresses
| | ... | and setup ARPs. Setup IPv6 addresses with /64 prefix on DUT-TG links
| | ... | and set routing with prefix /64. In case of 3-node set IPv6 adresses
| | ... | with /64 prefix on VLAN and set routing on both DUT nodes with prefix
| | ... | /64. Set next hop of neighbour DUT interface IPv6 address. All
| | ... | interfaces are brought up.
| |
| | ... | *Arguments:*
| | ... | - tg_if1_net - TG interface 1 IPv6 subnet used by traffic generator.
| | ... | Type: integer
| | ... | - tg_if2_net - TG interface 2 IPv6 subnet used by traffic generator.
| | ... | Type: integer
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| |
| | ... | _NOTE:_ This KW uses following test case variables:
| | ... | - dut1 - DUT1 node.
| | ... | - dut2 - DUT2 node.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2_if1 - DUT2 interface towards DUT1.
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv6 forwarding with VLAN dot1q sub-interfaces\
| | ... | in circular topology \| 2001:1::0 \| 2001:2::0 \| 10 \| pop-1 \|
| |
| | [Arguments] | ${tg_if1_net} | ${tg_if2_net} | ${subid} | ${tag_rewrite}
| |
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| |
| | Set interfaces in path up
| |
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Initialize VLAN dot1q sub-interfaces in circular topology
| | ... | ${dut1} | ${DUT1_${int}2}[0]
| | ... | ${dut2} | ${DUT2_${int}1}[0] | SUB_ID=${subid}
| | ... | ELSE | Initialize VLAN dot1q sub-interfaces in circular topology
| | ... | ${dut1} | ${DUT1_${int}2}[0] | SUB_ID=${subid}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1}
| | ... | ${dut2} | ${subif_index_2} | TAG_REWRITE_METHOD=${tag_rewrite}
| | ... | ELSE | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | TAG_REWRITE_METHOD=${tag_rewrite}
| |
| | ${prefix}= | Set Variable | 64
| | ${host_prefix}= | Set Variable | 64
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 2002:1::1 | ${TG_pf1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut1} | ${subif_index_1} | 2002:2::2 | ${DUT2_${int}1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut2} | ${subif_index_2} | 2002:2::1 | ${DUT1_${int}2_mac}[0]
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}2}[0]
| | ... | ELSE | Set Variable | ${subif_index_1}
| | VPP Add IP Neighbor
| | ... | ${dut} | ${dut_if2} | 2002:3::1 | ${TG_pf2_mac}[0]
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 2002:1::2 | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut1} | ${subif_index_1} | 2002:2::1
| | ... | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut2} | ${subif_index_2} | 2002:2::2
| | ... | ${prefix}
| | VPP Interface Set IP Address | ${dut} | ${dut_if2} | 2002:3::2 | ${prefix}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | Vpp Route Add | ${dut1} | ${tg_if1_net} | ${host_prefix}
| | ... | gateway=2002:1::1 | interface=${DUT1_${int}1}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${tg_if2_net} | ${host_prefix}
| | ... | gateway=2002:2::2 | interface=${subif_index_1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${tg_if1_net} | ${host_prefix}
| | ... | gateway=2002:2::1 | interface=${subif_index_2}
| | Vpp Route Add | ${dut} | ${tg_if2_net} | ${host_prefix}
| | ... | gateway=2002:3::1 | interface=${dut_if2}

