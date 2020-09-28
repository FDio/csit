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
| Library | resources.libraries.python.NATUtil
|
| Documentation | Keywords for NAT feature in VPP.

*** Keywords ***
| Configure inside and outside interfaces
| | [Documentation] | Configure inside and outside interfaces for NAT44.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node to set NAT44 interfaces on. Type: dictionary
| | ... | - int_in - Inside interface. Type: string
| | ... | - int_out - Outside interface. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Configure inside and outside interfaces \| ${nodes['DUT1']} \
| | ... | \| FortyGigabitEtherneta/0/0 \| FortyGigabitEtherneta/0/1 \|
| |
| | [Arguments] | ${node} | ${int_in} | ${int_out}
| |
| | ${int_in_name}= | Set variable | ${node['interfaces']['${int_in}']['name']}
| | ${int_out_name}= | Set variable
| | ... | ${node['interfaces']['${int_out}']['name']}
| | Set NAT44 Interfaces | ${node} | ${int_in_name} | ${int_out_name}

| Initialize NAT44 endpoint-dependent mode in circular topology
| | [Documentation] | Initialization of NAT44 endpoint-dependent mode on DUT1
| |
| | ... | This keyword also sets a test variable \${resetter}
| | ... | to hold a callable which resets VPP state.
| | ... | Keywords performing search will call it to get consistent trials.
| | ... | Unless \${do_not_reset_nat} variable is true (disables the reset).
| |
| | Configure inside and outside interfaces
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${DUT1_${int}2}[0]
| | ${resetter} = | Set NAT44 Address Range
| | ... | ${dut1} | ${out_net} | ${out_net_end}
| | ${return} = | Get Variable Value | \${do_not_reset_nat} | ${False}
| | Return From Keyword If | ${return}
| | Set Test Variable | \${resetter}

# TODO: Remove when 'ip4.Initialize IPv4 forwarding in circular topology' KW
# adapted to use IP values from variables
| Initialize IPv4 forwarding for NAT44 in circular topology
| | [Documentation]
| | ... | Set IPv4 forwarding for NAT44:
| | ... | - set interfaces up
| | ... | - set IP addresses
| | ... | - set ARP
| | ... | - create routes
| |
| | ${status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut2_status}= | Set Variable If | '${status}' == 'PASS' | ${True}
| | ... | ${False}
| |
| | Set interfaces in path up
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${dut1_if1_ip4} | ${dut1_if1_mask}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut1_if2_ip4} | ${dut1_if2_mask}
| | Run Keyword If | ${dut2_status}
| | ... | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut2_if1_ip4} | ${dut2_if1_mask}
| | Run Keyword If | ${dut2_status}
| | ... | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${dut2_if2_ip4} | ${dut2_if2_mask}
| |
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${tg_if1_ip4} | ${TG_pf1_mac}[0]
| | Run Keyword If |  ${dut2_status}
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${dut2_if1_ip4}
| | ... | ${DUT2_${int}1_mac}[0]
| | ... | ELSE | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${tg_if2_ip4} | ${TG_pf2_mac}[0]
| | Run Keyword If |  ${dut2_status}
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${dut1_if1_ip4}
| | ... | ${DUT1_${int}2_mac}[0]
| | Run Keyword If |  ${dut2_status}
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${tg_if2_ip4}| ${TG_pf2_mac}[0]
| |
| | Vpp Route Add
| | ... | ${dut1} | ${in_net} | ${in_mask} | gateway=${tg_if1_ip4}
| | ... | interface=${DUT1_${int}1}[0]
| | Run Keyword If | ${dut2_status}
| | ... | Vpp Route Add
| | ... | ${dut1} | ${dest_net} | ${dest_mask} | gateway=${dut2_if1_ip4}
| | ... | interface=${DUT1_${int}2}[0]
| | ... | ELSE | Vpp Route Add
| | ... | ${dut1} | ${dest_net} | ${dest_mask} | gateway=${tg_if2_ip4}
| | ... | interface=${DUT1_${int}2}[0]
| | Run Keyword If | ${dut2_status}
| | ... | Vpp Route Add
| | ... | ${dut2} | ${dest_net} | ${dest_mask} | gateway=${tg_if2_ip4}
| | ... | interface=${DUT2_${int}2}[0]
| | Run Keyword If | ${dut2_status}
| | ... | Vpp Route Add
| | ... | ${dut2} | ${out_net} | ${out_mask} | gateway=${dut1_if2_ip4}
| | ... | interface=${DUT2_${int}1}[0]

# DET44 - NAT44 deterministic
| Enable DET44 plugin on DUT
| | [Documentation] | Enable DET44 plugin on DUT.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node to enablr DET44 on.
| | ... | Type: dictionary
| | ... | - inside_vrf - Inside VRF ID; default value: 0.
| | ... | Type: string or integer
| | ... | - outside_vrf - Outside VRF ID; default value: 0.
| | ... | Type: string or integer
| |
| | ... | *Example:*
| |
| | ... | \| Enable DET44 plugin on all DUTs \|
| |
| | [Arguments] | ${node} | ${inside_vrf}=${0} | ${outside_vrf}=${0}
| |
| | Enable DET44 Plugin
| | ... | ${node} | inside_vrf=${inside_vrf} | outside_vrf=${outside_vrf}

| Configure DET44 interfaces
| | [Documentation] | Configure inside and outside interfaces for DET44.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node to set DET44 interfaces on. Type: dictionary
| | ... | - int_in - Inside interface key. Type: string
| | ... | - int_out - Outside interface key. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Configure DET44 interfaces \| ${nodes['DUT1']} \| port5 \| port6 \|
| |
| | [Arguments] | ${node} | ${int_in} | ${int_out}
| |
| | Set DET44 Interface | ${dut1} | ${int_in} | is_inside=${True}
| | Set DET44 Interface | ${dut1} | ${int_out} | is_inside=${False}

| Configure deterministic mode for NAT44
| | [Documentation] | Set deterministic behaviour of NAT44 (DET44).
| |
| | ... | This keyword also sets a test variable \${resetter}
| | ... | to hold a callable which resets VPP state.
| | ... | Keywords performing search will call it to get consistent trials.
| | ... | Unless \${do_not_reset_nat} variable is true (disables the reset).
| |
| | ... | *Arguments:*
| | ... | - node - DUT node to set deterministic mode for NAT44 on.
| | ... | Type: dictionary
| | ... | - ip_in - Inside IP. Type: string
| | ... | - subnet_in - Inside IP subnet. Type: string
| | ... | - ip_out - Outside IP. Type: string
| | ... | - subnet_out - Outside IP subnet. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Configure deterministic mode for NAT44 \| ${nodes['DUT1']} \
| | ... | \| 100.0.0.0 \| 12 \| 12.1.1.0 \| 24 \|
| |
| | [Arguments] | ${node} | ${ip_in} | ${subnet_in} | ${ip_out} | ${subnet_out}
| |
| | ${resetter} = | Set DET44 Mapping
| | ... | ${node} | ${ip_in} | ${subnet_in} | ${ip_out} | ${subnet_out}
| | ${return} = | Get Variable Value | \${do_not_reset_nat} | ${False}
| | Return From Keyword If | ${return}
| | Set Test Variable | \${resetter}

| Initialize NAT44 deterministic mode in circular topology
| | [Documentation] | Initialization of NAT44 deterministic mode (DET44)
| | ... | on DUT1.
| |
| | Enable DET44 plugin on DUT | ${dut1}
| | Configure DET44 interfaces
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${DUT1_${int}2}[0]
| | Configure deterministic mode for NAT44
| | ... | ${dut1} | ${in_net} | ${in_mask} | ${out_net} | ${out_mask}

| Show DET44 verbose
| | [Documentation] | Get DET44 settings on the node.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node to show NAT. Type: dictionary
| |
| | ... | *Example:*
| |
| | ... | \| Show DET44 verbose \| ${nodes['DUT1']} \|
| |
| | [Arguments] | ${node}
| |
| | Show DET44 | ${node}

| Verify DET44 sessions number
| | [Documentation] | Verify that all required DET44 sessions are established.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node. Type: dictionary
| | ... | - exp_n_sessions - Expected number of DET44 sessions. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Verify DET44 sessions number \| ${nodes['DUT1']} \| ${64512} \|
| |
| | [Arguments] | ${node} | ${exp_n_sessions}
| |
| | ${det44_sessions}= | Get DET44 Sessions Number | ${node}
| | Should Be Equal As Integers | ${det44_sessions} | ${exp_n_sessions}
| | ... | Not all DET44 sessions have been established
