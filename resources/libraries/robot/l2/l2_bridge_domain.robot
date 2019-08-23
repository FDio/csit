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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.Memif

*** Keywords ***
| Show Bridge Domain Data On All DUTs
| | [Documentation] | Show Bridge Domain data on all DUTs.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | VPP Get Bridge Domain Data | ${nodes['${dut}']}

| Create bridge domain
| | [Documentation]
| | ... | Create bridge domain on given VPP node with defined learning status.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${bd_id} - Bridge domain ID. Type: integer
| | ... | - ${learn} - Enable/disable MAC learn. Type: boolean, \
| | ... | default value: ${TRUE}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create bridge domain \| ${nodes['DUT1']} \| 2 \|
| | ... | \| Create bridge domain \| ${nodes['DUT1']} \| 5 \
| | ... | \| learn=${FALSE} \|
| | ...
| | [Arguments] | ${dut_node} | ${bd_id} | ${learn}=${TRUE}
| | ...
| | ${learn} = | Set Variable If | ${learn} == ${TRUE} | ${1} | ${0}
| | Create L2 BD | ${dut_node} | ${bd_id} | learn=${learn}

| Add interface to bridge domain
| | [Documentation]
| | ... | Set given interface admin state to up and add this
| | ... | interface to required L2 bridge domain on defined VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut_node} - DUT node. Type: dictionary
| | ... | - ${dut_if} - DUT node interface name. Type: string
| | ... | - ${bd_id} - Bridge domain ID. Type: integer
| | ... | - ${shg} - Split-horizon group ID. Type: integer, default value: 0
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add interface to bridge domain \| ${nodes['DUT2']} \
| | ... | \| GigabitEthernet0/8/0 \| 3 \|
| | ...
| | [Arguments] | ${dut_node} | ${dut_if} | ${bd_id} | ${shg}=0
| | ...
| | Set Interface State | ${dut_node} | ${dut_if} | up
| | Add Interface To L2 BD | ${dut_node} | ${dut_if} | ${bd_id} | ${shg}

| Initialize L2 bridge domain on node
| | [Documentation]
| | ... | Setup L2 bridge domain topology by adding two interfaces on DUT into
| | ... | separate bridge domains that are created automatically starting with
| | ... | index 1. Learning is enabled. Interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of bridge domains interfaces. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domain on node \| DUT1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${count}=${1}
| | ...
| | :FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | Add Interface To L2 BD
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_1} | ${id}
| | | Add Interface To L2 BD
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${id}_2} | ${id}

| Initialize L2 bridge domain
| | [Documentation]
| | ... | Setup L2 bridge domain topology by adding two interfaces on each DUT
| | ... | into separate bridge domains that are created automatically starting
| | ... | with index 1. Learning is enabled. Interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of bridge domains. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domain \| 1 \|
| | ...
| | [Arguments] | ${count}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize L2 bridge domain on node | ${dut} | count=${count}

| Initialize L2 bridge domains with Vhost-User on node
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on
| | ... | defined VPP node. Add each Vhost-User interface into L2 bridge
| | ... | domains with learning enabled with physical inteface or Vhost-User
| | ... | interface of another VM.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - nf_chain - NF chain. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ...
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /var/run/vpp/sock-\${VM_ID}-1
| | ... | - /var/run/vpp/sock-\${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domains with Vhost-User on node \| DUT1 \
| | ... | \| 1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${nf_chain}=${1} | ${nf_nodes}=${1}
| | ...
| | ${bd_id1}= | Evaluate | ${nf_nodes} * (${nf_chain} - 1) + ${nf_chain}
| | ${bd_id2}= | Evaluate | ${nf_nodes} * ${nf_chain} + ${nf_chain}
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | Add interface to bridge domain
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${nf_chain}_1}
| | ... | ${bd_id1}
| | Add interface to bridge domain
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${nf_chain}_2}
| | ... | ${bd_id2}
| | :FOR | ${nf_node} | IN RANGE | 1 | ${nf_nodes} + 1
| | | ${qemu_id}= | Evaluate | (${nf_chain} - ${1}) * ${nf_nodes} + ${nf_node}
| | | Configure vhost interfaces
| | | ... | ${nodes['${dut}']}
| | | ... | /var/run/vpp/sock-${qemu_id}-1 | /var/run/vpp/sock-${qemu_id}-2
| | | ... | ${dut}-vhost-${qemu_id}-if1 | ${dut}-vhost-${qemu_id}-if2
| | | ${bd_id1}= | Evaluate | ${qemu_id} + (${nf_chain} - 1)
| | | ${bd_id2}= | Evaluate | ${bd_id1} + 1
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut}-vhost-${qemu_id}-if1} | ${bd_id1}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut}-vhost-${qemu_id}-if2} | ${bd_id2}

| Initialize L2 bridge domains with Vhost-User
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VNF nodes
| | ... | on all defined VPP nodes. Add each Vhost-User interface into L2 bridge
| | ... | domains with learning enabled with physical inteface or Vhost-User
| | ... | interface of another VM.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chain - NF chain. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domains with Vhost-User \| 1 \| 1 \|
| | ...
| | [Arguments] | ${nf_chain}=${1} | ${nf_nodes}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize L2 bridge domains with Vhost-User on node
| | | ... | ${dut} | nf_chain=${nf_chain} | nf_nodes=${nf_nodes}

| Initialize L2 bridge domains for multiple chains with Vhost-User
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of NF chains
| | ... | with defined number of VNF nodes on all defined VPP nodes. Add each
| | ... | Vhost-User interface into L2 bridge domains with learning enabled
| | ... | with physical inteface or Vhost-User interface of another VM.
| | ... | Put all interfaces in path up.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chains - Number of chains of NFs. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ... | - start - Id of first chain, allows to add chains during test.
| | ... |     Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domains for multiple chains with Vhost-User \
| | ... | \| 3 \| 1 \| 2 \|
| | ...
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${start}=${1}
| | ...
| | Set interfaces in path up
| | :FOR | ${nf_chain} | IN RANGE | ${start} | ${nf_chains} + 1
| | | Initialize L2 bridge domains with Vhost-User
| | | ... | nf_chain=${nf_chain} | nf_nodes=${nf_nodes}

| Initialize L2 bridge domain with VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 bridge domain topology with VXLANoIPv4 by connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | between DUTs. VXLAN sub-interfaces has same IPv4 address as
| | ... | interfaces.
| | ...
| | Set interfaces in path up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if2} | 172.16.0.1
| | ... | 24
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if1} | 172.16.0.2
| | ... | 24
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 172.16.0.2 | ${dut2_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if1} | 172.16.0.1 | ${dut1_if2_mac}
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | VPP Add L2 Bridge Domain | ${dut1} | ${1} | ${dut1_if1} | ${dut1s_vxlan}
| | Set Interface State | ${dut1} | ${dut1s_vxlan} | up
| | VPP Add L2 Bridge Domain | ${dut2} | ${1} | ${dut2_if2} | ${dut2s_vxlan}
| | Set Interface State | ${dut2} | ${dut2s_vxlan} | up

| Initialize L2 bridge domain with VLAN and VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 bridge domain topology with VLAN and VXLANoIPv4 by connecting
| | ... | pairs of VLAN sub-interface and VXLAN interface to separate L2 bridge
| | ... | domain on each DUT. All interfaces are brought up. IPv4 addresses
| | ... | with prefix /32 are configured on interfaces between DUTs. VXLAN
| | ... | sub-interfaces has same IPv4 address as interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - vxlan_count - VXLAN count. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domain with VLAN and VXLANoIPv4 in 3-node \
| | ... | \| circular topology \| ${1} \|
| | ...
| | [Arguments] | ${vxlan_count}=${1}
| | ...
| | Set interfaces in path up
| | ...
| | ${bd_id_start}= | Set Variable | ${1}
| | ${vni_start} = | Set Variable | ${20}
| | ...
| | ${ip_step} = | Set Variable | ${2}
| | ${dut1_ip_start}= | Set Variable | 172.16.0.1
| | ${dut2_ip_start}= | Set Variable | 172.16.0.2
| | ...
| | Vpp create multiple VXLAN IPv4 tunnels | node=${dut1}
| | ... | node_vxlan_if=${dut1_if2} | node_vlan_if=${dut1_if1}
| | ... | op_node=${dut2} | op_node_if=${dut2_if1} | n_tunnels=${vxlan_count}
| | ... | vni_start=${vni_start} | src_ip_start=${dut1_ip_start}
| | ... | dst_ip_start=${dut2_ip_start} | ip_step=${ip_step}
| | ... | bd_id_start=${bd_id_start}
| | Vpp create multiple VXLAN IPv4 tunnels | node=${dut2}
| | ... | node_vxlan_if=${dut2_if1} | node_vlan_if=${dut2_if2}
| | ... | op_node=${dut1} | op_node_if=${dut1_if2} | n_tunnels=${vxlan_count}
| | ... | vni_start=${vni_start} | src_ip_start=${dut2_ip_start}
| | ... | dst_ip_start=${dut1_ip_start} | ip_step=${ip_step}
| | ... | bd_id_start=${bd_id_start}

| Initialize L2 bridge domains with Vhost-User and VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Add each
| | ... | Vhost-User interface into L2 bridge domains with learning enabled
| | ... | with physical inteface.
| | ... | Setup VXLANoIPv4 between DUTs by connecting physical and vxlan
| | ... | interfaces on each DUT. All interfaces are brought up.
| | ... | IPv4 addresses with prefix /24 are configured on interfaces between
| | ... | DUTs. VXLAN sub-interfaces has same IPv4 address as interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id1 - Bridge domain ID. Type: integer
| | ... | - bd_id2 - Bridge domain ID. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 bridge domains with Vhost-User and VXLANoIPv4 initialized in a\
| | ... | 3-node circular topology \| 1 \| 2 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2}
| | ...
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if2} | 172.16.0.1
| | ... | 24
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if1} | 172.16.0.2
| | ... | 24
| | Set interfaces in path up
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Configure vhost interfaces | ${dut1}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1s_vxlan} | ${bd_id2}
| | Configure vhost interfaces | ${dut2}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${dut2s_vxlan} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}

| Init L2 bridge domains with single DUT with Vhost-User and VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on one VPP node. Add each
| | ... | Vhost-User interface into L2 bridge domains with learning enabled
| | ... | one connected to physical interface, the other to VXLAN.
| | ... | Setup VXLANoIPv4 between DUTs and TG by connecting physical and vxlan
| | ... | interfaces on the DUT. All interfaces are brought up.
| | ... | IPv4 addresses with prefix /24 are configured on interfaces between
| | ... | DUT and TG.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_address - Address of physical interface on DUT1. Type: string
| | ... | - dut1_address_subnet - Subnet of the address of physical interface on
| | ... |                         DUT1. Type: string
| | ... | - dut2_address - Address of physical interface on DUT2. Type: string
| | ... | - dut2_address_subnet - Subnet of the address of physical interface on
| | ... |                         DUT2. Type: string
| | ... | - dut1_gw - Address of the _gateway_ to which the traffic will be
| | ... |             forwarded on DUT1. Type: string
| | ... | - dut2_gw - Address of the _gateway_ to which the traffic will be
| | ... |             forwarded on DUT2. Type: string
| | ... | - dut1_vxlans - List of VXLAN params to be configured on DUT1.
| | ... |                 Type: list of dicts, dict params vni, vtep
| | ... | - dut2_vxlans - List of VXLAN params to be configured on DUT2.
| | ... |                 Type: list of dicts, dict params vni, vtep
| | ... | - dut1_route_subnet - Subnet address to forward to  _gateway_ on DUT1.
| | ... |                       Type: string
| | ... | - dut1_route_mask - Subnet address mask to forward to  _gateway_
| | ... |                     on DUT1. Type: string
| | ... | - dut2_route_subnet - Subnet address to forward to  _gateway_ on DUT2.
| | ... |                       Type: string
| | ... | - dut2_route_mask - Subnet address mask to forward to  _gateway_
| | ... |                     on DUT2. Type: string
| | ...
| | ... | *Example:*
| | ...
| | [Arguments] | ${dut1_address} | ${dut1_address_subnet} |
| | ... | ${dut2_address} | ${dut2_address_subnet} | ${dut1_gw} | ${dut2_gw} |
| | ... | ${dut1_vxlans} | ${dut2_vxlans} | ${dut1_route_subnet} |
| | ... | ${dut1_route_mask} | ${dut2_route_subnet} | ${dut2_route_mask}
| | ...
| | Configure vhost interfaces | ${dut1}
| | ... | /var/run/vpp/sock-1-${dut1_bd_id1}
| | ... | /var/run/vpp/sock-1-${dut1_bd_id2}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} |
| | ... | ${dut1_address} | ${dut1_address_subnet}
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if2} |
| | ... | ${dut2_address} | ${dut2_address_subnet}
| | ${dut1_bd_id1}= | Set Variable | 1
| | ${dut1_bd_id2}= | Set Variable | 2
| | ${dut2_bd_id1}= | Set Variable | 1
| | :FOR | ${vxlan} | IN | @{dut1_vxlans}
| | | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | ${vxlan.vni}
| | | ... | ${dut1_address} | ${vxlan.vtep}
| | | Add interface to bridge domain | ${dut1} | ${dut1s_vxlan} | ${dut1_bd_id1}
| | :FOR | ${vxlan} | IN | @{dut2_vxlans}
| | | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | ${vxlan.vni}
| | | ... | ${dut2_address} | ${vxlan.vtep}
| | | Add interface to bridge domain | ${dut2} | ${dut2s_vxlan} | ${dut2_bd_id1}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | ${dut1_gw} | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | ${dut2_gw} | ${tg_if2_mac}
| | Vpp Route Add | ${dut1} | ${dut1_route_subnet} | ${dut1_route_mask}
| | ... | gateway=${dut1_gw} | interface=${dut1_if1}
| | Vpp Route Add | ${dut2} | ${dut2_route_subnet} | ${dut2_route_mask}
| | ... | gateway=${dut2_gw} | interface=${dut2_if2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if2} | ${dut1_bd_id2}
| | Add interface to bridge domain | ${dut2} | ${dut2_if1} | ${dut2_bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${dut1_bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${dut1_bd_id2}

| Initialize L2 bridge domains with VLAN dot1q sub-interfaces in circular topology
| | [Documentation]
| | ... | Setup L2 bridge domain topology with learning enabled with VLAN by
| | ... | connecting physical and vlan interfaces on each DUT. In case of 3-node
| | ... | topology create VLAN sub-interfaces between DUTs. In case of 2-node
| | ... | topology create VLAN sub-interface on dut1-if2 interface. All
| | ... | interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id1 - Bridge domain ID. Type: integer
| | ... | - bd_id2 - Bridge domain ID. Type: integer
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
| | ... | \| Initialize L2 bridge domains with VLAN dot1q sub-interfaces
| | ... | in a 3-node circular topology \| 1 \| 2 \| 10 \| pop-1 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${subid} | ${tag_rewrite}
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
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${subif_index_1} | ${bd_id1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${subif_index_2}
| | ... | ${bd_id2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${dut2_if2}
| | ... | ${bd_id2}

| Initialize L2 bridge domains with Vhost-User and VLAN in circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Add each
| | ... | Vhost-User interface into L2 bridge domains with learning enabled
| | ... | with physical inteface. In case of 3-node topology create VLAN
| | ... | sub-interfaces between DUTs. In case of 2-node topology create VLAN
| | ... | sub-interface on dut1-if2 interface. All interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id1 - Bridge domain ID. Type: integer
| | ... | - bd_id2 - Bridge domain ID. Type: integer
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 bridge domains with Vhost-User and VLAN initialized in circular\
| | ... | topology \| 1 \| 2 \| 10 \| pop-1 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${subid} | ${tag_rewrite}
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
| | Configure vhost interfaces | ${dut1}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${subif_index_1} | ${bd_id2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure vhost interfaces | ${dut2}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${subif_index_2}
| | ... | ${bd_id1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}

| Initialize L2 bridge domains with Vhost-User and VLAN with VPP link bonding in a 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Create one
| | ... | link bonding (BondEthernet) interface on both VPP nodes. Enslave one
| | ... | physical interface towards next DUT by BondEthernet interface. Setup
| | ... | VLAN on BondEthernet interfaces between DUTs. Add one Vhost-User
| | ... | interface into L2 bridge domains with learning enabled with physical
| | ... | interface towards TG and other Vhost-User interface into L2 bridge
| | ... | domains with learning enabled with VLAN sub-interface. All interfaces
| | ... | are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id1 - Bridge domain ID. Type: integer
| | ... | - bd_id2 - Bridge domain ID. Type: integer
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ... | - bond_mode - Link bonding mode. Type: string
| | ... | - lb_mode - Load balance mode. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domains with Vhost-User and VLAN with VPP\
| | ... | link bonding in a 3-node circular topology \| 1 \| 2 \
| | ... | \| 10 \| pop-1 \| xor \| l34 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${subid} | ${tag_rewrite}
| | ... | ${bond_mode} | ${lb_mode}
| | ...
| | Set interfaces in path up
| | ${dut1_eth_bond_if1}= | VPP Create Bond Interface | ${dut1} | ${bond_mode}
| | ... | ${lb_mode}
| | Set Interface State | ${dut1} | ${dut1_eth_bond_if1} | up
| | VPP Set interface MTU | ${dut1} | ${dut1_eth_bond_if1}
| | ${if2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut1_if2}
| | Run Keyword If | '${if2_status}' == 'PASS'
| | ... | VPP Enslave Physical Interface | ${dut1} | ${dut1_if2}
| | ... | ${dut1_eth_bond_if1}
| | ... | ELSE
| | ... | VPP Enslave Physical Interface | ${dut1} | ${dut1_if2_1}
| | ... | ${dut1_eth_bond_if1}
| | Run Keyword Unless | '${if2_status}' == 'PASS'
| | ... | VPP Enslave Physical Interface | ${dut1} | ${dut1_if2_2}
| | ... | ${dut1_eth_bond_if1}
| | ${dut2_eth_bond_if1}= | VPP Create Bond Interface | ${dut2} | ${bond_mode}
| | ... | ${lb_mode}
| | Set Interface State | ${dut2} | ${dut2_eth_bond_if1} | up
| | VPP Set interface MTU | ${dut2} | ${dut2_eth_bond_if1}
| | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2_if1}
| | Run Keyword If | '${if1_status}' == 'PASS'
| | ... | VPP Enslave Physical Interface | ${dut2} | ${dut2_if1}
| | ... | ${dut2_eth_bond_if1}
| | ... | ELSE
| | ... | VPP Enslave Physical Interface | ${dut2} | ${dut2_if1_1}
| | ... | ${dut2_eth_bond_if1}
| | Run Keyword Unless | '${if2_status}' == 'PASS'
| | ... | VPP Enslave Physical Interface | ${dut2} | ${dut2_if1_2}
| | ... | ${dut2_eth_bond_if1}
| | VPP Show Bond Data On All Nodes | ${nodes} | verbose=${TRUE}
| | Initialize VLAN dot1q sub-interfaces in circular topology
| | ... | ${dut1} | ${dut1_eth_bond_if1} | ${dut2} | ${dut2_eth_bond_if1}
| | ... | ${subid}
| | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | Configure vhost interfaces | ${dut1}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${subif_index_1} | ${bd_id2}
| | Configure vhost interfaces | ${dut2}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${subif_index_2} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}

| Initialize L2 Bridge Domain with memif pairs on DUT node
| | [Documentation]
| | ... | Create pairs of Memif interfaces on DUT node. Put each Memif interface
| | ... | to separate L2 bridge domain with one physical or memif interface
| | ... | to create a chain accross DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: dictionary
| | ... | - nf_chain - NF chain. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ... | - auto_scale - Whether to use same amount of RXQs for memif interface
| | ... | in containers as vswitch, otherwise use single RXQ. Type: boolean
| | ...
| | ... | *Note:*
| | ... | Socket paths for Memif are defined in following format:
| | ... | - /tmp/memif-\${dut}_CNF\${nf_id}-\${sid}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 Bridge Domain with memif pairs on DUT node \
| | ... | \| ${dut} \| 1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${nf_chain}=${1} | ${nf_nodes}=${1}
| | ... | ${auto_scale}=${True}
| | ...
| | ${rxq}= | Run Keyword If | ${auto_scale} == ${True}
| | ... | Set Variable | ${rxq_count_int}
| | ... | ELSE | Set Variable | ${1}
| | ${bd_id1}= | Evaluate | ${nf_nodes} * (${nf_chain} - 1) + ${nf_chain}
| | ${bd_id2}= | Evaluate | ${nf_nodes} * ${nf_chain} + ${nf_chain}
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | Add interface to bridge domain
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${nf_chain}_1}
| | ... | ${bd_id1}
| | Add interface to bridge domain
| | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${nf_chain}_2}
| | ... | ${bd_id2}
| | :FOR | ${nf_node} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${nf_id}= | Evaluate | (${nf_chain} - ${1}) * ${nf_nodes} + ${nf_node}
| | | ${sock1}= | Set Variable | memif-${dut}_CNF
| | | ${sock2}= | Set Variable | memif-${dut}_CNF
| | | ${bd_id1}= | Evaluate | ${nf_id} + (${nf_chain} - 1)
| | | ${bd_id2}= | Evaluate | ${bd_id1} + 1
| | | Set up memif interfaces on DUT node | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${nf_id} | ${dut}-memif-${nf_id}-if1
| | | ... | ${dut}-memif-${nf_id}-if2 | ${rxq} | ${rxq}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut}-memif-${nf_id}-if1} | ${bd_id1}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut}-memif-${nf_id}-if2} | ${bd_id2}

| Initialize L2 Bridge Domain with memif pairs
| | [Documentation]
| | ... | Create pairs of Memif interfaces on all defined VPP nodes. Put each
| | ... | Memif interface to separate L2 bridge domain with one physical or
| | ... | virtual interface to create a chain accross DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chain - NF chain. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ... | - auto_scale - Whether to use same amount of RXQs for memif interface
| | ... | in containers as vswitch, otherwise use single RXQ. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 Bridge Domain with memif pairs \| 1 \| 1 \|
| | ...
| | [Arguments] | ${nf_chain}=${1} | ${nf_nodes}=${1} | ${auto_scale}=${True}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize L2 Bridge Domain with memif pairs on DUT node | ${dut}
| | | ... | nf_chain=${nf_chain} | nf_nodes=${nf_nodes}
| | | ... | auto_scale=${auto_scale}

| Initialize L2 Bridge Domain for multiple chains with memif pairs
| | [Documentation]
| | ... | Create pairs of Memif interfaces for defined number of NF chains
| | ... | with defined number of NF nodes on all defined VPP nodes. Add each
| | ... | Memif interface into L2 bridge domains with learning enabled
| | ... | with physical inteface or Memif interface of another NF.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chains - Number of chains of NFs. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ... | - auto_scale - Whether to use same amount of RXQs for memif interface
| | ... | in containers as vswitch, otherwise use single RXQ. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 Bridge Domain for multiple chains with memif pairs \
| | ... | \| 1 \| 1 \|
| | ...
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${auto_scale}=${True}
| | ...
| | :FOR | ${nf_chain} | IN RANGE | 1 | ${nf_chains}+1
| | | Initialize L2 Bridge Domain with memif pairs | nf_chain=${nf_chain}
| | | ... | nf_nodes=${nf_nodes} | auto_scale=${auto_scale}
| | Set interfaces in path up
| | Show Memif on all DUTs | ${nodes}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=memif

| Initialize L2 Bridge Domain for pipeline with memif pairs
| | [Documentation]
| | ... | Create pairs of Memif interfaces on all defined VPP nodes. Put each
| | ... | Memif interface to separate L2 bridge domain with one physical or
| | ... | virtual interface to create a service pipeline on DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chain - NF pipe. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per pipeline. Type: integer
| | ... | - auto_scale - Whether to use same amount of RXQs for memif interface
| | ... | in containers as vswitch, otherwise use single RXQ. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 Bridge Domain for pipeline with memif pairs \
| | ... | \| 1 \| 1 \|
| | ...
| | [Arguments] | ${nf_chain}=${1} | ${nf_nodes}=${1} | ${auto_scale}=${True}
| | ...
| | ${rxq}= | Run Keyword If | ${auto_scale} == ${True}
| | ... | Set Variable | ${rxq_count_int}
| | ... | ELSE | Set Variable | ${1}
| | ${bd_id1}= | Evaluate | ${nf_nodes} * (${nf_chain} - 1) + ${nf_chain}
| | ${bd_id2}= | Evaluate | ${nf_nodes} * ${nf_chain} + ${nf_chain}
| | :FOR | ${dut} | IN | @{duts}
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${nf_chain}_1}
| | | ... | ${bd_id1}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut_str}_${prev_layer}_${nf_chain}_2}
| | | ... | ${bd_id2}
| | | ${nf_id_frst}= | Evaluate | (${nf_chain}-${1}) * ${nf_nodes} + ${1}
| | | ${nf_id_last}= | Evaluate | (${nf_chain}-${1}) * ${nf_nodes} + ${nf_nodes}
| | | ${sid_frst}= | Evaluate | ${nf_id_frst} * ${2} - ${1}
| | | ${sid_last}= | Evaluate | ${nf_id_last} * ${2}
| | | Set up single memif interface on DUT node | ${nodes['${dut}']}
| | | ... | memif-${dut}_CNF | mid=${nf_id_frst} | sid=${sid_frst}
| | | ... | memif_if=${dut}-memif-${nf_id_frst}-if1
| | | ... | rxq=${rxq} | txq=${rxq}
| | | Set up single memif interface on DUT node | ${nodes['${dut}']}
| | | ... | memif-${dut}_CNF | mid=${nf_id_last} | sid=${sid_last}
| | | ... | memif_if=${dut}-memif-${nf_id_last}-if2
| | | ... | rxq=${rxq} | txq=${rxq}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut}-memif-${nf_id_frst}-if1} | ${bd_id1}
| | | Add interface to bridge domain
| | | ... | ${nodes['${dut}']} | ${${dut}-memif-${nf_id_last}-if2} | ${bd_id2}

| Initialize L2 Bridge Domain for multiple pipelines with memif pairs
| | [Documentation]
| | ... | Create pairs of Memif interfaces for defined number of NF pipelines
| | ... | with defined number of NF nodes on all defined VPP nodes. Add each
| | ... | Memif interface into L2 bridge domains with learning enabled
| | ... | with physical inteface or Memif interface of another NF.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chains - Number of pipelines of NFs. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per pipeline. Type: integer
| | ... | - auto_scale - Whether to use same amount of RXQs for memif interface
| | ... | in containers as vswitch, otherwise use single RXQ. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 Bridge Domain for multiple pipelines with memif \
| | ... | pairs \| 1 \| 1 \|
| | ...
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${auto_scale}=${True}
| | ...
| | :FOR | ${nf_chain} | IN RANGE | 1 | ${nf_chains}+1
| | | Initialize L2 Bridge Domain for pipeline with memif pairs
| | | ... | nf_chain=${nf_chain} | nf_nodes=${nf_nodes}
| | | ... | auto_scale=${auto_scale}
| | Set interfaces in path up
| | Show Memif on all DUTs | ${nodes}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=memif

| Initialize L2 Bridge Domain with memif pairs and VLAN in circular topology
| | [Documentation]
| | ... | Create pairs of Memif interfaces on all defined VPP nodes. Put each
| | ... | Memif interface to separate L2 bridge domain with one physical or
| | ... | virtual interface to create a chain accross DUT node. In case of
| | ... | 3-node topology create VLAN sub-interfaces between DUTs. In case of
| | ... | 2-node topology create VLAN sub-interface on dut1-if2 interface. All
| | ... | interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id1 - Bridge domain ID. Type: integer
| | ... | - bd_id2 - Bridge domain ID. Type: integer
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 Bridge Domain with memif pairs and VLAN in circular\
| | ... | topology \| 1 \| 2 \| 10 \| pop-1 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${subid} | ${tag_rewrite}
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
| | ${number}= | Set Variable | ${1}
| | ${sock1}= | Set Variable | memif-DUT1_CNF
| | ${sock2}= | Set Variable | memif-DUT1_CNF
| | ${memif_if1_name}= | Set Variable | DUT1-memif-${number}-if1
| | ${memif_if2_name}= | Set Variable | DUT1-memif-${number}-if2
| | Set up memif interfaces on DUT node | ${dut1} | ${sock1} | ${sock2}
| | ... | ${number} | ${memif_if1_name} | ${memif_if2_name} | ${rxq_count_int}
| | ... | ${rxq_count_int}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${${memif_if1_name}} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${${memif_if2_name}} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${subif_index_1} | ${bd_id2}
| | ${sock1}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | memif-DUT2_CNF
| | ${sock2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | memif-DUT2_CNF
| | ${memif_if1_name}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | DUT2-memif-${number}-if1
| | ${memif_if2_name}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | DUT2-memif-${number}-if2
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set up memif interfaces on DUT node | ${dut2} | ${sock1} | ${sock2}
| | ... | ${number} | ${memif_if1_name} | ${memif_if2_name} | ${rxq_count_int}
| | ... | ${rxq_count_int}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${subif_index_2}
| | ... | ${bd_id1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${${memif_if1_name}}
| | ... | ${bd_id1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${${memif_if2_name}}
| | ... | ${bd_id2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | ...
| | Show Memif on all DUTs | ${nodes}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=memif

| Initialize L2 Bridge Domain for single memif
| | [Documentation]
| | ... | Create single Memif interface on all defined VPP nodes. Put Memif
| | ... | interface to separate L2 bridge domain with one physical interface.
| | ...
| | ... | *Arguments:*
| | ... | - number - Memif ID. Type: integer
| | ...
| | ... | *Note:*
| | ... | Socket paths for Memif are defined in following format:
| | ... | - /tmp/memif-DUT1_CNF\${number}-\${sid}
| | ...
| | ... | KW uses test variable ${rxq_count_int} set by KW Add worker threads
| | ... | and rxqueues to all DUTs
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 Bridge Domain for single memif \| 1 \|
| | ...
| | [Arguments] | ${number}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | ${sock}= | Set Variable | memif-${dut}_CNF
| | | ${sid}= | Evaluate | (${number} * ${2}) - ${1}
| | | Set up single memif interface on DUT node | ${nodes['${dut}']} | ${sock}
| | | ... | mid=${number} | sid=${sid} | memif_if=${dut}-memif-${number}-if1
| | | ... | rxq=${rxq_count_int} | txq=${rxq_count_int}
| | | Add interface to bridge domain | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ${number}
| | | Add interface to bridge domain | ${nodes['${dut}']}
| | | ... | ${${dut}-memif-${number}-if1} | ${number}
| | Set single interfaces in path up
| | Show Memif on all DUTs | ${nodes}

| Initialize L2 bridge domain with MACIP ACLs on DUT1 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2BD topology by adding two interfaces on DUT1 into bridge
| | ... | domain that is created automatically with index 1. Learning is
| | ... | enabled. Interfaces are brought up. Apply required MACIP ACL rules to
| | ... | DUT1 interfaces.
| | ...
| | Set interfaces in path up
| | VPP Add L2 Bridge Domain | ${dut1} | ${1} | ${dut1_if1} | ${dut1_if2}
| | Configure L2XC | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Configure MACIP ACLs | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Initialize L2 bridge domain with IPv4 ACLs on DUT1 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2BD topology by adding two interfaces on DUT1 into bridge
| | ... | domain that is created automatically with index 1. Learning is
| | ... | enabled. Interfaces are brought up. Apply required ACL rules to DUT1
| | ... | interfaces.
| | ...
| | Set interfaces in path up
| | VPP Add L2 Bridge Domain | ${dut1} | ${1} | ${dut1_if1} | ${dut1_if2}
| | Configure L2XC | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Configure IPv4 ACLs | ${dut1} | ${dut1_if1} | ${dut1_if2}
