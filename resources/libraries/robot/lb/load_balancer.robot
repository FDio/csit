# Copyright (c) 2019 Intel and/or its affiliates.
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
| Library | Collections
| Library | String

| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.LoadBalancerUtil
| Library | resources.libraries.python.NodePath
|
| Resource | resources/libraries/robot/shared/interfaces.robot
|
| Documentation | LoadBalancer suite keywords - configuration

*** Keywords ***
| Initialize loadbalancer maglev
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links.
| |
| | Set interfaces in path up
| |
| | ${fib_table}= | Set Variable | ${0}
| | Add Fib Table | ${dut1} | ${fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${ilayer}1}[0] | ${fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | ${fib_table}
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${ilayer}1}[0] | 192.168.50.72 | 24
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | 192.168.60.73 | 24
| |
| | Add Ip Neighbors
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | 192.168.60 | ${TG_${ilayer}2_mac}[0]
| |
| | Vpp Route Add
| | ... | ${dut1} | 192.168.60.0 | 24 | interface=${DUT1_${ilayer}2}[0]
| |
| | Vpp Lb Conf
| | ... | ${dut1} | ip4_src_addr=192.168.60.73 | buckets_per_core=${128}
| | Vpp Lb Add Del Vip
| | ... | ${dut1} | vip_addr=90.1.2.1 | encap=${0}
| | ... | new_len=${1024}
| | Add Lb As Addresses
| | ... | ${dut1} | 90.1.2.1 | 192.168.60

| Initialize loadbalancer l3dsr
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links.
| |
| | Set interfaces in path up
| |
| | ${fib_table}= | Set Variable | ${0}
| | Add Fib Table | ${dut1} | ${fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${ilayer}1}[0] | ${fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | ${fib_table}
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${ilayer}1}[0] | 192.168.50.72 | 24
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | 192.168.60.73 | 24
| |
| | Add Ip Neighbors
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | 192.168.60 | ${TG_${ilayer}2_mac}[0]
| |
| | Vpp Route Add
| | ... | ${dut1} | 192.168.60.0 | 24 | interface=${DUT1_${ilayer}2}[0]
| |
| | Vpp Lb Conf
| | ... | ${dut1} | ip4_src_addr=192.168.60.73 | buckets_per_core=${128}
| | Vpp Lb Add Del Vip
| | ... | ${dut1} | vip_addr=90.1.2.1 | encap=${2} | dscp=${7}
| | ... | new_len=${1024}
| | Add Lb As Addresses
| | ... | ${dut1} | 90.1.2.1 | 192.168.60

| Initialize loadbalancer nat4
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links.
| |
| | Set interfaces in path up
| |
| | ${fib_table}= | Set Variable | ${0}
| | Add Fib Table | ${dut1} | ${fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${ilayer}1}[0] | ${fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | ${fib_table}
| |
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${ilayer}1}[0] | 192.168.50.72 | 24
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | 192.168.60.73 | 24
| |
| | Add Ip Neighbors
| | ... | ${dut1} | ${DUT1_${ilayer}1}[0] | 192.168.50 | ${TG_${ilayer}1_mac}[0]
| | Add Ip Neighbors
| | ... | ${dut1} | ${DUT1_${ilayer}2}[0] | 192.168.60 | ${TG_${ilayer}2_mac}[0]
| |
| | Vpp Route Add
| | ... | ${dut1} | 192.168.50.0 | 24 | interface=${DUT1_${ilayer}1}[0]
| | Vpp Route Add
| | ... | ${dut1} | 192.168.60.0 | 24 | interface=${DUT1_${ilayer}2}[0]
| |
| | Vpp Lb Conf
| | ... | ${dut1} | ip4_src_addr=192.168.60.73 | buckets_per_core=${128}
| | Vpp Lb Add Del Vip
| | ... | ${dut1} | vip_addr=90.1.2.1 | encap=${3}
| | ... | protocol=${17} | port=${20000} | target_port=${3307} | new_len=${1024}
| | Add Lb As Addresses
| | ... | ${dut1} | 90.1.2.1 | 192.168.60 | protocol=${17} | port=${20000}
| | Vpp Lb Add Del Intf Nat4
| | ... | ${dut1} | interface=${DUT1_${ilayer}2}[0]

| Add Ip Neighbors
| | [Documentation] | Add IP neighbors to physical interface on DUT.
| |
| | ... | *Arguments:*
| | ... | - node - VPP node. Type: dictionary
| | ... | - interface - Interface key. Type: string
| | ... | - ip_addr - IP address of the interface. Type: string
| | ... | - mac_addr - MAC address of the interface. Type: string
| |
| | ... | *Example:*
| | ... | \| Add Ip Neighbors \| ${dut1} \| ${dut1_if1} \| 192.168.50 \
| | ... | \| ${tg_if1_mac}
| |
| | [Arguments] | ${node} | ${interface} | ${ip_addr} | ${mac_addr}
| |
| | FOR | ${number} | IN RANGE | 74 | 80
| | | VPP Add IP Neighbor
| | | ... | ${node} | ${interface} | ${ip_addr}.${number} | ${mac_addr}
| | END

| Add Lb As Addresses
| | [Documentation] | Add Lb As Addresses on Vpp node.
| |
| | ... | *Arguments:*
| | ... | - node - VPP node. Type: dictionary
| | ... | - vip_addr - IPv4 address to be used as source for IPv4 traffic.
| | ... | Type: string
| | ... | - as_addr - The application server address. Type: string
| | ... | - protocol - tcp or udp. Type: integer
| | ... | - port - destination port. Type: integer
| | ... | - is_del - 1 if the VIP should be removed otherwise 0. Type: integer
| | ... | - is_flush - 1 if the sessions related to this AS should be flushed
| | ... | otherwise 0. Type: integer
| |
| | ... | *Example:*
| | ... | \| Add Lb As Addresses \| ${dut1} \| 90.1.2.1 \| 192.168.60 \
| | ... | \| protocol=${17} \| port=${20000} \|
| |
| | [Arguments] | ${node} | ${vip_addr} | ${as_addr} | ${protocol}=${255}
| | ... | ${port}=${0} | ${is_del}=${0} | ${is_flush}=${0}
| |
| | FOR | ${number} | IN RANGE | 74 | 80
| | | VPP Lb Add Del As
| | | ... | ${node} | vip_addr=${vip_addr} | protocol=${protocol}
| | | ... | port=${port} | as_addr=${as_addr}.${number}
| | END
