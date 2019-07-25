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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.VatExecutor

*** Keywords ***
| VPP reports interfaces through VAT on '${node}'
| | Execute Script | dump_interfaces.vat | ${node}
| | Script Should Have Passed

| Configure MTU on TG based on MTU on DUT
| | [Documentation] | Type of the tg_node must be TG and dut_node must be DUT
| | [Arguments] | ${tg_node} | ${dut_node}
| | Append Nodes | ${tg_node} | ${dut_node}
| | Compute Path
| | ${tg_port} | ${tg_node}= | First Interface
| | ${dut_port} | ${dut_node}= | Last Interface
| | # get physical layer MTU (max. size of Ethernet frame)
| | ${mtu}= | Get Interface MTU | ${dut_node} | ${dut_port}
| | # Ethernet MTU is physical layer MTU minus size of Ethernet header and FCS
| | ${eth_mtu}= | Evaluate | ${mtu} - 14 - 4
| | Set Interface Ethernet MTU | ${tg_node} | ${tg_port} | ${eth_mtu}

| Get Vhost dump
| | [Documentation] | Get vhost-user dump.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node data. Type: dictionary
| | ...
| | [Arguments] | ${dut_node}
| | ...
| | [Return] | ${vhost_dump}
| | ...
| | ${vhost_dump}= | Vhost User Dump | ${dut_node}

| Initialize layer interface on node
| | [Documentation]
| | ... | Baseline interfaces variables to be created.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of baseline interface variables. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize layer interface on node \| DUT1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${count}=${1}
| | ...
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | :FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | Set Test Variable | ${${dut_str}_if_${id}_1} | ${${dut_str}_if1}
| | | Set Test Variable | ${${dut_str}_if_${id}_2} | ${${dut_str}_if2}

| Initialize layer interface
| | [Documentation]
| | ... | Physical interfaces variables to be created on all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of untagged interfaces variables. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize layer interface \| 1 \|
| | ...
| | [Arguments] | ${count}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize layer interface on node | ${dut} | count=${count}
| | Set Test Variable | ${prev_layer} | if
| | Set interfaces in path up

| Initialize layer bonding on node
| | [Documentation]
| | ... | Bonded interface and variables to be created on across east and
| | ... | west DUT's node interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - bond_mode - Link bonding mode. Type: string
| | ... | - lb_mode - Load balance mode. Type: string
| | ... | - count - Number of bond interface variables. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize layer bonding on node \| DUT1 \| xor \| l34 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${bond_mode}=xor | ${lb_mode}=l34 | ${count}=${1}
| | ...
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | ${if_index}= | VPP Create Bond Interface
| | ... | ${nodes['${dut}']} | ${bond_mode} | load_balance=${lb_mode}
| | ... | mac=00:00:00:01:01:01
| | Set Interface State | ${nodes['${dut}']} | ${if_index} | up
| | VPP Enslave Physical Interface
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_1} | ${if_index}
| | VPP Enslave Physical Interface
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_2} | ${if_index}
| | :FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | Set Test Variable | ${${dut_str}_bond_${id}_1} | ${if_index}
| | | Set Test Variable | ${${dut_str}_bond_${id}_2} | ${if_index}

| Initialize layer bonding
| | [Documentation]
| | ... | Bonded interfaces and variables to be created on all DUT's interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - bond_mode - Link bonding mode. Type: string
| | ... | - lb_mode - Load balance mode. Type: string
| | ... | - count - Number of bond interface variables. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize layer bonding \| xor \| l34 \| 1 \|
| | ...
| | [Arguments] | ${bond_mode}=xor | ${lb_mode}=l34 | ${count}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize layer bonding on node
| | | ... | ${dut} | bond_mode=${bond_mode} | lb_mode=${lb_mode}
| | | ... | count=${count}
| | Set Test Variable | ${prev_layer} | bond

| Initialize layer dot1q on node
| | [Documentation]
| | ... | Dot1q interfaces and variables to be created on all DUT's node
| | ... | interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of tagged interfaces. Type: integer
| | ... | - create - Whether to create vlan subinterface for each chain.
| | ... |     Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize layer dot1q on node \| DUT1 \| 1 \| True \|
| | ...
| | [Arguments] | ${dut} | ${count}=${1} | ${create}=${True}
| | ...
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | :FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | ${if1_vlan}= | Get Interface Vlan
| | | ...| ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_1}
| | | ${if2_vlan}= | Get Interface Vlan
| | | ...| ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_2}
| | | ${if1_vlan}= | Evaluate | ${if1_vlan} + ${id} - 1
| | | ${if2_vlan}= | Evaluate | ${if2_vlan} + ${id} - 1
| | | ${if1_name} | ${if1_index}= | Run Keyword Unless
| | | ... | ${create} and ${id} > ${1}
| | | ... | Create Vlan Subinterface
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_1}
| | | ... | ${if1_vlan}
| | | ${if2_name} | ${if2_index}= | Run Keyword Unless
| | | ... | ${create} and ${id} > ${1}
| | | ... | Create Vlan Subinterface
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_2}
| | | ... | ${if2_vlan}
| | | Configure L2 tag rewrite method on interfaces
| | | ... | ${nodes['${dut}']} | ${if1_index} | TAG_REWRITE_METHOD=pop-1
| | | Configure L2 tag rewrite method on interfaces
| | | ... | ${nodes['${dut}']} | ${if2_index} | TAG_REWRITE_METHOD=pop-1
| | | Run Keyword Unless | ${create} and ${id} > ${1}
| | | ... | Set Interface State | ${nodes['${dut}']} | ${if1_index} | up
| | | Run Keyword Unless | ${create} and ${id} > ${1}
| | | ... | Set Interface State | ${nodes['${dut}']} | ${if2_index} | up
| | | Set Test Variable | ${${dut_str}_dot1q_${id}_1} | ${if1_index}
| | | Set Test Variable | ${${dut_str}_dot1q_${id}_2} | ${if2_index}

| Initialize layer dot1q
| | [Documentation]
| | ... | Dot1q interfaces and variables to be created on all DUT's interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of tagged interfaces. Type: integer
| | ... | - create - Whether to create vlan for each chain. Type: boolean
| | ...
| | ... | \| Initialize layer dot1q \| 1 \| True \|
| | ...
| | [Arguments] | ${count}=${1} | ${create}=${True}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize layer dot1q on node | ${dut} | count=${count}
| | | ... | create=${create}
| | Set Test Variable | ${prev_layer} | dot1q

| Initialize layer ip4vxlan on node
| | [Documentation]
| | ... | Setup VXLANoIPv4 between TG and DUTs and DUT to DUT by connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | towards TG. VXLAN sub-interfaces has same IPv4 address as interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of vxlan interfaces. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize layer ip4vxlan on node \| DUT1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${count}=${1}
| | ...
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | Configure IP addresses on interfaces
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_1}
| | ... | 172.16.0.1 | 24
| | Configure IP addresses on interfaces
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_1_2}
| | ... | 172.26.0.1 | 24
| | :FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | ${subnet}= | Evaluate | ${id} - 1
| | | ${vni}= | Evaluate | ${id} - 1
| | | ${ip4vxlan_1}= | Create VXLAN interface
| | | ... | ${nodes['${dut}']} | ${vni} | 172.16.0.1 | 172.17.${subnet}.2
| | | ${ip4vxlan_2}= | Create VXLAN interface
| | | ... | ${nodes['${dut}']} | ${vni} | 172.26.0.1 | 172.27.${subnet}.2
| | | ${prev_mac}= | Set Variable If | '${dut}' == 'DUT1'
| | | ... | ${tg_if1_mac} | ${dut1_if2_mac}
| | | ${next_mac}= | Set Variable If | '${dut}' == 'DUT1' and ${duts_count} == 2
| | | ... | ${dut2_if1_mac} | ${tg_if2_mac}
| | | VPP Add IP Neighbor
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_1}
| | | ... | 172.16.${subnet}.2 | ${prev_mac}
| | | VPP Add IP Neighbor
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_2}
| | | ... | 172.26.${subnet}.2 | ${next_mac}
| | | VPP Route Add
| | | ... | ${nodes['${dut}']} | 172.17.${subnet}.0 | 24
| | | ... | gateway=172.16.${subnet}.2
| | | ... | interface=${${dut_str}_${prev_layer}_${id}_1}
| | | VPP Route Add
| | | ... | ${nodes['${dut}']} | 172.27.${subnet}.0 | 24
| | | ... | gateway=172.26.${subnet}.2
| | | ... | interface=${${dut_str}_${prev_layer}_${id}_2}
| | | Set VXLAN Bypass
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_1}
| | | Set VXLAN Bypass
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_2}
| | | Set Test Variable
| | | ... | ${${dut_str}_ip4vxlan_${id}_1} | ${ip4vxlan_1}
| | | Set Test Variable
| | | ... | ${${dut_str}_ip4vxlan_${id}_2} | ${ip4vxlan_2}

| Initialize layer ip4vxlan
| | [Documentation]
| | ... | VXLAN interfaces and variables to be created on all DUT's interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of vxlan interfaces. Type: integer
| | ...
| | ... | \| Initialize layer ip4vxlan \| 1 \|
| | ...
| | [Arguments] | ${count}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize layer ip4vxlan on node | ${dut} | count=${count}
| | Set Test Variable | ${prev_layer} | ip4vxlan
