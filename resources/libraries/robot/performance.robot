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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.DpdkUtil
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/qemu.robot
| Resource | resources/libraries/robot/tagging.robot
| Documentation | Performance suite keywords

*** Keywords ***
| Calculate pps
| | [Documentation]
| | ... | Calculate pps for given rate and L2 frame size,
| | ... | additional 20B are added to L2 frame size as padding.
| | ...
| | ... | *Arguments*
| | ... | - bps - Rate in bps. Type: integer
| | ... | - framesize - L2 frame size in Bytes. Type: integer
| | ...
| | ... | *Return*
| | ... | - Calculated pps. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Calculate pps \| 10000000000 \| 64 \|
| | ...
| | [Arguments] | ${bps} | ${framesize}
| | ...
| | ${framesize}= | Get Frame Size | ${framesize}
| | ${ret}= | Evaluate | (${bps}/((${framesize}+20)*8)).__trunc__()
| | Return From Keyword | ${ret}

| Get Frame Size
| | [Documentation]
| | ... | Framesize can be either integer in case of a single packet
| | ... | in stream, or set of packets in case of IMIX type or simmilar.
| | ... | This keyword returns average framesize.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - Framesize. Type: integer or string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get Frame Size \| IMIX_v4_1 \|
| | ...
| | [Arguments] | ${framesize}
| | ...
| | Run Keyword If | '${framesize}' == 'IMIX_v4_1'
| | ... | Return From Keyword | 353.83333
| | Return From Keyword | ${framesize}

| 2-node circular Topology Variables Setup
| | [Documentation]
| | ... | Compute path for testing on two given nodes in circular
| | ... | topology and set corresponding suite variables.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - 1st DUT interface towards TG.
| | ... | - dut1_if2 - 2nd DUT interface towards TG.
| | ...
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_if1} | ${tg}= | First Interface
| | ${dut1_if1} | ${dut1}= | First Ingress Interface
| | ${dut1_if2} | ${dut1}= | Last Egress Interface
| | ${tg_if2} | ${tg}= | Last Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}

| 3-node circular Topology Variables Setup
| | [Documentation]
| | ... | Compute path for testing on three given nodes in circular
| | ... | topology and set corresponding suite variables.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - TG interface towards DUT1.
| | ... | - tg_if2 - TG interface towards DUT2.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2 - DUT2 node
| | ... | - dut2_if1 - DUT2 interface towards TG.
| | ... | - dut2_if2 - DUT2 interface towards DUT1.
| | ...
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ... | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}
| | Set Suite Variable | ${dut2}
| | Set Suite Variable | ${dut2_if1}
| | Set Suite Variable | ${dut2_if2}

| 2-node circular Topology Variables Setup with DUT interface model
| | [Documentation]
| | ... | Compute path for testing on two given nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - 1st DUT interface towards TG.
| | ... | - dut1_if2 - 2nd DUT interface towards TG.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 2-node circular Topology Variables Setup with DUT interface model \
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
| | ${iface_model_list}= | Create list | ${iface_model}
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_if1} | ${tg}= | First Interface
| | ${dut1_if1} | ${dut1}= | First Ingress Interface
| | ${dut1_if2} | ${dut1}= | Last Egress Interface
| | ${tg_if2} | ${tg}= | Last Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}

| 3-node circular Topology Variables Setup with DUT interface model
| | [Documentation]
| | ... | Compute path for testing on three given nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - TG interface towards DUT1.
| | ... | - tg_if2 - TG interface towards DUT2.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2 - DUT2 node
| | ... | - dut2_if1 - DUT2 interface towards TG.
| | ... | - dut2_if2 - DUT2 interface towards DUT1.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 3-node circular Topology Variables Setup with DUT interface model \
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
| | ${iface_model_list}= | Create list | ${iface_model}
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['DUT2']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}
| | Set Suite Variable | ${dut2}
| | Set Suite Variable | ${dut2_if1}
| | Set Suite Variable | ${dut2_if2}

| VPP interfaces in path are up in a 2-node circular topology
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on nodes in 2-node circular
| | ... | topology.*
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}

| VPP interfaces in path are up in a 3-node circular topology
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

| IPv4 forwarding initialized in a 3-node circular topology
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

| IPv4 forwarding initialized in a 2-node switched topology
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

| Scale IPv4 forwarding initialized in a 3-node circular topology
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
| | ... | \| Scale IPv4 forwarding initialized in a 3-node circular topology \
| | ... | \| 100000 \|
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
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if1} | 1.1.1.2 | 30
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if2} | 2.2.2.1 | 30
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if1} | 2.2.2.2 | 30
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if2} | 3.3.3.2 | 30
| | Vpp Route Add | ${dut1} | 10.0.0.0 | 32 | 1.1.1.1 | ${dut1_if1}
| | ... | count=${count}
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 32 | 2.2.2.2 | ${dut1_if2}
| | ... | count=${count}
| | Vpp Route Add | ${dut2} | 10.0.0.0 | 32 | 2.2.2.1 | ${dut2_if1}
| | ... | count=${count}
| | Vpp Route Add | ${dut2} | 20.0.0.0 | 32 | 3.3.3.1 | ${dut2_if2}
| | ... | count=${count}
| | All Vpp Interfaces Ready Wait | ${nodes}

| IPv4 forwarding with vhost initialized in a 3-node circular topology
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
| | VPP interfaces in path are up in a 3-node circular topology
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| | ... | ${sock1} | ${sock2}
| | ${dut1_vif1}= | Set Variable | ${vhost_if1}
| | ${dut1_vif2}= | Set Variable | ${vhost_if2}
| | Set Interface State | ${dut1} | ${dut1_vif1} | up
| | Set Interface State | ${dut1} | ${dut1_vif2} | up
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
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
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if1} | 1.1.1.2 | 30
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if2} | 2.2.2.1 | 30
| | IP addresses are set on interfaces | ${dut1} | ${dut1_vif1} | 4.4.4.1 | 30
| | IP addresses are set on interfaces | ${dut1} | ${dut1_vif2} | 5.5.5.1 | 30
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if1} | 2.2.2.2 | 30
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if2} | 3.3.3.1 | 30
| | IP addresses are set on interfaces | ${dut2} | ${dut2_vif1} | 4.4.4.1 | 30
| | IP addresses are set on interfaces | ${dut2} | ${dut2_vif2} | 5.5.5.1 | 30
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

| IPv4 forwarding with Vhost-User for '${nr}' VMs initialized in a 3-node circular topology
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
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 forwarding with Vhost-User for '2' VMs initialized in \
| | ... | a 3-node circular topology \|
| | ...
| | VPP interfaces in path are up in a 3-node circular topology
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
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if1} | 1.1.1.2 | 30
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if2} | 2.2.2.1 | 30
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if1} | 2.2.2.2 | 30
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if2} | 3.3.3.1 | 30
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
| |      | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| |      | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| |      | ${fib_table_1}= | Evaluate | ${100}+${number}
| |      | ${fib_table_2}= | Evaluate | ${fib_table_1}+${1}
| |      | ${ip_base_vif1}= | Evaluate | ${ip_base_start}+(${number}-1)*2
| |      | ${ip_base_vif2}= | Evaluate | ${ip_base_vif1}+1
| |      | ${ip_net_vif1}= | Set Variable
| |      | ... | ${ip_base_vif1}.${ip_base_vif1}.${ip_base_vif1}
| |      | ${ip_net_vif2}= | Set Variable
| |      | ... | ${ip_base_vif2}.${ip_base_vif2}.${ip_base_vif2}
| |      | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| |      | ... | ${sock1} | ${sock2} | dut1-vhost-${number}-if1
| |      | ... | dut1-vhost-${number}-if2
| |      | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if1} | up
| |      | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if2} | up
| |      | ${dut1_vif1_idx}= | Get Interface SW Index | ${dut1}
| |      | ... | ${dut1-vhost-${number}-if1}
| |      | ${dut1_vif2_idx}= | Get Interface SW Index | ${dut1}
| |      | ... | ${dut1-vhost-${number}-if2}
| |      | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
| |      | ... | ${sock1} | ${sock2} | dut2-vhost-${number}-if1
| |      | ... | dut2-vhost-${number}-if2
| |      | Set Interface State | ${dut2} | ${dut2-vhost-${number}-if1} | up
| |      | Set Interface State | ${dut2} | ${dut2-vhost-${number}-if2} | up
| |      | ${dut2_vif1_idx}= | Get Interface SW Index | ${dut2}
| |      | ... | ${dut2-vhost-${number}-if1}
| |      | ${dut2_vif2_idx}= | Get Interface SW Index | ${dut2}
| |      | ... | ${dut2-vhost-${number}-if2}
| |      | Add fib table | ${dut1} | 20.20.20.0 | 24 | ${fib_table_1}
| |      | ... | via ${ip_net_vif1}.1 sw_if_index ${dut1_vif1_idx} multipath
| |      | Add fib table | ${dut1} | 10.10.10.0 | 24 | ${fib_table_2}
| |      | ... | via ${ip_net_vif2}.2 sw_if_index ${dut1_vif2_idx} multipath
| |      | Add fib table | ${dut2} | 20.20.20.0 | 24 | ${fib_table_1}
| |      | ... | via ${ip_net_vif1}.1 sw_if_index ${dut2_vif1_idx} multipath
| |      | Add fib table | ${dut2} | 10.10.10.0 | 24 | ${fib_table_2}
| |      | ... | via ${ip_net_vif2}.2 sw_if_index ${dut2_vif2_idx} multipath
| |      | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if1}
| |      | ... | ${fib_table_1}
| |      | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if2}
| |      | ... | ${fib_table_2}
| |      | Assign Interface To Fib Table | ${dut2} | ${dut2-vhost-${number}-if1}
| |      | ... | ${fib_table_1}
| |      | Assign Interface To Fib Table | ${dut2} | ${dut2-vhost-${number}-if2}
| |      | ... | ${fib_table_2}
| |      | IP addresses are set on interfaces
| |      | ... | ${dut1} | ${dut1-vhost-${number}-if1} | ${ip_net_vif1}.1 | 30
| |      | ... | ${dut1} | ${dut1-vhost-${number}-if2} | ${ip_net_vif2}.1 | 30
| |      | ... | ${dut2} | ${dut2-vhost-${number}-if1} | ${ip_net_vif1}.1 | 30
| |      | ... | ${dut2} | ${dut2-vhost-${number}-if2} | ${ip_net_vif2}.1 | 30
| |      | ${dut1-vhost-${number}-if1_mac}= | Get Vhost User Mac By Sw Index
| |      | ... | ${dut1} | ${dut1_vif1_idx}
| |      | ${dut1-vhost-${number}-if2_mac}= | Get Vhost User Mac By Sw Index
| |      | ... | ${dut1} | ${dut1_vif2_idx}
| |      | ${dut2-vhost-${number}-if1_mac}= | Get Vhost User Mac By Sw Index
| |      | ... | ${dut2} | ${dut2_vif1_idx}
| |      | ${dut2-vhost-${number}-if2_mac}= | Get Vhost User Mac By Sw Index
| |      | ... | ${dut2} | ${dut2_vif2_idx}
| |      | Set Test Variable | ${dut1-vhost-${number}-if1_mac}
| |      | Set Test Variable | ${dut1-vhost-${number}-if2_mac}
| |      | Set Test Variable | ${dut2-vhost-${number}-if1_mac}
| |      | Set Test Variable | ${dut2-vhost-${number}-if2_mac}
| |      | ${qemu_id}= | Set Variable If | ${number} < 10 | 0${number}
| |      | ... | ${number}
| |      | Add arp on dut | ${dut1} | ${dut1-vhost-${number}-if1}
| |      | ... | ${ip_net_vif1}.2 | 52:54:00:00:${qemu_id}:01
| |      | Add arp on dut | ${dut1} | ${dut1-vhost-${number}-if2}
| |      | ... | ${ip_net_vif2}.2 | 52:54:00:00:${qemu_id}:02
| |      | Add arp on dut | ${dut2} | ${dut2-vhost-${number}-if1}
| |      | ... | ${ip_net_vif1}.2 | 52:54:00:00:${qemu_id}:01
| |      | Add arp on dut | ${dut2} | ${dut2-vhost-${number}-if2}
| |      | ... | ${ip_net_vif2}.2 | 52:54:00:00:${qemu_id}:02
| |      | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | ${ip_net_vif1}.2
| |      | ... | ${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| |      | Vpp Route Add | ${dut1} | 10.10.10.0 | 24 | ${ip_net_vif2}.2
| |      | ... | ${dut1-vhost-${number}-if2} | vrf=${fib_table_2}
| |      | Vpp Route Add | ${dut2} | 20.20.20.0 | 24 | ${ip_net_vif1}.2
| |      | ... | ${dut2-vhost-${number}-if1} | vrf=${fib_table_1}
| |      | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | ${ip_net_vif2}.2
| |      | ... | ${dut2-vhost-${number}-if2} | vrf=${fib_table_2}

| IPv4 policer 2r3c-${t} initialized in a 3-node circular topology
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

| IPv6 forwarding initialized in a 3-node circular topology
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
| | Vpp nodes ra suppress link layer | ${nodes}
| | Add Ip Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg1_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg1_if2_mac}
| | Add Ip Neighbor | ${dut1} | ${dut1_if2} | 2001:3::2 | ${dut2_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if1} | 2001:3::1 | ${dut1_if2_mac}
| | Vpp Route Add | ${dut1} | 2001:2::0 | ${prefix} | 2001:3::2 | ${dut1_if2}
| | Vpp Route Add | ${dut2} | 2001:1::0 | ${prefix} | 2001:3::1 | ${dut2_if1}

| Scale IPv6 forwarding initialized in a 3-node circular topology
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
| | ... | \| Scale IPv6 forwarding initialized in a 3-node circular topology \
| | ... | \| 100000 \|
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
| | Vpp nodes ra suppress link layer | ${nodes}
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

| IPv6 iAcl whitelist initialized in a 3-node circular topology
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

| L2 xconnect initialized in a 3-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology by cross connecting two interfaces on
| | ... | each DUT. Interfaces are brought up.
| | ... |
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 xconnect with VXLANoIPv4 initialized in a 3-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology with VXLANoIPv4 by cross connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | between DUTs. VXLAN sub-interfaces has same IPv4 address as
| | ... | interfaces.
| | ...
| | VPP interfaces in path are up in a 3-node circular topology
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if2} | 172.16.0.1 | 24
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if1} | 172.16.0.2 | 24
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 172.16.0.2 | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | 172.16.0.1 | ${dut1_if2_mac}
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if2} | ${dut2s_vxlan}

| L2 xconnect with Vhost-User initialized in a 3-node circular topology
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
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| | ... | ${sock1} | ${sock2}
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${vhost_if1}
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if2} | ${vhost_if2}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
| | ... | ${sock1} | ${sock2}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${vhost_if1}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if2} | ${vhost_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 xconnect with Vhost-User and VLAN initialized in a 3-node circular topology
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
| | VPP interfaces in path are up in a 3-node circular topology
| | VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| | ... | ${sock1} | ${sock2}
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${vhost_if1}
| | L2 setup xconnect on DUT | ${dut1} | ${subif_index_1} | ${vhost_if2}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
| | ... | ${sock1} | ${sock2}
| | L2 setup xconnect on DUT | ${dut2} | ${subif_index_2} | ${vhost_if1}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if2} | ${vhost_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 bridge domain initialized in a 3-node circular topology
| | [Documentation]
| | ... | Setup L2 DB topology by adding two interfaces on each DUT into BD
| | ... | that is created automatically with index 1. Learning is enabled.
| | ... | Interfaces are brought up.
| | ...
| | Vpp l2bd forwarding setup | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Vpp l2bd forwarding setup | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 bridge domains with Vhost-User initialized in a 3-node circular topology
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
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
| | ... | ${sock1} | ${sock2}
| | Interface is added to bridge domain | ${dut2} | ${dut2_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 bridge domains with Vhost-User for '${nr}' VMs initialized in a 3-node circular topology
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
| | ... | Socket paths for VM are defined in following fromat:
| | ... | - /tmp/sock-${VM_ID}-1
| | ... | - /tmp/sock-${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 bridge domains with Vhost-User for '2' VMs initialized in \
| | ... | a 3-node circular topology \|
| | ...
| | ${bd_id2}= | Evaluate | ${nr}+1
| | Interface is added to bridge domain | ${dut1} | ${dut1_if1} | ${1}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut2} | ${dut2_if1} | ${1}
| | Interface is added to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| |      | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| |      | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| |      | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| |      | ... | ${sock1} | ${sock2} | dut1-vhost-${number}-if1
| |      | ... | dut1-vhost-${number}-if2
| |      | ${bd_id2}= | Evaluate | ${number}+1
| |      | Interface is added to bridge domain | ${dut1}
| |      | ... | ${dut1-vhost-${number}-if1} | ${number}
| |      | Interface is added to bridge domain | ${dut1}
| |      | ... | ${dut1-vhost-${number}-if2} | ${bd_id2}
| |      | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
| |      | ... | ${sock1} | ${sock2} | dut2-vhost-${number}-if1
| |      | ... | dut2-vhost-${number}-if2
| |      | Interface is added to bridge domain | ${dut2}
| |      | ... | ${dut2-vhost-${number}-if1} | ${number}
| |      | Interface is added to bridge domain | ${dut2}
| |      | ... | ${dut2-vhost-${number}-if2} | ${bd_id2}

| L2 bridge domain with VXLANoIPv4 initialized in a 3-node circular topology
| | [Documentation]
| | ... | Setup L2 bridge domain topology with VXLANoIPv4 by connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | between DUTs. VXLAN sub-interfaces has same IPv4 address as
| | ... | interfaces.
| | ...
| | VPP interfaces in path are up in a 3-node circular topology
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if2} | 172.16.0.1 | 24
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if1} | 172.16.0.2 | 24
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 172.16.0.2 | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | 172.16.0.1 | ${dut1_if2_mac}
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Vpp l2bd forwarding setup | ${dut1} | ${dut1_if1} | ${dut1s_vxlan}
| | Vpp l2bd forwarding setup | ${dut2} | ${dut2_if2} | ${dut2s_vxlan}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 bridge domains with Vhost-User and VXLANoIPv4 initialized in a 3-node circular topology
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
| | VPP interfaces in path are up in a 3-node circular topology
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if2} | 172.16.0.1 | 24
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if1} | 172.16.0.2 | 24
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut1} | ${dut1s_vxlan} | ${bd_id2}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
| | ... | ${sock1} | ${sock2}
| | Interface is added to bridge domain | ${dut2} | ${dut2s_vxlan} | ${bd_id1}
| | Interface is added to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 bridge domains with Vhost-User initialized in a 2-node circular topology
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
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 bridge domains with Vhost-User and VLAN initialized in a 3-node circular topology
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
| | VPP interfaces in path are up in a 3-node circular topology
| | VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| | ... | ${sock1} | ${sock2}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut1} | ${subif_index_1} | ${bd_id2}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
| | ... | ${sock1} | ${sock2}
| | Interface is added to bridge domain | ${dut2} | ${subif_index_2} | ${bd_id1}
| | Interface is added to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| 2-node Performance Suite Setup with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that setup default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 2-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | Show vpp version on all DUTs
| | 2-node circular Topology Variables Setup with DUT interface model
| | ... | ${nic_model}
| | Setup 2-node startup configuration of VPP on all DUTs
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${topology_type}

| 2-node-switched Performance Suite Setup with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that setup default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ... | - tg_if1_dest_mac - Interface 1 destination MAC address. Type: string
| | ... | - tg_if2_dest_mac - Interface 2 destination MAC address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 2-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \
| | ... | \| 22:22:33:44:55:66 \| 22:22:33:44:55:55 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model} | ${tg_if1_dest_mac}
| | ... | ${tg_if2_dest_mac}
| | ...
| | Show vpp version on all DUTs
| | 2-node circular Topology Variables Setup with DUT interface model
| | ... | ${nic_model}
| | Setup 2-node startup configuration of VPP on all DUTs
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${topology_type}
| | ... | ${tg_if1_dest_mac} | ${tg_if2_dest_mac}

| 3-node Performance Suite Setup with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that setup default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 3-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | Show vpp version on all DUTs
| | 3-node circular Topology Variables Setup with DUT interface model
| | ... | ${nic_model}
| | Setup default startup configuration of VPP on all DUTs
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${topology_type}

| 3-node Performance Suite Teardown
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ...
| | Teardown traffic generator | ${tg}

| 2-node Performance Suite Teardown
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ...
| | Teardown traffic generator | ${tg}

| Find NDR using linear search and pps
| | [Documentation]
| | ... | Find throughput by using RFC2544 linear search with non drop rate.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - start_rate - Initial start rate [pps]. Type: float
| | ... | - step_rate - Step of linear search [pps]. Type: float
| | ... | - topology_type - Topology type. Type: string
| | ... | - min_rate - Lower limit of search [pps]. Type: float
| | ... | - max_rate - Upper limit of search [pps]. Type: float
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find NDR using linear search and pps \| 64 \| 5000000 \
| | ... | \| 100000 \| 3-node-IPv4 \| 100000 \| 14880952 \|
| | ...
| | [Arguments] | ${framesize} | ${start_rate} | ${step_rate}
| | ... | ${topology_type} | ${min_rate} | ${max_rate}
| | ...
| | ${duration}= | Set Variable | ${perf_trial_duration}
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Linear Step | ${step_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Linear Search | ${start_rate} | ${topology_type}
| | ${rate_per_stream} | ${lat}= | Verify Search Result
| | ${tmp}= | Create List | 100%NDR | ${lat}
| | ${latency}= | Create List | ${tmp}
| | ${rate_50p}= | Evaluate | int(${rate_per_stream}*0.5)
| | ${lat_50p}= | Measure latency pps | ${duration} | ${rate_50p}
| | ... | ${framesize} | ${topology_type}
| | ${tmp}= | Create List | 50%NDR | ${lat_50p}
| | Append To List | ${latency} | ${tmp}
| | ${rate_10p}= | Evaluate | int(${rate_per_stream}*0.1)
| | ${lat_10p}= | Measure latency pps | ${duration} | ${rate_10p}
| | ... | ${framesize} | ${topology_type}
| | ${tmp}= | Create List | 10%NDR | ${lat_10p}
| | Append To List | ${latency} | ${tmp}
| | Display result of NDR search | ${rate_per_stream} | ${framesize} | 2
| | ... | ${latency}
| | Traffic should pass with no loss | ${duration} | ${rate_per_stream}pps
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}

| Find PDR using linear search and pps
| | [Documentation]
| | ... | Find throughput by using RFC2544 linear search with partial drop rate
| | ... | with PDR threshold and type specified by parameter.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - start_rate - Initial start rate [pps]. Type: float
| | ... | - step_rate - Step of linear search [pps]. Type: float
| | ... | - topology_type - Topology type. Type: string
| | ... | - min_rate - Lower limit of search [pps]. Type: float
| | ... | - max_rate - Upper limit of search [pps]. Type: float
| | ... | - loss_acceptance - Accepted loss during search. Type: float
| | ... | - loss_acceptance_type - Percentage or frames. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find PDR using linear search and pps \| 64 \| 5000000 \
| | ... | \| 100000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 0.5 \| percentage \|
| | ...
| | [Arguments] | ${framesize} | ${start_rate} | ${step_rate}
| | ... | ${topology_type} | ${min_rate} | ${max_rate}
| | ... | ${loss_acceptance}=0 | ${loss_acceptance_type}='frames'
| | ...
| | ${duration}= | Set Variable | ${perf_trial_duration}
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Linear Step | ${step_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Loss Acceptance | ${loss_acceptance}
| | Run Keyword If | '${loss_acceptance_type}' == 'percentage'
| | ... | Set Loss Acceptance Type Percentage
| | Linear Search | ${start_rate} | ${topology_type}
| | ${rate_per_stream} | ${lat}= | Verify Search Result
| | ${tmp}= | Create List | 100%PDR | ${lat}
| | ${latency}= | Create List | ${tmp}
| | Display result of PDR search | ${rate_per_stream} | ${framesize} | 2
| | ... | ${loss_acceptance} | ${loss_acceptance_type} | ${latency}
| | Traffic should pass with partial loss | ${duration} | ${rate_per_stream}pps
| | ... | ${framesize} | ${topology_type} | ${loss_acceptance}
| | ... | ${loss_acceptance_type} | fail_on_loss=${False}

| Find NDR using binary search and pps
| | [Documentation]
| | ... | Find throughput by using RFC2544 binary search with non drop rate.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - binary_min - Lower boundary of search [pps]. Type: float
| | ... | - binary_max - Upper boundary of search [pps]. Type: float
| | ... | - topology_type - Topology type. Type: string
| | ... | - min_rate - Lower limit of search [pps]. Type: float
| | ... | - max_rate - Upper limit of search [pps]. Type: float
| | ... | - threshold - Threshold to stop search [pps]. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find NDR using binary search and pps \| 64 \| 6000000 \
| | ... | \| 12000000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 50000 \|
| | ...
| | [Arguments] | ${framesize} | ${binary_min} | ${binary_max}
| | ... | ${topology_type} | ${min_rate} | ${max_rate} | ${threshold}
| | ...
| | ${duration}= | Set Variable | ${perf_trial_duration}
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Binary Convergence Threshold | ${threshold}
| | Binary Search | ${binary_min} | ${binary_max} | ${topology_type}
| | ${rate_per_stream} | ${lat}= | Verify Search Result
| | ${tmp}= | Create List | 100%NDR | ${lat}
| | ${latency}= | Create List | ${tmp}
| | ${rate_50p}= | Evaluate | int(${rate_per_stream}*0.5)
| | ${lat_50p}= | Measure latency pps | ${duration} | ${rate_50p}
| | ... | ${framesize} | ${topology_type}
| | ${tmp}= | Create List | 50%NDR | ${lat_50p}
| | Append To List | ${latency} | ${tmp}
| | ${rate_10p}= | Evaluate | int(${rate_per_stream}*0.1)
| | ${lat_10p}= | Measure latency pps | ${duration} | ${rate_10p}
| | ... | ${framesize} | ${topology_type}
| | ${tmp}= | Create List | 10%NDR | ${lat_10p}
| | Append To List | ${latency} | ${tmp}
| | Display result of NDR search | ${rate_per_stream} | ${framesize} | 2
| | ... | ${latency}
| | Traffic should pass with no loss | ${duration} | ${rate_per_stream}pps
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}

| Find PDR using binary search and pps
| | [Documentation]
| | ... | Find throughput by using RFC2544 binary search with partial drop rate
| | ... | with PDR threshold and type specified by parameter.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - binary_min - Lower boundary of search [pps]. Type: float
| | ... | - binary_max - Upper boundary of search [pps]. Type: float
| | ... | - topology_type - Topology type. Type: string
| | ... | - min_rate - Lower limit of search [pps]. Type: float
| | ... | - max_rate - Upper limit of search [pps]. Type: float
| | ... | - threshold - Threshold to stop search [pps]. Type: integer
| | ... | - loss_acceptance - Accepted loss during search. Type: float
| | ... | - loss_acceptance_type - Percentage or frames. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find PDR using binary search and pps \| 64 \| 6000000 \
| | ... | \| 12000000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 50000 \| 0.5 \
| | ... | \| percentage \|
| | ...
| | [Arguments] | ${framesize} | ${binary_min} | ${binary_max}
| | ... | ${topology_type} | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${loss_acceptance}=0 | ${loss_acceptance_type}='frames'
| | ...
| | ${duration}= | Set Variable | ${perf_trial_duration}
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Loss Acceptance | ${loss_acceptance}
| | Run Keyword If | '${loss_acceptance_type}' == 'percentage'
| | ... | Set Loss Acceptance Type Percentage
| | Set Binary Convergence Threshold | ${threshold}
| | Binary Search | ${binary_min} | ${binary_max} | ${topology_type}
| | ${rate_per_stream} | ${lat}= | Verify Search Result
| | ${tmp}= | Create List | 100%PDR | ${lat}
| | ${latency}= | Create List | ${tmp}
| | Display result of PDR search | ${rate_per_stream} | ${framesize} | 2
| | ... | ${loss_acceptance} | ${loss_acceptance_type} | ${latency}
| | Traffic should pass with partial loss | ${duration} | ${rate_per_stream}pps
| | ... | ${framesize} | ${topology_type} | ${loss_acceptance}
| | ... | ${loss_acceptance_type} | fail_on_loss=${False}

| Find NDR using combined search and pps
| | [Documentation]
| | ... | Find throughput by using RFC2544 combined search (linear+binary) with
| | ... | non drop rate.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - start_rate - Initial start rate [pps]. Type: float
| | ... | - step_rate - Step of linear search [pps]. Type: float
| | ... | - topology_type - Topology type. Type: string
| | ... | - min_rate - Lower limit of search [pps]. Type: float
| | ... | - max_rate - Upper limit of search [pps]. Type: float
| | ... | - threshold - Threshold to stop search [pps]. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find NDR using combined search and pps \| 64 \| 5000000 \
| | ... | \| 100000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 5000 \|
| | ...
| | [Arguments] | ${framesize} | ${start_rate} | ${step_rate}
| | ... | ${topology_type} | ${min_rate} | ${max_rate} | ${threshold}
| | ...
| | ${duration}= | Set Variable | ${perf_trial_duration}
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Linear Step | ${step_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Binary Convergence Threshold | ${threshold}
| | Combined Search | ${start_rate} | ${topology_type}
| | ${rate_per_stream} | ${lat}= | Verify Search Result
| | ${tmp}= | Create List | 100%NDR | ${lat}
| | ${latency}= | Create List | ${tmp}
| | ${rate_50p}= | Evaluate | int(${rate_per_stream}*0.5)
| | ${lat_50p}= | Measure latency pps | ${duration} | ${rate_50p}
| | ... | ${framesize} | ${topology_type}
| | ${tmp}= | Create List | 50%NDR | ${lat_50p}
| | Append To List | ${latency} | ${tmp}
| | ${rate_10p}= | Evaluate | int(${rate_per_stream}*0.1)
| | ${lat_10p}= | Measure latency pps | ${duration} | ${rate_10p}
| | ... | ${framesize} | ${topology_type}
| | ${tmp}= | Create List | 10%NDR | ${lat_10p}
| | Append To List | ${latency} | ${tmp}
| | Display result of NDR search | ${rate_per_stream} | ${framesize} | 2
| | ... | ${latency}
| | Traffic should pass with no loss | ${duration} | ${rate_per_stream}pps
| | ... | ${framesize} | ${topology_type}
| | ... | fail_on_loss=${False}

| Find PDR using combined search and pps
| | [Documentation]
| | ... | Find throughput by using RFC2544 combined search (linear+binary) with
| | ... | partial drop rate with PDR threshold and type specified by parameter.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - start_rate - Initial start rate [pps]. Type: float
| | ... | - step_rate - Step of linear search [pps]. Type: float
| | ... | - topology_type - Topology type. Type: string
| | ... | - min_rate - Lower limit of search [pps]. Type: float
| | ... | - max_rate - Upper limit of search [pps]. Type: float
| | ... | - threshold - Threshold to stop search [pps]. Type: integer
| | ... | - loss_acceptance - Accepted loss during search. Type: float
| | ... | - loss_acceptance_type - Percentage or frames. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find PDR using combined search and pps \| 64 \| 5000000 \
| | ... | \| 100000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 5000 \| 0.5 \
| | ... | \| percentage \|
| | ...
| | [Arguments] | ${framesize} | ${start_rate} | ${step_rate}
| | ... | ${topology_type} | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${loss_acceptance}=0 | ${loss_acceptance_type}='frames'
| | ...
| | ${duration}= | Set Variable | ${perf_trial_duration}
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Linear Step | ${step_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Loss Acceptance | ${loss_acceptance}
| | Run Keyword If | '${loss_acceptance_type}' == 'percentage'
| | ... | Set Loss Acceptance Type Percentage
| | Set Binary Convergence Threshold | ${threshold}
| | Combined Search | ${start_rate} | ${topology_type}
| | ${rate_per_stream} | ${lat}= | Verify Search Result
| | ${tmp}= | Create List | 100%PDR | ${lat}
| | ${latency}= | Create List | ${tmp}
| | Display result of PDR search | ${rate_per_stream} | ${framesize} | 2
| | ... | ${loss_acceptance} | ${loss_acceptance_type} | ${latency}
| | Traffic should pass with partial loss | ${duration} | ${rate_per_stream}pps
| | ... | ${framesize} | ${topology_type} | ${loss_acceptance}
| | ... | ${loss_acceptance_type} | fail_on_loss=${False}

| Display result of NDR search
| | [Documentation]
| | ... | Display result of NDR search in packet per seconds (total and per
| | ... | stream) and Gbps total bandwidth with untagged packet.
| | ... | Througput is calculated as:
| | ... | Measured rate per stream * Total number of streams
| | ... | Bandwidth is calculated as:
| | ... | (Througput * (L2 Frame Size + IPG) * 8) / Max bitrate of NIC
| | ...
| | ... | *Arguments:*
| | ... | - rate_per_stream - Measured rate per stream [pps]. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - nr_streams - Total number of streams. Type: integer
| | ... | - latency - Latency stats. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Display result of NDR search \| 4400000 \| 64 \| 2 \
| | ... | \| [100%NDR, [10/10/10, 1/2/3]] \|
| | ...
| | [Arguments] | ${rate_per_stream} | ${framesize} | ${nr_streams} | ${latency}
| | ...
| | ${framesize}= | Get Frame Size | ${framesize}
| | ${rate_total}= | Evaluate | ${rate_per_stream}*${nr_streams}
| | ${bandwidth_total}= | Evaluate | ${rate_total}*(${framesize}+20)*8/(10**9)
| | Set Test Message | FINAL_RATE: ${rate_total} pps
| | Set Test Message | (${nr_streams}x ${rate_per_stream} pps) | append=yes
| | Set Test Message | ${\n}FINAL_BANDWIDTH: ${bandwidth_total} Gbps (untagged)
| | ... | append=yes
| | Set Test Message | ${\n}LATENCY usec [min/avg/max] | append=yes
| | :FOR | ${lat} | IN | @{latency}
| | | Set Test Message | ${\n}LAT_${lat[0]}: ${lat[1]} | append=yes

| Display result of PDR search
| | [Documentation]
| | ... | Display result of PDR search in packet per seconds (total and per
| | ... | stream) and Gbps total bandwidth with untagged packet.
| | ... | Througput is calculated as:
| | ... | Measured rate per stream * Total number of streams
| | ... | Bandwidth is calculated as:
| | ... | (Througput * (L2 Frame Size + IPG) * 8) / Max bitrate of NIC
| | ...
| | ... | *Arguments:*
| | ... | - rate_per_stream - Measured rate per stream [pps]. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - nr_streams - Total number of streams. Type: integer
| | ... | - loss_acceptance - Accepted loss during search. Type: float
| | ... | - loss_acceptance_type - Percentage or frames. Type: string
| | ... | - latency - Latency stats. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Display result of PDR search \| 4400000 \| 64 \| 2 \| 0.5 \
| | ... | \| percentage \| [100%NDR, [10/10/10, 1/2/3]] \|
| | ...
| | [Arguments] | ${rate_per_stream} | ${framesize} | ${nr_streams}
| | ... | ${loss_acceptance} | ${loss_acceptance_type} | ${latency}
| | ...
| | ${framesize}= | Get Frame Size | ${framesize}
| | ${rate_total}= | Evaluate | ${rate_per_stream}*${nr_streams}
| | ${bandwidth_total}= | Evaluate | ${rate_total}*(${framesize}+20)*8/(10**9)
| | Set Test Message | FINAL_RATE: ${rate_total} pps
| | Set Test Message | (${nr_streams}x ${rate_per_stream} pps) | append=yes
| | Set Test Message | ${\n}FINAL_BANDWIDTH: ${bandwidth_total} Gbps (untagged)
| | ... | append=yes
| | Set Test Message | ${\n}LATENCY usec [min/avg/max] | append=yes
| | :FOR | ${lat} | IN | @{latency}
| | | Set Test Message | ${\n}LAT_${lat[0]}: ${lat[1]} | append=yes
| | Set Test Message
| | ... | ${\n}LOSS_ACCEPTANCE: ${loss_acceptance} ${loss_acceptance_type}
| | ... | append=yes

| Measure latency pps
| | [Documentation]
| | ... | Send traffic at specified rate. Measure min/avg/max latency
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: integer
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Measure latency \| 10 \| 4.0 \| 64 \| 3-node-IPv4 \|
| | ...
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ...
| | Return From Keyword If | ${rate} <= 10000 | ${-1}
| | ${ret}= | For DPDK Performance Test
| | Run Keyword If | ${ret}==${FALSE} | Clear all counters on all DUTs
| | Send traffic on tg | ${duration} | ${rate}pps | ${framesize}
| | ... | ${topology_type} | warmup_time=0
| | Run Keyword If | ${ret}==${FALSE} | Show statistics on all DUTs
| | Run keyword and return | Get latency

| Traffic should pass with no loss
| | [Documentation]
| | ... | Send traffic at specified rate. No packet loss is accepted at loss
| | ... | evaluation.
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ... | - fail_on_loss - If True, the keyword fails if loss occurred.
| | ... | Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Traffic should pass with no loss \| 10 \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \|
| | ...
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ... | ${fail_on_loss}=${True}
| | ...
| | Clear and show runtime counters with running traffic | ${duration}
| | ... | ${rate} | ${framesize} | ${topology_type}
| | ${ret}= | For DPDK Performance Test
| | Run Keyword If | ${ret}==${FALSE} | Clear all counters on all DUTs
| | Send traffic on tg | ${duration} | ${rate} | ${framesize}
| | ... | ${topology_type} | warmup_time=0
| | Run Keyword If | ${ret}==${FALSE} | Show statistics on all DUTs
| | Run Keyword If | ${fail_on_loss} | No traffic loss occurred

| Traffic should pass with partial loss
| | [Documentation]
| | ... | Send traffic at specified rate. Partial packet loss is accepted
| | ... | within loss acceptance value specified as argument.
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ... | - loss_acceptance - Accepted loss during search. Type: float
| | ... | - loss_acceptance_type - Percentage or frames. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Traffic should pass with partial loss \| 10 \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \| 0.5 \| percentage \|
| | ...
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ... | ${loss_acceptance} | ${loss_acceptance_type}
| | ... | ${fail_on_loss}=${True}
| | ...
| | Clear and show runtime counters with running traffic | ${duration}
| | ... | ${rate} | ${framesize} | ${topology_type}
| | ${ret}= | For DPDK Performance Test
| | Run Keyword If | ${ret}==${FALSE} | Clear all counters on all DUTs
| | Send traffic on tg | ${duration} | ${rate} | ${framesize}
| | ... | ${topology_type} | warmup_time=0
| | Run Keyword If | ${ret}==${FALSE} | Show statistics on all DUTs
| | Run Keyword If | ${fail_on_loss} | Partial traffic loss accepted
| | ... | ${loss_acceptance} | ${loss_acceptance_type}

| Clear and show runtime counters with running traffic
| | [Documentation]
| | ... | Start traffic at specified rate then clear runtime counters on all
| | ... | DUTs. Wait for specified amount of time and capture runtime counters
| | ... | on all DUTs. Finally stop traffic
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Traffic should pass with partial loss \| 10 \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \| 0.5 \| percentage \|
| | ...
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ...
| | Send traffic on tg | -1 | ${rate} | ${framesize} | ${topology_type}
| | ... | warmup_time=0 | async_call=${True} | latency=${False}
| | ${ret}= | For DPDK Performance Test
| | Run Keyword If | ${ret}==${FALSE} | Clear runtime counters on all DUTs
| | Sleep | ${duration}
| | Run Keyword If | ${ret}==${FALSE} | Show runtime counters on all DUTs
| | Stop traffic on tg

| Add PCI devices to DUTs from 3-node single link topology
| | ${dut1_if1_pci}= | Get Interface PCI Addr | ${dut1} | ${dut1_if1}
| | ${dut1_if2_pci}= | Get Interface PCI Addr | ${dut1} | ${dut1_if2}
| | ${dut2_if1_pci}= | Get Interface PCI Addr | ${dut2} | ${dut2_if1}
| | ${dut2_if2_pci}= | Get Interface PCI Addr | ${dut2} | ${dut2_if2}
| | Add PCI device | ${dut1} | ${dut1_if1_pci} | ${dut1_if2_pci}
| | Add PCI device | ${dut2} | ${dut2_if1_pci} | ${dut2_if2_pci}

| Add PCI devices to DUTs from 2-node single link topology
| | ${dut1_if1_pci}= | Get Interface PCI Addr | ${dut1} | ${dut1_if1}
| | ${dut1_if2_pci}= | Get Interface PCI Addr | ${dut1} | ${dut1_if2}
| | Add PCI device | ${dut1} | ${dut1_if1_pci} | ${dut1_if2_pci}

| Guest VM with dpdk-testpmd connected via vhost-user is setup
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
| | ... | - skip - Number of cpus which will be skipped. Type: int
| | ... | - count - Number of cpus which will be allocated for qemu. Type: int
| | ... | - qemu_id - Qemu Id when starting more then one guest VM on DUT node.
| | ... | Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Guest VM with dpdk-testpmd connected via vhost-user is setup \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM \| ${6} \
| | ... | \| ${5} \|
| | ... | \| Guest VM with dpdk-testpmd connected via vhost-user is setup \
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
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Run keyword | ${vm_name}.Qemu Set Scheduler Policy
| | Dpdk Testpmd Start | ${vm} | eal_coremask=0x1f | eal_mem_channels=4
| | ... | pmd_fwd_mode=io | pmd_disable_hw_vlan=${True}
| | Return From Keyword | ${vm}

| '${nr}' Guest VMs with dpdk-testpmd connected via vhost-user is setup in a 3-node circular topology
| | [Documentation]
| | ... | Start QEMU guests with two vhost-user interfaces and interconnecting
| | ... | DPDK testpmd for defined number of VMs on all defined VPP nodes.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | _NOTE:_ This KW expects following test case variables to be set:
| | ... | - ${vpp_cpus} - Number of CPUs allocated for VPP.
| | ... | - ${vm_cpus} - Number of CPUs to be allocated per QEMU instance.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| '2' Guest VM with dpdk-testpmd connected via vhost-user is setup \
| | ... | in a 3-node circular topology \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| |      | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| |      | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| |      | ${vm1}= | Guest VM with dpdk-testpmd connected via vhost-user is setup
| |      | ...     | ${dut1} | ${sock1} | ${sock2} | DUT1_VM${number}
| |      | ...     | skip=${vpp_cpus} | count=${vm_cpus} | qemu_id=${number}
| |      | Set To Dictionary | ${dut1_vm_refs} | DUT1_VM${number} | ${vm1}
| |      | ${vm2}= | Guest VM with dpdk-testpmd connected via vhost-user is setup
| |      | ...     | ${dut2} | ${sock1} | ${sock2} | DUT2_VM${number}
| |      | ...     | skip=${vpp_cpus} | count=${vm_cpus} | qemu_id=${number}
| |      | Set To Dictionary | ${dut2_vm_refs} | DUT2_VM${number} | ${vm2}

| Guest VM with dpdk-testpmd using SMT connected via vhost-user is setup
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
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Run keyword | ${vm_name}.Qemu Set Scheduler Policy
| | Dpdk Testpmd Start | ${vm} | eal_coremask=0x1f | eal_mem_channels=4
| | ... | pmd_fwd_mode=io | pmd_disable_hw_vlan=${True}
| | Return From Keyword | ${vm}

| Guest VM with dpdk-testpmd-mac connected via vhost-user is setup
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
| | ... | - qemu_id - Qemu Id when starting more then one guest VM on DUT node.
| | ... | Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Guest VM with dpdk-testpmd for Vhost L2BD forwarding is setup \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM \
| | ... | \| 00:00:00:00:00:01 \| 00:00:00:00:00:02 \| ${6} \| ${5} \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name}
| | ... | ${eth0_mac} | ${eth1_mac} | ${skip}=${6} | ${count}=${5}
| | ... | ${qemu_id}=${1}
| | ...
| | Import Library | resources.libraries.python.QemuUtils
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
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Run keyword | ${vm_name}.Qemu Set Scheduler Policy
| | Dpdk Testpmd Start | ${vm} | eal_coremask=0x1f
| | ... | eal_mem_channels=4 | pmd_fwd_mode=mac | pmd_eth_peer_0=0,${eth0_mac}
| | ... | pmd_eth_peer_1=1,${eth1_mac} | pmd_disable_hw_vlan=${True}
| | Return From Keyword | ${vm}

| '${nr}' Guest VMs with dpdk-testpmd-mac connected via vhost-user is setup in a 3-node circular topology
| | [Documentation]
| | ... | Start QEMU guests with two vhost-user interfaces and interconnecting
| | ... | DPDK testpmd with fwd mode set to mac rewrite for defined number of
| | ... | VMs on all defined VPP nodes.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | _NOTE:_ This KW expects following test case variables to be set:
| | ... | - ${vpp_cpus} - Number of CPUs allocated for VPP.
| | ... | - ${vm_cpus} - Number of CPUs to be allocated per QEMU instance.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| '2' Guest VMs with dpdk-testpmd-mac connected via vhost-user is \
| | ... | setup in a 3-node circular topology \|
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nr}+1
| |      | ${sock1}= | Set Variable | /tmp/sock-${number}-1
| |      | ${sock2}= | Set Variable | /tmp/sock-${number}-2
| |      | ${dut1_vif1_mac}=
| |      | ... | Replace Variables | ${dut1-vhost-${number}-if1_mac}
| |      | ${dut1_vif2_mac}=
| |      | ... | Replace Variables | ${dut1-vhost-${number}-if2_mac}
| |      | ${dut2_vif1_mac}=
| |      | ... | Replace Variables | ${dut2-vhost-${number}-if1_mac}
| |      | ${dut2_vif2_mac}=
| |      | ... | Replace Variables | ${dut2-vhost-${number}-if2_mac}
| |      | ${vm1}= | Guest VM with dpdk-testpmd-mac connected via vhost-user is setup
| |      | ...     | ${dut1} | ${sock1} | ${sock2} | DUT1_VM${number}
| |      | ...     | ${dut1_vif1_mac} | ${dut1_vif2_mac} | skip=${vpp_cpus}
| |      | ...     | count=${vm_cpus} | qemu_id=${number}
| |      | Set To Dictionary | ${dut1_vm_refs} | DUT1_VM${number} | ${vm1}
| |      | ${vm2}= | Guest VM with dpdk-testpmd-mac connected via vhost-user is setup
| |      | ...     | ${dut2} | ${sock1} | ${sock2} | DUT2_VM${number}
| |      | ...     | ${dut2_vif1_mac} | ${dut2_vif2_mac} | skip=${vpp_cpus}
| |      | ...     | count=${vm_cpus} | qemu_id=${number}
| |      | Set To Dictionary | ${dut2_vm_refs} | DUT2_VM${number} | ${vm2}

| Guest VM with dpdk-testpmd-mac using SMT connected via vhost-user is setup
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
| | ... | \| Guest VM with dpdk-testpmd-mac using SMT connected via vhost-user \
| | ... | is setup \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM \
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
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Run keyword | ${vm_name}.Qemu Set Scheduler Policy
| | Dpdk Testpmd Start | ${vm} | eal_coremask=0x1f
| | ... | eal_mem_channels=4 | pmd_fwd_mode=mac | pmd_eth_peer_0=0,${eth0_mac}
| | ... | pmd_eth_peer_1=1,${eth1_mac} | pmd_disable_hw_vlan=${True}
| | Return From Keyword | ${vm}

| Guest VM with Linux Bridge connected via vhost-user is setup
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
| | ... | \| Guest VM with Linux Bridge connected via vhost-user is setup \
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
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Run keyword | ${vm_name}.Qemu Set Scheduler Policy
| | ${br}= | Set Variable | br0
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | ${br} | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Interface State | ${vm} | ${br} | up | if_type=name
| | Return From Keyword | ${vm}

| Guest VM with Linux Bridge using SMT connected via vhost-user is setup
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
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | ${count} | ${count} | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Disk Image | ${perf_vm_image}
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Run keyword | ${vm_name}.Qemu Set Affinity | @{qemu_cpus}
| | Run keyword | ${vm_name}.Qemu Set Scheduler Policy
| | ${br}= | Set Variable | br0
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | ${br} | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Interface State | ${vm} | ${br} | up | if_type=name
| | Return From Keyword | ${vm}

| Guest VM with dpdk-testpmd Teardown
| | [Documentation]
| | ... | Stop all qemu processes with dpdk-testpmd running on ${dut_node}.
| | ... | Argument is dictionary of all qemu nodes running with its names.
| | ... | Dpdk-testpmd is stopped gracefully with printing stats.
| | ... |
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dictionary
| | ... | - dut_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Guest VM with dpdk-testpmd Teardown \| ${node['DUT1']} \
| | ... | \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${dut_node} | ${dut_vm_refs}
| | ${vms_number}= | Get Length | ${dut_vm_refs}
| | ${index}= | Set Variable | ${0}
| | :FOR | ${vm_name} | IN | @{dut_vm_refs}
| | | ${vm}= | Get From Dictionary | ${dut_vm_refs} | ${vm_name}
| | | ${index}= | Evaluate | ${index} + 1
| | | Dpdk Testpmd Stop | ${vm}
| | | Run Keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | | Run Keyword | ${vm_name}.Qemu Clear Socks
| | | Run Keyword If | '${index}' == '${vms_number}' | ${vm_name}.Qemu Kill

| Guest VM Teardown
| | [Documentation]
| | ... | Stop all qemu processes running on ${dut_node}.
| | ... | Argument is dictionary of all qemu nodes running with its names.
| | ... |
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dictionary
| | ... | - dut_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Guest VM Teardown \| ${node['DUT1']} \
| | ... | \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${dut_node} | ${dut_vm_refs}
| | ${vms_number}= | Get Length | ${dut_vm_refs}
| | ${index}= | Set Variable | ${0}
| | :FOR | ${vm_name} | IN | @{dut_vm_refs}
| | | ${vm}= | Get From Dictionary | ${dut_vm_refs} | ${vm_name}
| | | ${index}= | Evaluate | ${index} + 1
| | | Run Keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | | Run Keyword | ${vm_name}.Qemu Clear Socks
| | | Run Keyword If | '${index}' == '${vms_number}' | ${vm_name}.Qemu Kill

| Lisp IPv4 forwarding initialized in a 3-node circular topology
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
| | ... | \| Lisp IPv4 forwarding initialized in a 3-node circular topology \
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
| | dut1_v4.set_arp | ${dut1_if1} | 10.10.10.2 | ${tg1_if1_mac}
| | dut1_v4.set_arp | ${dut1_if2} | ${dut2_dut1_address} | ${dut2_if1_mac}
| | dut2_v4.set_arp | ${dut2_if1} | ${dut1_dut2_address} | ${dut1_if2_mac}
| | dut2_v4.set_arp | ${dut2_if2} | 20.20.20.2 | ${tg1_if2_mac}
| | dut1_v4.set_ip | ${dut1_if1} | ${dut1_tg_address} | ${duts_prefix}
| | dut1_v4.set_ip | ${dut1_if2} | ${dut1_dut2_address} | ${duts_prefix}
| | dut2_v4.set_ip | ${dut2_if1} | ${dut2_dut1_address} | ${duts_prefix}
| | dut2_v4.set_ip | ${dut2_if2} | ${dut2_tg_address} | ${duts_prefix}
| | All Vpp Interfaces Ready Wait | ${nodes}

| Lisp IPv6 forwarding initialized in a 3-node circular topology
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
| | ... | \| Lisp IPv6 forwarding initialized in a 3-node circular topology \
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
| | Vpp nodes ra suppress link layer | ${nodes}
| | Add Ip Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg1_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg1_if2_mac}
| | Add Ip Neighbor | ${dut1} | ${dut1_if2} | ${dut2_dut1_address}
| | ... | ${dut2_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if1} | ${dut1_dut2_address}
| | ... | ${dut1_if2_mac}

| Lisp IPv4 over IPv6 forwarding initialized in a 3-node circular topology
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
| | dut1_v4.set_ip | ${dut1_if1} | ${dut1_tg_ip4_address} | ${prefix4}
| | VPP Set If IPv6 Addr | ${dut1} | ${dut1_if2} | ${dut1_dut2_ip6_address}
| | ... | ${prefix6}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if1} | ${dut2_dut1_ip6_address}
| | ... | ${prefix6}
| | dut2_v4.set_ip | ${dut2_if2} | ${dut2_tg_ip4_address} | ${prefix4}
| | Vpp nodes ra suppress link layer | ${nodes}
| | dut1_v4.set_arp | ${dut1_if1} | 10.10.10.2 | ${tg1_if1_mac}
| | dut2_v4.set_arp | ${dut2_if2} | 20.20.20.2 | ${tg1_if2_mac}
| | Add Ip Neighbor | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip6_address}
| | ... | ${dut2_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip6_address}
| | ... | ${dut1_if2_mac}

| Lisp IPv6 over IPv4 forwarding initialized in a 3-node circular topology
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
| | dut1_v4.set_ip | ${dut1_if2} | ${dut1_dut2_ip4_address} | ${prefix4}
| | dut2_v4.set_ip | ${dut2_if1} | ${dut2_dut1_ip4_address} | ${prefix4}
| | VPP Set If IPv6 Addr | ${dut2} | ${dut2_if2} | ${dut2_tg_ip6_address}
| | ... | ${prefix6}
| | Vpp nodes ra suppress link layer | ${nodes}
| | Add Ip Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg1_if1_mac}
| | Add Ip Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg1_if2_mac}
| | dut1_v4.set_arp | ${dut1_if2} | ${dut2_dut1_ip4_address} | ${dut2_if1_mac}
| | dut2_v4.set_arp | ${dut2_if1} | ${dut1_dut2_ip4_address} | ${dut1_if2_mac}

| DPDK 2-node Performance Suite Setup with DUT's NIC model
| | [Documentation]
| | ... | Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator. Initializes DPDK test
| | ... | environment.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| DPDK 2-node Performance Suite Setup with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | 2-node circular Topology Variables Setup with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${topology_type}
| | Initialize DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}

| DPDK 3-node Performance Suite Setup with DUT's NIC model
| | [Documentation]
| | ... | Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator. Initializes DPDK test
| | ... | environment.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 3-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | 3-node circular Topology Variables Setup with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${topology_type}
| | Initialize DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Initialize DPDK Environment | ${dut2} | ${dut2_if1} | ${dut2_if2}

| DPDK 3-node Performance Suite Teardown
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ... | Cleanup DPDK test environment.
| | ...
| | Teardown traffic generator | ${tg}
| | Cleanup DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Cleanup DPDK Environment | ${dut2} | ${dut2_if1} | ${dut2_if2}

| DPDK 2-node Performance Suite Teardown
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ... | Cleanup DPDK test environment.
| | ...
| | Teardown traffic generator | ${tg}
| | Cleanup DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}

| For DPDK Performance Test
| | [Documentation]
| | ... | Return TRUE if variable DPDK_TEST exist, otherwise FALSE.
| | ${ret} | ${tmp}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${DPDK_TEST}
| | Return From Keyword If | "${ret}" == "PASS" | ${TRUE}
| | Return From Keyword | ${FALSE}

| Performance test setup
| | [Documentation] | Common test setup for performance tests.
| | ...
| | Setup all DUTs before test
| | Reset VAT History On All DUTs | ${nodes}

| Performance test teardown
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Performance test teardown \| 4.0mpps \| 64 \| 3-node-IPv4 \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${topology_type}
| | ...
| | Show VAT History On All DUTs | ${nodes}
| | Show statistics on all DUTs
| | Run Keyword If Test Failed
| | ... | Traffic should pass with no loss | ${perf_trial_duration} | ${rate}
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}
| | Remove startup configuration of VPP from all DUTs

| Performance ndrchk test teardown
| | [Documentation] | Common test teardown for ndrchk performance tests.
| | ...
| | Show VAT History On All DUTs | ${nodes}
| | Show statistics on all DUTs
| | Remove startup configuration of VPP from all DUTs

| Performance test with vhost and VM with dpdk-testpmd teardown
| | [Documentation] | Common test teardown for performance tests which use
| | ... | vhost(s) and VM(s) with dpdk-testpmd.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ... | - dut1_node - Node where to clean qemu. Type: dictionary
| | ... | - dut1_vm_refs - VM references on node. Type: dictionary
| | ... | - dut2_node - Node where to clean qemu. Type: dictionary
| | ... | - dut2_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Performance test with vhost and VM with dpdk-testpmd teardown \
| | ... | \| 4.0mpps \| 64 \| 3-node-IPv4 \| ${node['DUT1']} \| ${dut_vm_refs} \
| | ... | \| ${node['DUT2']} \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${topology_type}
| | ... | ${dut1_node}=${None} | ${dut1_vm_refs}=${None}
| | ... | ${dut2_node}=${None} | ${dut2_vm_refs}=${None}
| | ...
| | Show VAT History On All DUTs | ${nodes}
| | Show Vpp Vhost On All DUTs
| | Show Packet Trace on All DUTs | ${nodes}
| | Show statistics on all DUTs
| | Run Keyword If Test Failed
| | ... | Traffic should pass with no loss | ${perf_trial_duration} | ${rate}
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}
| | Remove startup configuration of VPP from all DUTs
| | Run keyword unless | ${dut1_node}==${None}
| | ... | Guest VM with dpdk-testpmd Teardown | ${dut1} | ${dut1_vm_refs}
| | Run keyword unless | ${dut2_node}==${None}
| | ... | Guest VM with dpdk-testpmd Teardown | ${dut2} | ${dut2_vm_refs}
