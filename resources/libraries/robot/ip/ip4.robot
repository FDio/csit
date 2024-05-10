# Copyright (c) 2023 Cisco and/or its affiliates.
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
| Documentation | IPv4 keywords

*** Keywords ***
| Initialize IPv4 forwarding in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| |
| | ... | *Arguments:*
| | ... | - remote_host1_ip - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip - IP address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_mask - Mask of remote host IP addresses (Optional).
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv4 forwarding in circular topology \
| | ... | \| 192.168.0.1 \| 192.168.0.2 \| 24 \|
| |
| | [Arguments] | ${remote_host1_ip}=${NONE} | ${remote_host2_ip}=${NONE}
| | ... | ${remote_host_mask}=32
| |
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| |
| | Set interfaces in path up
| |
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 10.10.10.2 | ${TG_pf1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 1.1.1.2 | ${DUT2_${int}1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 1.1.1.1 | ${DUT1_${int}2_mac}[0]
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}2}[0]
| | ... | ELSE | Set Variable | ${DUT1_${int}2}[0]
| | VPP Add IP Neighbor
| | ... | ${dut} | ${dut_if2} | 20.20.20.2 | ${TG_pf2_mac}[0]
| |
| | VPP Interface Set IP Address | ${dut1} | ${DUT1_${int}1}[0]
| | ... | 10.10.10.1 | 24
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut1} | ${DUT1_${int}2}[0]
| | ... | 1.1.1.1 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut2} | ${DUT2_${int}1}[0]
| | ... | 1.1.1.2 | 30
| | VPP Interface Set IP Address | ${dut} | ${dut_if2}
| | ... | 20.20.20.1 | 24
| |
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | gateway=1.1.1.2
| | ... | interface=${DUT1_${int}2}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | gateway=1.1.1.1
| | ... | interface=${DUT2_${int}1}[0]
| |
| | Run Keyword If | '${remote_host1_ip}' != '${NONE}'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip} | ${remote_host_mask}
| | ... | gateway=10.10.10.2 | interface=${DUT1_${int}1}[0]
| | Run Keyword If | '${remote_host2_ip}' != '${NONE}'
| | ... | Vpp Route Add | ${dut} | ${remote_host2_ip} | ${remote_host_mask}
| | ... | gateway=20.20.20.2 | interface=${dut_if2}
| | Run Keyword If | '${remote_host1_ip}' != '${NONE}'
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip} | ${remote_host_mask}
| | ... | gateway=1.1.1.2 | interface=${DUT1_${int}2}[0]
| | Run Keyword If | '${remote_host2_ip}' != '${NONE}'
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${remote_host2_ip} | ${remote_host_mask}
| | ... | gateway=1.1.1.1 | interface=${DUT2_${int}1}[0]

| Initialize IPv4 routing with memif pairs
| | [Documentation]
| | ... | Create pairs of Memif interfaces on all defined VPP nodes. Put each
| | ... | Memif interface to separate IPv4 VRF with one physical or
| | ... | virtual interface to create a chain accross DUT node.
| |
| | ... | *Arguments:*
| | ... | - count - Number of memif pairs (containers). Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv4 routing with memif pairs \| ${1} \|
| |
| | [Arguments] | ${count}=${1}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize IPv4 routing with memif pairs on DUT node | ${dut} | ${count}
| | END
| | Set interfaces in path up
| | Show Memif on all DUTs | ${nodes}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=memif

| Initialize IPv4 routing with memif pairs on DUT node
| | [Documentation]
| | ... | Create pairs of Memif interfaces on DUT node. Put each Memif interface
| | ... | to separate IPv4 VRF with one physical or virtual interface
| | ... | to create a chain accross DUT node.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: dictionary
| | ... | - count - Number of memif pairs (containers). Type: integer
| |
| | ... | *Note:*
| | ... | Socket paths for Memif are defined in following format:
| | ... | - /tmp/memif-\${dut}_CNF\${number}-\${sid}
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv4 routing with memif pairs on DUT node \
| | ... | \| ${dut} \| ${1} \|
| |
| | [Arguments] | ${dut} | ${count}
| |
| | ${dut_index}= | Get Index From List | ${duts} | ${dut}
| | ${last_dut_index}= | Evaluate | ${duts_count} - ${1}
| |
| | ${tg_if1_net}= | Set Variable | 10.10.10.0
| | ${tg_if2_net}= | Set Variable | 20.20.20.0
| |
| | ${fib_table_1}= | Set Variable | ${10}
| | Run Keyword If | ${fib_table_1} > ${0}
| | # FIXME: Maybe wrong.
| | ... | Add Fib Table | ${nodes['${dut}']} | ${fib_table_1}
| | ${ip_base_if1}= | Evaluate | ${dut_index} + ${1}
| | ${ip_net_if1}= | Set Variable
| | ... | ${ip_base_if1}.${ip_base_if1}.${ip_base_if1}
| | Vpp Route Add | ${nodes['${dut}']} | ${tg_if1_net} | 24
| | ... | vrf=${fib_table_1} | gateway=${ip_net_if1}.1
| | ... | interface=${${dut}_${int}1}[0] | multipath=${TRUE}
| | Assign Interface To Fib Table | ${nodes['${dut}']} | ${${dut}_${int}1}[0]
| | ... | ${fib_table_1}
| | VPP Interface Set IP Address | ${nodes['${dut}']} | ${${dut}_${int}1}[0]
| | ... | ${ip_net_if1}.2 | 30
| | ${prev_node}= | Run Keyword If | ${dut_index} == ${0}
| | ... | Set Variable | TG
| | ... | ELSE | Get From List | ${duts} | ${dut_index-${1}}
| | ${prev_if}= | Run Keyword If | ${dut_index} == ${0}
| | ... | Set Variable | pf1
| | ... | ELSE | Set Variable | ${int}2
| | ${prev_if_mac}= | Get Interface MAC | ${nodes['${prev_node}']}
| | ... | ${${prev_node}_${prev_if}}[0]
| | VPP Add IP Neighbor
| | ... | ${nodes['${dut}']} | ${${dut}_${int}1}[0] | ${ip_net_if1}.1
| | ... | ${prev_if_mac}
| |
| | ${fib_table_2}= | Evaluate | ${fib_table_1} + ${count}
| | Add Fib Table | ${nodes['${dut}']} | ${fib_table_2}
| | ${ip_base_if2}= | Evaluate | ${ip_base_if1} + ${1}
| | ${ip_net_if2}= | Set Variable
| | ... | ${ip_base_if2}.${ip_base_if2}.${ip_base_if2}
| | Vpp Route Add | ${nodes['${dut}']} | ${tg_if2_net} | 24
| | ... | vrf=${fib_table_2} | gateway=${ip_net_if2}.2
| | ... | interface=${${dut}_${int}2}[0] | multipath=${TRUE}
| | Assign Interface To Fib Table | ${nodes['${dut}']} | ${${dut}_${int}2}[0]
| | ... | ${fib_table_2}
| | VPP Interface Set IP Address | ${nodes['${dut}']} | ${${dut}_${int}2}[0]
| | ... | ${ip_net_if2}.1 | 30
| | ${next_node}= | Run Keyword If | ${dut_index} == ${last_dut_index}
| | ... | Set Variable | TG
| | ... | ELSE | Get From List | ${duts} | ${dut_index+${1}}
| | ${next_if}= | Run Keyword If | ${dut_index} == ${last_dut_index}
| | ... | Set Variable | pf2
| | ... | ELSE | Set Variable | ${int}1
| | ${next_if_mac}= | Get Interface MAC | ${nodes['${next_node}']}
| | ... | ${${next_node}_${next_if}}[0]
| | VPP Add IP Neighbor
| | ... | ${nodes['${dut}']} | ${${dut}_${int}2}[0] | ${ip_net_if2}.2
| | ... | ${next_if_mac}
| |
| | ${fib_table_1}= | Evaluate | ${fib_table_1} - ${1}
| | ${ip_base_start}= | Set Variable | ${31}
| | FOR | ${number} | IN RANGE | 1 | ${count+${1}}
| | | ${sock1}= | Set Variable | memif-${dut}_CNF
| | | ${sock2}= | Set Variable | memif-${dut}_CNF
| | | Set up memif interfaces on DUT node | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${number} | ${dut}-memif-${number}-if1
| | | ... | ${dut}-memif-${number}-if2 | ${rxq_count_int} | ${rxq_count_int}
| | | ${memif1}= | Set Variable | ${${dut}-memif-${number}-if1}
| | | ${memif2}= | Set Variable | ${${dut}-memif-${number}-if2}
| | | ${fib_table_1}= | Evaluate | ${fib_table_1} + ${1}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1} + ${1}
| | | Run Keyword If | ${number} != ${count}
| | | ... | Add Fib Table | ${nodes['${dut}']} | ${fib_table_2}
| | | Assign Interface To Fib Table | ${nodes['${dut}']}
| | | ... | ${memif1} | ${fib_table_1}
| | | Assign Interface To Fib Table | ${nodes['${dut}']}
| | | ... | ${memif2} | ${fib_table_2}
| | | ${ip_base_memif1}= | Evaluate
| | | ... | ${ip_base_start} + (${number} - ${1}) * ${2}
| | | ${ip_base_memif2}= | Evaluate | ${ip_base_memif1} + ${1}
| | | ${ip_net_memif1}= | Set Variable
| | | ... | ${ip_base_memif1}.${ip_base_memif1}.${ip_base_memif1}
| | | ${ip_net_memif2}= | Set Variable
| | | ... | ${ip_base_memif2}.${ip_base_memif2}.${ip_base_memif2}
| | | VPP Interface Set IP Address
| | | ... | ${nodes['${dut}']} | ${memif1} | ${ip_net_memif1}.1 | 30
| | | VPP Interface Set IP Address
| | | ... | ${nodes['${dut}']} | ${memif2} | ${ip_net_memif2}.1 | 30
| | | Vpp Route Add | ${nodes['${dut}']} | ${tg_if2_net} | 24
| | | ... | vrf=${fib_table_1} | gateway=${ip_net_memif2}.1
| | | ... | interface=${memif1}
| | | Vpp Route Add | ${nodes['${dut}']} | ${tg_if1_net} | 24
| | | ... | vrf=${fib_table_2} | gateway=${ip_net_memif1}.1
| | | ... | interface=${memif2}
| | | ${memif_if1_key}= | Get interface by sw index | ${nodes['${dut}']}
| | | ... | ${memif1}
| | | ${memif_if1_mac}= | Get interface mac | ${nodes['${dut}']}
| | | ... | ${memif_if1_key}
| | | ${memif_if2_key}= | Get interface by sw index | ${nodes['${dut}']}
| | | ... | ${memif2}
| | | ${memif_if2_mac}= | Get interface mac | ${nodes['${dut}']}
| | | ... | ${memif_if2_key}
| | | VPP Add IP Neighbor | ${nodes['${dut}']}
| | | ... | ${memif1} | ${ip_net_memif2}.1 | ${memif_if2_mac}
| | | VPP Add IP Neighbor | ${nodes['${dut}']}
| | | ... | ${memif2} | ${ip_net_memif1}.1 | ${memif_if1_mac}
| | END

| Initialize IPv4 routing with memif pairs and ipsec on DUT node
| | [Documentation] FIXME!
| |
| | [Arguments] | ${dut}
| |
| | Run Keyword If | "${duts_count}" != "2" | Fail | FIXME
| | ${dut_index}= | Get Index From List | ${duts} | ${dut}
| | ${last_dut_index}= | Evaluate | ${duts_count} - ${1}
| |
| | # FIXME I bet those two are wrong for ipsec traffic profiles.
| | ${tg_if1_net}= | Set Variable | 10.10.10.0
| | ${tg_if2_net}= | Set Variable | 20.20.20.0
| |
| | ${prev_node}= | Run Keyword If | ${dut_index} == ${0}
| | ... | Set Variable | TG
| | ... | ELSE | Get From List | ${duts} | ${dut_index-${1}}
| | ${prev_if}= | Run Keyword If | ${dut_index} == ${0}
| | ... | Set Variable | pf1
| | ... | ELSE | Set Variable | ${int}2
| | ${prev_if_mac}= | Get Interface MAC | ${nodes['${prev_node}']}
| | ... | ${${prev_node}_${prev_if}}[0]
| | ${fib_table_1}= | Set Variable If | "${prev_node}" == "TG" | ${10} | ${0}
| | Run Keyword If | ${fib_table_1} > ${0}
| | ... | Add Fib Table | ${nodes['${dut}']} | ${fib_table_1}
| | # FIXME: I also bet this next value is wrong.
| | ${ip_base_if1}= | Evaluate | ${dut_index} + ${1}
| | ${ip_net_if1}= | Set Variable
| | ... | ${ip_base_if1}.${ip_base_if1}.${ip_base_if1}
| | # FIXME: Is /24 enough?
| | Vpp Route Add | ${nodes['${dut}']} | ${tg_if1_net} | 24
| | ... | vrf=${fib_table_1} | gateway=${ip_net_if1}.1
| | ... | interface=${${dut}_${int}1}[0] | multipath=${TRUE}
| | # FIXME: Skip these 3 commands if "${fib_table_1}" == "0".
| | Assign Interface To Fib Table | ${nodes['${dut}']} | ${${dut}_${int}1}[0]
| | ... | ${fib_table_1}
| | VPP Interface Set IP Address | ${nodes['${dut}']} | ${${dut}_${int}1}[0]
| | ... | ${ip_net_if1}.2 | 30
| | VPP Add IP Neighbor
| | ... | ${nodes['${dut}']} | ${${dut}_${int}1}[0] | ${ip_net_if1}.1
| | ... | ${prev_if_mac}
| |
| | ${fib_table_2}= | Evaluate | ${fib_table_1} + ${count}
| | Add Fib Table | ${nodes['${dut}']} | ${fib_table_2}
| | # FIXME: Also suspicious.
| | ${ip_base_if2}= | Evaluate | ${ip_base_if1} + ${1}
| | ${ip_net_if2}= | Set Variable
| | ... | ${ip_base_if2}.${ip_base_if2}.${ip_base_if2}
| | # FIXME: Investigate which of those need to be skipped.
| | Vpp Route Add | ${nodes['${dut}']} | ${tg_if2_net} | 24
| | ... | vrf=${fib_table_2} | gateway=${ip_net_if2}.2
| | ... | interface=${${dut}_${int}2}[0] | multipath=${TRUE}
| | Assign Interface To Fib Table | ${nodes['${dut}']} | ${${dut}_${int}2}[0]
| | ... | ${fib_table_2}
| | VPP Interface Set IP Address | ${nodes['${dut}']} | ${${dut}_${int}2}[0]
| | ... | ${ip_net_if2}.1 | 30
| | ${next_node}= | Run Keyword If | ${dut_index} == ${last_dut_index}
| | ... | Set Variable | TG
| | ... | ELSE | Get From List | ${duts} | ${dut_index+${1}}
| | ${next_if}= | Run Keyword If | ${dut_index} == ${last_dut_index}
| | ... | Set Variable | pf2
| | ... | ELSE | Set Variable | ${int}1
| | ${next_if_mac}= | Get Interface MAC | ${nodes['${next_node}']}
| | ... | ${${next_node}_${next_if}}[0]
| | VPP Add IP Neighbor
| | ... | ${nodes['${dut}']} | ${${dut}_${int}2}[0] | ${ip_net_if2}.2
| | ... | ${next_if_mac}
| |
| | # FIXME: Wrong.
| | ${fib_table_1}= | Evaluate | ${fib_table_1} - ${1}
| | # FIXME: Maybe wrong.
| | ${ip_base_start}= | Set Variable | ${31}
| | # FIXME: Hardcode count==1.
| | FOR | ${number} | IN RANGE | 1 | ${count+${1}}
| | | ${sock1}= | Set Variable | memif-${dut}_CNF
| | | ${sock2}= | Set Variable | memif-${dut}_CNF
| | | Set up memif interfaces on DUT node | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${number} | ${dut}-memif-${number}-if1
| | | ... | ${dut}-memif-${number}-if2 | ${rxq_count_int} | ${rxq_count_int}
| | | ${memif1}= | Set Variable | ${${dut}-memif-${number}-if1}
| | | ${memif2}= | Set Variable | ${${dut}-memif-${number}-if2}
| | | # FIXME Needs care.
| | | ${fib_table_1}= | Evaluate | ${fib_table_1} + ${1}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1} + ${1}
| | | Run Keyword If | ${number} != ${count}
| | | ... | Add Fib Table | ${nodes['${dut}']} | ${fib_table_2}
| | | Assign Interface To Fib Table | ${nodes['${dut}']}
| | | ... | ${memif1} | ${fib_table_1}
| | | Assign Interface To Fib Table | ${nodes['${dut}']}
| | | ... | ${memif2} | ${fib_table_2}
| | | ${ip_base_memif1}= | Evaluate
| | | ... | ${ip_base_start} + (${number} - ${1}) * ${2}
| | | ${ip_base_memif2}= | Evaluate | ${ip_base_memif1} + ${1}
| | | ${ip_net_memif1}= | Set Variable
| | | ... | ${ip_base_memif1}.${ip_base_memif1}.${ip_base_memif1}
| | | ${ip_net_memif2}= | Set Variable
| | | ... | ${ip_base_memif2}.${ip_base_memif2}.${ip_base_memif2}
| | | VPP Interface Set IP Address
| | | ... | ${nodes['${dut}']} | ${memif1} | ${ip_net_memif1}.1 | 30
| | | VPP Interface Set IP Address
| | | ... | ${nodes['${dut}']} | ${memif2} | ${ip_net_memif2}.1 | 30
| | | Vpp Route Add | ${nodes['${dut}']} | ${tg_if2_net} | 24
| | | ... | vrf=${fib_table_1} | gateway=${ip_net_memif2}.1
| | | ... | interface=${memif1}
| | | Vpp Route Add | ${nodes['${dut}']} | ${tg_if1_net} | 24
| | | ... | vrf=${fib_table_2} | gateway=${ip_net_memif1}.1
| | | ... | interface=${memif2}
| | | ${memif_if1_key}= | Get interface by sw index | ${nodes['${dut}']}
| | | ... | ${memif1}
| | | ${memif_if1_mac}= | Get interface mac | ${nodes['${dut}']}
| | | ... | ${memif_if1_key}
| | | ${memif_if2_key}= | Get interface by sw index | ${nodes['${dut}']}
| | | ... | ${memif2}
| | | ${memif_if2_mac}= | Get interface mac | ${nodes['${dut}']}
| | | ... | ${memif_if2_key}
| | | VPP Add IP Neighbor | ${nodes['${dut}']}
| | | ... | ${memif1} | ${ip_net_memif2}.1 | ${memif_if2_mac}
| | | VPP Add IP Neighbor | ${nodes['${dut}']}
| | | ... | ${memif2} | ${ip_net_memif1}.1 | ${memif_if1_mac}
| | END

| Initialize IPv4 forwarding with vhost in 2-node circular topology
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on
| | ... | VPP node. Set UP state of all VPP interfaces in path. Create
| | ... | nf_nodes+1 FIB tables on DUT with multipath routing. Assign each
| | ... | Virtual interface to FIB table with Physical interface or Virtual
| | ... | interface on both nodes. Setup IPv4 addresses with /30 prefix on
| | ... | DUT-TG links. Set routing on DUT nodes in all FIB tables with prefix
| | ... | /8 and next hop of neighbour IPv4 address. Setup ARP on all VPP
| | ... | interfaces.
| |
| | ... | *Arguments:*
| | ... | - nf_nodes - Number of guest VMs. Type: integer
| | ... | - testpmd_mac - Switch for testpmd_mac test configuration.
| | ... | Type: boolean
| | ... | - virtio_feature_mask - Enabled Virtio features (Optional).
| | ... | Type: integer
| |
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /var/run/vpp/sock-${VM_ID}-1
| | ... | - /var/run/vpp/sock-${VM_ID}-2
| |
| | ... | *Example:*
| |
| | ... | \| IPv4 forwarding with Vhost-User initialized in a 2-node circular\
| | ... | topology \| 1 \|
| |
| | [Arguments] | ${nf_nodes}=${1} | ${testpmd_mac}=${FALSE}
| | ... | ${virtio_feature_mask}=${None}
| |
| | Set interfaces in path up
| | ${fib_table_1}= | Set Variable | ${101}
| | ${fib_table_2}= | Evaluate | ${fib_table_1}+${nf_nodes}
| | Add Fib Table | ${dut1} | ${fib_table_1}
| | Add Fib Table | ${dut1} | ${fib_table_2}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${fib_table_1}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${fib_table_2}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 100.0.0.1 | 30
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 200.0.0.1 | 30
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 100.0.0.2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 200.0.0.2 | ${TG_pf2_mac}[0]
| | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=100.0.0.2
| | ... | interface=${DUT1_${int}1}[0] | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=200.0.0.2
| | ... | interface=${DUT1_${int}2}[0] | vrf=${fib_table_2}
| | FOR | ${number} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${fib_table_1}= | Evaluate | ${100}+${number}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1}+${1}
| | | Configure vhost interfaces | ${dut1}
| | | ... | /var/run/vpp/sock-${number}-1 | /var/run/vpp/sock-${number}-2
| | | ... | dut1-vhost-${number}-if1 | dut1-vhost-${number}-if2
| | | ... | virtio_feature_mask=${virtio_feature_mask}
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if1} | up
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if2} | up
| | | Add Fib Table | ${dut1} | ${fib_table_1}
| | | Add Fib Table | ${dut1} | ${fib_table_2}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | ${fib_table_1}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | ${fib_table_2}
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${dut1-vhost-${number}-if1} | 1.1.1.2 | 30
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${dut1-vhost-${number}-if2} | 1.1.2.2 | 30
| | | Run Keyword If | not ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=1.1.1.1
| | | ... | interface=${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Run Keyword If | not ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=1.1.2.1
| | | ... | interface=${dut1-vhost-${number}-if2} | vrf=${fib_table_2}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | VPP Add IP Neighbor | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | 1.1.2.2 | ${dut1-vhost-${number}-if2_mac}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | VPP Add IP Neighbor | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | 1.1.1.2 | ${dut1-vhost-${number}-if1_mac}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=1.1.2.2
| | | ... | interface=${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=1.1.1.2
| | | ... | interface=${dut1-vhost-${number}-if2} | vrf=${fib_table_2}
| | END

| Initialize IPv4 forwarding with vhost in 3-node circular topology
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on all
| | ... | VPP nodes. Set UP state of all VPP interfaces in path. Create
| | ... | nf_nodes+1 FIB tables on each DUT with multipath routing. Assign
| | ... | each Virtual interface to FIB table with Physical interface or Virtual
| | ... | interface on both nodes. Setup IPv4 addresses with /30 prefix on
| | ... | DUT-TG links and /30 prefix on DUT1-DUT2 link. Set routing on all DUT
| | ... | nodes in all FIB tables with prefix /8 and next hop of neighbour IPv4
| | ... | address. Setup ARP on all VPP interfaces.
| |
| | ... | *Arguments:*
| | ... | - nf_nodes - Number of guest VMs. Type: integer
| | ... | - virtio_feature_mask - Enabled Virtio features (Optional).
| | ... | Type: integer
| |
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /var/run/vpp/sock-\${VM_ID}-1
| | ... | - /var/run/vpp/sock-\${VM_ID}-2
| |
| | ... | *Example:*
| |
| | ... | \| IPv4 forwarding with Vhost-User initialized in a 3-node circular\
| | ... | topology \| 1 \|
| |
| | [Arguments] | ${nf_nodes}=${1} | ${testpmd_mac}=${FALSE}
| | ... | ${virtio_feature_mask}=${None}
| |
| | Set interfaces in path up
| | ${fib_table_1}= | Set Variable | ${101}
| | ${fib_table_2}= | Evaluate | ${fib_table_1}+${nf_nodes}
| | Add Fib Table | ${dut1} | ${fib_table_1}
| | Add Fib Table | ${dut1} | ${fib_table_2}
| | Add Fib Table | ${dut2} | ${fib_table_1}
| | Add Fib Table | ${dut2} | ${fib_table_2}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${fib_table_1}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ${fib_table_2}
| | Assign Interface To Fib Table
| | ... | ${dut2} | ${DUT2_${int}1}[0] | ${fib_table_1}
| | Assign Interface To Fib Table
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ${fib_table_2}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 100.0.0.1 | 30
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 150.0.0.1 | 30
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 150.0.0.2 | 30
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${DUT2_${int}2}[0] | 200.0.0.1 | 30
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 100.0.0.2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}2}[0] | 200.0.0.2 | ${TG_pf2_mac}[0]
| | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=100.0.0.2
| | ... | interface=${DUT1_${int}1}[0] | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=150.0.0.2
| | ... | interface=${DUT1_${int}2}[0] | vrf=${fib_table_2}
| | Vpp Route Add | ${dut2} | 10.0.0.0 | 8 | gateway=150.0.0.1
| | ... | interface=${DUT2_${int}1}[0] | vrf=${fib_table_1}
| | Vpp Route Add | ${dut2} | 20.0.0.0 | 8 | gateway=200.0.0.2
| | ... | interface=${DUT2_${int}2}[0] | vrf=${fib_table_2}
| | FOR | ${number} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${fib_table_1}= | Evaluate | ${100}+${number}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1}+${1}
| | | Configure vhost interfaces | ${dut1}
| | | ... | /var/run/vpp/sock-${number}-1 | /var/run/vpp/sock-${number}-2
| | | ... | dut1-vhost-${number}-if1 | dut1-vhost-${number}-if2
| | | ... | virtio_feature_mask=${virtio_feature_mask}
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if1} | up
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if2} | up
| | | Configure vhost interfaces | ${dut2}
| | | ... | /var/run/vpp/sock-${number}-1 | /var/run/vpp/sock-${number}-2
| | | ... | dut2-vhost-${number}-if1 | dut2-vhost-${number}-if2
| | | ... | virtio_feature_mask=${virtio_feature_mask}
| | | Set Interface State | ${dut2} | ${dut2-vhost-${number}-if1} | up
| | | Set Interface State | ${dut2} | ${dut2-vhost-${number}-if2} | up
| | | Add Fib Table | ${dut1} | ${fib_table_1}
| | | Add Fib Table | ${dut1} | ${fib_table_2}
| | | Add Fib Table | ${dut2} | ${fib_table_1}
| | | Add Fib Table | ${dut2} | ${fib_table_2}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | ${fib_table_1}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | ${fib_table_2}
| | | Assign Interface To Fib Table | ${dut2} | ${dut2-vhost-${number}-if1}
| | | ... | ${fib_table_1}
| | | Assign Interface To Fib Table | ${dut2} | ${dut2-vhost-${number}-if2}
| | | ... | ${fib_table_2}
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${dut1-vhost-${number}-if1} | 1.1.1.2 | 30
| | | VPP Interface Set IP Address
| | | ... | ${dut1} | ${dut1-vhost-${number}-if2} | 1.1.2.2 | 30
| | | VPP Interface Set IP Address
| | | ... | ${dut2} | ${dut2-vhost-${number}-if1} | 1.1.1.2 | 30
| | | VPP Interface Set IP Address
| | | ... | ${dut2} | ${dut2-vhost-${number}-if2} | 1.1.2.2 | 30
| | | Run Keyword If | not ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=1.1.1.1
| | | ... | interface=${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Run Keyword If | not ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=1.1.2.1
| | | ... | interface=${dut1-vhost-${number}-if2} | vrf=${fib_table_2}
| | | Run Keyword If | not ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut2} | 20.0.0.0 | 8 | gateway=1.1.1.1
| | | ... | interface=${dut2-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Run Keyword If | not ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut2} | 10.0.0.0 | 8 | gateway=1.1.2.1
| | | ... | interface=${dut2-vhost-${number}-if2} | vrf=${fib_table_2}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | VPP Add IP Neighbor | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | 1.1.2.2 | ${dut1-vhost-${number}-if2_mac}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | VPP Add IP Neighbor | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | 1.1.1.2 | ${dut1-vhost-${number}-if1_mac}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | VPP Add IP Neighbor | ${dut2} | ${dut2-vhost-${number}-if1}
| | | ... | 1.1.2.2 | ${dut2-vhost-${number}-if2_mac}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | VPP Add IP Neighbor | ${dut2} | ${dut2-vhost-${number}-if2}
| | | ... | 1.1.1.2 | ${dut2-vhost-${number}-if1_mac}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=1.1.2.2
| | | ... | interface=${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=1.1.1.2
| | | ... | interface=${dut1-vhost-${number}-if2} | vrf=${fib_table_2}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut2} | 20.0.0.0 | 8 | gateway=1.1.2.2
| | | ... | interface=${dut2-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Run Keyword If | ${testpmd_mac}
| | | ... | Vpp Route Add | ${dut2} | 10.0.0.0 | 8 | gateway=1.1.1.2
| | | ... | interface=${dut2-vhost-${number}-if2} | vrf=${fib_table_2}
| | END

| Initialize IPv4 forwarding with VLAN dot1q sub-interfaces in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. In case of 3-node topology create VLAN
| | ... | sub-interfaces between DUTs. In case of 2-node topology create VLAN
| | ... | sub-interface on dut1-if2 interface. Get the interface MAC addresses
| | ... | and setup ARPs. Setup IPv4 addresses with /30 prefix on DUT-TG links
| | ... | and set routing with prefix /30. In case of 3-node set IPv4 adresses
| | ... | with /30 prefix on VLAN and set routing on both DUT nodes with prefix
| | ... | /30. Set next hop of neighbour DUT interface IPv4 address. All
| | ... | interfaces are brought up.
| |
| | ... | *Arguments:*
| | ... | - tg_if1_net - TG interface 1 IP subnet used by traffic generator.
| | ... | Type: integer
| | ... | - tg_if2_net - TG interface 2 IP subnet used by traffic generator.
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
| | ... | \| Initialize IPv4 forwarding with VLAN dot1q sub-interfaces\
| | ... | in circular topology \| 10.10.10.0 \| 20.20.20.0 \| 10 \| pop-1 \|
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
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 1.1.1.1 | ${TG_pf1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${subif_index_1} | 2.2.2.2 | ${DUT2_${int}1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${subif_index_2} | 2.2.2.1 | ${DUT1_${int}2_mac}[0]
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}2}[0]
| | ... | ELSE | Set Variable | ${subif_index_1}
| | VPP Add IP Neighbor
| | ... | ${dut} | ${dut_if2} | 3.3.3.1 | ${TG_pf2_mac}[0]
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 1.1.1.2 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut1} | ${subif_index_1}
| | ... | 2.2.2.1 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut2} | ${subif_index_2}
| | ... | 2.2.2.2 | 30
| | VPP Interface Set IP Address
| | ... | ${dut} | ${dut_if2} | 3.3.3.2 | 30
| | Vpp Route Add | ${dut1} | ${tg_if1_net} | 30 | gateway=1.1.1.1
| | ... | interface=${DUT1_${int}1}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${tg_if2_net} | 30 | gateway=2.2.2.2
| | ... | interface=${subif_index_1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${tg_if1_net} | 30 | gateway=2.2.2.1
| | ... | interface=${subif_index_2}
| | Vpp Route Add | ${dut} | ${tg_if2_net} | 30 | gateway=3.3.3.1
| | ... | interface=${dut_if2}
