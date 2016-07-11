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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/qemu.robot
| Documentation | Performance suite keywords

*** Keywords ***
| Setup performance rate Variables
| | [Documentation] | Setup performance rates as Suite Variables
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - ${10Ge_linerate_pps_64B} - Maximum number of packet per second
| | ... |                              for 10GE with 64B L2 Frame.
| | ... | - ${10Ge_linerate_pps_68B} - Maximum number of packet per second
| | ... |                              for 10GE with 68B L2 Frame.
| | ... | - ${10Ge_linerate_pps_78B} - Maximum number of packet per second
| | ... |                              for 10GE with 78B L2 Frame.
| | ... | - ${10Ge_linerate_pps_1518B} - Maximum number of packet per second
| | ... |                                for 10GE with 1518B L2 Frame.
| | ... | - ${10Ge_linerate_pps_1522B} - Maximum number of packet per second
| | ... |                                for 10GE with 1522B L2 Frame.
| | ... | - ${10Ge_linerate_pps_9000B} - Maximum number of packet per second
| | ... |                                for 10GE with 9000B L2 Frame.
| | ... | - ${10Ge_linerate_pps_9004B} - Maximum number of packet per second
| | ... |                                for 10GE with 9004B L2 Frame.
| | ...
| | ${10Ge_linerate_pps_64B}= | Set Variable | 14880952
| | ${10Ge_linerate_pps_68B}= | Set Variable | 14204545
| | ${10Ge_linerate_pps_78B}= | Set Variable | 12755102
| | ${10Ge_linerate_pps_1518B}= | Set Variable | 812743
| | ${10Ge_linerate_pps_1522B}= | Set Variable | 810635
| | ${10Ge_linerate_pps_9000B}= | Set Variable | 138580
| | ${10Ge_linerate_pps_9004B}= | Set Variable | 138519
| | Set Suite Variable | ${10Ge_linerate_pps_64B}
| | Set Suite Variable | ${10Ge_linerate_pps_68B}
| | Set Suite Variable | ${10Ge_linerate_pps_78B}
| | Set Suite Variable | ${10Ge_linerate_pps_1518B}
| | Set Suite Variable | ${10Ge_linerate_pps_1522B}
| | Set Suite Variable | ${10Ge_linerate_pps_9000B}
| | Set Suite Variable | ${10Ge_linerate_pps_9004B}

| Setup performance global Variables
| | [Documentation] | Setup performance global Variables
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - ${glob_loss_acceptance} - Loss acceptance treshold
| | ... | - ${glob_loss_acceptance_type} - Loss acceptance treshold type
| | ...
| | ${glob_loss_acceptance}= | Set Variable | 0.5
| | ${glob_loss_acceptance_type}= | Set Variable | percentage
| | Set Suite Variable | ${glob_loss_acceptance}
| | Set Suite Variable | ${glob_loss_acceptance_type}

| 2-node circular Topology Variables Setup
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}

| 3-node circular Topology Variables Setup
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...          | ${nodes['TG']}
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
| | [Documentation] | Find a path between TG-DUT1-TG based on interface
| | ...             | model provided as an argument. Set suite variables
| | ...             | tg, tg_if1, tg_if2, dut1, dut1_if1, dut1_if2,
| | [Arguments] | ${iface_model}
| | ${iface_model_list}= | Create list | ${iface_model}
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}

| 3-node circular Topology Variables Setup with DUT interface model
| | [Documentation] | Find a path between TG-DUT1-DUT2-TG based on interface
| | ...             | model provided as an argument. Set suite variables
| | ...             | tg, tg_if1, tg_if2, dut1, dut1_if1, dut1_if2,
| | ...             | dut2, dut2_if1, dut2_if2
| | [Arguments] | ${iface_model}
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
| | [Documentation] | *Set UP state on VPP interfaces in path on nodes.*
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}

| VPP interfaces in path are up in a 3-node circular topology
| | [Documentation] | *Set UP state on VPP interfaces in path on nodes.*
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Vpp Node Interfaces Ready Wait | ${dut2}

| IPv4 forwarding initialized in a 3-node circular topology
| | [Documentation] | Custom setup of IPv4 addresses on all DUT nodes and TG
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

| IPv6 forwarding initialized in a 3-node circular topology
| | [Documentation] | Custom setup of IPv6 topology on all DUT nodes
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
| | Vpp set IPv6 neighbor | ${dut1} | ${dut1_if1} | 2001:1::2
| | ...                    | ${tg1_if1_mac}
| | Vpp set IPv6 neighbor | ${dut2} | ${dut2_if2} | 2001:2::2
| | ...                    | ${tg1_if2_mac}
| | Vpp set IPv6 neighbor | ${dut1} | ${dut1_if2} | 2001:3::2
| | ...                    | ${dut2_if1_mac}
| | Vpp set IPv6 neighbor | ${dut2} | ${dut2_if1} | 2001:3::1
| | ...                    | ${dut1_if2_mac}
| | Vpp Route Add | ${dut1} | 2001:2::0 | ${prefix} | 2001:3::2 | ${dut1_if2}
| | Vpp Route Add | ${dut2} | 2001:1::0 | ${prefix} | 2001:3::1 | ${dut2_if1}

| L2 xconnect initialized in a 3-node circular topology
| | [Documentation] | Custom setup of L2 xconnect topology
| | L2 setup xconnect on DUT | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | L2 setup xconnect on DUT | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| L2 bridge domain initialized in a 3-node circular topology
| | [Documentation] | Custom setup of L2 bridge topology
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
| | ... |    circular topology \| 1 \| 2 \| /tmp/sock1 \| /tmp/sock2
| | [Arguments] | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut1}
| | ...                                                | ${sock1}
| | ...                                                | ${sock2}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut1} | ${dut1_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut1} | ${vhost_if2} | ${bd_id2}
| | VPP Vhost interfaces for L2BD forwarding are setup | ${dut2}
| | ...                                                | ${sock1}
| | ...                                                | ${sock2}
| | Interface is added to bridge domain | ${dut2} | ${dut2_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut2} | ${vhost_if1} | ${bd_id1}
| | Interface is added to bridge domain | ${dut2} | ${dut2_if2} | ${bd_id2}
| | Interface is added to bridge domain | ${dut2} | ${vhost_if2} | ${bd_id2}
| | All Vpp Interfaces Ready Wait | ${nodes}

| 2-node Performance Suite Setup
| | [Arguments] | ${topology_type}
| | Setup default startup configuration of VPP on all DUTs
| | Update All Interface Data On All Nodes | ${nodes}
| | Show vpp version on all DUTs
| | Setup performance rate Variables
| | Setup performance global Variables
| | 2-node circular Topology Variables Setup
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ...                          | ${dut1} | ${dut1_if1}
| | ...                          | ${dut1} | ${dut1_if2}
| | ...                          | ${topology_type}

| 3-node Performance Suite Setup
| | [Arguments] | ${topology_type}
| | Setup default startup configuration of VPP on all DUTs
| | Update All Interface Data On All Nodes | ${nodes}
| | Show vpp version on all DUTs
| | Setup performance rate Variables
| | Setup performance global Variables
| | 3-node circular Topology Variables Setup
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ...                          | ${dut1} | ${dut1_if1}
| | ...                          | ${dut2} | ${dut2_if2}
| | ...                          | ${topology_type}

2-node Performance Suite Setup with DUT's NIC model
| | [Arguments] | ${topology_type} | ${nic_model}
| | Setup default startup configuration of VPP on all DUTs
| | Update All Interface Data On All Nodes | ${nodes}
| | Show vpp version on all DUTs
| | Setup performance rate Variables
| | Setup performance global Variables
| | 2-node circular Topology Variables Setup with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ...                          | ${dut1} | ${dut1_if1}
| | ...                          | ${dut1} | ${dut1_if2}
| | ...                          | ${topology_type}

3-node Performance Suite Setup with DUT's NIC model
| | [Arguments] | ${topology_type} | ${nic_model}
| | Setup default startup configuration of VPP on all DUTs
| | Update All Interface Data On All Nodes | ${nodes}
| | Show vpp version on all DUTs
| | Setup performance rate Variables
| | Setup performance global Variables
| | 3-node circular Topology Variables Setup with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ...                          | ${dut1} | ${dut1_if1}
| | ...                          | ${dut2} | ${dut2_if2}
| | ...                          | ${topology_type}

| 3-node Performance Suite Teardown
| | Teardown traffic generator | ${tg}

| Find NDR using linear search and pps
| | [Documentation] | Find throughput by using RFC2544 linear search with
| | ...             | non drop rate
| | ...
| | ... | *Arguments:*
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${start_rate} - Initial start rate [pps]. Type: float
| | ... | - ${step_rate} - Step of linear search [pps]. Type: float
| | ... | - ${topology_type} - Topology type. Type: string
| | ... | - ${min_rate} - Lower limit of search [pps]. Type: float
| | ... | - ${max_rate} - Upper limit of search [pps]. Type: float
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find NDR using linear search and pps \| 64 \| 5000000 \| \
| | ... | \| 100000 \| 3-node-IPv4 \| 100000 \| 14880952
| | [Arguments] | ${framesize} | ${start_rate} | ${step_rate}
| | ...         | ${topology_type} | ${min_rate} | ${max_rate}
| | ${duration}= | Set Variable | 10
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Linear Step | ${step_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Linear Search | ${start_rate} | ${topology_type}
| | ${rate_per_stream}= | Verify Search Result
| | Display result of NDR search | ${rate_per_stream} | ${framesize} | 2
| | Traffic should pass with no loss | ${duration} | ${rate_per_stream}pps
| | ...                              | ${framesize} | ${topology_type}
| | ...                              | fail_on_loss=${False}

| Find PDR using linear search and pps
| | [Documentation] | Find throughput by using RFC2544 linear search with
| | ...             | partial drop rate, with PDR threshold 0.5%.
| | ...
| | ... | *Arguments:*
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${start_rate} - Initial start rate [pps]. Type: float
| | ... | - ${step_rate} - Step of linear search [pps]. Type: float
| | ... | - ${topology_type} - Topology type. Type: string
| | ... | - ${min_rate} - Lower limit of search [pps]. Type: float
| | ... | - ${max_rate} - Upper limit of search [pps]. Type: float
| | ... | - ${loss_acceptance} - Accepted loss during search. Type: float
| | ... | - ${loss_acceptance_type} - Percentage or frames. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find PDR using linear search and pps \| 64 \| 5000000 \
| | ... | \| 100000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 0.5 \| percentage
| | [Arguments] | ${framesize} | ${start_rate} | ${step_rate}
| | ...         | ${topology_type} | ${min_rate} | ${max_rate}
| | ...         | ${loss_acceptance}=0 | ${loss_acceptance_type}='frames'
| | ${duration}= | Set Variable | 10
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Linear Step | ${step_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Loss Acceptance | ${loss_acceptance}
| | Run Keyword If | '${loss_acceptance_type}' == 'percentage'
| | ...            | Set Loss Acceptance Type Percentage
| | Linear Search | ${start_rate} | ${topology_type}
| | ${rate_per_stream}= | Verify Search Result
| | Display result of PDR search | ${rate_per_stream} | ${framesize} | 2
| | ...                          | ${loss_acceptance} | ${loss_acceptance_type}
| | Traffic should pass with partial loss | ${duration} | ${rate_per_stream}pps
| | ...                                   | ${framesize} | ${topology_type}
| | ...                                   | ${loss_acceptance}
| | ...                                   | ${loss_acceptance_type}
| | ...                                   | fail_on_loss=${False}

| Find NDR using binary search and pps
| | [Documentation] | Find throughput by using RFC2544 binary search with
| | ...             | non drop rate
| | ...
| | ... | *Arguments:*
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${binary_min} - Lower boundary of search [pps]. Type: float
| | ... | - ${binary_max} - Upper boundary of search [pps]. Type: float
| | ... | - ${topology_type} - Topology type. Type: string
| | ... | - ${min_rate} - Lower limit of search [pps]. Type: float
| | ... | - ${max_rate} - Upper limit of search [pps]. Type: float
| | ... | - ${threshold} - Threshold to stop search [pps]. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find NDR using binary search and pps \| 64 \| 6000000 \
| | ... | \| 12000000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 50000
| | [Arguments] | ${framesize} | ${binary_min} | ${binary_max}
| | ...         | ${topology_type} | ${min_rate} | ${max_rate} | ${threshold}
| | ${duration}= | Set Variable | 10
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Binary Convergence Threshold | ${threshold}
| | Binary Search | ${binary_min} | ${binary_max} | ${topology_type}
| | ${rate_per_stream}= | Verify Search Result
| | Display result of NDR search | ${rate_per_stream} | ${framesize} | 2
| | Traffic should pass with no loss | ${duration} | ${rate_per_stream}pps
| | ...                              | ${framesize} | ${topology_type}
| | ...                              | fail_on_loss=${False}

| Find PDR using binary search and pps
| | [Documentation] | Find throughput by using RFC2544 binary search with
| | ...             | partial drop rate, with PDR threshold 0.5%.
| | ...
| | ... | *Arguments:*
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${binary_min} - Lower boundary of search [pps]. Type: float
| | ... | - ${binary_max} - Upper boundary of search [pps]. Type: float
| | ... | - ${topology_type} - Topology type. Type: string
| | ... | - ${min_rate} - Lower limit of search [pps]. Type: float
| | ... | - ${max_rate} - Upper limit of search [pps]. Type: float
| | ... | - ${threshold} - Threshold to stop search [pps]. Type: integer
| | ... | - ${loss_acceptance} - Accepted loss during search. Type: float
| | ... | - ${loss_acceptance_type} - Percentage or frames. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find PDR using binary search and pps \| 64 \| 6000000 \
| | ... | \| 12000000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 50000 \| 0.5 \
| | ... | \| percentage
| | [Arguments] | ${framesize} | ${binary_min} | ${binary_max}
| | ...         | ${topology_type} | ${min_rate} | ${max_rate} | ${threshold}
| | ...         | ${loss_acceptance}=0 | ${loss_acceptance_type}='frames'
| | ${duration}= | Set Variable | 10
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Loss Acceptance | ${loss_acceptance}
| | Run Keyword If | '${loss_acceptance_type}' == 'percentage'
| | ...            | Set Loss Acceptance Type Percentage
| | Set Binary Convergence Threshold | ${threshold}
| | Binary Search | ${binary_min} | ${binary_max} | ${topology_type}
| | ${rate_per_stream}= | Verify Search Result
| | Display result of PDR search | ${rate_per_stream} | ${framesize} | 2
| | ...                          | ${loss_acceptance} | ${loss_acceptance_type}
| | Traffic should pass with partial loss | ${duration} | ${rate_per_stream}pps
| | ...                                   | ${framesize} | ${topology_type}
| | ...                                   | ${loss_acceptance}
| | ...                                   | ${loss_acceptance_type}
| | ...                                   | fail_on_loss=${False}

| Find NDR using combined search and pps
| | [Documentation] | Find throughput by using RFC2544 combined search
| | ...             | (linear + binary) with non drop rate
| | ...
| | ... | *Arguments:*
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${start_rate} - Initial start rate [pps]. Type: float
| | ... | - ${step_rate} - Step of linear search [pps]. Type: float
| | ... | - ${topology_type} - Topology type. Type: string
| | ... | - ${min_rate} - Lower limit of search [pps]. Type: float
| | ... | - ${max_rate} - Upper limit of search [pps]. Type: float
| | ... | - ${threshold} - Threshold to stop search [pps]. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find NDR using combined search and pps \| 64 \| 5000000 \
| | ... | \| 100000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 5000
| | [Arguments] | ${framesize} | ${start_rate} | ${step_rate}
| | ...         | ${topology_type} | ${min_rate} | ${max_rate} | ${threshold}
| | ${duration}= | Set Variable | 10
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Linear Step | ${step_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Binary Convergence Threshold | ${threshold}
| | Combined Search | ${start_rate} | ${topology_type}
| | ${rate_per_stream}= | Verify Search Result
| | Display result of NDR search | ${rate_per_stream} | ${framesize} | 2
| | Traffic should pass with no loss | ${duration} | ${rate_per_stream}pps
| | ...                              | ${framesize} | ${topology_type}
| | ...                              | fail_on_loss=${False}

| Find PDR using combined search and pps
| | [Documentation] | Find throughput by using RFC2544 combined search
| | ...             | (linear + binary) with partial drop rate, with PDR
| | ...             | threshold 0.5%.
| | ...
| | ... | *Arguments:*
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${start_rate} - Initial start rate [pps]. Type: float
| | ... | - ${step_rate} - Step of linear search [pps]. Type: float
| | ... | - ${topology_type} - Topology type. Type: string
| | ... | - ${min_rate} - Lower limit of search [pps]. Type: float
| | ... | - ${max_rate} - Upper limit of search [pps]. Type: float
| | ... | - ${threshold} - Threshold to stop search [pps]. Type: integer
| | ... | - ${loss_acceptance} - Accepted loss during search. Type: float
| | ... | - ${loss_acceptance_type} - Percentage or frames. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find PDR using combined search and pps \| 64 \| 5000000 \
| | ... | \| 100000 \| 3-node-IPv4 \| 100000 \| 14880952 \| 5000 \| 0.5 \
| | ... | \| percentage
| | [Arguments] | ${framesize} | ${start_rate} | ${step_rate}
| | ...         | ${topology_type} | ${min_rate} | ${max_rate} | ${threshold}
| | ...         | ${loss_acceptance}=0 | ${loss_acceptance_type}='frames'
| | ${duration}= | Set Variable | 10
| | Set Duration | ${duration}
| | Set Search Rate Boundaries | ${max_rate} | ${min_rate}
| | Set Search Linear Step | ${step_rate}
| | Set Search Frame Size | ${framesize}
| | Set Search Rate Type pps
| | Set Loss Acceptance | ${loss_acceptance}
| | Run Keyword If | '${loss_acceptance_type}' == 'percentage'
| | ...            | Set Loss Acceptance Type Percentage
| | Set Binary Convergence Threshold | ${threshold}
| | Combined Search | ${start_rate} | ${topology_type}
| | ${rate_per_stream}= | Verify Search Result
| | Display result of PDR search | ${rate_per_stream} | ${framesize} | 2
| | ...                          | ${loss_acceptance} | ${loss_acceptance_type}
| | Traffic should pass with partial loss | ${duration} | ${rate_per_stream}pps
| | ...                                   | ${framesize} | ${topology_type}
| | ...                                   | ${loss_acceptance}
| | ...                                   | ${loss_acceptance_type}
| | ...                                   | fail_on_loss=${False}

| Display result of NDR search
| | [Documentation] | Display result of NDR search in packet per seconds (total
| | ...             | and per stream) and Gbps.
| | ...
| | ... | *Arguments:*
| | ... | - ${rate_per_stream} - Measured rate per stream [pps]. Type: string
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${nr_streams} - Total number of streams. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Display result of NDR search \| 4400000 \| 64 \| 2
| | [Arguments] | ${rate_per_stream} | ${framesize} | ${nr_streams}
| | ${rate_total}= | Evaluate | ${rate_per_stream}*${nr_streams}
| | ${bandwidth_total}= | Evaluate | ${rate_total}*(${framesize}+20)*8/(10**9)
| | Set Test Message | FINAL_RATE: ${rate_total} pps
| | Set Test Message | (${nr_streams}x ${rate_per_stream} pps) | append=yes
| | Set Test Message | FINAL_BANDWIDTH: ${bandwidth_total} Gbps | append=yes

| Display result of PDR search
| | [Documentation] | Display result of PDR search in packet per seconds (total
| | ...             | and per stream) and Gbps.
| | ...
| | ... | *Arguments:*
| | ... | - ${rate_per_stream} - Measured rate per stream [pps]. Type: string
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${nr_streams} - Total number of streams. Type: integer
| | ... | - ${loss_acceptance} - Accepted loss during search. Type: float
| | ... | - ${loss_acceptance_type} - Percentage or frames. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Display result of PDR search \| 4400000 \| 64 \| 2 \| 0.5 \
| | ... | \| percentage
| | [Arguments] | ${rate_per_stream} | ${framesize} | ${nr_streams}
| | ...         | ${loss_acceptance} | ${loss_acceptance_type}
| | ${rate_total}= | Evaluate | ${rate_per_stream}*${nr_streams}
| | ${bandwidth_total}= | Evaluate | ${rate_total}*(${framesize}+20)*8/(10**9)
| | Set Test Message | FINAL_RATE: ${rate_total} pps
| | Set Test Message | (${nr_streams}x ${rate_per_stream} pps) | append=yes
| | Set Test Message | FINAL_BANDWIDTH: ${bandwidth_total} Gbps | append=yes
| | Set Test Message | ${\n}LOSS_ACCEPTANCE: ${loss_acceptance} ${loss_acceptance_type}
| | ...              | append=yes

| Traffic should pass with no loss
| | [Documentation] | Send traffic at specified rate. No packet loss is
| | ...             | accepted at loss evaluation.
| | ...
| | ... | *Arguments:*
| | ... | - ${duration} - Duration of traffic run [s]. Type: integer
| | ... | - ${rate} - Rate for sending packets. Type: string
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${topology_type} - Topology type. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Traffic should pass with no loss \| 10 \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ...         | ${fail_on_loss}=${True}
| | Clear and show runtime counters with running traffic | ${duration}
| | ...  | ${rate} | ${framesize} | ${topology_type}
| | Clear all counters on all DUTs
| | Send traffic on tg | ${duration} | ${rate} | ${framesize}
| | ...                | ${topology_type} | warmup_time=0
| | Show statistics on all DUTs
| | Run Keyword If | ${fail_on_loss} | No traffic loss occurred

| Traffic should pass with partial loss
| | [Documentation] | Send traffic at specified rate. Partial packet loss is
| | ...             | accepted within loss acceptance value.
| | ...
| | ... | *Arguments:*
| | ... | - ${duration} - Duration of traffic run [s]. Type: integer
| | ... | - ${rate} - Rate for sending packets. Type: string
| | ... | - ${framesize} - L2 Frame Size [B]. Type: integer
| | ... | - ${topology_type} - Topology type. Type: string
| | ... | - ${loss_acceptance} - Accepted loss during search. Type: float
| | ... | - ${loss_acceptance_type} - Percentage or frames. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Traffic should pass with partial loss \| 10 \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \| 0.5 \| percentage
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ...         | ${loss_acceptance} | ${loss_acceptance_type}
| | ...         | ${fail_on_loss}=${True}
| | Clear and show runtime counters with running traffic | ${duration}
| | ...  | ${rate} | ${framesize} | ${topology_type}
| | Clear all counters on all DUTs
| | Send traffic on tg | ${duration} | ${rate} | ${framesize}
| | ...                | ${topology_type} | warmup_time=0
| | Show statistics on all DUTs
| | Run Keyword If | ${fail_on_loss} | Partial traffic loss accepted
| | ...            | ${loss_acceptance} | ${loss_acceptance_type}

| Clear and show runtime counters with running traffic
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | Send traffic on tg | -1 | ${rate} | ${framesize}
| | ...                | ${topology_type} | warmup_time=0 | async_call=True
| | Clear runtime counters on all DUTs
| | Sleep | ${duration}
| | Show runtime counters on all DUTs
| | Stop traffic on tg

| VM with dpdk-testpmd for Vhost L2BD forwarding is setup
| | [Documentation]
| | ... | Setup QEMU and start VM with two vhost interfaces and interconnecting
| | ... | DPDK testpmd.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node to start VM on. Type: dictionary
| | ... | - sock1 - Sock path for first Vhost-User interface. Type: string
| | ... | - sock2 - Sock path for second Vhost-User interface. Type: string
| | ... | - vm_name - QemuUtil instance name. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VM with dpdk-testpmd for Vhost L2BD forwarding is setup \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name}
| | Import Library | resources.libraries.python.QemuUtils
| | ...            | WITH NAME | ${vm_name}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock2}
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | 3 | 3 | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Affinity | 0x000000E0
| | Run keyword | ${vm_name}.Qemu Set Disk Image
| | ...         | /var/lib/vm/csit-nested-1.3.img
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | Dpdk Testpmd Start | ${vm}
| | Return From Keyword | ${vm}

| VM with Linux Bridge for Vhost L2BD forwarding is setup
| | [Documentation]
| | ... | Setup QEMU and start VM with two vhost interfaces and interconnecting
| | ... | linux bridge.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node to start VM on. Type: dictionary
| | ... | - sock1 - Sock path for first Vhost-User interface. Type: string
| | ... | - sock2 - Sock path for second Vhost-User interface. Type: string
| | ... | - vm_name - QemuUtil instance name. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VM with Linux Bridge for Vhost L2BD forwarding is setup \
| | ... | \| ${nodes['DUT1']} \| /tmp/sock1 \| /tmp/sock2 \| DUT1_VM
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${vm_name}
| | Import Library | resources.libraries.python.QemuUtils
| | ...            | WITH NAME | ${vm_name}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${vm_name}.Qemu Add Vhost User If | ${sock2}
| | Run keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | Run keyword | ${vm_name}.Qemu Set Smp | 3 | 3 | 1 | 1
| | Run keyword | ${vm_name}.Qemu Set Mem Size | 2048
| | Run keyword | ${vm_name}.Qemu Set Affinity | 0x000000E0
| | Run keyword | ${vm_name}.Qemu Set Disk Image
| | ...         | /var/lib/vm/csit-nested-1.3.img
| | ${vm}= | Run keyword | ${vm_name}.Qemu Start
| | ${br}= | Set Variable | br0
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | ${br} | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up
| | Set Interface State | ${vm} | ${vhost2} | up
| | Set Interface State | ${vm} | ${br} | up
| | Return From Keyword | ${vm}

| VM with dpdk-testpmd Teardown
| | [Documentation]
| | ... | Stop all qemu instances with dpdk-testpmd running on ${dut_node}.
| | ... | Argument is dictionary of all running qemu instances with its names.
| | ... | Dpdk-testpmd is stopped gracefully with printing stats.
| | ... |
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dictionary
| | ... | - dut_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| VM with dpdk-testpmd Teardown \| ${node['DUT1']} \
| | ... | \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${dut_node} | ${dut_vm_refs}
| | :FOR | ${vm_name} | IN | @{dut_vm_refs}
| | | ${vm}= | Get From Dictionary | ${dut_vm_refs} | ${vm_name}
| | | Dpdk Testpmd Stop | ${vm}
| | | ${set_node}= | Replace Variables | ${vm_name}.Qemu Set Node
| | | ${sys_status}= | Replace Variables | ${vm_name}.Qemu System Status
| | | ${kill}= | Replace Variables | ${vm_name}.Qemu Kill
| | | ${sys_pd}= | Replace Variables | ${vm_name}.Qemu System Powerdown
| | | ${quit}= | Replace Variables | ${vm_name}.Qemu Quit
| | | ${clear_socks}= | Replace Variables | ${vm_name}.Qemu Clear Socks
| | | Run Keyword | ${set_node} | ${dut_node}
| | | ${status} | ${value}= | Run Keyword And Ignore Error | ${sys_status}
| | | Run Keyword If | "${status}" == "FAIL" | ${kill}
| | | ... | ELSE IF | "${value}" == "running" | ${sys_pd}
| | | ... | ELSE | ${quit}
| | | Run Keyword | ${clear_socks}
| | | Run Keyword If | ${vm} is not None | Disconnect | ${vm}
