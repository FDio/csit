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
| Library | Collections
| Library | String
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.DpdkUtil
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TestConfig
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Library | resources.libraries.python.VhostUser
| ...
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/l2/l2_patch.robot
| Resource | resources/libraries/robot/l2/l2_xconnect.robot
| Resource | resources/libraries/robot/l2/tagging.robot
| Resource | resources/libraries/robot/overlay/srv6.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| ...
| Documentation | Performance suite keywords - configuration

*** Keywords ***
| Set interfaces in path up
| | [Documentation]
| | ... | *Set UP state on VPP interfaces in path on all DUT nodes and set
| | ... | maximal MTU.*
| | ...
# TODO: Rework KW to set all interfaces in path UP and set MTU (including
# software interfaces. Run KW at the start phase of VPP setup to split
# from other "functional" configuration. This will allow modularity of this
# library
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut}_if1}
| | | Run Keyword If | '${if1_status}' == 'PASS'
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if1} | up
| | | ... | ELSE
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if1_1} | up
| | | Run Keyword Unless | '${if1_status}' == 'PASS'
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if1_2} | up
| | | ${if2_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut}_if2}
| | | Run Keyword If | '${if2_status}' == 'PASS'
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if2} | up
| | | ... | ELSE
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if2_1} | up
| | | Run Keyword Unless | '${if2_status}' == 'PASS'
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if2_2} | up
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut}_if1}
| | | Run Keyword If | '${if1_status}' == 'PASS'
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ELSE
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if1_1}
| | | Run Keyword Unless | '${if1_status}' == 'PASS'
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if1_2}
| | | ${if2_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut}_if2}
| | | Run Keyword If | '${if2_status}' == 'PASS'
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if2}
| | | ... | ELSE
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if2_1}
| | | Run Keyword Unless | '${if2_status}' == 'PASS'
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if2_2}
| | All VPP Interfaces Ready Wait | ${nodes} | retries=${300}

| Set single interfaces in path up
| | [Documentation]
| | ... | *Set UP state on single VPP interfaces in path on all DUT nodes and set
| | ... | maximal MTU.*
| | ...
# TODO: Rework KW to set all interfaces in path UP and set MTU (including
# software interfaces. Run KW at the start phase of VPP setup to split
# from other "functional" configuration. This will allow modularity of this
# library
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut}_if1}
| | | Run Keyword If | '${if1_status}' == 'PASS'
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if1} | up
| | | ... | ELSE
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if1_1} | up
| | | Run Keyword Unless | '${if1_status}' == 'PASS'
| | | ... | Set Interface State | ${nodes['${dut}']} | ${${dut}_if1_2} | up
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut}_if1}
| | | Run Keyword If | '${if1_status}' == 'PASS'
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ELSE
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if1_1}
| | | Run Keyword Unless | '${if1_status}' == 'PASS'
| | | ... | VPP Set Interface MTU | ${nodes['${dut}']} | ${${dut}_if1_2}
| | All VPP Interfaces Ready Wait | ${nodes}

| Initialize AVF interfaces
| | [Documentation]
| | ... | Initialize AVF interfaces on each DUT. Interfaces are brought up.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_pci}= | Get Interface PCI Addr | ${nodes['${dut}']}
| | | ... | ${${dut}_if1_vf0}
| | | ${if2_pci}= | Get Interface PCI Addr | ${nodes['${dut}']}
| | | ... | ${${dut}_if2_vf0}
| | | ${dut_eth_vf_if1}= | VPP Create AVF Interface | ${nodes['${dut}']}
| | | ... | ${if1_pci} | ${rxq_count_int}
| | | ${dut_eth_vf_if2}= | VPP Create AVF Interface | ${nodes['${dut}']}
| | | ... | ${if2_pci} | ${rxq_count_int}
| | | Set Test Variable | ${${dut}_if1} | ${dut_eth_vf_if1}
| | | Set Test Variable | ${${dut}_if2} | ${dut_eth_vf_if2}
| | Set interfaces in path up

| Initialize IPSec in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup ARP on all VPP
| | ... | interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG and
| | ... | DUT1-DUT2 links. Set routing for encrypted traffic on both DUT nodes
| | ... | with prefix /8 and next hop of neighbour DUT or TG interface IPv4
| | ... | address.
| | ...
| | Set interfaces in path up
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if1_mac}= | Get Interface MAC | ${dut1} | ${dut1_if1}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | ${dut2_if2_mac}= | Get Interface MAC | ${dut2} | ${dut2_if2}
| | Set Test Variable | ${tg_if1_mac}
| | Set Test Variable | ${tg_if2_mac}
| | Set Test Variable | ${dut1_if1_mac}
| | Set Test Variable | ${dut1_if2_mac}
| | Set Test Variable | ${dut2_if1_mac}
| | Set Test Variable | ${dut2_if2_mac}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | ${dut1_if1_ip4} | 24
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2}
| | ... | ${dut2_if2_ip4} | 24
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | ${tg_if1_ip4} | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | ${tg_if2_ip4} | ${tg_if2_mac}
| | Vpp Route Add | ${dut1} | ${laddr_ip4} | 8 | gateway=${tg_if1_ip4}
| | ... | interface=${dut1_if1}
| | Vpp Route Add | ${dut2} | ${raddr_ip4} | 8 | gateway=${tg_if2_ip4}
| | ... | interface=${dut2_if2}

| Initialize IPv4 forwarding in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| | ...
| | ... | *Arguments:*
| | ... | - remote_host1_ip - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip - IP address of remote host2 (Optional).
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv4 forwarding in circular topology \
| | ... | \| 192.168.0.1 \| 192.168.0.2 \|
| | ...
| | [Arguments] | ${remote_host1_ip}=${NONE} | ${remote_host2_ip}=${NONE}
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ...
| | Set interfaces in path up
| | ...
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | 1.1.1.2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | 1.1.1.1 | ${dut1_if2_mac}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 20.20.20.2 | ${tg_if2_mac}
| | ...
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | 10.10.10.1 | 24
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | 1.1.1.1 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1}
| | ... | 1.1.1.2 | 30
| | Configure IP addresses on interfaces | ${dut} | ${dut_if2}
| | ... | 20.20.20.1 | 24
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | gateway=1.1.1.2
| | ... | interface=${dut1_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | gateway=1.1.1.1
| | ... | interface=${dut2_if1}
| | ...
| | Run Keyword Unless | '${remote_host1_ip}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip} | 32
| | ... | gateway=10.10.10.2 | interface=${dut1_if1}
| | Run Keyword Unless | '${remote_host2_ip}' == '${NONE}'
| | ... | Vpp Route Add | ${dut} | ${remote_host2_ip} | 32
| | ... | gateway=20.20.20.2 | interface=${dut_if2}
| | Run Keyword Unless | '${remote_host1_ip}' == '${NONE}'
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip} | 32
| | ... | gateway=1.1.1.2 | interface=${dut1_if2}
| | Run Keyword Unless | '${remote_host2_ip}' == '${NONE}'
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${remote_host2_ip} | 32
| | ... | gateway=1.1.1.1 | interface=${dut2_if1}

| Initialize IPv4 forwarding with scaling in circular topology
| | [Documentation]
| | ... | Custom setup of IPv4 topology with scalability of ip routes on all
| | ... | DUT nodes in 2-node / 3-node circular topology
| | ...
| | ... | *Arguments:*
| | ... | - count - IP route count. Type: integer
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
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ...
| | Set interfaces in path up
| | ...
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 1.1.1.1 | ${tg1_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | 2.2.2.2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | 2.2.2.1 | ${dut1_if2_mac}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 3.3.3.1 | ${tg1_if2_mac}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1} | 1.1.1.2 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 2.2.2.1
| | ... | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 2.2.2.2
| | ... | 30
| | Configure IP addresses on interfaces | ${dut} | ${dut_if2} | 3.3.3.2 | 30
| | Vpp Route Add | ${dut1} | 10.0.0.0 | 32 | gateway=1.1.1.1
| | ... | interface=${dut1_if1} | count=${count}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 20.0.0.0 | 32 | gateway=2.2.2.2
| | ... | interface=${dut1_if2} | count=${count}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 10.0.0.0 | 32 | gateway=2.2.2.1
| | ... | interface=${dut2_if1} | count=${count}
| | Vpp Route Add | ${dut} | 20.0.0.0 | 32 | gateway=3.3.3.1
| | ... | interface=${dut_if2} | count=${count}

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
| | ...
| | ... | *Arguments:*
| | ... | - nf_nodes - Number of guest VMs. Type: integer
| | ...
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /var/run/vpp/sock-${VM_ID}-1
| | ... | - /var/run/vpp/sock-${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 forwarding with Vhost-User initialized in a 2-node circular\
| | ... | topology \| 1 \|
| | ...
| | [Arguments] | ${nf_nodes}=${1}
| | ...
| | Set interfaces in path up
| | ${fib_table_1}= | Set Variable | ${101}
| | ${fib_table_2}= | Evaluate | ${fib_table_1}+${nf_nodes}
| | Add Fib Table | ${dut1} | ${fib_table_1}
| | Add Fib Table | ${dut1} | ${fib_table_2}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if2} | ${fib_table_2}
| | Configure IP addresses on interfaces
| | ... | ${dut1} | ${dut1_if1} | 100.0.0.1 | 30
| | Configure IP addresses on interfaces
| | ... | ${dut1} | ${dut1_if2} | 200.0.0.1 | 30
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 100.0.0.2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 200.0.0.2 | ${tg_if2_mac}
| | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=100.0.0.2
| | ... | interface=${dut1_if1} | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=200.0.0.2
| | ... | interface=${dut1_if2} | vrf=${fib_table_2}
| | :FOR | ${number} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${fib_table_1}= | Evaluate | ${100}+${number}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1}+${1}
| | | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | | ... | /var/run/vpp/sock-${number}-1 | /var/run/vpp/sock-${number}-2
| | | ... | dut1-vhost-${number}-if1 | dut1-vhost-${number}-if2
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if1} | up
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if2} | up
| | | Add Fib Table | ${dut1} | ${fib_table_1}
| | | Add Fib Table | ${dut1} | ${fib_table_2}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | ${fib_table_1}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | ${fib_table_2}
| | | Configure IP addresses on interfaces
| | | ... | ${dut1} | ${dut1-vhost-${number}-if1} | 1.1.1.2 | 30
| | | ... | ${dut1} | ${dut1-vhost-${number}-if2} | 1.1.2.2 | 30
| | | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=1.1.1.1
| | | ... | interface=${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=1.1.2.1
| | | ... | interface=${dut1-vhost-${number}-if2} | vrf=${fib_table_2}

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
| | ...
| | ... | *Arguments:*
| | ... | - nf_nodes - Number of guest VMs. Type: integer
| | ...
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /var/run/vpp/sock-\${VM_ID}-1
| | ... | - /var/run/vpp/sock-\${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv4 forwarding with Vhost-User initialized in a 3-node circular\
| | ... | topology \| 1 \|
| | ...
| | [Arguments] | ${nf_nodes}=${1}
| | ...
| | Set interfaces in path up
| | ${fib_table_1}= | Set Variable | ${101}
| | ${fib_table_2}= | Evaluate | ${fib_table_1}+${nf_nodes}
| | Add Fib Table | ${dut1} | ${fib_table_1}
| | Add Fib Table | ${dut1} | ${fib_table_2}
| | Add Fib Table | ${dut2} | ${fib_table_1}
| | Add Fib Table | ${dut2} | ${fib_table_2}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if2} | ${fib_table_2}
| | Assign Interface To Fib Table | ${dut2} | ${dut2_if1} | ${fib_table_1}
| | Assign Interface To Fib Table | ${dut2} | ${dut2_if2} | ${fib_table_2}
| | Configure IP addresses on interfaces
| | ... | ${dut1} | ${dut1_if1} | 100.0.0.1 | 30
| | Configure IP addresses on interfaces
| | ... | ${dut1} | ${dut1_if2} | 150.0.0.1 | 30
| | Configure IP addresses on interfaces
| | ... | ${dut2} | ${dut2_if1} | 150.0.0.2 | 30
| | Configure IP addresses on interfaces
| | ... | ${dut2} | ${dut2_if2} | 200.0.0.1 | 30
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 100.0.0.2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 200.0.0.2 | ${tg_if2_mac}
| | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=100.0.0.2
| | ... | interface=${dut1_if1} | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=150.0.0.2
| | ... | interface=${dut1_if2} | vrf=${fib_table_2}
| | Vpp Route Add | ${dut2} | 10.0.0.0 | 8 | gateway=150.0.0.1
| | ... | interface=${dut2_if1} | vrf=${fib_table_1}
| | Vpp Route Add | ${dut2} | 20.0.0.0 | 8 | gateway=200.0.0.2
| | ... | interface=${dut2_if2} | vrf=${fib_table_2}
| | :FOR | ${number} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${fib_table_1}= | Evaluate | ${100}+${number}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1}+${1}
| | | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | | ... | /var/run/vpp/sock-${number}-1 | /var/run/vpp/sock-${number}-2
| | | ... | dut1-vhost-${number}-if1 | dut1-vhost-${number}-if2
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if1} | up
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if2} | up
| | | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | | ... | /var/run/vpp/sock-${number}-1 | /var/run/vpp/sock-${number}-2
| | | ... | dut2-vhost-${number}-if1 | dut2-vhost-${number}-if2
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
| | | Configure IP addresses on interfaces
| | | ... | ${dut1} | ${dut1-vhost-${number}-if1} | 1.1.1.2 | 30
| | | ... | ${dut1} | ${dut1-vhost-${number}-if2} | 1.1.2.2 | 30
| | | ... | ${dut2} | ${dut2-vhost-${number}-if1} | 1.1.1.2 | 30
| | | ... | ${dut2} | ${dut2-vhost-${number}-if2} | 1.1.2.2 | 30
| | | Vpp Route Add | ${dut1} | 20.0.0.0 | 8 | gateway=1.1.1.1
| | | ... | interface=${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Vpp Route Add | ${dut1} | 10.0.0.0 | 8 | gateway=1.1.2.1
| | | ... | interface=${dut1-vhost-${number}-if2} | vrf=${fib_table_2}
| | | Vpp Route Add | ${dut2} | 20.0.0.0 | 8 | gateway=1.1.1.1
| | | ... | interface=${dut2-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Vpp Route Add | ${dut2} | 10.0.0.0 | 8 | gateway=1.1.2.1
| | | ... | interface=${dut2-vhost-${number}-if2} | vrf=${fib_table_2}

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
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_net - TG interface 1 IP subnet used by traffic generator.
| | ... | Type: integer
| | ... | - tg_if2_net - TG interface 2 IP subnet used by traffic generator.
| | ... | Type: integer
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
| | ... | \| Initialize IPv4 forwarding with VLAN dot1q sub-interfaces\
| | ... | in circular topology \| 10.10.10.0 \| 20.20.20.0 \| 10 \| pop-1 \|
| | ...
| | [Arguments] | ${tg_if1_net} | ${tg_if2_net} | ${subid} | ${tag_rewrite}
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
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 1.1.1.1 | ${tg1_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${subif_index_1} | 2.2.2.2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${subif_index_2} | 2.2.2.1 | ${dut1_if2_mac}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${subif_index_1}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 3.3.3.1 | ${tg1_if2_mac}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1} | 1.1.1.2 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut1} | ${subif_index_1}
| | ... | 2.2.2.1 | 30
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut2} | ${subif_index_2}
| | ... | 2.2.2.2 | 30
| | Configure IP addresses on interfaces | ${dut} | ${dut_if2} | 3.3.3.2 | 30
| | Vpp Route Add | ${dut1} | ${tg_if1_net} | 30 | gateway=1.1.1.1
| | ... | interface=${dut1_if1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${tg_if2_net} | 30 | gateway=2.2.2.2
| | ... | interface=${subif_index_1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${tg_if1_net} | 30 | gateway=2.2.2.1
| | ... | interface=${subif_index_2}
| | Vpp Route Add | ${dut} | ${tg_if2_net} | 30 | gateway=3.3.3.1
| | ... | interface=${dut_if2}

| Initialize IPv6 forwarding in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup neighbor
| | ... | on all VPP interfaces. Setup IPv6 addresses with /64 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv6 adresses with /64 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /64
| | ... | and next hop of neighbour DUT interface IPv4 address.
| | ...
| | ... | *Arguments:*
| | ... | - remote_host1_ip - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip - IP address of remote host2 (Optional).
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv6 forwarding in circular topology \
| | ... | \| 3ffe:5f::1 \| 3ffe:5f::2 \|
| | ...
| | [Arguments] | ${remote_host1_ip}=${NONE} | ${remote_host2_ip}=${NONE}
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ...
| | Set interfaces in path up
| | ...
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | 2001:3::1 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | 2001:3::2 | ${dut1_if2_mac}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 2001:2::2 | ${tg_if2_mac}
| | ...
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 2001:1::1 | 64
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut1} | ${dut1_if2} | 2001:3::1 | 64
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut2} | ${dut2_if1} | 2001:3::2 | 64
| | VPP Interface Set IP Address | ${dut} | ${dut_if2} | 2001:2::1 | 64
| | ...
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 2001:2::0 | 64 | gateway=2001:3::2
| | ... | interface=${dut1_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 2001:1::0 | 64 | gateway=2001:3::1
| | ... | interface=${dut2_if1}
| | ...
| | Run Keyword Unless | '${remote_host1_ip}' == '${NONE}'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip} | 128
| | ... | gateway=2001:1::2 | interface=${dut1_if1}
| | Run Keyword Unless | '${remote_host2_ip}' == '${NONE}'
| | ... | Vpp Route Add | ${dut} | ${remote_host2_ip} | 128
| | ... | gateway=2001:2::2 | interface=${dut_if2}
| | Run Keyword Unless | '${remote_host1_ip}' == '${NONE}'
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${remote_host1_ip} | 128
| | ... | gateway=2001:3::2 | interface=${dut1_if2}
| | Run Keyword Unless | '${remote_host2_ip}' == '${NONE}'
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${remote_host2_ip} | 128
| | ... | gateway=2001:3::1 | interface=${dut2_if1}

| Initialize IPv6 forwarding with scaling in circular topology
| | [Documentation]
| | ... | Custom setup of IPv6 topology with scalability of ip routes on all
| | ... | DUT nodes in 2-node / 3-node circular topology
| | ...
| | ... | *Arguments:*
| | ... | - count - IP route count. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv6 forwarding with scaling in circular \
| | ... | topology \| 100000 \|
| | ...
| | [Arguments] | ${count}
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ...
| | Set interfaces in path up
| | ...
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut2} | ${dut2_if1}
| | ${prefix}= | Set Variable | 64
| | ${host_prefix}= | Set Variable | 128
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 2001:3::1 | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | 2001:4::1 | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | 2001:4::2 | ${prefix}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | VPP Interface Set IP Address | ${dut} | ${dut_if2} | 2001:5::1 | ${prefix}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:3::2 | ${tg1_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut1} | ${dut1_if2} | 2001:4::2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut2} | ${dut2_if1} | 2001:4::1 | ${dut1_if2_mac}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 2001:5::2 | ${tg1_if2_mac}
| | Vpp Route Add | ${dut1} | 2001:1::0 | ${host_prefix} | gateway=2001:3::2
| | ... | interface=${dut1_if1} | count=${count}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 2001:2::0 | ${host_prefix}
| | ... | gateway=2001:4::2 | interface=${dut1_if2} | count=${count}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 2001:1::0 | ${host_prefix}
| | ... | gateway=2001:4::1 | interface=${dut2_if1} | count=${count}
| | Vpp Route Add | ${dut} | 2001:2::0 | ${host_prefix} | gateway=2001:5::2
| | ... | interface=${dut_if2} | count=${count}

| Initialize IPv6 forwarding with vhost in 2-node circular topology
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on \
| | ... | VPP node. Set UP state of all VPP interfaces in path. Create \
| | ... | nf_nodes+1 FIB tables on DUT with multipath routing. Assign each \
| | ... | Virtual interface to FIB table with Physical interface or Virtual \
| | ... | interface on both nodes. Setup IPv6 addresses with /64 prefix on \
| | ... | DUT-TG links. Set routing on DUT nodes in all FIB tables with \
| | ... | prefix /64 and next hop of neighbour IPv6 address. Setup neighbours \
| | ... | on all VPP interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - nf_nodes - Number of guest VMs. Type: integer
| | ...
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /var/run/vpp/sock-${VM_ID}-1
| | ... | - /var/run/vpp/sock-${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv6 forwarding with Vhost-User initialized in a 2-node circular\
| | ... | topology \| 1 \|
| | ...
| | [Arguments] | ${nf_nodes}=${1}
| | ...
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | Set interfaces in path up
| | ${prefix}= | Set Variable | 64
| | ${fib_table_1}= | Set Variable | ${101}
| | ${fib_table_2}= | Evaluate | ${fib_table_1}+${nf_nodes}
| | Add Fib Table | ${dut1} | ${fib_table_1} | ipv6=${True}
| | Add Fib Table | ${dut1} | ${fib_table_2} | ipv6=${True}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if1} | ${fib_table_1}
| | ... | ipv6=${True}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if2} | ${fib_table_2}
| | ... | ipv6=${True}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 2001:100::1
| | ... | ${prefix}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if2} | 2001:200::1
| | ... | ${prefix}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:100::2 | ${tg_if1_mac}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 2001:200::2 | ${tg_if2_mac}
| | Vpp Route Add | ${dut1} | 2001:1::0 | 64 | gateway=2001:100::2
| | ... | interface=${dut1_if1} | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1} | 2001:2::0 | 64 | gateway=2001:200::2
| | ... | interface=${dut1_if2} | vrf=${fib_table_2}
| | :FOR | ${number} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${fib_table_1}= | Evaluate | ${100}+${number}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1}+${1}
| | | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | | ... | /var/run/vpp/sock-${number}-1 | /var/run/vpp/sock-${number}-2
| | | ... | dut1-vhost-${number}-if1 | dut1-vhost-${number}-if2
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if1} | up
| | | Set Interface State | ${dut1} | ${dut1-vhost-${number}-if2} | up
| | | Add Fib Table | ${dut1} | ${fib_table_1} | ipv6=${True}
| | | Add Fib Table | ${dut1} | ${fib_table_2} | ipv6=${True}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if1}
| | | ... | ${fib_table_1} | ipv6=${True}
| | | Assign Interface To Fib Table | ${dut1} | ${dut1-vhost-${number}-if2}
| | | ... | ${fib_table_2} | ipv6=${True}
| | | Configure IP addresses on interfaces
| | | ... | ${dut1} | ${dut1-vhost-${number}-if1} | 1:1::2 | 64
| | | ... | ${dut1} | ${dut1-vhost-${number}-if2} | 1:2::2 | 64
| | | Vpp Route Add | ${dut1} | 2001:2::0 | 64 | gateway=1:1::1
| | | ... | interface=${dut1-vhost-${number}-if1} | vrf=${fib_table_1}
| | | Vpp Route Add | ${dut1} | 2001:1::0 | 64 | gateway=1:2::1
| | | ... | interface=${dut1-vhost-${number}-if2} | vrf=${fib_table_2}

| Initialize IPv6 forwarding with VLAN dot1q sub-interfaces in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. In case of 3-node topology create VLAN
| | ... | sub-interfaces between DUTs. In case of 2-node topology create VLAN
| | ... | sub-interface on dut1-if2 interface. Get the interface MAC addresses
| | ... | and setup ARPs. Setup IPv6 addresses with /64 prefix on DUT-TG links
| | ... | and set routing with prefix /64. In case of 3-node set IPv6 adresses
| | ... | with /64 prefix on VLAN and set routing on both DUT nodes with prefix
| | ... | /64. Set next hop of neighbour DUT interface IPv6 address. All
| | ... | interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - tg_if1_net - TG interface 1 IPv6 subnet used by traffic generator.
| | ... | Type: integer
| | ... | - tg_if2_net - TG interface 2 IPv6 subnet used by traffic generator.
| | ... | Type: integer
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
| | ... | \| Initialize IPv6 forwarding with VLAN dot1q sub-interfaces\
| | ... | in circular topology \| 2001:1::0 \| 2001:2::0 \| 10 \| pop-1 \|
| | ...
| | [Arguments] | ${tg_if1_net} | ${tg_if2_net} | ${subid} | ${tag_rewrite}
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
| | ${prefix}= | Set Variable | 64
| | ${host_prefix}= | Set Variable | 64
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2002:1::1 | ${tg1_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut1} | ${subif_index_1} | 2002:2::2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add Ip Neighbor
| | ... | ${dut2} | ${subif_index_2} | 2002:2::1 | ${dut1_if2_mac}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${subif_index_1}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 2002:3::1 | ${tg1_if2_mac}
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 2002:1::2 | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut1} | ${subif_index_1} | 2002:2::1
| | ... | ${prefix}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut2} | ${subif_index_2} | 2002:2::2
| | ... | ${prefix}
| | VPP Interface Set IP Address | ${dut} | ${dut_if2} | 2002:3::2 | ${prefix}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | Vpp Route Add | ${dut1} | ${tg_if1_net} | ${host_prefix}
| | ... | gateway=2002:1::1 | interface=${dut1_if1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | ${tg_if2_net} | ${host_prefix}
| | ... | gateway=2002:2::2 | interface=${subif_index_1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | ${tg_if1_net} | ${host_prefix}
| | ... | gateway=2002:2::1 | interface=${subif_index_2}
| | Vpp Route Add | ${dut} | ${tg_if2_net} | ${host_prefix}
| | ... | gateway=2002:3::1 | interface=${dut_if2}

| Initialize IPv6 forwarding over SRv6 with encapsulation with '${n}' x SID '${prepos}' decapsulation in 3-node circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 3-node circular
| | ... | topology. Get the interface MAC addresses and setup neighbours on all
| | ... | VPP interfaces. Setup IPv6 addresses on all interfaces. Set segment
| | ... | routing for IPv6 for required number of SIDs and configure IPv6 routes
| | ... | on both DUT nodes.
| | ...
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip6} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_if2_ip6} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_if1_ip6} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_if2_ip6} | ${prefix}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | :FOR | ${number} | IN RANGE | 2 | ${dst_addr_nr}+2
| | | ${hexa_nr}= | Convert To Hex | ${number}
| | | VPP Add IP Neighbor | ${dut1}
| | | ... | ${dut1_if1} | ${tg_if1_ip6_subnet}${hexa_nr} | ${tg1_if1_mac}
| | | VPP Add IP Neighbor | ${dut2}
| | | ... | ${dut2_if2} | ${tg_if2_ip6_subnet}${hexa_nr} | ${tg1_if2_mac}
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
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
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
| | ${duts}= | Get Matches | ${nodes} | DUT*
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
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_if1_ip6} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_if2_ip6} | ${dut1_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if1} | ${tg_if1_ip6_subnet}2 | ${tg1_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if2} | ${tg_if2_ip6_subnet}2 | ${tg1_if2_mac}
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

| Initialize L2 patch
| | [Documentation]
| | ... | Setup L2 patch topology by cross connecting two interfaces on
| | ... | each DUT. Interfaces are brought up.
| | ...
| | Set interfaces in path up
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Configure L2patch | ${nodes['${dut}']} | ${${dut}_if1} | ${${dut}_if2}

| Initialize L2 xconnect in 2-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology by cross connecting two interfaces on
| | ... | each DUT. Interfaces are brought up.
| | ...
| | Set interfaces in path up
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Initialize L2 xconnect in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology by cross connecting two interfaces on
| | ... | each DUT. Interfaces are brought up.
| | ... |
| | Set interfaces in path up
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure L2XC | ${dut2} | ${dut2_if1} | ${dut2_if2}

| Initialize L2 xconnect with VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 xconnect topology with VXLANoIPv4 by cross connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | between DUTs. VXLAN sub-interfaces has same IPv4 address as
| | ... | interfaces.
| | ...
| | Set interfaces in path up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if2} | 172.16.0.1 | 24
| | VPP Interface Set IP Address | ${dut2} | ${dut2_if1} | 172.16.0.2 | 24
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 172.16.0.2 | ${dut2_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if1} | 172.16.0.1 | ${dut1_if2_mac}
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${dut2s_vxlan}

| Initialize L2 xconnect with Vhost-User on node
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on
| | ... | defined VPP node. Add each Vhost-User interface into L2 cross-connect
| | ... | with with physical inteface or Vhost-User interface of another VM.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - nf_nodes - VM count. Type: integer
| | ...
| | ... | *Note:*
| | ... | Socket paths for VM are defined in following format:
| | ... | - /tmp/sock-\${VM_ID}-1
| | ... | - /tmp/sock-\${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 xconnect with Vhost-User on node \| DUT1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${nf_nodes}=${1}
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${sock1}= | Set Variable | /var/run/vpp/sock-${number}-1
| | | ${sock2}= | Set Variable | /var/run/vpp/sock-${number}-2
| | | ${prev_index}= | Evaluate | ${number}-1
| | | Configure vhost interfaces for L2BD forwarding | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${dut}-vhost-${number}-if1
| | | ... | ${dut}-vhost-${number}-if2
| | | ${dut_xconnect_if1}= | Set Variable If | ${number}==1 | ${${dut}_if1}
| | | ... | ${${dut}-vhost-${prev_index}-if2}
| | | Configure L2XC | ${nodes['${dut}']} | ${dut_xconnect_if1}
| | | ... | ${${dut}-vhost-${number}-if1}
| | | Run Keyword If | ${number}==${nf_nodes} | Configure L2XC
| | | ... | ${nodes['${dut}']} | ${${dut}-vhost-${number}-if2} | ${${dut}_if2}

| Initialize L2 xconnect with Vhost-User
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of VMs on
| | ... | all VPP nodes. Add each Vhost-User interface into L2 cross-connect
| | ... | with with physical inteface or Vhost-User interface of another VM.
| | ...
| | ... | *Arguments:*
| | ... | - nf_nodes - VM count. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 xconnect with Vhost-User \| 1 \|
| | ...
| | [Arguments] | ${nf_nodes}=${1}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize L2 xconnect with Vhost-User on node | ${dut}
| | | ... | nf_nodes=${nf_nodes}

| Initialize L2 xconnect with Vhost-User and VLAN in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Cross
| | ... | connect each Vhost interface with one physical interface.
| | ... | Setup VLAN between DUTs. All interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| L2 xconnect with Vhost-User and VLAN initialized in a 3-node\
| | ... | circular topology \| 10 \| pop-1 \|
| | ...
| | [Arguments] | ${subid} | ${tag_rewrite}
| | ...
| | Set interfaces in path up
| | Initialize VLAN dot1q sub-interfaces in circular topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | Configure L2 tag rewrite method on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | /var/run/vpp/sock-1-1 | /var/run/vpp/sock-1-2
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${vhost_if1}
| | Configure L2XC | ${dut1} | ${subif_index_1} | ${vhost_if2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | /var/run/vpp/sock-1-1 | /var/run/vpp/sock-1-2
| | Configure L2XC | ${dut2} | ${subif_index_2} | ${vhost_if1}
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${vhost_if2}

| Initialize L2 xconnect with Vhost-User and VLAN with VPP link bonding in 3-node circular topology
| | [Documentation]
| | ... | Create two Vhost-User interfaces on all defined VPP nodes. Create one
| | ... | link bonding (BondEthernet) interface on both VPP nodes. Enslave one
| | ... | physical interface towards next DUT by BondEthernet interface. Setup
| | ... | VLAN on BondEthernet interfaces between DUTs. Cross connect one Vhost
| | ... | interface with physical interface towards TG and other Vhost interface
| | ... | with VLAN sub-interface. All interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - subid - ID of the sub-interface to be created. Type: string
| | ... | - tag_rewrite - Method of tag rewrite. Type: string
| | ... | - bond_mode - Link bonding mode. Type: string
| | ... | - lb_mode - Load balance mode. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 xconnect with Vhost-User and VLAN with VPP link\
| | ... | bonding in 3-node circular topology \| 10 \| pop-1 \| xor \| l34 \|
| | ...
| | [Arguments] | ${subid} | ${tag_rewrite} | ${bond_mode} | ${lb_mode}
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
| | VPP Set interface MTU | ${dut1} | ${dut1_eth_bond_if1}
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
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | /var/run/vpp/sock-1-1 | /var/run/vpp/sock-1-2
| | Configure L2XC | ${dut1} | ${dut1_if1} | ${vhost_if1}
| | Configure L2XC | ${dut1} | ${subif_index_1} | ${vhost_if2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | /var/run/vpp/sock-1-1 | /var/run/vpp/sock-1-2
| | Configure L2XC | ${dut2} | ${subif_index_2} | ${vhost_if1}
| | Configure L2XC | ${dut2} | ${dut2_if2} | ${vhost_if2}

| Initialize L2 bridge domain in circular topology
| | [Documentation]
| | ... | Setup L2 DB topology by adding two interfaces on each DUT into BD
| | ... | that is created automatically with index 1. Learning is enabled.
| | ... | Interfaces are brought up.
| | ...
| | ... | *Arguments:*
| | ... | - bd_id - Bridge domain ID. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domain in circular topology \| 1 \|
| | ...
| | [Arguments] | ${bd_id}=${1}
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ...
| | Set interfaces in path up
| | ...
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id}
| | Add interface to bridge domain | ${dut1} | ${dut1_if2} | ${bd_id}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${dut2_if1} | ${bd_id}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id}

| Configure IPv4 ACLs
| | [Documentation]
| | ... | Configure ACL with required number of not-hitting permit ACEs plus two
| | ... | hitting ACEs for both traffic directions.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - dut_if1 - DUT node interface1 name (Optional). Type: string
| | ... | - dut_if2 - DUT node interface2 name (Optional). Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure IPv4 ACLs \| ${nodes['DUT1']} \| GigabitEthernet0/7/0 \
| | ... | \| GigabitEthernet0/8/0 \|
| | ...
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
| | ...
| | [Arguments] | ${dut} | ${dut_if1}=${NONE} | ${dut_if2}=${NONE}
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

| Initialize L2 bridge domain with IPv4 ACLs on DUT1 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2BD topology by adding two interfaces on DUT1 into bridge
| | ... | domain that is created automatically with index 1. Learning is
| | ... | enabled. Interfaces are brought up. Apply required ACL rules to DUT1
| | ... | interfaces.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domain with IPv4 ACLs on DUT1 in 3-node \
| | ... | circular topology \|
| | ...
| | ... | _NOTE:_ This KW uses following test case variables:
| | ... | - dut1 - DUT1 node.
| | ... | - dut2 - DUT2 node.
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2_if1 - DUT2 interface towards DUT1.
| | ... | - dut2_if2 - DUT2 interface towards TG.
| | ...
| | Set interfaces in path up
| | Configure L2BD forwarding | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure L2XC | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Configure IPv4 ACLs | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Initialize IPv4 routing for '${ip_nr}' addresses with IPv4 ACLs on DUT1 in circular topology
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| | ... | Apply required ACL rules to DUT1 interfaces.
| | ...
| | ... | *Arguments:*
| | ... | - ip_nr - Number of IPs to be used. Type: integer or string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv4 routing for '10' addresses with IPv4 ACLs on DUT1 \
| | ... | in 3-node circular topology \|
| | ...
| | ... | _NOTE:_ This KW uses following test case variables:
| | ... | - tg - TG node.
| | ... | - dut1 - DUT1 node.
| | ... | - dut2 - DUT2 node.
| | ... | - tg_if1 - TG interface 1 towards DUT1.
| | ... | - tg_if2 - TG interface 2 towards DUT2 (3-node topo) or DUT1
| | ... | (2-node topo).
| | ... | - dut1_if1 - DUT1 interface 1 towards TG.
| | ... | - dut1_if2 - DUT1 interface 2 towards DUT2 (3-node topo) or TG
| | ... | (2-node topo).
| | ... | - dut2_if1 - DUT2 interface 1 towards DUT1.
| | ... | - dut2_if2 - DUT2 interface 2 towards TG.
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | ...
| | Set interfaces in path up
| | ...
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut2} | ${dut2_if1}
| | ...
| | :FOR | ${number} | IN RANGE | 2 | ${ip_nr}+2
| | | VPP Add IP Neighbor
| | | ... | ${dut1} | ${dut1_if1} | 10.10.10.${number} | ${tg1_if1_mac}
| | | VPP Add IP Neighbor
| | | ... | ${dut} | ${dut_if2} | 20.20.20.${number} | ${tg1_if2_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | 1.1.1.2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | 1.1.1.1 | ${dut1_if2_mac}
| | ...
| | Configure IP addresses on interfaces
| | ... | ${dut1} | ${dut1_if1} | 10.10.10.1 | 24
| | ... | ${dut} | ${dut_if2} | 20.20.20.1 | 24
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces
| | ... | ${dut1} | ${dut1_if2} | 1.1.1.1 | 30
| | ... | ${dut2} | ${dut2_if1} | 1.1.1.2 | 30
| | ...
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 20.20.20.0 | 24 | gateway=1.1.1.2
| | ... | interface=${dut1_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 10.10.10.0 | 24 | gateway=1.1.1.1
| | ... | interface=${dut2_if1}
| | ...
| | Configure IPv4 ACLs | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Configure MACIP ACLs
| | [Documentation]
| | ... | Configure MACIP ACL with required number of not-hitting permit ACEs
| | ... | plus two hitting ACEs for both traffic directions.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - dut_if1 - DUT node interface1 name (Optional). Type: string
| | ... | - dut_if2 - DUT node interface2 name (Optional). Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure MACIP ACLs \| ${nodes['DUT1']} \| GigabitEthernet0/7/0 \
| | ... | \| GigabitEthernet0/8/0 \|
| | ...
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
| | ...
| | [Arguments] | ${dut} | ${dut_if1}=${NONE} | ${dut_if2}=${NONE}
| | ...
| | ${src_ip_int} = | IP To Int | ${src_ip_start}
| | ${src_ip_int} = | Evaluate | ${src_ip_int} - ${ip_step}
| | ...
| | ${ip_limit} = | Set Variable | 255.255.255.255
| | ${ip_limit_int} = | IP To Int | ${ip_limit}
| | ...
| | ${src_mac_int} = | Mac To Int | ${src_mac_start}
| | ${src_mac_int} = | Evaluate | ${src_mac_int} - ${src_mac_step}
| | ...
| | ${mac_limit} = | Set Variable | ff:ff:ff:ff:ff:ff
| | ${mac_limit_int} = | Mac To Int | ${mac_limit}
| | ...
| | ${acl}= | Set Variable | ipv4 permit
| | :FOR | ${nr} | IN RANGE | 0 | ${no_hit_aces_number}
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

| Initialize L2 bridge domain with MACIP ACLs on DUT1 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2BD topology by adding two interfaces on DUT1 into bridge
| | ... | domain that is created automatically with index 1. Learning is
| | ... | enabled. Interfaces are brought up. Apply required MACIP ACL rules to
| | ... | DUT1 interfaces.
| | ...
| | ... | *Arguments:*
| | ... | _None_
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domain with MACIP ACLs on DUT1 in 3-node \
| | ... | circular topology \|
| | ...
| | ... | _NOTE 1:_ This KW uses following test case variables:
| | ... | - tg - TG node.
| | ... | - dut1 - DUT1 node.
| | ... | - dut2 - DUT2 node.
| | ... | - tg_if1 - TG interface towards DUT1.
| | ... | - tg_if2 - TG interface towards DUT2.
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2_if1 - DUT2 interface towards DUT1.
| | ... | - dut2_if2 - DUT2 interface towards TG.
| | ...
| | Set interfaces in path up
| | Configure L2BD forwarding | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure L2XC | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Configure MACIP ACLs | ${dut1} | ${dut1_if1} | ${dut1_if2}

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
| | ... | - /tmp/sock-\${VM_ID}-1
| | ... | - /tmp/sock-\${VM_ID}-2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domains with Vhost-User on node \| DUT1 \
| | ... | \| 1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${nf_chain}=${1} | ${nf_nodes}=${1}
| | ...
| | ${bd_id2}= | Evaluate | ${nf_nodes}+1
| | Add interface to bridge domain | ${nodes['${dut}']}
| | ... | ${${dut}_if1} | ${1}
| | Add interface to bridge domain | ${nodes['${dut}']}
| | ... | ${${dut}_if2} | ${bd_id2}
| | :FOR | ${nf_node} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${qemu_id}= | Evaluate | (${nf_chain} - ${1}) * ${nf_nodes} + ${nf_node}
| | | ${sock1}= | Set Variable | /var/run/vpp/sock-${qemu_id}-1
| | | ${sock2}= | Set Variable | /var/run/vpp/sock-${qemu_id}-2
| | | Configure vhost interfaces for L2BD forwarding | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2}
| | | ... | ${dut}-vhost-${qemu_id}-if1
| | | ... | ${dut}-vhost-${qemu_id}-if2
| | | ${bd_id2}= | Evaluate | ${nf_node}+1
| | | Add interface to bridge domain | ${nodes['${dut}']}
| | | ... | ${${dut}-vhost-${qemu_id}-if1} | ${nf_node}
| | | Add interface to bridge domain | ${nodes['${dut}']}
| | | ... | ${${dut}-vhost-${qemu_id}-if2} | ${bd_id2}

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
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize L2 bridge domains with Vhost-User on node | ${dut}
| | | ... | nf_chain=${nf_chain} | nf_nodes=${nf_nodes}

| Initialize L2 bridge domains for multiple chains with Vhost-User
| | [Documentation]
| | ... | Create pairs of Vhost-User interfaces for defined number of NF chains
| | ... | with defined number of VNF nodes on all defined VPP nodes. Add each
| | ... | Vhost-User interface into L2 bridge domains with learning enabled
| | ... | with physical inteface or Vhost-User interface of another VM.
| | ...
| | ... | *Arguments:*
| | ... | - nf_chains - Number of chains of NFs. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 bridge domains for multiple chains with Vhost-User \
| | ... | \| 1 \| 1 \|
| | ...
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1}
| | ...
| | :FOR | ${nf_chain} | IN RANGE | 1 | ${nf_chains}+1
| | | Initialize L2 bridge domains with Vhost-User | nf_chain=${nf_chain}
| | | ... | nf_nodes=${nf_nodes}

| Initialize L2 bridge domain with VXLANoIPv4 in 3-node circular topology
| | [Documentation]
| | ... | Setup L2 bridge domain topology with VXLANoIPv4 by connecting
| | ... | physical and vxlan interfaces on each DUT. All interfaces are brought
| | ... | up. IPv4 addresses with prefix /24 are configured on interfaces
| | ... | between DUTs. VXLAN sub-interfaces has same IPv4 address as
| | ... | interfaces.
| | ...
| | Set interfaces in path up
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 172.16.0.1
| | ... | 24
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 172.16.0.2
| | ... | 24
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 172.16.0.2 | ${dut2_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if1} | 172.16.0.1 | ${dut1_if2_mac}
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Configure L2BD forwarding | ${dut1} | ${dut1_if1} | ${dut1s_vxlan}
| | Configure L2BD forwarding | ${dut2} | ${dut2_if2} | ${dut2s_vxlan}

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
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2} | 172.16.0.1
| | ... | 24
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1} | 172.16.0.2
| | ... | 24
| | Set interfaces in path up
| | ${dut1s_vxlan}= | Create VXLAN interface | ${dut1} | 24
| | ... | 172.16.0.1 | 172.16.0.2
| | ${dut2s_vxlan}= | Create VXLAN interface | ${dut2} | 24
| | ... | 172.16.0.2 | 172.16.0.1
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1s_vxlan} | ${bd_id2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
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
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | /var/run/vpp/sock-1-${dut1_bd_id1}
| | ... | /var/run/vpp/sock-1-${dut1_bd_id2}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1} |
| | ... | ${dut1_address} | ${dut1_address_subnet}
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2} |
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
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
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
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${subif_index_1} | ${bd_id2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure vhost interfaces for L2BD forwarding | ${dut2}
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
| | Configure vhost interfaces for L2BD forwarding | ${dut1}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut1} | ${subif_index_1} | ${bd_id2}
| | Configure vhost interfaces for L2BD forwarding | ${dut2}
| | ... | /var/run/vpp/sock-1-${bd_id1} | /var/run/vpp/sock-1-${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${subif_index_2} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Add interface to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | Add interface to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}

| Initialize LISP IPv4 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 addresses on all DUT nodes and TG \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_dut2_address - Ip address from DUT1 to DUT2. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_address - Ip address from DUT2 to DUT1. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - duts_prefix - ip prefix. Type: int
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
| | Set interfaces in path up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg1_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_address} | ${dut1_if2_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 20.20.20.2 | ${tg1_if2_mac}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | ${dut1_tg_address} | ${duts_prefix}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | ${dut1_dut2_address} | ${duts_prefix}
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1}
| | ... | ${dut2_dut1_address} | ${duts_prefix}
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2}
| | ... | ${dut2_tg_address} | ${duts_prefix}

| Initialize LISP GPE IPv4 over IPsec in 3-node circular topology
| | [Documentation] | Setup Lisp GPE IPv4 forwarding over IPsec.
| | ...
| | ... | *Arguments:*
| | ... | - encr_alg - Encryption algorithm. Type: string
| | ... | - auth_alg - Authentication algorithm. Type: string
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
| | ... | - dut1_dut2_address - Ip address from DUT1 to DUT2. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_address - Ip address from DUT2 to DUT1. Type: string
| | ... | - dut1_tg_address - Ip address from DUT1 to tg. Type: string
| | ... | - duts_prefix - ip prefix. Type: int
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
| | Set interfaces in path up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_tg_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_address} | ${prefix}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_tg_address} | ${prefix}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg1_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg1_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_address} | ${dut1_if2_mac}

| Initialize LISP IPv4 over IPv6 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 over IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_dut2_ip6_address - IPv6 address from DUT1 to DUT2.
| | ... | Type: string
| | ... | - dut1_tg_ip4_address - IPv4 address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_ip6_address - IPv6 address from DUT2 to DUT1.
| | ... | Type: string
| | ... | - dut1_tg_ip4_address - IPv4 address from DUT1 to tg. Type: string
| | ... | - prefix4 - IPv4 prefix. Type: int
| | ... | - prefix6 - IPv6 prefix. Type: int
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
| | Set interfaces in path up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | ${dut1_tg_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_ip6_address} | ${prefix6}
| | Configure IP addresses on interfaces | ${dut2} | ${dut2_if2}
| | ... | ${dut2_tg_ip4_address} | ${prefix4}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.10.10.2 | ${tg1_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 20.20.20.2 | ${tg1_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip6_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip6_address} | ${dut1_if2_mac}

| Initialize LISP IPv6 over IPv4 forwarding in 3-node circular topology
| | [Documentation] | Custom setup of IPv4 over IPv6 topology on all DUT nodes \
| | ... | Don`t set route.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_dut2_ip4_address - IPv4 address from DUT1 to DUT2.
| | ... | Type: string
| | ... | - dut1_tg_ip6_address - IPv6 address from DUT1 to tg. Type: string
| | ... | - dut2_dut1_ip4_address - IPv4 address from DUT2 to DUT1.
| | ... | Type: string
| | ... | - dut1_tg_ip6_address - IPv6 address from DUT1 to tg. Type: string
| | ... | - prefix4 - IPv4 prefix. Type: int
| | ... | - prefix6 - IPv6 prefix. Type: int
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
| | Set interfaces in path up
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if1} | ${dut1_tg_ip6_address} | ${prefix6}
| | VPP Interface Set IP Address
| | ... | ${dut1} | ${dut1_if2} | ${dut1_dut2_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if1} | ${dut2_dut1_ip4_address} | ${prefix4}
| | VPP Interface Set IP Address
| | ... | ${dut2} | ${dut2_if2} | ${dut2_tg_ip6_address} | ${prefix6}
| | Suppress ICMPv6 router advertisement message | ${nodes}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 2001:1::2 | ${tg1_if1_mac}
| | VPP Add IP Neighbor | ${dut2} | ${dut2_if2} | 2001:2::2 | ${tg1_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | ${dut2_dut1_ip4_address} | ${dut2_if1_mac}
| | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | ${dut1_dut2_ip4_address} | ${dut1_if2_mac}

| Initialize NAT44 in circular topology
| | [Documentation] | Initialization of 2-node / 3-node topology with NAT44
| | ... | between DUTs:
| | ... | - set interfaces up
| | ... | - set IP addresses
| | ... | - set ARP
| | ... | - create routes
| | ... | - set NAT44 - only on DUT1
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ...
| | Set interfaces in path up
| | ...
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1} | 10.0.0.1 | 20
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | 11.0.0.1 | 20
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Configure IP addresses on interfaces | ${dut2} | ${dut2_if1}
| | ... | 11.0.0.2 | 20
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | Configure IP addresses on interfaces | ${dut} | ${dut_if2} | 12.0.0.1 | 20
| | ...
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Get Interface MAC | ${dut2} | ${dut2_if1}
| | ...
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if1} | 10.0.0.2 | ${tg_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${dut1_if2} | 11.0.0.2 | ${dut2_if1_mac}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${dut2_if1} | 11.0.0.1 | ${dut1_if2_mac}
| | VPP Add IP Neighbor | ${dut} | ${dut_if2} | 12.0.0.2 | ${tg_if2_mac}
| | ...
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 18 | gateway=10.0.0.2
| | ... | interface=${dut1_if1}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 12.0.0.2 | 32 | gateway=11.0.0.2
| | ... | interface=${dut1_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 12.0.0.0 | 24 | gateway=12.0.0.2
| | ... | interface=${dut2_if2}
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 200.0.0.0 | 30 | gateway=11.0.0.1
| | ... | interface=${dut2_if1}
| | ...
| | Configure inside and outside interfaces
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Configure deterministic mode for NAT44
| | ... | ${dut1} | 20.0.0.0 | 18 | 200.0.0.0 | 30

| Initialize L2 xconnect with memif pairs on DUT node
| | [Documentation]
| | ... | Create pairs of Memif interfaces on DUT node. Cross connect each Memif
| | ... | interface with one physical interface or virtual interface to create
| | ... | a chain accross DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: dictionary
| | ... | - count - Number of memif pairs (containers). Type: integer
| | ...
| | ... | *Note:*
| | ... | Socket paths for Memif are defined in following format:
| | ... | - /tmp/memif-\${dut}_CNF\${number}-\${sid}
| | ...
| | ... | KW uses test variable \${rxq_count_int} set by KW Add worker threads
| | ... | and rxqueues to all DUTs
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 xconnect with memif pairs on DUT node \| ${dut} \
| | ... | \| ${1} \|
| | ...
| | [Arguments] | ${dut} | ${count}
| | ...
| | :FOR | ${number} | IN RANGE | 1 | ${count}+1
| | | ${sock1}= | Set Variable | memif-${dut}_CNF
| | | ${sock2}= | Set Variable | memif-${dut}_CNF
| | | ${prev_index}= | Evaluate | ${number}-1
| | | Set up memif interfaces on DUT node | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${number} | ${dut}-memif-${number}-if1
| | | ... | ${dut}-memif-${number}-if2 | ${rxq_count_int} | ${rxq_count_int}
| | | ${xconnect_if1}= | Set Variable If | ${number}==1 | ${${dut}_if1}
| | | ... | ${${dut}-memif-${prev_index}-if2}
| | | Configure L2XC | ${nodes['${dut}']} | ${xconnect_if1}
| | | ... | ${${dut}-memif-${number}-if1}
| | | Run Keyword If | ${number}==${count} | Configure L2XC
| | | ... | ${nodes['${dut}']} | ${${dut}-memif-${number}-if2} | ${${dut}_if2}

| Initialize L2 xconnect with memif pairs
| | [Documentation]
| | ... | Create pairs of Memif interfaces on all defined VPP nodes. Cross
| | ... | connect each Memif interface with one physical interface or virtual
| | ... | interface to create a chain accross DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of memif pairs (containers). Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize L2 xconnect with memif pairs \| ${1} \|
| | ...
| | [Arguments] | ${count}=${1}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize L2 xconnect with memif pairs on DUT node | ${dut} | ${count}
| | Set interfaces in path up
| | Show Memif on all DUTs | ${nodes}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=memif

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
| | ${bd_id2}= | Evaluate | ${nf_nodes}+1
| | Add interface to bridge domain | ${nodes['${dut}']} | ${${dut}_if1} | ${1}
| | Add interface to bridge domain | ${nodes['${dut}']} | ${${dut}_if2}
| | ... | ${bd_id2}
| | :FOR | ${nf_node} | IN RANGE | 1 | ${nf_nodes}+1
| | | ${nf_id}= | Evaluate | (${nf_chain} - ${1}) * ${nf_nodes} + ${nf_node}
| | | ${sock1}= | Set Variable | memif-${dut}_CNF
| | | ${sock2}= | Set Variable | memif-${dut}_CNF
| | | Set up memif interfaces on DUT node | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${nf_id} | ${dut}-memif-${nf_id}-if1
| | | ... | ${dut}-memif-${nf_id}-if2 | ${rxq} | ${rxq}
| | | ${bd_id2}= | Evaluate | ${nf_node}+1
| | | Add interface to bridge domain | ${nodes['${dut}']}
| | | ... | ${${dut}-memif-${nf_id}-if1} | ${nf_node}
| | | Add interface to bridge domain | ${nodes['${dut}']}
| | | ... | ${${dut}-memif-${nf_id}-if2} | ${bd_id2}

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
| | ${duts}= | Get Matches | ${nodes} | DUT*
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
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add interface to bridge domain | ${nodes['${dut}']} | ${${dut}_if1} | ${1}
| | | Add interface to bridge domain | ${nodes['${dut}']} | ${${dut}_if2} | ${2}
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
| | | Add interface to bridge domain | ${nodes['${dut}']}
| | | ... | ${${dut}-memif-${nf_id_frst}-if1} | ${1}
| | | Add interface to bridge domain | ${nodes['${dut}']}
| | | ... | ${${dut}-memif-${nf_id_last}-if2} | ${2}

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

| Initialize IPv4 routing with memif pairs on DUT node
| | [Documentation]
| | ... | Create pairs of Memif interfaces on DUT node. Put each Memif interface
| | ... | to separate IPv4 VRF with one physical or virtual interface
| | ... | to create a chain accross DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: dictionary
| | ... | - count - Number of memif pairs (containers). Type: integer
| | ...
| | ... | *Note:*
| | ... | Socket paths for Memif are defined in following format:
| | ... | - /tmp/memif-\${dut}_CNF\${number}-\${sid}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv4 routing with memif pairs on DUT node \
| | ... | \| ${dut} \| ${1} \|
| | ...
| | [Arguments] | ${dut} | ${count}
| | ...
| | ${dut_index}= | Get Index From List | ${duts} | ${dut}
| | ${last_dut_index}= | Evaluate | ${duts_count} - ${1}
| | ...
| | ${tg_if1_net}= | Set Variable | 10.10.10.0
| | ${tg_if2_net}= | Set Variable | 20.20.20.0
| | ...
| | ${fib_table_1}= | Set Variable | ${10}
| | Run Keyword If | ${fib_table_1} > ${0}
| | ... | Add Fib Table | ${nodes['${dut}']} | ${fib_table_1}
| | ${ip_base_if1}= | Evaluate | ${dut_index} + ${1}
| | ${ip_net_if1}= | Set Variable
| | ... | ${ip_base_if1}.${ip_base_if1}.${ip_base_if1}
| | Vpp Route Add | ${nodes['${dut}']} | ${tg_if1_net} | 24
| | ... | vrf=${fib_table_1} | gateway=${ip_net_if1}.1
| | ... | interface=${${dut}_if1} | multipath=${TRUE}
| | Assign Interface To Fib Table | ${nodes['${dut}']} | ${${dut}_if1}
| | ... | ${fib_table_1}
| | Configure IP addresses on interfaces | ${nodes['${dut}']} | ${${dut}_if1}
| | ... | ${ip_net_if1}.2 | 30
| | ${prev_node}= | Run Keyword If | ${dut_index} == ${0}
| | ... | Set Variable | TG
| | ... | ELSE | Get From List | ${duts} | ${dut_index-${1}}
| | ${prev_if}= | Run Keyword If | ${dut_index} == ${0}
| | ... | Set Variable | if1
| | ... | ELSE | Set Variable | if2
| | ${prev_if_mac}= | Get Interface MAC | ${nodes['${prev_node}']}
| | ... | ${${prev_node}_${prev_if}}
| | VPP Add IP Neighbor
| | ... | ${nodes['${dut}']} | ${${dut}_if1} | ${ip_net_if1}.1 | ${prev_if_mac}
| | ...
| | ${fib_table_2}= | Evaluate | ${fib_table_1} + ${count}
| | Add Fib Table | ${nodes['${dut}']} | ${fib_table_2}
| | ${ip_base_if2}= | Evaluate | ${ip_base_if1} + ${1}
| | ${ip_net_if2}= | Set Variable
| | ... | ${ip_base_if2}.${ip_base_if2}.${ip_base_if2}
| | Vpp Route Add | ${nodes['${dut}']} | ${tg_if2_net} | 24
| | ... | vrf=${fib_table_2} | gateway=${ip_net_if2}.2
| | ... | interface=${${dut}_if2} | multipath=${TRUE}
| | Assign Interface To Fib Table | ${nodes['${dut}']} | ${${dut}_if2}
| | ... | ${fib_table_2}
| | Configure IP addresses on interfaces | ${nodes['${dut}']} | ${${dut}_if2}
| | ... | ${ip_net_if2}.1 | 30
| | ${next_node}= | Run Keyword If | ${dut_index} == ${last_dut_index}
| | ... | Set Variable | TG
| | ... | ELSE | Get From List | ${duts} | ${dut_index+${1}}
| | ${next_if}= | Run Keyword If | ${dut_index} == ${last_dut_index}
| | ... | Set Variable | if2
| | ... | ELSE | Set Variable | if1
| | ${next_if_mac}= | Get Interface MAC | ${nodes['${next_node}']}
| | ... | ${${next_node}_${next_if}}
| | VPP Add IP Neighbor
| | ... | ${nodes['${dut}']} | ${${dut}_if2} | ${ip_net_if2}.2 | ${next_if_mac}
| | ...
| | ${fib_table_1}= | Evaluate | ${fib_table_1} - ${1}
| | ${ip_base_start}= | Set Variable | ${31}
| | :FOR | ${number} | IN RANGE | 1 | ${count+${1}}
| | | ${sock1}= | Set Variable | memif-${dut}_CNF
| | | ${sock2}= | Set Variable | memif-${dut}_CNF
| | | Set up memif interfaces on DUT node | ${nodes['${dut}']}
| | | ... | ${sock1} | ${sock2} | ${number} | ${dut}-memif-${number}-if1
| | | ... | ${dut}-memif-${number}-if2 | ${rxq_count_int} | ${rxq_count_int}
| | | ${memif1}= | Set Variable | ${${dut}-memif-${number}-if1}
| | | ${memif2}= | Set Variable | ${${dut}-memif-${number}-if2}
| | | ${fib_table_1}= | Evaluate | ${fib_table_1} + ${1}
| | | ${fib_table_2}= | Evaluate | ${fib_table_1} + ${1}
| | | Run Keyword Unless | ${number} == ${count}
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
| | | Configure IP addresses on interfaces
| | | ... | ${nodes['${dut}']} | ${memif1} | ${ip_net_memif1}.1 | 30
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

| Initialize IPv4 routing with memif pairs
| | [Documentation]
| | ... | Create pairs of Memif interfaces on all defined VPP nodes. Put each
| | ... | Memif interface to separate IPv4 VRF with one physical or
| | ... | virtual interface to create a chain accross DUT node.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of memif pairs (containers). Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize IPv4 routing with memif pairs \| ${1} \|
| | ...
| | [Arguments] | ${count}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize IPv4 routing with memif pairs on DUT node | ${dut} | ${count}
| | Set interfaces in path up
| | Show Memif on all DUTs | ${nodes}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=memif

| Initialize L2 xconnect for single memif
| | [Documentation]
| | ... | Create single Memif interface on all defined VPP nodes. Cross
| | ... | connect Memif interface with one physical interface.
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
| | ... | \| Initialize L2 xconnect for single memif \| 1 \|
| | ...
| | [Arguments] | ${number}=${1}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${sock}= | Set Variable | memif-${dut}_CNF
| | | ${sid}= | Evaluate | (${number} * ${2}) - ${1}
| | | Set up single memif interface on DUT node | ${nodes['${dut}']} | ${sock}
| | | ... | mid=${number} | sid=${sid} | memif_if=${dut}-memif-${number}-if1
| | | ... | rxq=${rxq_count_int} | txq=${rxq_count_int}
| | | Configure L2XC | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ${${dut}-memif-${number}-if1}
| | Set single interfaces in path up
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
| | ${duts}= | Get Matches | ${nodes} | DUT*
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

| Configure ACLs on a single interface
| | [Documentation]
| | ... | Configure ACL
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - dut_if - DUT node interface name. Type: string
| | ... | - acl_apply_type - To what path apply the ACL - input or output.
| | ... | - acl_action - Action for the rule - deny, permit, permit+reflect.
| | ... | - subnets - Subnets to apply the specific ACL. Type: list
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure ACLs on a single interface \| ${nodes['DUT1']}
| | ... | \| ... \| GigabitEthernet0/7/0 \| input \| permit | 0.0.0.0/0
| | ...
| | [Arguments] | ${dut} | ${dut_if} | ${acl_apply_type} | ${acl_action}
| | ... | @{subnets}
| | Set Test variable | ${acl} | ${EMPTY}
| | :FOR | ${subnet} | IN | @{subnets}
| | | ${acl} = | Run Keyword If | '${acl}' == '${EMPTY}'
| | | ... | Set Variable | ipv4 ${acl_action} src ${subnet}
| | | ... | ELSE
| | | ... | Catenate | SEPARATOR=, | ${acl}
| | | ... | ipv4 ${acl_action} src ${subnet}
| | Add Replace Acl Multi Entries | ${dut} | rules=${acl}
| | @{acl_list} = | Create List | ${0}
| | Set Acl List For Interface | ${dut} | ${dut_if} | ${acl_apply_type}
| | ... | ${acl_list}
