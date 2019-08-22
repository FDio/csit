# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.SRv6
| Documentation | Keywords for SRv6 feature in VPP.

*** Keywords ***
| Configure SR LocalSID on DUT
| | [Documentation] | Create SRv6 LocalSID and binds it to a particular\
| | ... | behavior on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to create localSID on. Type: dictionary
| | ... | - local_sid - LocalSID IPv6 address. Type: string
| | ... | - behavior - SRv6 LocalSID function. Type: string
| | ... | - interface - Interface name (Optional, default value: None; required
| | ... | for L2/L3 xconnects). Type: string
| | ... | - next_hop - Next hop IPv4/IPv6 address (Optional, default value:
| | ... | None; required for L3 xconnects). Type: string
| | ... | - fib_table - FIB table for IPv4/IPv6 lookup (Optional, default value:
| | ... | None; required for L3 routing). Type: string
| | ... | - out_if - Interface name of local interface for sending traffic
| | ... | towards the Service Function (Optional, default value: None;
| | ... | required for SRv6 endpoint to SR-unaware appliance). Type: string
| | ... | - in_if - Interface name of local interface receiving the traffic
| | ... | coming back from the Service Function (Optional, default value:
| | ... | None; required for SRv6 endpoint to SR-unaware appliance).
| | ... | Type: string
| | ... | - src_addr - Source address on the packets coming back on in_if
| | ... | interface (Optional, default value: None; required for SRv6 endpoint
| | ... | to SR-unaware appliance via static proxy). Type: string
| | ... | - sid_list - SID list (Optional, default value: []; required for SRv6
| | ... | endpoint to SR-unaware appliance via static proxy). Type: list
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure SR LocalSID on DUT \| ${nodes['DUT1']} \| B:: \| end \|
| | ... | \| Configure SR LocalSID on DUT \| ${nodes['DUT1']} \| C:: \
| | ... | \| end.dx2 \| interface=GigabitEthernet0/10/0 \|
| | ... | \| Configure SR LocalSID on DUT \| ${nodes['DUT1']} \| D:: \
| | ... | \| end.dx4 \| interface=GigabitEthernet0/8/0 \| next_hop=10.0.0.1 \|
| | ... | \| Configure SR LocalSID on DUT \| ${nodes['DUT2']} \| E:: \
| | ... | \| end.dt6 \| fib_table=2 \|
| | ... | \| Configure SR LocalSID on DUT \| ${nodes['DUT2']} \| E:: \
| | ... | \| end.ad \| next_hop=10.0.0.1 \| out_if=DUT2_VHOST1 \
| | ... | \| in_if=DUT2_VHOST2 \|
| | ... | \| Configure SR LocalSID on DUT \| ${nodes['DUT2']} \| E:: \
| | ... | \| end.as \| next_hop=10.0.0.1 \| out_if=DUT2_VHOST1 \
| | ... | \| in_if=DUT2_VHOST2 \| src_addr=B:: \| sid_list=['C::', 'D::'] \|
| | ...
| | [Arguments] | ${dut_node} | ${local_sid} | ${behavior}
| | ... | ${interface}=${None} | ${next_hop}=${None} | ${fib_table}=${None}
| | ... | ${out_if}=${None} | ${in_if}=${None} | ${src_addr}=${None}
| | ... | @{sid_list}
| | ...
| | Configure SR LocalSID | ${dut_node} | ${local_sid} | ${behavior}
| | ... | interface=${interface} | next_hop=${next_hop} | fib_table=${fib_table}
| | ... | out_if=${out_if} | in_if=${in_if} | src_addr=${src_addr}
| | ... | sid_list=${sid_list}

| Show SR LocalSIDs on DUT
| | [Documentation] | Show SRv6 LocalSIDs on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to show SR localSIDs on. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Show SR LocalSIDs on DUT \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ...
| | Show SR LocalSIDs | ${dut_node}

| Configure SR Policy on DUT
| | [Documentation] | Create SRv6 policy on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to create SRv6 policy on. Type: dictionary
| | ... | - bsid - BindingSID - local SID IPv6 address. Type: string
| | ... | - mode - Encapsulation / insertion mode. Type: string
| | ... | - sid_list - SID list. Type: list
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure SR Policy on DUT \| ${nodes['DUT2']} \| A:: \| encap \
| | ... | \| B::\| C:: \|
| | ... | \| Configure SR Policy on DUT \| ${nodes['DUT2']} \| D:: \| insert \
| | ... | \| E::\| F:: \|
| | ...
| | [Arguments] | ${dut_node} | ${bsid} | ${mode} | @{sid_list}
| | ...
| | Configure SR Policy | ${dut_node} | ${bsid} | ${sid_list} | mode=${mode}

| Show SR Policies on DUT
| | [Documentation] | Show SRv6 policies on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to show SR policies on. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Show SR Policies on DUT \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ...
| | Show SR Policies | ${dut_node}

| Configure SR Steer on DUT
| | [Documentation] | Create SRv6 steering policy on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to create SR steering policy on.
| | ... | Type: dictionary
| | ... | - mode - Mode of operation - L2 or L3. Type: string
| | ... | - bsid - BindingSID - local SID IPv6 address. Type: string
| | ... | - interface - Interface name (Optional, default value: None; required
| | ... | in case of L2 mode). Type: string
| | ... | - ip_addr - IPv4/IPv6 address (Optional, default value: None; required
| | ... | in case of L3 mode). Type: string
| | ... | - prefix - IP address prefix (Optional, default value: None; required
| | ... | for L3 mode). Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure SR Steer on DUT \| ${nodes['DUT1']} \| L2 \| B:: \
| | ... | \| interface=GigabitEthernet0/10/0 \|
| | ... | \| Configure SR Steer on DUT \| ${nodes['DUT1']} \| L3 \| C:: \
| | ... | \| ip_address=2001::1 \| prefix=64 \|
| | ...
| | [Arguments] | ${dut_node} | ${mode} | ${bsid}
| | ... | ${interface}=${None} | ${ip_addr}=${None} | ${prefix}=${None}
| | ...
| | Configure SR Steer | ${dut_node} | ${mode} | ${bsid}
| | ... | interface=${interface} | ip_addr=${ip_addr} | prefix=${prefix}

| Show SR Steering Policies on DUT
| | [Documentation] | Show SRv6 steering policies on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to show SR steering policies on.
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Show SR Steering Policies on DUT \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${dut_node}
| | ...
| | Show SR Steering Policies | ${dut_node}

| Set SR Encaps Source Address on DUT
| | [Documentation] | Set SRv6 encapsulation source address on the given DUT
| | ... | node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to set SRv6 encapsulation source address
| | ... | on. Type: dictionary
| | ... | - ip6_addr - Local SID IPv6 address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set SR Encaps Source Address on DUT \| ${nodes['DUT1']} \| B:: \|
| | ...
| | [Arguments] | ${dut_node} | ${ip6_addr}
| | ...
| | Set SR Encaps Source Address | ${dut_node} | ip6_addr=${ip6_addr}

| Show SR Policies on all DUTs
| | [Documentation] | Show SRv6 policies on all DUT nodes in topology.
| | ...
| | ... | *Arguments:*
| | ... | - nodes - Topology. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Show SR Policies on all DUTs \| ${nodes} \|
| | ...
| | [Arguments] | ${nodes}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Show SR Policies | ${nodes['${dut}']}

| Show SR Steering Policies on all DUTs
| | [Documentation] | Show SRv6 steering policies on all DUT nodes in topology.
| | ...
| | ... | *Arguments:*
| | ... | - nodes - Topology. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Show SR Steering Policies on all DUTs \| ${nodes} \|
| | ...
| | [Arguments] | ${nodes}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Show SR Steering Policies | ${nodes['${dut}']}

| Show SR LocalSIDs on all DUTs
| | [Documentation] | Show SRv6 LocalSIDs on all DUT nodes in topology.
| | ...
| | ... | *Arguments:*
| | ... | - nodes - Topology. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Show SR LocalSIDs on all DUTs \| ${nodes} \|
| | ...
| | [Arguments] | ${nodes}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Show SR LocalSIDs | ${nodes['${dut}']}

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
