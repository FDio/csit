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
| Library | resources.libraries.python.DpdkUtil
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.TestConfig
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Library | resources.libraries.python.VhostUser
| ...
| Documentation | Performance suite keywords - configuration

*** Keywords ***
| Initialize IPSec in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG and
| | ... | DUT1-DUT2 links. Set routing for encrypted traffic on both DUT nodes
| | ... | with prefix /8 and next hop of neighbour DUT or TG interface IPv4
| | ... | address.
| | ...
| | Set interfaces in path up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1}
| | ... | ${dut1_if1_ip4} | 24
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if2}
| | ... | ${dut2_if2_ip4} | 24
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | ${tg_if1_ip4} | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | ${tg_if2_ip4} | ${tg_if2_mac}
| | Vpp Route Add | ${dut1} | ${laddr_ip4} | 8 | gateway=${tg_if1_ip4}
| | ... | interface=${dut1_if1}
| | Vpp Route Add | ${dut2} | ${raddr_ip4} | 8 | gateway=${tg_if2_ip4}
| | ... | interface=${dut2_if2}

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
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_net - TG interface 1 IPv6 subnet used by traffic generator.
| | ... | Type: integer
| | ... | - tg_if2_net - TG interface 2 IPv6 subnet used by traffic generator.
| | ... | Type: integer
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ...
| | ... | _NOTE:_ This KW uses following test case variables:
| | ... | - dut1 - DUT1 node.
| | ... | - dut2 - DUT2 node.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2_if1 - DUT2 interface towards DUT1.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv6 forwarding with VLAN dot1q sub-interfaces\
| | ... | in circular topology \| 2001:1::0 \| 2001:2::0 \| 10 \| pop-1 \|
| | ...
| | [Arguments] | ${tg_if1_net} | ${tg_if2_net} | ${subid} | ${tag_rewrite}
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ...
| | Set interfaces in path up
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Initialize VLAN dot1q sub-interfaces in circular topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ELSE | Initialize VLAN dot1q sub-interfaces in circular topology
| | ... | ${dut1} | ${dut1_if2} | SUB_ID=${subid}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure L2 tag rewrite method on interfaces | ${dut1}
| | ... | ${subif_index_1} | ${dut2} | ${subif_index_2} | ${tag_rewrite}
| | ... | ELSE | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | TAG_REWRITE_METHOD=${tag_rewrite}
| | ...
| | ${prefix}= | Set Variable | 64
| | ${host_prefix}= | Set Variable | 64
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2002:1::1 | ${tg_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut1} | ${subif_index_1} | 2002:2::2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut2} | ${subif_index_2} | 2002:2::1 | ${dut1_if2_mac}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${subif_index_1}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 2002:3::1 | ${tg_if2_mac}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 2002:1::2 | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut1} | ${subif_index_1} | 2002:2::1
| | ... | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut2} | ${subif_index_2} | 2002:2::2
| | ... | ${prefix}
| | VPP Interface Set IP Address | ${dut} | ${dut_if2} | 2002:3::2 | ${prefix}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | Vpp Route Add | ${dut1} | ${tg_if1_net} | ${host_prefix}
| | ... | gateway=2002:1::1 | interface=${dut1_if1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${tg_if2_net} | ${host_prefix}
| | ... | gateway=2002:2::2 | interface=${subif_index_1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${tg_if1_net} | ${host_prefix}
| | ... | gateway=2002:2::1 | interface=${subif_index_2}
| | Vpp Route Add | ${dut} | ${tg_if2_net} | ${host_prefix}
| | ... | gateway=2002:3::1 | interface=${dut_if2}

| Initialize IPv6 forwarding over SRv6 with encapsulation with '${n}' x SID '${prepos}' decapsulation in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup neighbours on all
| | ... | VPP interfaces. Setup IPv6 addresses on all interfaces. Set segment
| | ... | routing for IPv6 for required number of SIDs and configure IPv6 routes
| | ... | on both DUT nodes.
| | ...
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip6} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_if2_ip6} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_if1_ip6} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_if2_ip6} | ${prefix}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | :FOR | ${number} | IN RANGE | 2 | ${dst_addr_nr}+2
| | | ${hexa_nr}= | Convert To Hex | ${number}
| | | VPP Add IP Neighbor | ${dut1}
| | | ... | ${dut1_if1} | ${tg_if1_ip6_subnet}${hexa_nr} | ${tg_if1_mac}
| | | VPP Add IP Neighbor | ${dut2}
| | | ... | ${dut2_if2} | ${tg_if2_ip6_subnet}${hexa_nr} | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_if1_ip6} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_if2_ip6} | ${dut1_if2_mac}
| | ${sid1}= | Set Variable If
| | ... | "${n}" == "1" | ${dut2_sid1}
| | ... | "${n}" == "2" | ${dut2_sid1_1}
| | ${sid2}= | Set Variable If
| | ... | "${n}" == "1" | ${dut1_sid2}
| | ... | "${n}" == "2" | ${dut1_sid2_1}
| | Vpp Route Add | ${dut1} | ${sid1} | ${sid_prefix} | gateway=${dut2_if1_ip6}
| | ... | interface=${dut1_if2}
| | Vpp Route Add | ${dut2} | ${sid2} | ${sid_prefix} | gateway=${dut1_if2_ip6}
| | ... | interface=${dut2_if1}
# Configure SRv6 for direction0
| | Set SR Encaps Source Address on DUT | ${dut1} | ${dut1_sid1}
| | @{sid_list_dir0}= | Run Keyword If | "${n}" == "1"
| | ... | Create List | ${dut2_sid1}
| | ... | ELSE IF | "${n}" == "2"
| | ... | Create List | ${dut2_sid1_1} | ${dut2_sid1_2}
| | Configure SR Policy on DUT | ${dut1} | ${dut1_bsid} | encap
| | ... | @{sid_list_dir0}
| | Configure SR Steer on DUT | ${dut1} | L3 | ${dut1_bsid}
| | ... | ip_addr=${tg_if2_ip6_subnet} | prefix=${sid_prefix}
| | Run Keyword If | "${n}" == "1"
| | ... | Configure SR LocalSID on DUT | ${dut2} | ${dut2_sid1} | end.dx6
| | ... | interface=${dut2_if2} | next_hop=${tg_if2_ip6_subnet}2
| | Run Keyword If | "${n}" == "2"
| | ... | Configure SR LocalSID on DUT | ${dut2} | ${dut2_sid1_1} | end
| | Run Keyword If | "${n}" == "2" and "${prepos}" != "without"
| | ... | Configure SR LocalSID on DUT | ${dut2} | ${dut2_sid1_2} | end.dx6
| | ... | interface=${dut2_if2} | next_hop=${tg_if2_ip6_subnet}2
| | Run Keyword If | "${n}" == "2" and "${prepos}" == "without"
| | ... | Vpp Route Add | ${dut2} | ${dut2_sid1_2} | ${sid_prefix}
| | ... | gateway=${tg_if2_ip6_subnet}2 | interface=${dut2_if2}
# Configure SRv6 for direction1
| | Set SR Encaps Source Address on DUT | ${dut2} | ${dut2_sid2}
| | @{sid_list_dir1}= | Run Keyword If | "${n}" == "1"
| | ... | Create List | ${dut1_sid2}
| | ... | ELSE IF | "${n}" == "2"
| | ... | Create List | ${dut1_sid2_1} | ${dut1_sid2_2}
| | Configure SR Policy on DUT | ${dut2} | ${dut2_bsid} | encap
| | ... | @{sid_list_dir1}
| | Configure SR Steer on DUT | ${dut2} | L3 | ${dut2_bsid}
| | ... | ip_addr=${tg_if1_ip6_subnet} | prefix=${sid_prefix}
| | Run Keyword If | "${n}" == "1"
| | ... | Configure SR LocalSID on DUT | ${dut1} | ${dut1_sid2} | end.dx6
| | ... | interface=${dut1_if1} | next_hop=${tg_if1_ip6_subnet}2
| | Run Keyword If | "${n}" == "2"
| | ... | Configure SR LocalSID on DUT | ${dut1} | ${dut1_sid2_1} | end
| | Run Keyword If | "${n}" == "2" and "${prepos}" != "without"
| | ... | Configure SR LocalSID on DUT | ${dut1} | ${dut1_sid2_2} | end.dx6
| | ... | interface=${dut1_if1} | next_hop=${tg_if1_ip6_subnet}2
| | Run Keyword If | "${n}" == "2" and "${prepos}" == "without"
| | ... | Vpp Route Add | ${dut1} | ${dut1_sid2_2} | ${sid_prefix}
| | ... | gateway=${tg_if1_ip6_subnet}2 | interface=${dut1_if1}
| | Set interfaces in path up

| Initialize IPv6 forwarding over SRv6 with endpoint to SR-unaware Service Function via '${behavior}' behaviour in 3-node circular topology
| | [Documentation]
| | ... | Create pair of Memif interfaces on all defined VPP nodes. Set UP
| | ... | state on VPP interfaces in path on nodes in 3-node circular topology.
| | ... | Get the interface MAC addresses and setup neighbours on all VPP
| | ... | interfaces. Setup IPv6 addresses on all interfaces. Set segment
| | ... | routing for IPv6 with defined behaviour function and configure IPv6
| | ... | routes on both DUT nodes.
| | ...
| | ... | *Note:*
| | ... | KW uses test variable rxq_count_int set by KW Add worker threads
| | ... | and rxqueues to all DUTs
| | ...
| | ${sock1}= | Set Variable | memif-DUT1_CNF
| | ${sock2}= | Set Variable | memif-DUT2_CNF
| | Set up memif interfaces on DUT node | ${dut1} | ${sock1} | ${sock1}
| | ... | ${1} | dut1-memif-1-if1 | dut1-memif-1-if2 | ${rxq_count_int}
| | ... | ${rxq_count_int}
| | VPP Set interface MTU | ${dut1} | ${dut1-memif-1-if1}
| | VPP Set interface MTU | ${dut1} | ${dut1-memif-1-if2}
| | Set up memif interfaces on DUT node | ${dut2} | ${sock2} | ${sock2}
| | ... | ${1} | dut2-memif-1-if1 | dut2-memif-1-if2 | ${rxq_count_int}
| | ... | ${rxq_count_int}
| | VPP Set interface MTU | ${dut2} | ${dut2-memif-1-if1}
| | VPP Set interface MTU | ${dut2} | ${dut2-memif-1-if2}
| | :FOR | ${dut} | IN | @{duts}
| | | Show Memif | ${nodes['${dut}']}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip6} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_if2_ip6} | ${prefix}
| | VPP Interface Set IP Address | ${dut1} | ${dut1-memif-1-if1}
| | ... | ${dut1-memif-1-if1_ip6} | ${mem_prefix}
| | VPP Interface Set IP Address | ${dut1} | ${dut1-memif-1-if2}
| | ... | ${dut1-memif-1-if2_ip6} | ${mem_prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_if1_ip6} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_if2_ip6} | ${prefix}
| | VPP Interface Set IP Address | ${dut2} | ${dut2-memif-1-if1}
| | ... | ${dut2-memif-1-if1_ip6} | ${mem_prefix}
| | VPP Interface Set IP Address | ${dut2} | ${dut2-memif-1-if2}
| | ... | ${dut2-memif-1-if2_ip6} | ${mem_prefix}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_if1_ip6} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_if2_ip6} | ${dut1_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${tg_if1_ip6_subnet}2 | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if2} | ${tg_if2_ip6_subnet}2 | ${tg_if2_mac}
| | ${dut1-memif-1-if2_mac}= | Get Interface MAC | ${dut1} | memif2
| | ${dut2-memif-1-if2_mac}= | Get Interface MAC | ${dut2} | memif2
| | VPP Add IP Neighbor | ${dut1}
| | ... | ${dut1-memif-1-if1} | ${dut1_nh} | ${dut1-memif-1-if2_mac}
| | VPP Add IP Neighbor | ${dut2}
| | ... | ${dut2-memif-1-if1} | ${dut2_nh} | ${dut2-memif-1-if2_mac}
| | Vpp Route Add | ${dut1} | ${dut2_sid1} | ${sid_prefix}
| | ... | gateway=${dut2_if1_ip6} | interface=${dut1_if2}
| | Vpp Route Add | ${dut1} | ${out_sid2_1} | ${sid_prefix}
| | ... | gateway=${tg_if1_ip6_subnet}2 | interface=${dut1_if1}
| | Vpp Route Add | ${dut2} | ${dut1_sid2} | ${sid_prefix}
| | ... | gateway=${dut1_if2_ip6} | interface=${dut2_if1}
| | Vpp Route Add | ${dut2} | ${out_sid1_1} | ${sid_prefix}
| | ... | gateway=${tg_if2_ip6_subnet}2 | interface=${dut2_if2}
# Configure SRv6 for direction0 on DUT1
| | Set SR Encaps Source Address on DUT | ${dut1} | ${dut1_sid1}
| | @{sid_list_dir0}= | Create List | ${dut2_sid1} | ${out_sid1_1}
| | ... | ${out_sid1_2}
| | Configure SR Policy on DUT | ${dut1} | ${dut1_bsid} | encap
| | ... | @{sid_list_dir0}
| | Configure SR Steer on DUT | ${dut1} | L3 | ${dut1_bsid}
| | ... | ip_addr=${tg_if2_ip6_subnet} | prefix=${sid_prefix}
# Configure SRv6 for direction1 on DUT2
| | Set SR Encaps Source Address on DUT | ${dut2} | ${dut2_sid2}
| | @{sid_list_dir1}= | Create List | ${dut1_sid2} | ${out_sid2_1}
| | ... | ${out_sid2_2}
| | Configure SR Policy on DUT | ${dut2} | ${dut2_bsid} | encap
| | ... | @{sid_list_dir1}
| | Configure SR Steer on DUT | ${dut2} | L3 | ${dut2_bsid}
| | ... | ip_addr=${tg_if1_ip6_subnet} | prefix=${sid_prefix}
# Configure SRv6 for direction0 on DUT2
| | ${dut2_out_if}= | Get Interface Name | ${dut2} | memif1
| | ${dut2_in_if}= | Get Interface Name | ${dut2} | memif2
| | Remove Values From List | ${sid_list_dir0} | ${dut2_sid1}
| | Run Keyword If | "${behavior}" == "static_proxy"
| | ... | Configure SR LocalSID on DUT | ${dut2} | ${dut2_sid1} | end.as
| | ... | ${NONE} | ${dut2_nh} | ${NONE} | ${dut2_out_if} | ${dut2_in_if}
| | ... | ${dut1_sid1} | @{sid_list_dir0}
| | ... | ELSE IF | "${behavior}" == "dynamic_proxy"
| | ... | Configure SR LocalSID on DUT | ${dut2} | ${dut2_sid1} | end.ad
| | ... | next_hop=${dut2_nh} | out_if=${dut2_out_if} | in_if=${dut2_in_if}
| | ... | ELSE IF | "${behavior}" == "masquerading"
| | ... | Configure SR LocalSID on DUT | ${dut2} | ${dut2_sid1} | end.am
| | ... | next_hop=${dut2_nh} | out_if=${dut2_out_if} | in_if=${dut2_in_if}
| | ... | ELSE | Fail | Unsupported behaviour: ${behavior}
# Configure SRv6 for direction1 on DUT1
| | ${dut1_out_if}= | Get Interface Name | ${dut1} | memif1
| | ${dut1_in_if}= | Get Interface Name | ${dut1} | memif2
| | Remove Values From List | ${sid_list_dir1} | ${dut1_sid2}
| | Run Keyword If | "${behavior}" == "static_proxy"
| | ... | Configure SR LocalSID on DUT | ${dut1} | ${dut1_sid2} | end.as
| | ... | ${NONE} | ${dut1_nh} | ${NONE} | ${dut1_out_if} | ${dut1_in_if}
| | ... | ${dut2_sid2} | @{sid_list_dir1}
| | ... | ELSE IF | "${behavior}" == "dynamic_proxy"
| | ... | Configure SR LocalSID on DUT | ${dut1} | ${dut1_sid2} | end.ad
| | ... | next_hop=${dut1_nh} | out_if=${dut1_out_if} | in_if=${dut1_in_if}
| | ... | ELSE IF | "${behavior}" == "masquerading"
| | ... | Configure SR LocalSID on DUT | ${dut1} | ${dut1_sid2} | end.am
| | ... | next_hop=${dut1_nh} | out_if=${dut1_out_if} | in_if=${dut1_in_if}
| | ... | ELSE | Fail | Unsupported behaviour: ${behavior}
| | Set interfaces in path up

| Configure IPv4 ACLs
| | [Documentation]
| | ... | Configure ACL with required number of not-hitting permit ACEs plus two
| | ... | hitting ACEs for both traffic directions.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - dut_if1 - DUT node interface1 name (Optional). Type: string
| | ... | - dut_if2 - DUT node interface2 name (Optional). Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IPv4 ACLs \| ${nodes['DUT1']} \| GigabitEthernet0/7/0 \
| | ... | \| GigabitEthernet0/8/0 \|
| | ...
| | ... | _NOTE:_ This KW uses following test case variables:
| | ... | - src_ip_start - Source IP address start. Type: string
| | ... | - dst_ip_start - Destination IP address start. Type: string
| | ... | - ip_step - IP address step. Type: string
| | ... | - sport_start - Source port number start. Type: string
| | ... | - dport_start - Destination port number start. Type: string
| | ... | - port_step - Port number step. Type: string
| | ... | - no_hit_aces_number - Number of not-hitting ACEs to be configured.
| | ... | Type: integer
| | ... | - acl_apply_type - To what path apply the ACL - input or output.
| | ... | Type: string
| | ... | - acl_action - Action for the rule - deny, permit, permit+reflect.
| | ... | Type: string
| | ... | - trex_stream1_subnet - IP subnet used by T-Rex in direction 0->1.
| | ... | Type: string
| | ... | - trex_stream2_subnet - IP subnet used by T-Rex in direction 1->0.
| | ... | Type: string
| | ...
| | [Arguments] | ${dut} | ${dut_if1}=${NONE} | ${dut_if2}=${NONE}
| | ${src_ip_int} = | Evaluate
| | ... | int(ipaddress.ip_address(unicode($src_ip_start))) - $ip_step
| | ... | modules=ipaddress
| | ${dst_ip_int} = | Evaluate
| | ... | int(ipaddress.ip_address(unicode($dst_ip_start))) - $ip_step
| | ... | modules=ipaddress
| | ${ip_limit} = | Set Variable | 255.255.255.255
| | ${ip_limit_int} = | Evaluate
| | ... | int(ipaddress.ip_address(unicode($ip_limit))) | modules=ipaddress
| | ${sport}= | Evaluate | $sport_start - $port_step
| | ${dport}= | Evaluate | $dport_start - $port_step
| | ${port_limit}= | Set Variable | ${65535}
| | ${acl}= | Set Variable | ipv4 permit
| | :FOR | ${nr} | IN RANGE | 0 | ${no_hit_aces_number}
| | | ${src_ip_int} = | Evaluate | $src_ip_int + $ip_step
| | | ${dst_ip_int} = | Evaluate | $dst_ip_int + $ip_step
| | | ${sport}= | Evaluate | $sport + $port_step
| | | ${dport}= | Evaluate | $dport + $port_step
| | | ${ipv4_limit_reached}= | Set Variable If
| | | ... | $src_ip_int > $ip_limit_int or $src_ip_int > $ip_limit_int
| | | ... | ${TRUE}
| | | ${udp_limit_reached}= | Set Variable If
| | | ... | $sport > $port_limit or $dport > $port_limit | ${TRUE}
| | | Run Keyword If | $ipv4_limit_reached is True | Log
| | | ... | Can't do more iterations - IPv4 address limit has been reached.
| | | ... | WARN
| | | Run Keyword If | $udp_limit_reached is True | Log
| | | ... | Can't do more iterations - UDP port limit has been reached.
| | | ... | WARN
| | | ${src_ip} = | Run Keyword If | $ipv4_limit_reached is True
| | | ... | Set Variable | ${ip_limit}
| | | ... | ELSE | Evaluate | str(ipaddress.ip_address($src_ip_int))
| | | ... | modules=ipaddress
| | | ${dst_ip} = | Run Keyword If | $ipv4_limit_reached is True
| | | ... | Set Variable | ${ip_limit}
| | | ... | ELSE | Evaluate | str(ipaddress.ip_address($dst_ip_int))
| | | ... | modules=ipaddress
| | | ${sport}= | Set Variable If | ${sport} > $port_limit | $port_limit
| | | ... | ${sport}
| | | ${dport}= | Set Variable If | ${dport} > $port_limit | $port_limit
| | | ... | ${dport}
| | | ${acl}= | Catenate | ${acl} | src ${src_ip}/32 dst ${dst_ip}/32
| | | ... | sport ${sport} | dport ${dport},
| | | Exit For Loop If
| | | ... | $ipv4_limit_reached is True or $udp_limit_reached is True
| | ${acl}= | Catenate | ${acl}
| | ... | ipv4 ${acl_action} src ${trex_stream1_subnet},
| | ... | ipv4 ${acl_action} src ${trex_stream2_subnet}
| | Add Replace Acl Multi Entries | ${dut} | rules=${acl}
| | @{acl_list}= | Create List | ${0}
| | Run Keyword If | 'input' in $acl_apply_type and $dut_if1 is not None
| | ... | Set Acl List For Interface | ${dut} | ${dut_if1} | input | ${acl_list}
| | Run Keyword If | 'input' in $acl_apply_type and $dut_if2 is not None
| | ... | Set Acl List For Interface | ${dut} | ${dut_if2} | input | ${acl_list}
| | Run Keyword If | 'output' in $acl_apply_type and $dut_if1 is not None
| | ... | Set Acl List For Interface | ${dut} | ${dut_if1} | output
| | ... | ${acl_list}
| | Run Keyword If | 'output' in $acl_apply_type and $dut_if2 is not None
| | ... | Set Acl List For Interface | ${dut} | ${dut_if2} | output
| | ... | ${acl_list}

| Initialize IPv4 routing for '${ip_nr}' addresses with IPv4 ACLs on DUT1 in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| | ... | Apply required ACL rules to DUT1 interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - ip_nr - Number of IPs to be used. Type: integer or string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv4 routing for '10' addresses with IPv4 ACLs on DUT1 \
| | ... | in 3-node circular topology \|
| | ...
| | ... | _NOTE:_ This KW uses following test case variables:
| | ... | - tg - TG node.
| | ... | - dut1 - DUT1 node.
| | ... | - dut2 - DUT2 node.
| | ... | - tg_if1 - TG interface 1 towards DUT1.
| | ... | - tg_if2 - TG interface 2 towards DUT2 (3-node topo) or DUT1
| | ... | (2-node topo).
| | ... | - dut1_if1 - DUT1 interface 1 towards TG.
| | ... | - dut1_if2 - DUT1 interface 2 towards DUT2 (3-node topo) or TG
| | ... | (2-node topo).
| | ... | - dut2_if1 - DUT2 interface 1 towards DUT1.
| | ... | - dut2_if2 - DUT2 interface 2 towards TG.
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | ...
| | Set interfaces in path up
| | ...
| | :FOR | ${number} | IN RANGE | 2 | ${ip_nr}+2
| | | VPP Add IP Neighbor
| | | ... | ${dut1} | ${dut1_if1} | 10.10.10.${number} | ${tg_if1_mac}
| | | VPP Add IP Neighbor
| | | ... | ${dut} | ${dut_if2} | 20.20.20.${number} | ${tg_if2_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | 1.1.1.2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | 1.1.1.1 | ${dut1_if2_mac}
| | ...
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | 10.10.10.1 | 24
| | VPP Interface Set IP Address
| | ... | ${dut} | ${dut_if2} | 20.20.20.1 | 24
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | 1.1.1.1 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | 1.1.1.2 | 30
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | gateway=1.1.1.2
| | ... | interface=${dut1_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | gateway=1.1.1.1
| | ... | interface=${dut2_if1}
| | ...
| | Configure IPv4 ACLs | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Configure MACIP ACLs
| | [Documentation]
| | ... | Configure MACIP ACL with required number of not-hitting permit ACEs
| | ... | plus two hitting ACEs for both traffic directions.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - dut_if1 - DUT node interface1 name (Optional). Type: string
| | ... | - dut_if2 - DUT node interface2 name (Optional). Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure MACIP ACLs \| ${nodes['DUT1']} \| GigabitEthernet0/7/0 \
| | ... | \| GigabitEthernet0/8/0 \|
| | ...
| | ... | _NOTE:_ This KW uses following test case variables:
| | ... | - src_ip_start - Source IP address start. Type: string
| | ... | - ip_step - IP address step. Type: string
| | ... | - src_mac_start - Source MAC address start in format with colons.
| | ... | Type: string
| | ... | - src_mac_step - Source MAC address step. Type: string
| | ... | - src_mac_mask - Source MAC address mask. 00:00:00:00:00:00 is a
| | ... | wildcard mask. Type: string
| | ... | - no_hit_aces_number - Number of not-hitting ACEs to be configured.
| | ... | Type: integer
| | ... | - acl_action - Action for the rule - deny, permit, permit+reflect.
| | ... | Type: string
| | ... | - tg_stream1_subnet - IP subnet used by TG in direction 0->1.
| | ... | Type: string
| | ... | - tg_stream2_subnet - IP subnet used by TG in direction 1->0.
| | ... | Type: string
| | ... | - tg_stream1_mac - Source MAC address of traffic stream 1.
| | ... | Type: string
| | ... | - tg_stream2_mac - Source MAC address of traffic stream 2.
| | ... | Type: string
| | ... | - tg_mac_mask - MAC address mask for traffic streams.
| | ... | 00:00:00:00:00:00 is a wildcard mask. Type: string
| | ...
| | [Arguments] | ${dut} | ${dut_if1}=${NONE} | ${dut_if2}=${NONE}
| | ...
| | ${src_ip_int} = | IP To Int | ${src_ip_start}
| | ${src_ip_int} = | Evaluate | ${src_ip_int} - ${ip_step}
| | ...
| | ${ip_limit} = | Set Variable | 255.255.255.255
| | ${ip_limit_int} = | IP To Int | ${ip_limit}
| | ...
| | ${src_mac_int} = | Mac To Int | ${src_mac_start}
| | ${src_mac_int} = | Evaluate | ${src_mac_int} - ${src_mac_step}
| | ...
| | ${mac_limit} = | Set Variable | ff:ff:ff:ff:ff:ff
| | ${mac_limit_int} = | Mac To Int | ${mac_limit}
| | ...
| | ${acl}= | Set Variable | ipv4 permit
| | :FOR | ${nr} | IN RANGE | 0 | ${no_hit_aces_number}
| | | ${src_ip_int} = | Evaluate | ${src_ip_int} + ${ip_step}
| | | ${src_mac_int} = | Evaluate | ${src_mac_int} + ${src_mac_step}
| | | ${ipv4_limit_reached}= | Set Variable If
| | | ... | ${src_ip_int} > ${ip_limit_int} | ${TRUE}
| | | ${mac_limit_reached}= | Set Variable If
| | | ... | ${src_mac_int} > ${mac_limit_int} | ${TRUE}
| | | Run Keyword If | '${ipv4_limit_reached}' == '${TRUE}' | Log
| | | ... | Can't do more iterations - IPv4 address limit has been reached.
| | | ... | WARN
| | | Run Keyword If | '${mac_limit_reached}' == '${TRUE}' | Log
| | | ... | Can't do more iterations - MAC address limit has been reached.
| | | ... | WARN
| | | ${src_ip} = | Run Keyword If | '${ipv4_limit_reached}' == '${TRUE}'
| | | ... | Set Variable | ${ip_limit}
| | | ... | ELSE | Int To IP | ${src_ip_int}
| | | ${src_mac}= | Run Keyword If | '${mac_limit_reached}' == '${TRUE}'
| | | ... | Set Variable | ${mac_limit}
| | | ... | ELSE | Int To Mac | ${src_mac_int}
| | | ${acl}= | Catenate | ${acl} | ip ${src_ip}/32
| | | ... | mac ${src_mac} | mask ${src_mac_mask},
| | | Exit For Loop If | '${ipv4_limit_reached}' == '${TRUE}' or '${mac_limit_reached}' == '${TRUE}'
| | ${acl0}= | Catenate | ${acl}
| | ... | ipv4 ${acl_action} ip ${tg_stream1_subnet} mac ${tg_stream1_mac}
| | ... | mask ${tg_mac_mask}
| | ${acl1}= | Catenate | ${acl}
| | ... | ipv4 ${acl_action} ip ${tg_stream2_subnet} mac ${tg_stream2_mac}
| | ... | mask ${tg_mac_mask}
| | Add Macip Acl Multi Entries | ${dut} | rules=${acl0}
| | Add Macip Acl Multi Entries | ${dut} | rules=${acl1}
| | ${acl_idx}= | Set Variable | 0
| | Run Keyword Unless | '${dut_if1}' == '${NONE}'
| | ... | Add Del Macip Acl Interface | ${dut} | ${dut_if1} | add | ${acl_idx}
| | ${acl_idx}= | Set Variable | 1
| | Run Keyword Unless | '${dut_if2}' == '${NONE}'
| | ... | Add Del Macip Acl Interface | ${dut} | ${dut_if2} | add | ${acl_idx}

| Initialize LISP IPv4 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 addresses on all DUT nodes and TG \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_dut2_address - Ip address from DUT1 to DUT2. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_address - Ip address from DUT2 to DUT1. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - duts_prefix - ip prefix. Type: int
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Initialize LISP IPv4 forwarding in 3-node circular topology \
| | ... | \| ${dut1_dut2_address} \| ${dut1_tg_address} \
| | ... | \| ${dut2_dut1_address} \| ${dut2_tg_address} \| ${duts_prefix} \|
| | ...
| | [Arguments] | ${dut1_dut2_address} | ${dut1_tg_address}
| | ... | ${dut2_dut1_address} | ${dut2_tg_address} | ${duts_prefix}
| | ...
| | Set interfaces in path up
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_address} | ${dut1_if2_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 20.20.20.2 | ${tg_if2_mac}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1}
| | ... | ${dut1_tg_address} | ${duts_prefix}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if2}
| | ... | ${dut1_dut2_address} | ${duts_prefix}
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if1}
| | ... | ${dut2_dut1_address} | ${duts_prefix}
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if2}
| | ... | ${dut2_tg_address} | ${duts_prefix}

| Initialize LISP GPE IPv4 over IPsec in 3-node circular topology
| | [Documentation] | Setup Lisp GPE IPv4 forwarding over IPsec.
| | ...
| | ... | *Arguments:*
| | ... | - encr_alg - Encryption algorithm. Type: string
| | ... | - auth_alg - Authentication algorithm. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Initialize LISP GPE IPv4 over IPsec in 3-node circular topology\
| | ... | \| ${encr_alg} \| ${auth_alg}
| | ...
| | [Arguments] | ${encr_alg} | ${auth_alg}
| | ...
| | Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | Initialize LISP IPv4 forwarding in 3-node circular topology
| | ... | ${dut1_to_dut2_ip4} | ${dut1_to_tg_ip4} | ${dut2_to_dut1_ip4}
| | ... | ${dut2_to_tg_ip4} | ${prefix4}
| | Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${dut2} | ${dut2_if1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_ip4_static_adjacency} | ${dut2_ip4_static_adjacency}
| | Configure manual keyed connection for IPSec
| | ... | ${dut1} | ${dut1_if2} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip4} | ${dut2_to_dut1_ip4}
| | Configure manual keyed connection for IPSec
| | ... | ${dut2} | ${dut2_if1} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi}
| | ... | ${dut2_to_dut1_ip4} | ${dut1_to_dut2_ip4}

| Initialize LISP IPv6 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_dut2_address - Ip address from DUT1 to DUT2. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_address - Ip address from DUT2 to DUT1. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - duts_prefix - ip prefix. Type: int
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Initialize LISP IPv6 forwarding in 3-node circular topology \
| | ... | \| ${dut1_dut2_address} \| ${dut1_tg_address} \
| | ... | \| ${dut2_dut1_address} \| ${dut2_tg_address} \| ${duts_prefix} \|
| | ...
| | [Arguments] | ${dut1_dut2_address} | ${dut1_tg_address}
| | ... | ${dut2_dut1_address} | ${dut2_tg_address} | ${prefix}
| | ...
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_tg_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_tg_address} | ${prefix}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_address} | ${dut1_if2_mac}

| Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 over IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_dut2_ip6_address - IPv6 address from DUT1 to DUT2.
| | ... | Type: string
| | ... | - dut1_tg_ip4_address - IPv4 address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_ip6_address - IPv6 address from DUT2 to DUT1.
| | ... | Type: string
| | ... | - dut1_tg_ip4_address - IPv4 address from DUT1 to tg. Type: string
| | ... | - prefix4 - IPv4 prefix. Type: int
| | ... | - prefix6 - IPv6 prefix. Type: int
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular \
| | ... | topology \| ${dut1_dut2_ip6_address} \| ${dut1_tg_ip4_address} \
| | ... | \| ${dut2_dut1_ip6_address} \| ${dut2_tg_ip4_address} \
| | ... | \| ${prefix4} \| ${prefix6} \|
| | ...
| | [Arguments] | ${dut1_dut2_ip6_address} | ${dut1_tg_ip4_address}
| | ... | ${dut2_dut1_ip6_address} | ${dut2_tg_ip4_address}
| | ... | ${prefix4} | ${prefix6}
| | ...
| | Set interfaces in path up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1}
| | ... | ${dut1_tg_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if2}
| | ... | ${dut2_tg_ip4_address} | ${prefix4}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 20.20.20.2 | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip6_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip6_address} | ${dut1_if2_mac}

| Initialize LISP IPv6 over IPv4 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 over IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_dut2_ip4_address - IPv4 address from DUT1 to DUT2.
| | ... | Type: string
| | ... | - dut1_tg_ip6_address - IPv6 address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_ip4_address - IPv4 address from DUT2 to DUT1.
| | ... | Type: string
| | ... | - dut1_tg_ip6_address - IPv6 address from DUT1 to tg. Type: string
| | ... | - prefix4 - IPv4 prefix. Type: int
| | ... | - prefix6 - IPv6 prefix. Type: int
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular \
| | ... | topology \| ${dut1_dut2_ip4_address} \| ${dut1_tg_ip6_address} \
| | ... | \| ${dut2_dut1_ip4_address} \| ${dut2_tg_ip6_address} \
| | ... | \| ${prefix6} \| ${prefix4} \|
| | ...
| | [Arguments] | ${dut1_dut2_ip4_address} | ${dut1_tg_ip6_address}
| | ... | ${dut2_dut1_ip4_address} | ${dut2_tg_ip6_address}
| | ... | ${prefix6} | ${prefix4}
| | ...
| | Set interfaces in path up
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_tg_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_tg_ip6_address} | ${prefix6}
| | Vpp All Ra Suppress Link Layer | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip4_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip4_address} | ${dut1_if2_mac}

| Initialize NAT44 in circular topology
| | [Documentation] | Initialization of 2-node / 3-node topology with NAT44
| | ... | between DUTs:
| | ... | - set interfaces up
| | ... | - set IP addresses
| | ... | - set ARP
| | ... | - create routes
| | ... | - set NAT44 - only on DUT1
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ...
| | Set interfaces in path up
| | ...
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 10.0.0.1 | 20
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut1} | ${dut1_if2}
| | ... | 11.0.0.1 | 20
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut2} | ${dut2_if1}
| | ... | 11.0.0.2 | 20
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | VPP Interface Set IP Address | ${dut} | ${dut_if2} | 12.0.0.1 | 20
| | ...
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.0.0.2 | ${tg_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | 11.0.0.2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | 11.0.0.1 | ${dut1_if2_mac}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 12.0.0.2 | ${tg_if2_mac}
| | ...
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 18 | gateway=10.0.0.2
| | ... | interface=${dut1_if1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 12.0.0.2 | 32 | gateway=11.0.0.2
| | ... | interface=${dut1_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 12.0.0.0 | 24 | gateway=12.0.0.2
| | ... | interface=${dut2_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 200.0.0.0 | 30 | gateway=11.0.0.1
| | ... | interface=${dut2_if1}
| | ...
| | Configure inside and outside interfaces
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure deterministic mode for NAT44
| | ... | ${dut1} | 20.0.0.0 | 18 | 200.0.0.0 | 30

| Configure ACLs on a single interface
| | [Documentation]
| | ... | Configure ACL
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - dut_if - DUT node interface name. Type: string
| | ... | - acl_apply_type - To what path apply the ACL - input or output.
| | ... | - acl_action - Action for the rule - deny, permit, permit+reflect.
| | ... | - subnets - Subnets to apply the specific ACL. Type: list
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure ACLs on a single interface \| ${nodes['DUT1']}
| | ... | \| ... \| GigabitEthernet0/7/0 \| input \| permit | 0.0.0.0/0
| | ...
| | [Arguments] | ${dut} | ${dut_if} | ${acl_apply_type} | ${acl_action}
| | ... | @{subnets}
| | Set Test variable | ${acl} | ${EMPTY}
| | :FOR | ${subnet} | IN | @{subnets}
| | | ${acl} = | Run Keyword If | '${acl}' == '${EMPTY}'
| | | ... | Set Variable | ipv4 ${acl_action} src ${subnet}
| | | ... | ELSE
| | | ... | Catenate | SEPARATOR=", " | ${acl}
| | | ... | ipv4 ${acl_action} src ${subnet}
| | Add Replace Acl Multi Entries | ${dut} | rules=${acl}
| | @{acl_list} = | Create List | ${0}
| | Set Acl List For Interface | ${dut} | ${dut_if} | ${acl_apply_type}
| | ... | ${acl_list}
