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

| Delete SR LocalSID on DUT
| | [Documentation] | Delete SRv6 LocalSID on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to delete localSID on. Type: dictionary
| | ... | - local_sid - LocalSID IPv6 address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Delete SR LocalSID on DUT \| ${nodes['DUT1']} \| B:: \|
| | ...
| | [Arguments] | ${dut_node} | ${local_sid}
| | ...
| | Delete SR LocalSID | ${dut_node} | ${local_sid}

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

| Delete SR Policy on DUT
| | [Documentation] | Delete SRv6 policy on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to delete SRv6 policy on. Type: dictionary
| | ... | - bsid - BindingSID - local SID IPv6 address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Delete SR Policy on DUT \| ${nodes['DUT1']} \| A:: \|
| | ...
| | [Arguments] | ${dut_node} | ${bsid}
| | ...
| | Delete SR Policy | ${dut_node} | ${bsid}

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

| Delete SR Steer on DUT
| | [Documentation] | Delete SRv6 steering policy on the given DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node where to delete SR steering policy on.
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
| | ... | \| Delete SR Steer on DUT \| ${nodes['DUT1']} \| L2 \| B:: \
| | ... | \| interface=GigabitEthernet0/10/0 \|
| | ... | \| Delete SR Steer on DUT \| ${nodes['DUT1']} \| L3 \| C:: \
| | ... | \| ip_address=2001::1 \| prefix=64 \|
| | ...
| | [Arguments] | ${dut_node} | ${mode} | ${bsid}
| | ... | ${interface}=${None} | ${ip_addr}=${None} | ${prefix}=${None}
| | ...
| | Delete SR Steer | ${dut_node} | ${mode} | ${bsid}
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
