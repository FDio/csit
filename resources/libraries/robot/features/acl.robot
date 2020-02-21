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
| Documentation | ACL keywords.

*** Keywords ***
| Configure MACIP ACLs
| | [Documentation]
| | ... | Configure MACIP ACL with required number of not-hitting permit ACEs
| | ... | plus two hitting ACEs for both traffic directions.
| |
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - dut_if1 - DUT node interface1 name (Optional). Type: string
| | ... | - dut_if2 - DUT node interface2 name (Optional). Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Configure MACIP ACLs \| ${nodes['DUT1']} \| GigabitEthernet0/7/0 \
| | ... | \| GigabitEthernet0/8/0 \|
| |
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
| |
| | [Arguments] | ${dut} | ${dut_if1}=${NONE} | ${dut_if2}=${NONE}
| |
| | ${src_ip_int} = | IP To Int | ${src_ip_start}
| | ${src_ip_int} = | Evaluate | ${src_ip_int} - ${ip_step}
| |
| | ${ip_limit} = | Set Variable | 255.255.255.255
| | ${ip_limit_int} = | IP To Int | ${ip_limit}
| |
| | ${src_mac_int} = | Mac To Int | ${src_mac_start}
| | ${src_mac_int} = | Evaluate | ${src_mac_int} - ${src_mac_step}
| |
| | ${mac_limit} = | Set Variable | ff:ff:ff:ff:ff:ff
| | ${mac_limit_int} = | Mac To Int | ${mac_limit}
| |
| | ${acl}= | Set Variable | ipv4 permit
| | FOR | ${nr} | IN RANGE | 0 | ${no_hit_aces_number}
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
| | END
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

| Configure IPv4 ACLs
| | [Documentation]
| | ... | Configure ACL with required number of not-hitting permit ACEs plus two
| | ... | hitting ACEs for both traffic directions.
| |
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - dut_if1 - DUT node interface1 name (Optional). Type: string
| | ... | - dut_if2 - DUT node interface2 name (Optional). Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Configure IPv4 ACLs \| ${nodes['DUT1']} \| GigabitEthernet0/7/0 \
| | ... | \| GigabitEthernet0/8/0 \|
| |
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
| |
| | [Arguments] | ${dut} | ${dut_if1}=${NONE} | ${dut_if2}=${NONE}
| | ${src_ip_int} = | Evaluate
| | ... | int(ipaddress.ip_address($src_ip_start)) - $ip_step
| | ... | modules=ipaddress
| | ${dst_ip_int} = | Evaluate
| | ... | int(ipaddress.ip_address($dst_ip_start)) - $ip_step
| | ... | modules=ipaddress
| | ${ip_limit} = | Set Variable | 255.255.255.255
| | ${ip_limit_int} = | Evaluate
| | ... | int(ipaddress.ip_address($ip_limit)) | modules=ipaddress
| | ${sport}= | Evaluate | $sport_start - $port_step
| | ${dport}= | Evaluate | $dport_start - $port_step
| | ${port_limit}= | Set Variable | ${65535}
| | ${acl}= | Set Variable | ipv4 permit
| | FOR | ${nr} | IN RANGE | 0 | ${no_hit_aces_number}
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
| | END
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

| Configure ACLs on a single interface
| | [Documentation]
| | ... | Configure ACL
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - dut_if - DUT node interface name. Type: string
| | ... | - acl_apply_type - To what path apply the ACL - input or output.
| | ... | - acl_action - Action for the rule - deny, permit, permit+reflect.
| | ... | - subnets - Subnets to apply the specific ACL. Type: list
| |
| | ... | *Example:*
| |
| | ... | \| Configure ACLs on a single interface \| ${nodes['DUT1']}
| | ... | \| ... \| GigabitEthernet0/7/0 \| input \| permit | 0.0.0.0/0
| |
| | [Arguments] | ${dut} | ${dut_if} | ${acl_apply_type} | ${acl_action}
| | ... | @{subnets}
| | Set Test variable | ${acl} | ${EMPTY}
| | FOR | ${subnet} | IN | @{subnets}
| | | ${acl} = | Run Keyword If | '${acl}' == '${EMPTY}'
| | | ... | Set Variable | ipv4 ${acl_action} src ${subnet}
| | | ... | ELSE
| | | ... | Catenate | SEPARATOR=", " | ${acl}
| | | ... | ipv4 ${acl_action} src ${subnet}
| | END
| | Add Replace Acl Multi Entries | ${dut} | rules=${acl}
| | @{acl_list} = | Create List | ${0}
| | Set Acl List For Interface | ${dut} | ${dut_if} | ${acl_apply_type}
| | ... | ${acl_list}

| Initialize IPv4 routing with IPv4 ACLs on DUT1 in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| | ... | Apply required ACL rules to DUT1 interfaces.
| |
| | ... | *Arguments:*
| | ... | - ip_nr - Number of IPs to be used. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv4 routing fwith IPv4 ACLs on DUT1 \
| | ... | in 3-node circular topology \|
| |
| | [Arguments] | ${ip_nr}=${1}
| |
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}2}[0]
| | ... | ELSE | Set Variable | ${DUT1_${int}2}[0]
| |
| | Set interfaces in path up
| |
| | FOR | ${number} | IN RANGE | 2 | ${ip_nr}+2
| | | VPP Add IP Neighbor
| | | ... | ${dut1} | ${dut1_${int}1}[0] | 10.10.10.${number} | ${TG_pf1_mac}[0]
| | | VPP Add IP Neighbor
| | | ... | ${dut} | ${dut_if2} | 20.20.20.${number} | ${TG_pf2_mac}[0]
| | END
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 1.1.1.2 | ${DUT2_${int}1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 1.1.1.1 | ${DUT1_${int}2_mac}[0]
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 10.10.10.1 | 24
| | VPP Interface Set IP Address
| | ... | ${dut} | ${dut_if2} | 20.20.20.1 | 24
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 1.1.1.1 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 1.1.1.2 | 30
| |
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | gateway=1.1.1.2
| | ... | interface=${DUT1_${int}2}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | gateway=1.1.1.1
| | ... | interface=${DUT2_${int}1}[0]
| |
| | Configure IPv4 ACLs
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${DUT1_${int}2}[0]
