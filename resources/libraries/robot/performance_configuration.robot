# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.DpdkUtil
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Library | resources.libraries.python.Classify
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/qemu.robot
| Resource | resources/libraries/robot/tagging.robot
| Documentation | Performance suite keywords - configuration.

*** Keywords ***
| Set interfaces in path in 2-node circular topology up
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on nodes in 2-node circular
| | ... | topology.*
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}

| Set interfaces in path in 3-node circular topology up
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology.*
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Vpp Node Interfaces Ready Wait | ${dut2}

| Initialize IPSec in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG and
| | ... | DUT1-DUT2 links. Set routing for encrypted traffic on both DUT nodes
| | ... | with prefix /8 and next hop of neighbour DUT or TG interface IPv4
| | ... | address.
| | ...
| | VPP Show Crypto Device Mapping | ${dut1}
| | VPP Show Crypto Device Mapping | ${dut2}
| | Set interfaces in path in 3-node circular topology up
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if1_mac}= | Get Interface MAC | ${dut1} | ${dut1_if1}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | ${dut2_if2_mac}= | Get Interface MAC | ${dut2} | ${dut2_if2}
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | Set Test Variable | ${tg_if1_mac}
| | Set Test Variable | ${tg_if2_mac}
| | Set Test Variable | ${dut1_if1_mac}
| | Set Test Variable | ${dut1_if2_mac}
| | Set Test Variable | ${dut2_if1_mac}
| | Set Test Variable | ${dut2_if2_mac}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | ${dut1_if1_ip4} | 24
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | ${dut1_if2_ip4} | 24
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1}
| | ... | ${dut2_if1_ip4} | 24
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2}
| | ... | ${dut2_if2_ip4} | 24
| | Add arp on dut | ${dut1} | ${dut1_if1} | ${tg_if1_ip4} | ${tg_if1_mac}
| | Add arp on dut | ${dut1} | ${dut1_if2} | ${dut2_if1_ip4} | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if2} | ${tg_if2_ip4} | ${tg_if2_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | ${dut1_if2_ip4} | ${dut1_if2_mac}
| | Vpp Route Add | ${dut1} | ${laddr_ip4} | 8 | ${tg_if1_ip4} | ${dut1_if1}
| | Vpp Route Add | ${dut2} | ${raddr_ip4} | 8 | ${tg_if2_ip4} | ${dut2_if2}

| Initialize IPv4 forwarding in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG links and
| | ... | /30 prefix on DUT1-DUT2 link. Set routing on both DUT nodes with
| | ... | prefix /24 and next hop of neighbour DUT interface IPv4 address.
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | dut1_v4.set_arp | ${dut1_if1} | 10.10.10.2 | ${tg1_if1_mac}
| | dut1_v4.set_arp | ${dut1_if2} | 1.1.1.2 | ${dut2_if1_mac}
| | dut2_v4.set_arp | ${dut2_if1} | 1.1.1.1 | ${dut1_if2_mac}
| | dut2_v4.set_arp | ${dut2_if2} | 20.20.20.2 | ${tg1_if2_mac}
| | dut1_v4.set_ip | ${dut1_if1} | 10.10.10.1 | 24
| | dut1_v4.set_ip | ${dut1_if2} | 1.1.1.1 | 30
| | dut2_v4.set_ip | ${dut2_if1} | 1.1.1.2 | 30
| | dut2_v4.set_ip | ${dut2_if2} | 20.20.20.1 | 24
| | dut1_v4.set_route | 20.20.20.0 | 24 | 1.1.1.2 | ${dut1_if2}
| | dut2_v4.set_route | 10.10.10.0 | 24 | 1.1.1.1 | ${dut2_if1}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize IPv4 forwarding in 2-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG links and
| | ... | /30 prefix on DUT1 link. Set routing on DUT node with prefix /24 and
| | ... | next hop of neighbour DUT interface IPv4 address.
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | dut1_v4.set_arp | ${dut1_if1} | 10.10.10.3 | ${tg1_if1_mac}
| | dut1_v4.set_arp | ${dut1_if2} | 20.20.20.3 | ${tg1_if2_mac}
| | dut1_v4.set_ip | ${dut1_if1} | 10.10.10.2 | 24
| | dut1_v4.set_ip | ${dut1_if2} | 20.20.20.2 | 24
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize IPv4 forwarding with scaling in 3-node circular topology
| | [Documentation]
| | ... | Custom setup of IPv4 topology with scalability of ip routes on all
| | ... | DUT nodes in 3-node circular topology
| | ...
| | ... | *Arguments:*
| | ... | - ${count} - IP route count. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv4 forwarding with scaling in 3-node circular \
| | ... | topology \| 100000 \|
| | ...
| | [Arguments] | ${count}
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Add arp on dut | ${dut1} | ${dut1_if1} | 1.1.1.1 | ${tg1_if1_mac}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 2.2.2.2 | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | 2.2.2.1 | ${dut1_if2_mac}
| | Add arp on dut | ${dut2} | ${dut2_if2} | 3.3.3.1 | ${tg1_if2_mac}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1} | 1.1.1.2 | 30
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 2.2.2.1 | 30
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 2.2.2.2 | 30
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2} | 3.3.3.2 | 30
| | Vpp Route Add | ${dut1} | 10.0.0.0 | 32 | 1.1.1.1 | ${dut1_if1}
| | ... | count=${count}
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 32 | 2.2.2.2 | ${dut1_if2}
| | ... | count=${count}
| | Vpp Route Add | ${dut2} | 10.0.0.0 | 32 | 2.2.2.1 | ${dut2_if1}
| | ... | count=${count}
| | Vpp Route Add | ${dut2} | 20.0.0.0 | 32 | 3.3.3.1 | ${dut2_if2}
| | ... | count=${count}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize IPv4 forwarding with vhost in 3-node circular topology
| | [Documentation]
| | ... | Create vhost-user interfaces in VPP. Set UP state of all VPP
| | ... | interfaces in path on nodes in 3-node circular topology. Create 2
| | ... | FIB tables on each DUT with multipath routing. Assign pair of
| | ... | Physical and Virtual interfaces on both nodes to each FIB table.
| | ... | Setup IPv4 addresses with /30 prefix on DUT-TG links and /30 prefix
| | ... | on DUT1-DUT2 link. Set routing on all DUT nodes in all FIB tables
| | ... | with prefix /24 and next hop of neighbour IPv4 address. Setup
| | ... | ARP on all VPP interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - sock1 - Sock path for first Vhost-User interface. Type: string
| | ... | - sock2 - Sock path for second Vhost-User interface. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 forwarding with vhost initialized in a 3-node circular \
| | ... | topology \| /tmp/sock1 \| /tmp/sock2 \|
| | ...
| | [Arguments] | ${sock1} | ${sock2}
| | ...
| | Set interfaces in path in 3-node circular topology up
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | ${sock1} | ${sock2}
| | ${dut1_vif1}= | Set Variable | ${vhost_if1}
| | ${dut1_vif2}= | Set Variable | ${vhost_if2}
| | Set Interface State | ${dut1} | ${dut1_vif1} | up
| | Set Interface State | ${dut1} | ${dut1_vif2} | up
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | ${sock1} | ${sock2}
| | ${dut2_vif1}= | Set Variable | ${vhost_if1}
| | ${dut2_vif2}= | Set Variable | ${vhost_if2}
| | Set Interface State | ${dut2} | ${dut2_vif1} | up
| | Set Interface State | ${dut2} | ${dut2_vif2} | up
| | ${dut1_vif1_idx}= | Get Interface SW Index | ${dut1} | ${dut1_vif1}
| | ${dut1_vif2_idx}= | Get Interface SW Index | ${dut1} | ${dut1_vif2}
| | ${dut1_if1_idx}= | Get Interface SW Index | ${dut1} | ${dut1_if1}
| | ${dut1_if2_idx}= | Get Interface SW Index | ${dut1} | ${dut1_if2}
| | ${dut2_vif1_idx}= | Get Interface SW Index | ${dut2} | ${dut2_vif1}
| | ${dut2_vif2_idx}= | Get Interface SW Index | ${dut2} | ${dut2_vif2}
| | ${dut2_if1_idx}= | Get Interface SW Index | ${dut2} | ${dut2_if1}
| | ${dut2_if2_idx}= | Get Interface SW Index | ${dut2} | ${dut2_if2}
| | Add fib table | ${dut1} | 20.20.20.0 | 24 | ${fib_table_1}
| | ... | via 4.4.4.2 sw_if_index ${dut1_vif1_idx} multipath
| | Add fib table | ${dut1} | 10.10.10.0 | 24 | ${fib_table_1}
| | ... | via 1.1.1.2 sw_if_index ${dut1_if1_idx} multipath
| | Add fib table | ${dut1} | 20.20.20.0 | 24 | ${fib_table_2}
| | ... | via 2.2.2.2 sw_if_index ${dut1_if2_idx} multipath
| | Add fib table | ${dut1} | 10.10.10.0 | 24 | ${fib_table_2}
| | ... | via 5.5.5.2 sw_if_index ${dut1_vif2_idx} multipath
| | Add fib table | ${dut2} | 10.10.10.0 | 24 | ${fib_table_1}
| | ... | via 2.2.2.1 sw_if_index ${dut2_if1_idx} multipath
| | Add fib table | ${dut2} | 20.20.20.0 | 24 | ${fib_table_1}
| | ... | via 4.4.4.1 sw_if_index ${dut2_vif1_idx} multipath
| | Add fib table | ${dut2} | 10.10.10.0 | 24 | ${fib_table_2}
| | ... | via 5.5.5.2 sw_if_index ${dut2_vif2_idx} multipath
| | Add fib table | ${dut2} | 20.20.20.0 | 24 | ${fib_table_2}
| | ... | via 3.3.3.2 sw_if_index ${dut2_if2_idx} multipath
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_vif1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if2} | ${fib_table_2}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_vif2} | ${fib_table_2}
| | Assign Interface To Fib Table | ${dut2} | ${dut2_if1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut2} | ${dut2_vif1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut2} | ${dut2_if2} | ${fib_table_2}
| | Assign Interface To Fib Table | ${dut2} | ${dut2_vif2} | ${fib_table_2}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1} | 1.1.1.2 | 30
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 2.2.2.1 | 30
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_vif1} | 4.4.4.1 | 30
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_vif2} | 5.5.5.1 | 30
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 2.2.2.2 | 30
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2} | 3.3.3.1 | 30
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_vif1} | 4.4.4.1 | 30
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_vif2} | 5.5.5.1 | 30
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | ${dut1_vif1_mac}= | Get Vhost User Mac By Sw Index | ${dut1}
| | ... | ${dut1_vif1_idx}
| | ${dut1_vif2_mac}= | Get Vhost User Mac By Sw Index | ${dut1}
| | ... | ${dut1_vif2_idx}
| | ${dut2_vif1_mac}= | Get Vhost User Mac By Sw Index | ${dut2}
| | ... | ${dut2_vif1_idx}
| | ${dut2_vif2_mac}= | Get Vhost User Mac By Sw Index | ${dut2}
| | ... | ${dut2_vif2_idx}
| | Set Test Variable | ${dut1_vif1_mac}
| | Set Test Variable | ${dut1_vif2_mac}
| | Set Test Variable | ${dut2_vif1_mac}
| | Set Test Variable | ${dut2_vif2_mac}
| | Add arp on dut | ${dut1} | ${dut1_if1} | 1.1.1.1 | ${tg1_if1_mac}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 2.2.2.2 | ${dut2_if1_mac}
| | Add arp on dut | ${dut1} | ${dut1_vif1} | 4.4.4.2 | 52:54:00:00:04:01
| | Add arp on dut | ${dut1} | ${dut1_vif2} | 5.5.5.2 | 52:54:00:00:04:02
| | Add arp on dut | ${dut2} | ${dut2_if1} | 2.2.2.1 | ${dut1_if2_mac}
| | Add arp on dut | ${dut2} | ${dut2_if2} | 3.3.3.2 | ${tg1_if2_mac}
| | Add arp on dut | ${dut2} | ${dut2_vif1} | 4.4.4.2 | 52:54:00:00:04:01
| | Add arp on dut | ${dut2} | ${dut2_vif2} | 5.5.5.2 | 52:54:00:00:04:02
| | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | 4.4.4.2 | ${dut1_vif1}
| | ... | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 10.10.10.0 | 24 | 1.1.1.1 | ${dut1_if1}
| | ... | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | 2.2.2.2 | ${dut1_if2}
| | ... | vrf=${fib_table_2}
| | Vpp Route Add | ${dut1} | 10.10.10.0 | 24 | 5.5.5.2 | ${dut1_vif2}
| | ... | vrf=${fib_table_2}
| | Vpp Route Add | ${dut2} | 20.20.20.0 | 24 | 4.4.4.2 | ${dut2_vif1}
| | ... | vrf=${fib_table_1}
| | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | 2.2.2.1 | ${dut2_if1}
| | ... | vrf=${fib_table_1}
| | Vpp Route Add | ${dut2} | 20.20.20.0 | 24 | 3.3.3.2 | ${dut2_if2}
| | ... | vrf=${fib_table_2}
| | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | 5.5.5.2 | ${dut2_vif2}
| | ... | vrf=${fib_table_2}

| Initialize IPv4 forwarding with vhost for '${nr}' VMs in 3-node circular topology
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on all
| | ... | VPP nodes. Set UP state of all VPP interfaces in path. Create ${nr}+1
| | ... | FIB tables on each DUT with multipath routing. Assign each Virtual
| | ... | interface to FIB table with Physical interface or Virtual interface on
| | ... | both nodes. Setup IPv4 addresses with /30 prefix on DUT-TG links and
| | ... | /30 prefix on DUT1-DUT2 link. Set routing on all DUT nodes in all FIB
| | ... | tables with prefix /24 and next hop of neighbour IPv4 address. Setup
| | ... | ARP on all VPP interfaces.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /tmp/sock-${VM_ID}-1
| | ... | - /tmp/sock-${VM_ID}-2
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 forwarding with Vhost-User for '2' VMs initialized in \
| | ... | a 3-node circular topology \|
| | ...
| | Set interfaces in path in 3-node circular topology up
| | ${fib_table_1}= | Set Variable | ${101}
| | ${fib_table_2}= | Evaluate | ${fib_table_1}+${nr}
| | ${dut1_if1_idx}= | Get Interface SW Index | ${dut1} | ${dut1_if1}
| | ${dut1_if2_idx}= | Get Interface SW Index | ${dut1} | ${dut1_if2}
| | Add fib table | ${dut1} | 10.10.10.0 | 24 | ${fib_table_1}
| | ... | via 1.1.1.2 sw_if_index ${dut1_if1_idx} multipath
| | Add fib table | ${dut1} | 20.20.20.0 | 24 | ${fib_table_2}
| | ... | via 2.2.2.2 sw_if_index ${dut1_if2_idx} multipath
| | ${dut2_if1_idx}= | Get Interface SW Index | ${dut2} | ${dut2_if1}
| | ${dut2_if2_idx}= | Get Interface SW Index | ${dut2} | ${dut2_if2}
| | Add fib table | ${dut2} | 10.10.10.0 | 24 | ${fib_table_1}
| | ... | via 2.2.2.1 sw_if_index ${dut2_if1_idx} multipath
| | Add fib table | ${dut2} | 20.20.20.0 | 24 | ${fib_table_2}
| | ... | via 3.3.3.2 sw_if_index ${dut2_if2_idx} multipath
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if2} | ${fib_table_2}
| | Assign Interface To Fib Table | ${dut2} | ${dut2_if1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut2} | ${dut2_if2} | ${fib_table_2}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1} | 1.1.1.2 | 30
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 2.2.2.1 | 30
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 2.2.2.2 | 30
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2} | 3.3.3.1 | 30
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Add arp on dut | ${dut1} | ${dut1_if1} | 1.1.1.1 | ${tg1_if1_mac}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 2.2.2.2 | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | 2.2.2.1 | ${dut1_if2_mac}
| | Add arp on dut | ${dut2} | ${dut2_if2} | 3.3.3.2 | ${tg1_if2_mac}
| | Vpp Route Add | ${dut1} | 10.10.10.0 | 24 | 1.1.1.1 | ${dut1_if1}
| | ... | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | 2.2.2.2 | ${dut1_if2}
| | ... | vrf=${fib_table_2}
| | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | 2.2.2.1 | ${dut2_if1}
| | ... | vrf=${fib_table_1}
| | Vpp Route Add | ${dut2} | 20.20.20.0 | 24 | 3.3.3.2 | ${dut2_if2}
| | ... | vrf=${fib_table_2}
| | ${ip_base_start}= | Set Variable | ${4}
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| | | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| | | ${fib_table_1}= | Evaluate | ${100}+${number}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1}+${1}
| | | ${ip_base_vif1}= | Evaluate | ${ip_base_start}+(${number}-1)*2
| | | ${ip_base_vif2}= | Evaluate | ${ip_base_vif1}+1
| | | ${ip_net_vif1}= | Set Variable
| | | ... | ${ip_base_vif1}.${ip_base_vif1}.${ip_base_vif1}
| | | ${ip_net_vif2}= | Set Variable
| | | ... | ${ip_base_vif2}.${ip_base_vif2}.${ip_base_vif2}
| | | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | | ... | ${sock1} | ${sock2} | dut1-vhost-${number}-if1
| | | ... | dut1-vhost-${number}-if2
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if1} | up
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if2} | up
| | | ${dut1_vif1_idx}= | Get Interface SW Index | ${dut1}
| | | ... | ${dut1-vhost-${number}-if1}
| | | ${dut1_vif2_idx}= | Get Interface SW Index | ${dut1}
| | | ... | ${dut1-vhost-${number}-if2}
| | | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | | ... | ${sock1} | ${sock2} | dut2-vhost-${number}-if1
| | | ... | dut2-vhost-${number}-if2
| | | Set Interface State | ${dut2} | ${dut2-vhost-${number}-if1} | up
| | | Set Interface State | ${dut2} | ${dut2-vhost-${number}-if2} | up
| | | ${dut2_vif1_idx}= | Get Interface SW Index | ${dut2}
| | | ... | ${dut2-vhost-${number}-if1}
| | | ${dut2_vif2_idx}= | Get Interface SW Index | ${dut2}
| | | ... | ${dut2-vhost-${number}-if2}
| | | Add fib table | ${dut1} | 20.20.20.0 | 24 | ${fib_table_1}
| | | ... | via ${ip_net_vif1}.1 sw_if_index ${dut1_vif1_idx} multipath
| | | Add fib table | ${dut1} | 10.10.10.0 | 24 | ${fib_table_2}
| | | ... | via ${ip_net_vif2}.2 sw_if_index ${dut1_vif2_idx} multipath
| | | Add fib table | ${dut2} | 20.20.20.0 | 24 | ${fib_table_1}
| | | ... | via ${ip_net_vif1}.1 sw_if_index ${dut2_vif1_idx} multipath
| | | Add fib table | ${dut2} | 10.10.10.0 | 24 | ${fib_table_2}
| | | ... | via ${ip_net_vif2}.2 sw_if_index ${dut2_vif2_idx} multipath
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | ${fib_table_1}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | ${fib_table_2}
| | | Assign Interface To Fib Table | ${dut2} | ${dut2-vhost-${number}-if1}
| | | ... | ${fib_table_1}
| | | Assign Interface To Fib Table | ${dut2} | ${dut2-vhost-${number}-if2}
| | | ... | ${fib_table_2}
| | | Configure IP addresses on interfaces
| | | ... | ${dut1} | ${dut1-vhost-${number}-if1} | ${ip_net_vif1}.1 | 30
| | | ... | ${dut1} | ${dut1-vhost-${number}-if2} | ${ip_net_vif2}.1 | 30
| | | ... | ${dut2} | ${dut2-vhost-${number}-if1} | ${ip_net_vif1}.1 | 30
| | | ... | ${dut2} | ${dut2-vhost-${number}-if2} | ${ip_net_vif2}.1 | 30
| | | ${dut1_vif1_mac}= | Get Vhost User Mac By Sw Index | ${dut1}
| | | ... | ${dut1_vif1_idx}
| | | ${dut1_vif2_mac}= | Get Vhost User Mac By Sw Index | ${dut1}
| | | ... | ${dut1_vif2_idx}
| | | ${dut2_vif1_mac}= | Get Vhost User Mac By Sw Index | ${dut2}
| | | ... | ${dut2_vif1_idx}
| | | ${dut2_vif2_mac}= | Get Vhost User Mac By Sw Index | ${dut2}
| | | ... | ${dut2_vif2_idx}
| | | Set Test Variable | ${dut1-vhost-${number}-if1_mac}
| | | ... | ${dut1_vif1_mac}
| | | Set Test Variable | ${dut1-vhost-${number}-if2_mac}
| | | ... | ${dut1_vif2_mac}
| | | Set Test Variable | ${dut2-vhost-${number}-if1_mac}
| | | ... | ${dut2_vif1_mac}
| | | Set Test Variable | ${dut2-vhost-${number}-if2_mac}
| | | ... | ${dut2_vif2_mac}
| | | ${qemu_id}= | Set Variable If | ${number} < 10 | 0${number}
| | | ... | ${number}
| | | Add arp on dut | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | ${ip_net_vif1}.2 | 52:54:00:00:${qemu_id}:01
| | | Add arp on dut | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | ${ip_net_vif2}.2 | 52:54:00:00:${qemu_id}:02
| | | Add arp on dut | ${dut2} | ${dut2-vhost-${number}-if1}
| | | ... | ${ip_net_vif1}.2 | 52:54:00:00:${qemu_id}:01
| | | Add arp on dut | ${dut2} | ${dut2-vhost-${number}-if2}
| | | ... | ${ip_net_vif2}.2 | 52:54:00:00:${qemu_id}:02
| | | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | ${ip_net_vif1}.2
| | | ... | ${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Vpp Route Add | ${dut1} | 10.10.10.0 | 24 | ${ip_net_vif2}.2
| | | ... | ${dut1-vhost-${number}-if2} | vrf=${fib_table_2}
| | | Vpp Route Add | ${dut2} | 20.20.20.0 | 24 | ${ip_net_vif1}.2
| | | ... | ${dut2-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | ${ip_net_vif2}.2
| | | ... | ${dut2-vhost-${number}-if2} | vrf=${fib_table_2}

| Initialize IPv4 policer 2r3c-${t} in 3-node circular topology
| | [Documentation]
| | ... | Setup of 2r3c color-aware or color-blind policer with dst ip match
| | ... | on all DUT nodes in 3-node circular topology. Policer is applied on
| | ... | links TG - DUT1 and DUT2 - TG.
| | ...
| | ${dscp}= | DSCP AF22
| | Policer Set Name | policer1
| | Policer Set CIR | ${cir}
| | Policer Set EIR | ${eir}
| | Policer Set CB | ${cb}
| | Policer Set EB | ${eb}
| | Policer Set Rate Type pps
| | Policer Set Round Type Closest
| | Policer Set Type 2R3C 2698
| | Policer Set Conform Action Transmit
| | Policer Set Exceed Action Mark and Transmit | ${dscp}
| | Policer Set Violate Action Transmit
| | Policer Enable Color Aware
| | Run Keyword If | ${t} == 'ca' | Policer Enable Color Aware
| | Policer Classify Set Precolor Exceed
| | Policer Set Node | ${dut1}
| | Policer Classify Set Interface | ${dut1_if1}
| | Policer Classify Set Match IP | 20.20.20.2 | ${False}
| | Policer Set Configuration
| | Policer Set Node | ${dut2}
| | Policer Classify Set Interface | ${dut2_if2}
| | Policer Classify Set Match IP | 10.10.10.2 | ${False}
| | Policer Set Configuration

| Initialize IPv6 forwarding in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup neighbour on all
| | ... | VPP interfaces. Setup IPv6 addresses with /128 prefixes on all
| | ... | interfaces. Set routing on both DUT nodes with prefix /64 and
| | ... | next hop of neighbour DUT interface IPv6 address.
| | ...
| | ${prefix}= | Set Variable | 64
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if1} | 2001:1::1 | ${prefix}
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if2} | 2001:3::1 | ${prefix}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if1} | 2001:3::2 | ${prefix}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if2} | 2001:2::1 | ${prefix}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | Add Ip Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg1_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg1_if2_mac}
| | Add Ip Neighbor | ${dut1} | ${dut1_if2} | 2001:3::2 | ${dut2_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if1} | 2001:3::1 | ${dut1_if2_mac}
| | Vpp Route Add | ${dut1} | 2001:2::0 | ${prefix} | 2001:3::2 | ${dut1_if2}
| | Vpp Route Add | ${dut2} | 2001:1::0 | ${prefix} | 2001:3::1 | ${dut2_if1}

| Initialize IPv6 forwarding with scaling in 3-node circular topology
| | [Documentation]
| | ... | Custom setup of IPv6 topology with scalability of ip routes on all
| | ... | DUT nodes in 3-node circular topology
| | ...
| | ... | *Arguments:*
| | ... | - ${count} - IP route count. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv6 forwarding with scaling in 3-node circular \
| | ... | topology \| 100000 \|
| | ...
| | [Arguments] | ${count}
| | ...
| | ${subn_prefix}= | Set Variable | 64
| | ${host_prefix}= | Set Variable | 128
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if1} | 2001:3::1 | ${subn_prefix}
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if2} | 2001:4::1 | ${subn_prefix}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if1} | 2001:4::2 | ${subn_prefix}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if2} | 2001:5::1 | ${subn_prefix}
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | Add Ip Neighbor | ${dut1} | ${dut1_if1} | 2001:3::2 | ${tg1_if1_mac}
| | Add Ip Neighbor | ${dut1} | ${dut1_if2} | 2001:4::2 | ${dut2_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if1} | 2001:4::1 | ${dut1_if2_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if2} | 2001:5::2 | ${tg1_if2_mac}
| | Vpp Route Add | ${dut1} | 2001:2::0 | ${host_prefix} | 2001:4::2
| | ... | interface=${dut1_if2} | count=${count}
| | Vpp Route Add | ${dut1} | 2001:1::0 | ${host_prefix} | 2001:3::2
| | ... | interface=${dut1_if1} | count=${count}
| | Vpp Route Add | ${dut2} | 2001:1::0 | ${host_prefix} | 2001:4::1
| | ... | interface=${dut2_if1} | count=${count}
| | Vpp Route Add | ${dut2} | 2001:2::0 | ${host_prefix} | 2001:5::2
| | ... | interface=${dut2_if2} | count=${count}

| Initialize IPv6 iAcl whitelist in 3-node circular topology
| | [Documentation]
| | ... | Creates classify L3 table on DUTs. IPv6 iAcl security whitelist
| | ... | ingress /64 filter entries applied on links TG - DUT1 and DUT2 - TG.
| | ...
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip6 | dst
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n}
| | ... | ip6 | dst | 2001:2::2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if1} | ip6 | ${table_idx}
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut2} | ip6 | dst
| | And Vpp Configures Classify Session L3
| | ... | ${dut2} | permit | ${table_idx} | ${skip_n} | ${match_n}
| | ... | ip6 | dst | 2001:1::2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if2} | ip6 | ${table_idx}

| Initialize L2 xconnect in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology by cross connecting two interfaces on
| | ... | each DUT. Interfaces are brought up.
| | ... |
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure L2XC | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize L2 xconnect with VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology with VXLANoIPv4 by cross connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | between DUTs. VXLAN sub-interfaces has same IPv4 address as
| | ... | interfaces.
| | ...
| | Set interfaces in path in 3-node circular topology up
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 172.16.0.1 | 24
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 172.16.0.2 | 24
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 172.16.0.2 | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | 172.16.0.1 | ${dut1_if2_mac}
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${dut2s_vxlan}

| Initialize L2 xconnect with Vhost-User in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Cross
| | ... | connect each Vhost interface with one physical interface.
| | ...
| | ... | *Arguments:*
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 xconnect with Vhost-User initialized in a 3-node \
| | ... | circular topology \| /tmp/sock1 \| /tmp/sock2 \|
| | ...
| | [Arguments] | ${sock1} | ${sock2}
| | ...
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${vhost_if1}
| | Configure L2XC | ${dut1} | ${dut1_if2} | ${vhost_if2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | ${sock1} | ${sock2}
| | Configure L2XC | ${dut2} | ${dut2_if1} | ${vhost_if1}
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${vhost_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize L2 xconnect with Vhost-User for '${nr}' in 3-node circular topology
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces on all defined VPP nodes. Cross
| | ... | connect each Vhost interface with one physical interface or virtual
| | ... | interface to create a chain accross DUT node.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /tmp/sock-${VM_ID}-1
| | ... | - /tmp/sock-${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 xconnect with Vhost-User for '2' initialized in a 3-node \
| | ... | circular topology \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| | | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| | | ${prev_index}= | Evaluate | ${number}-1
| | | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | | ... | ${sock1} | ${sock2} | dut1-vhost-${number}-if1
| | | ... | dut1-vhost-${number}-if2
| | | ${dut1_xconnect_if1}= | Set Variable If | ${number}==1 | ${dut1_if1}
| | | ... | ${dut1-vhost-${prev_index}-if2}
| | | Configure L2XC | ${dut1} | ${dut1_xconnect_if1}
| | | ... | ${dut1-vhost-${number}-if1}
| | | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | | ... | ${sock1} | ${sock2} | dut2-vhost-${number}-if1
| | | ... | dut2-vhost-${number}-if2
| | | ${dut2_xconnect_if1}= | Set Variable If | ${number}==1 | ${dut2_if1}
| | | ... | ${dut2-vhost-${prev_index}-if2}
| | | Configure L2XC | ${dut2} | ${dut2_xconnect_if1}
| | | ... | ${dut2-vhost-${number}-if1}
| | | Run Keyword If | ${number}==${nr} | Configure L2XC
| | | ... | ${dut1} | ${dut1-vhost-${number}-if2} | ${dut1_if2}
| | | Run Keyword If | ${number}==${nr} | Configure L2XC
| | | ... | ${dut2} | ${dut2-vhost-${number}-if2} | ${dut2_if2}

| Initialize L2 xconnect with Vhost-User and VLAN in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Cross
| | ... | connect each Vhost interface with one physical interface.
| | ... | Setup VLAN between DUTs. All interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 xconnect with Vhost-User and VLAN initialized in a 3-node\
| | ... | circular topology \| /tmp/sock1 \| /tmp/sock2 \| 10 \| pop-1 \|
| | ...
| | [Arguments] | ${sock1} | ${sock2} | ${subid} | ${tag_rewrite}
| | ...
| | Set interfaces in path in 3-node circular topology up
| | Initialize VLAN dot1q sub-interfaces in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${vhost_if1}
| | Configure L2XC | ${dut1} | ${subif_index_1} | ${vhost_if2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | ${sock1} | ${sock2}
| | Configure L2XC | ${dut2} | ${subif_index_2} | ${vhost_if1}
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${vhost_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize L2 bridge domain in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 DB topology by adding two interfaces on each DUT into BD
| | ... | that is created automatically with index 1. Learning is enabled.
| | ... | Interfaces are brought up.
| | ...
| | Configure L2BD forwarding | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure L2BD forwarding | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Configure IPv4 ACLs
| | [Documentation]
| | ... | TODO
| | ...
| | [Arguments] | ${dut} | ${dut_if1}=${None} | ${dut_if2}=${None}
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
| |      | ${src_ip_int} = | Evaluate | $src_ip_int + $ip_step
| |      | ${dst_ip_int} = | Evaluate | $dst_ip_int + $ip_step
| |      | ${sport}= | Evaluate | $sport + $port_step
| |      | ${dport}= | Evaluate | $dport + $port_step
| |      | ${ipv4_limit_reached}= | Set Variable If
| |      | ... | $src_ip_int > $ip_limit_int or $src_ip_int > $ip_limit_int
| |      | ... | ${True}
| |      | ${udp_limit_reached}= | Set Variable If
| |      | ... | $sport > $port_limit or $dport > $port_limit | ${True}
| |      | Run Keyword If | $ipv4_limit_reached is True | Log
| |      | ... | Can't do more iterations - IPv4 address limit has been reached.
| |      | ... | WARN
| |      | Run Keyword If | $udp_limit_reached is True | Log
| |      | ... | Can't do more iterations - UDP port limit has been reached.
| |      | ... | WARN
| |      | ${src_ip} = | Run Keyword If | $ipv4_limit_reached is True
| |      | ... | Set Variable | ${ip_limit}
| |      | ... | ELSE | Evaluate | str(ipaddress.ip_address($src_ip_int))
| |      | ... | modules=ipaddress
| |      | ${dst_ip} = | Run Keyword If | $ipv4_limit_reached is True
| |      | ... | Set Variable | ${ip_limit}
| |      | ... | ELSE | Evaluate | str(ipaddress.ip_address($dst_ip_int))
| |      | ... | modules=ipaddress
| |      | ${sport}= | Set Variable If | ${sport} > $port_limit | $port_limit
| |      | ... | ${sport}
| |      | ${dport}= | Set Variable If | ${dport} > $port_limit | $port_limit
| |      | ... | ${dport}
| |      | ${acl}= | Catenate | ${acl} | src ${src_ip}/32 dst ${dst_ip}/32
| |      | ... | sport ${sport} | dport ${dport},
| |      | Exit For Loop If
| |      | ... | $ipv4_limit_reached is True or $udp_limit_reached is True
| | ${acl}= | Catenate | ${acl}
| | ...     | ipv4 ${acl_action} src ${trex_stream1_subnet},
| | ...     | ipv4 ${acl_action} src ${trex_stream2_subnet}
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

| Initialize L2 bridge domain with IPv4 ACLs on DUT1 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 DB topology by adding two interfaces on DUT1 into BD
| | ... | that is created automatically with index 1. Learning is enabled.
| | ... | Interfaces are brought up.
| | ...
| | Configure L2BD forwarding | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure L2XC | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}
| | Configure IPv4 ACLs | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Initialize L2 bridge domains with Vhost-User in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Add each
| | ... | Vhost-User interface into L2 bridge domains with learning enabled
| | ... | with physical inteface.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id1 - Bridge domain ID. Type: integer
| | ... | - bd_id2 - Bridge domain ID. Type: integer
| | ... | - sock1 - Sock path for first Vhost-User interface. Type: string
| | ... | - sock2 - Sock path for second Vhost-User interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 bridge domains with Vhost-User initialized in a 3-node \
| | ... | circular topology \| 1 \| 2 \| /tmp/sock1 \| /tmp/sock2 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ...
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${dut1_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | ${sock1} | ${sock2}
| | Add interface to bridge domain | ${dut2} | ${dut2_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize L2 bridge domains with Vhost-User for '${nr}' VMs in 3-node circular topology
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on all
| | ... | defined VPP nodes. Add each Vhost-User interface into L2 bridge
| | ... | domains with learning enabled with physical inteface or Vhost-User
| | ... | interface of another VM.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /tmp/sock-${VM_ID}-1
| | ... | - /tmp/sock-${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 bridge domains with Vhost-User for '2' VMs initialized in \
| | ... | a 3-node circular topology \|
| | ...
| | ${bd_id2}= | Evaluate | ${nr}+1
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${1}
| | Add interface to bridge domain | ${dut1} | ${dut1_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${dut2_if1} | ${1}
| | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| | | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| | | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | | ... | ${sock1} | ${sock2} | dut1-vhost-${number}-if1
| | | ... | dut1-vhost-${number}-if2
| | | ${bd_id2}= | Evaluate | ${number}+1
| | | Add interface to bridge domain | ${dut1}
| | | ... | ${dut1-vhost-${number}-if1} | ${number}
| | | Add interface to bridge domain | ${dut1}
| | | ... | ${dut1-vhost-${number}-if2} | ${bd_id2}
| | | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | | ... | ${sock1} | ${sock2} | dut2-vhost-${number}-if1
| | | ... | dut2-vhost-${number}-if2
| | | Add interface to bridge domain | ${dut2}
| | | ... | ${dut2-vhost-${number}-if1} | ${number}
| | | Add interface to bridge domain | ${dut2}
| | | ... | ${dut2-vhost-${number}-if2} | ${bd_id2}

| Initialize L2 bridge domain with VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 bridge domain topology with VXLANoIPv4 by connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | between DUTs. VXLAN sub-interfaces has same IPv4 address as
| | ... | interfaces.
| | ...
| | Set interfaces in path in 3-node circular topology up
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 172.16.0.1
| | ... | 24
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 172.16.0.2
| | ... | 24
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 172.16.0.2 | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | 172.16.0.1 | ${dut1_if2_mac}
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Configure L2BD forwarding | ${dut1} | ${dut1_if1} | ${dut1s_vxlan}
| | Configure L2BD forwarding | ${dut2} | ${dut2_if2} | ${dut2s_vxlan}
| | All Vpp Interfaces Ready Wait | ${nodes}

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
| | ... | - sock1 - Sock path for first Vhost-User interface. Type: string
| | ... | - sock2 - Sock path for second Vhost-User interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 bridge domains with Vhost-User and VXLANoIPv4 initialized in a\
| | ... | 3-node circular topology \| 1 \| 2 \| /tmp/sock1 \| /tmp/sock2 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ...
| | Set interfaces in path in 3-node circular topology up
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 172.16.0.1
| | ... | 24
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 172.16.0.2
| | ... | 24
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1s_vxlan} | ${bd_id2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | ${sock1} | ${sock2}
| | Add interface to bridge domain | ${dut2} | ${dut2s_vxlan} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize L2 bridge domains with Vhost-User in 2-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Add each
| | ... | Vhost-User interface into L2 bridge domains with learning enabled
| | ... | with physical inteface.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id1 - Bridge domain ID. Type: integer
| | ... | - bd_id2 - Bridge domain ID. Type: integer
| | ... | - sock1 - Sock path for first Vhost-User interface. Type: string
| | ... | - sock2 - Sock path for second Vhost-User interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 bridge domains with Vhost-User initialized in a 2-node \
| | ... | circular topology \| 1 \| 2 \| /tmp/sock1 \| /tmp/sock2 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ...
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${dut1_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize L2 bridge domains with Vhost-User and VLAN in a 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Add each
| | ... | Vhost-User interface into L2 bridge domains with learning enabled
| | ... | with physical inteface.
| | ... | Setup VLAN between DUTs. All interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id1 - Bridge domain ID. Type: integer
| | ... | - bd_id2 - Bridge domain ID. Type: integer
| | ... | - sock1 - Sock path for first Vhost-User interface. Type: string
| | ... | - sock2 - Sock path for second Vhost-User interface. Type: string
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 bridge domains with Vhost-User and VLAN initialized in a 3-node\
| | ... | circular topology \| 1 \| 2 \| /tmp/sock1 \| /tmp/sock2 \| 10\
| | ... | pop-1 \|
| | ...
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2} | ${subid}
| | ... | ${tag_rewrite}
| | ...
| | Set interfaces in path in 3-node circular topology up
| | Initialize VLAN dot1q sub-interfaces in 3-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${subif_index_1} | ${bd_id2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | ${sock1} | ${sock2}
| | Add interface to bridge domain | ${dut2} | ${subif_index_2} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Add PCI devices to DUTs in 3-node single link topology
| | [Documentation]
| | ... | Add PCI devices to VPP configuration file.
| | ...
| | ${dut1_if1_pci}= | Get Interface PCI Addr | ${dut1} | ${dut1_if1}
| | ${dut1_if2_pci}= | Get Interface PCI Addr | ${dut1} | ${dut1_if2}
| | ${dut2_if1_pci}= | Get Interface PCI Addr | ${dut2} | ${dut2_if1}
| | ${dut2_if2_pci}= | Get Interface PCI Addr | ${dut2} | ${dut2_if2}
| | Run keyword | DUT1.Add DPDK Dev | ${dut1_if1_pci} | ${dut1_if2_pci}
| | Run keyword | DUT2.Add DPDK Dev | ${dut2_if1_pci} | ${dut2_if2_pci}

| Add PCI devices to DUTs in 2-node single link topology
| | [Documentation]
| | ... | Add PCI devices to VPP configuration file.
| | ...
| | ${dut1_if1_pci}= | Get Interface PCI Addr | ${dut1} | ${dut1_if1}
| | ${dut1_if2_pci}= | Get Interface PCI Addr | ${dut1} | ${dut1_if2}
| | Run keyword | DUT1.Add DPDK Dev | ${dut1_if1_pci} | ${dut1_if2_pci}

| Configure guest VM with dpdk-testpmd connected via vhost-user
| | [Documentation]
| | ... | Start QEMU guest with two vhost-user interfaces and interconnecting
| | ... | DPDK testpmd. Qemu Guest uses by default 5 cores and 2048M. Testpmd
| | ... | uses 5 cores (1 main core and 4 cores dedicated to io) mem-channel=4,
| | ... | txq/rxq=256, burst=64, disable-hw-vlan, disable-rss,
| | ... | driver usr/lib/librte_pmd_virtio.so and fwd mode is io.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node to start guest VM on. Type: dictionary
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - vm_name - QemuUtil instance name. Type: string
| | ... | - skip - Number of cpus which will be skipped. Type: integer
| | ... | - count - Number of cpus which will be allocated for qemu.
| | ... | Type: integer
| | ... | - qemu_id - Qemu Id when starting more then one guest VM on DUT node.
| | ... | Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure guest VM with dpdk-testpmd connected via vhost-user \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM \| ${6} \
| | ... | \| ${5} \|
| | ... | \| Configure guest VM with dpdk-testpmd connected via vhost-user \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock-2-1 \| /tmp/sock-2-2 \| DUT1_VM2 \
| | ... | \| qemu_id=${2} \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name} | ${skip}=${6}
| | ... | ${count}=${5} | ${qemu_id}=${1}
| | ...
| | Import Library | resources.libraries.python.QemuUtils | qemu_id=${qemu_id}
| | ... | WITH NAME | ${vm_name}
| | ${serial_port}= | Evaluate | ${qemu_id} + ${4555}
| | Run keyword | ${vm_name}.Qemu Set Serial Port | ${serial_port}
| | ${ssh_fwd_port}= | Evaluate | ${qemu_id} + ${10021}
| | Run keyword | ${vm_name}.Qemu Set Ssh Fwd Port | ${ssh_fwd_port}
| | ${dut_numa}= | Get interfaces numa node | ${dut_node}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${skip_cnt}= | Evaluate | ${skip} + (${qemu_id} - 1) * ${count}
| | ${qemu_cpus}= | Cpu slice of list per node | ${dut_node} | ${dut_numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${count} | smt_used=${False}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock2}
| | Run Keyword | ${vm_name}.Build QEMU | ${dut_node} | apply_patch=${True}
| | Run keyword | ${vm_name}.Qemu Set Bin | ${perf_qemu_bin}
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Dpdk Testpmd Start | ${vm} | eal_coremask=0x1f | eal_mem_channels=4
| | ... | pmd_fwd_mode=io | pmd_disable_hw_vlan=${True}
| | ... | pmd_txd=${perf_qemu_qsz} | pmd_rxd=${perf_qemu_qsz}
| | Return From Keyword | ${vm}

| Configure '${nr}' guest VMs with dpdk-testpmd connected via vhost-user in 3-node circular topology
| | [Documentation]
| | ... | Start QEMU guests with two vhost-user interfaces and interconnecting
| | ... | DPDK testpmd for defined number of VMs on all defined VPP nodes.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | _NOTE:_ This KW expects following test case variables to be set:
| | ... | - ${system_cpus} - Number of CPUs allocated for OS itself.
| | ... | - ${vpp_cpus} - Number of CPUs allocated for VPP.
| | ... | - ${vm_cpus} - Number of CPUs to be allocated per QEMU instance.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| '2' Configure guest VM with dpdk-testpmd connected via vhost-user \
| | ... | in a 3-node circular topology \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| | | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| | | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
| | | ${vm1}= | Configure guest VM with dpdk-testpmd connected via vhost-user
| | | ... | ${dut1} | ${sock1} | ${sock2} | DUT1_VM${number}
| | | ... | skip=${skip_cpus} | count=${vm_cpus} | qemu_id=${number}
| | | Set To Dictionary | ${dut1_vm_refs} | DUT1_VM${number} | ${vm1}
| | | ${vm2}= | Configure guest VM with dpdk-testpmd connected via vhost-user
| | | ... | ${dut2} | ${sock1} | ${sock2} | DUT2_VM${number}
| | | ... | skip=${skip_cpus} | count=${vm_cpus} | qemu_id=${number}
| | | Set To Dictionary | ${dut2_vm_refs} | DUT2_VM${number} | ${vm2}

| Configure guest VM with dpdk-testpmd using SMT connected via vhost-user
| | [Documentation]
| | ... | Start QEMU guest with two vhost-user interfaces and interconnecting
| | ... | DPDK testpmd. Qemu Guest uses by default 5 cores and 2048M. Testpmd
| | ... | uses 5 cores (1 main core and 4 cores dedicated to io) mem-channel=4,
| | ... | txq/rxq=256, burst=64, disable-hw-vlan, disable-rss,
| | ... | driver usr/lib/librte_pmd_virtio.so and fwd mode is io.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node to start guest VM on. Type: dictionary
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - vm_name - QemuUtil instance name. Type: string
| | ... | - skip - number of cpus which will be skipped. Type: int
| | ... | - count - number of cpus which will be allocated for qemu. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Guest VM with dpdk-testpmd using SMT connected via vhost-user is \
| | ... | setup \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM \
| | ... | \| ${6} \| ${5} \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name} | ${skip}=${6}
| | ... | ${count}=${5}
| | ...
| | Import Library | resources.libraries.python.QemuUtils
| | ... | WITH NAME | ${vm_name}
| | ${dut_numa}= | Get interfaces numa node | ${dut_node}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${qemu_cpus}= | Cpu slice of list per node | ${dut_node} | ${dut_numa}
| | ... | skip_cnt=${skip} | cpu_cnt=${count} | smt_used=${True}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock2}
| | Run Keyword | ${vm_name}.Build QEMU | ${dut_node} | apply_patch=${True}
| | Run keyword | ${vm_name}.Qemu Set Bin | ${perf_qemu_bin}
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Dpdk Testpmd Start | ${vm} | eal_coremask=0x1f | eal_mem_channels=4
| | ... | pmd_fwd_mode=io | pmd_disable_hw_vlan=${True}
| | ... | pmd_txd=${perf_qemu_qsz} | pmd_rxd=${perf_qemu_qsz}
| | Return From Keyword | ${vm}

| Configure guest VM with dpdk-testpmd-mac connected via vhost-user
| | [Documentation]
| | ... | Start QEMU guest with two vhost-user interfaces and interconnecting
| | ... | DPDK testpmd. Qemu Guest uses by default 5 cores and 2048M. Testpmd
| | ... | uses 5 cores (1 main core and 4 cores dedicated to io) mem-channel=4,
| | ... | txq/rxq=256, burst=64, disable-hw-vlan, disable-rss,
| | ... | driver usr/lib/librte_pmd_virtio.so and fwd mode is mac rewrite.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node to start guest VM on. Type: dictionary
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - vm_name - QemuUtil instance name. Type: string
| | ... | - eth0_mac - MAC address of first Vhost interface. Type: string
| | ... | - eth1_mac - MAC address of second Vhost interface. Type: string
| | ... | - skip - number of cpus which will be skipped. Type: integer
| | ... | - count - number of cpus which will be allocated for qemu.
| | ... | Type: integer
| | ... | - qemu_id - Qemu Id when starting more then one guest VM on DUT node.
| | ... | Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Guest VM with dpdk-testpmd for Vhost L2BD forwarding is setup \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM \
| | ... | \| 00:00:00:00:00:01 \| 00:00:00:00:00:02 \| ${6} \| ${5} \|
| | ... | \| Guest VM with dpdk-testpmd for Vhost L2BD forwarding is setup \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock-2-1 \| /tmp/sock-2-2 \| DUT1_VM2 \
| | ... | \| 00:00:00:00:02:01 \| 00:00:00:00:02:02 \| ${6} \| ${5} \
| | ... | \| qemu_id=${2} \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name}
| | ... | ${eth0_mac} | ${eth1_mac} | ${skip}=${6} | ${count}=${5}
| | ... | ${qemu_id}=${1}
| | ...
| | Import Library | resources.libraries.python.QemuUtils | qemu_id=${qemu_id}
| | ... | WITH NAME | ${vm_name}
| | ${serial_port}= | Evaluate | ${qemu_id} + ${4555}
| | Run keyword | ${vm_name}.Qemu Set Serial Port | ${serial_port}
| | ${ssh_fwd_port}= | Evaluate | ${qemu_id} + ${10021}
| | Run keyword | ${vm_name}.Qemu Set Ssh Fwd Port | ${ssh_fwd_port}
| | ${dut_numa}= | Get interfaces numa node | ${dut_node}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${skip_cnt}= | Evaluate | ${skip} + (${qemu_id} - 1) * ${count}
| | ${qemu_cpus}= | Cpu slice of list per node | ${dut_node} | ${dut_numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${count} | smt_used=${False}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock2}
| | Run Keyword | ${vm_name}.Build QEMU | ${dut_node} | apply_patch=${True}
| | Run keyword | ${vm_name}.Qemu Set Bin | ${perf_qemu_bin}
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Dpdk Testpmd Start | ${vm} | eal_coremask=0x1f
| | ... | eal_mem_channels=4 | pmd_fwd_mode=mac | pmd_eth_peer_0=0,${eth0_mac}
| | ... | pmd_eth_peer_1=1,${eth1_mac} | pmd_disable_hw_vlan=${True}
| | ... | pmd_txd=${perf_qemu_qsz} | pmd_rxd=${perf_qemu_qsz}
| | Return From Keyword | ${vm}

| Configure '${nr}' guest VMs with dpdk-testpmd-mac connected via vhost-user in 3-node circular topology
| | [Documentation]
| | ... | Start QEMU guests with two vhost-user interfaces and interconnecting
| | ... | DPDK testpmd with fwd mode set to mac rewrite for defined number of
| | ... | VMs on all defined VPP nodes.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | _NOTE:_ This KW expects following test case variables to be set:
| | ... | - ${system_cpus} - Number of CPUs allocated for OS itself.
| | ... | - ${vpp_cpus} - Number of CPUs allocated for VPP.
| | ... | - ${vm_cpus} - Number of CPUs to be allocated per QEMU instance.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| '2' Guest VMs with dpdk-testpmd-mac connected via vhost-user is \
| | ... | setup in a 3-node circular topology \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| | | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| | | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| | | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
| | | ${vm1}=
| | | ... | Configure guest VM with dpdk-testpmd-mac connected via vhost-user
| | | ... | ${dut1} | ${sock1} | ${sock2} | DUT1_VM${number}
| | | ... | ${dut1-vhost-${number}-if1_mac}
| | | ... | ${dut1-vhost-${number}-if2_mac} | skip=${skip_cpus}
| | | ... | count=${vm_cpus} | qemu_id=${number}
| | | Set To Dictionary | ${dut1_vm_refs} | DUT1_VM${number} | ${vm1}
| | | ${vm2}=
| | | ... | Configure guest VM with dpdk-testpmd-mac connected via vhost-user
| | | ... | ${dut2} | ${sock1} | ${sock2} | DUT2_VM${number}
| | | ... | ${dut2-vhost-${number}-if1_mac}
| | | ... | ${dut2-vhost-${number}-if2_mac} | skip=${skip_cpus}
| | | ... | count=${vm_cpus} | qemu_id=${number}
| | | Set To Dictionary | ${dut2_vm_refs} | DUT2_VM${number} | ${vm2}

| Configure guest VM with dpdk-testpmd-mac using SMT connected via vhost-user
| | [Documentation]
| | ... | Start QEMU guest with two vhost-user interfaces and interconnecting
| | ... | DPDK testpmd. Qemu Guest uses by default 5 cores and 2048M. Testpmd
| | ... | uses 5 cores (1 main core and 4 cores dedicated to io) mem-channel=4,
| | ... | txq/rxq=256, burst=64, disable-hw-vlan, disable-rss,
| | ... | driver usr/lib/librte_pmd_virtio.so and fwd mode is mac rewrite.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node to start guest VM on. Type: dictionary
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - vm_name - QemuUtil instance name. Type: string
| | ... | - eth0_mac - MAC address of first Vhost interface. Type: string
| | ... | - eth1_mac - MAC address of second Vhost interface. Type: string
| | ... | - skip - number of cpus which will be skipped. Type: int
| | ... | - count - number of cpus which will be allocated for qemu. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure guest VM with dpdk-testpmd-mac using SMT connected via \
| | ... | vhost-user \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM\
| | ... | \| 00:00:00:00:00:01 \| 00:00:00:00:00:02 \| ${6} \| ${5} \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name}
| | ... | ${eth0_mac} | ${eth1_mac} | ${skip}=${6} | ${count}=${5}
| | ...
| | Import Library | resources.libraries.python.QemuUtils
| | ... | WITH NAME | ${vm_name}
| | ${dut_numa}= | Get interfaces numa node | ${dut_node}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${qemu_cpus}= | Cpu slice of list per node | ${dut_node} | ${dut_numa}
| | ... | skip_cnt=${skip} | cpu_cnt=${count} | smt_used=${True}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock2}
| | Run Keyword | ${vm_name}.Build QEMU | ${dut_node} | apply_patch=${True}
| | Run keyword | ${vm_name}.Qemu Set Bin | ${perf_qemu_bin}
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Dpdk Testpmd Start | ${vm} | eal_coremask=0x1f
| | ... | eal_mem_channels=4 | pmd_fwd_mode=mac | pmd_eth_peer_0=0,${eth0_mac}
| | ... | pmd_eth_peer_1=1,${eth1_mac} | pmd_disable_hw_vlan=${True}
| | ... | pmd_txd=${perf_qemu_qsz} | pmd_rxd=${perf_qemu_qsz}
| | Return From Keyword | ${vm}

| Configure guest VM with linux bridge connected via vhost-user
| | [Documentation]
| | ... | Start QEMU guest with two vhost-user interfaces and interconnecting
| | ... | linux bridge. Qemu Guest uses 2048M.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node to start guest VM on. Type: dictionary
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - vm_name - QemuUtil instance name. Type: string
| | ... | - skip - number of cpus which will be skipped. Type: int
| | ... | - count - number of cpus which will be allocated for qemu. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure guest VM with linux bridge connected via vhost-user \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM \| ${6} \
| | ... | \| ${5} \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name} | ${skip}=${6}
| | ... | ${count}=${5}
| | ...
| | Import Library | resources.libraries.python.QemuUtils
| | ... | WITH NAME | ${vm_name}
| | ${dut_numa}= | Get interfaces numa node | ${dut_node}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${qemu_cpus}= | Cpu slice of list per node | ${dut_node} | ${dut_numa}
| | ... | skip_cnt=${skip} | cpu_cnt=${count} | smt_used=${False}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock2}
| | Run Keyword | ${vm_name}.Build QEMU | ${dut_node} | apply_patch=${True}
| | Run keyword | ${vm_name}.Qemu Set Bin | ${perf_qemu_bin}
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | ${br}= | Set Variable | br0
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | ${br} | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Interface State | ${vm} | ${br} | up | if_type=name
| | Return From Keyword | ${vm}

| Configure guest VM with linux bridge using SMT connected via vhost-user
| | [Documentation]
| | ... | Start QEMU guest with two vhost-user interfaces and interconnecting
| | ... | linux bridge. Qemu Guest uses 2048M.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node to start guest VM on. Type: dictionary
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - vm_name - QemuUtil instance name. Type: string
| | ... | - skip - number of cpus which will be skipped. Type: int
| | ... | - count - number of cpus which will be allocated for qemu. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Guest VM with Linux Bridge using SMT connected via vhost-user is \
| | ... | setup \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM \
| | ... | \| ${6}\| ${5} \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name} | ${skip}=${6}
| | ... | ${count}=${5}
| | ...
| | Import Library | resources.libraries.python.QemuUtils
| | ... | WITH NAME | ${vm_name}
| | ${dut_numa}= | Get interfaces numa node | ${dut_node}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${qemu_cpus}= | Cpu slice of list per node | ${dut_node} | ${dut_numa}
| | ... | skip_cnt=${skip} | cpu_cnt=${count} | smt_used=${True}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock2}
| | Run Keyword | ${vm_name}.Build QEMU | ${dut_node} | apply_patch=${True}
| | Run keyword | ${vm_name}.Qemu Set Bin | ${perf_qemu_bin}
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | ${br}= | Set Variable | br0
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | ${br} | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Interface State | ${vm} | ${br} | up | if_type=name
| | Return From Keyword | ${vm}

| Initialize LISP IPv4 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 addresses on all DUT nodes and TG \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | -${dut1_dut2_address} - Ip address from DUT1 to DUT2. Type: string
| | ... | -${dut1_tg_address} - Ip address from DUT1 to tg. Type: string
| | ... | -${dut2_dut1_address} - Ip address from DUT2 to DUT1. Type: string
| | ... | -${dut1_tg_address} - Ip address from DUT1 to tg. Type: string
| | ... | -${duts_prefix} - ip prefix. Type: int
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
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Add arp on dut | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg1_if1_mac}
| | Add arp on dut | ${dut1} | ${dut1_if2} | ${dut2_dut1_address}
| | ... | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | ${dut1_dut2_address}
| | ... | ${dut1_if2_mac}
| | Add arp on dut | ${dut2} | ${dut2_if2} | 20.20.20.2 | ${tg1_if2_mac}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | ${dut1_tg_address} | ${duts_prefix}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | ${dut1_dut2_address} | ${duts_prefix}
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1}
| | ... | ${dut2_dut1_address} | ${duts_prefix}
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2}
| | ... | ${dut2_tg_address} | ${duts_prefix}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Initialize LISP GPE IPv4 over IPsec in 3-node circular topology
| | [Documentation] | Setup Lisp GPE IPv4 forwarding over IPsec.
| | ...
| | ... | *Arguments:*
| | ... | -${encr_alg} - Encryption algorithm. Type: string
| | ... | -${auth_alg} - Authentication algorithm. Type: string
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
| | ... | -${dut1_dut2_address} - Ip address from DUT1 to DUT2. Type: string
| | ... | -${dut1_tg_address} - Ip address from DUT1 to tg. Type: string
| | ... | -${dut2_dut1_address} - Ip address from DUT2 to DUT1. Type: string
| | ... | -${dut1_tg_address} - Ip address from DUT1 to tg. Type: string
| | ... | -${duts_prefix} - ip prefix. Type: int
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
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if1} | ${dut1_tg_address}
| | ... | ${prefix}
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if2} | ${dut1_dut2_address}
| | ... | ${prefix}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if1} | ${dut2_dut1_address}
| | ... | ${prefix}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if2} | ${dut2_tg_address}
| | ... | ${prefix}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | Add Ip Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg1_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg1_if2_mac}
| | Add Ip Neighbor | ${dut1} | ${dut1_if2} | ${dut2_dut1_address}
| | ... | ${dut2_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if1} | ${dut1_dut2_address}
| | ... | ${dut1_if2_mac}

| Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 over IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut1_dut2_ip6_address} - IPv6 address from DUT1 to DUT2.
| | ... | Type: string
| | ... | - ${dut1_tg_ip4_address} - IPv4 address from DUT1 to tg. Type: string
| | ... | - ${dut2_dut1_ip6_address} - IPv6 address from DUT2 to DUT1.
| | ... | Type: string
| | ... | - ${dut1_tg_ip4_address} - IPv4 address from DUT1 to tg. Type: string
| | ... | - ${prefix4} - IPv4 prefix. Type: int
| | ... | - ${prefix6} - IPv6 prefix. Type: int
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
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | ${dut1_tg_ip4_address} | ${prefix4}
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if2} | ${dut1_dut2_ip6_address}
| | ... | ${prefix6}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if1} | ${dut2_dut1_ip6_address}
| | ... | ${prefix6}
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2}
| | ... | ${dut2_tg_ip4_address} | ${prefix4}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | Add arp on dut | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg1_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if2} | 20.20.20.2 | ${tg1_if2_mac}
| | Add Ip Neighbor | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip6_address}
| | ... | ${dut2_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip6_address}
| | ... | ${dut1_if2_mac}

| Initialize LISP IPv6 over IPv4 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 over IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut1_dut2_ip4_address} - IPv4 address from DUT1 to DUT2.
| | ... | Type: string
| | ... | - ${dut1_tg_ip6_address} - IPv6 address from DUT1 to tg. Type: string
| | ... | - ${dut2_dut1_ip4_address} - IPv4 address from DUT2 to DUT1.
| | ... | Type: string
| | ... | - ${dut1_tg_ip6_address} - IPv6 address from DUT1 to tg. Type: string
| | ... | - ${prefix4} - IPv4 prefix. Type: int
| | ... | - ${prefix6} - IPv6 prefix. Type: int
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
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if1} | ${dut1_tg_ip6_address}
| | ... | ${prefix6}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | ${dut1_dut2_ip4_address} | ${prefix4}
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1}
| | ... | ${dut2_dut1_ip4_address} | ${prefix4}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if2} | ${dut2_tg_ip6_address}
| | ... | ${prefix6}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | Add Ip Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg1_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg1_if2_mac}
| | Add arp on dut | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip4_address}
| | ... | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip4_address}
| | ... | ${dut1_if2_mac}

| Initialize SNAT in 3-node circular topology
| | [Documentation] | Initialization of 3-node topology with SNAT between DUTs:
| | ... | - set interfaces up
| | ... | - set IP addresses
| | ... | - set ARP
| | ... | - create routes
| | ... | - set SNAT - only on DUT1
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | All Vpp Interfaces Ready Wait | ${nodes}
| | ...
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1} | 10.0.0.1 | 20
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 11.0.0.1 | 20
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 11.0.0.2 | 20
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2} | 12.0.0.1 | 20
| | ...
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | ...
| | Add arp on dut | ${dut1} | ${dut1_if1} | 10.0.0.2 | ${tg_if1_mac}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 11.0.0.2 | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | 11.0.0.1 | ${dut1_if2_mac}
| | Add arp on dut | ${dut2} | ${dut2_if2} | 12.0.0.2 | ${tg_if2_mac}
| | ...
| | Vpp Route Add | ${dut1} | 12.0.0.2 | 32 | 11.0.0.2 | ${dut1_if2}
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 18 | 10.0.0.2 | ${dut1_if1}
| | Vpp Route Add | ${dut2} | 12.0.0.0 | 24 | 12.0.0.2 | ${dut2_if2}
| | Vpp Route Add | ${dut2} | 200.0.0.0 | 30 | 11.0.0.1 | ${dut2_if1}
| | ...
| | Configure inside and outside interfaces
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure deterministic mode for SNAT
| | ... | ${dut1} | 20.0.0.0 | 18 | 200.0.0.0 | 30
