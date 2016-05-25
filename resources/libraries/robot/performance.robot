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
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
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
| | ... | - ${10Ge_linerate_pps_72B} - Maximum number of packet per second
| | ... |                              for 10GE with 72B L2 Frame.
| | ... | - ${10Ge_linerate_pps_78B} - Maximum number of packet per second
| | ... |                              for 10GE with 78B L2 Frame.
| | ... | - ${10Ge_linerate_pps_1518B} - Maximum number of packet per second
| | ... |                                for 10GE with 1518B L2 Frame.
| | ... | - ${10Ge_linerate_pps_1522B} - Maximum number of packet per second
| | ... |                                for 10GE with 1522B L2 Frame.
| | ... | - ${10Ge_linerate_pps_1526B} - Maximum number of packet per second
| | ... |                                for 10GE with 1526B L2 Frame.
| | ... | - ${10Ge_linerate_pps_9000B} - Maximum number of packet per second
| | ... |                                for 10GE with 9000B L2 Frame.
| | ... | - ${10Ge_linerate_pps_9004B} - Maximum number of packet per second
| | ... |                                for 10GE with 9004B L2 Frame.
| | ... | - ${10Ge_linerate_pps_9008B} - Maximum number of packet per second
| | ... |                                for 10GE with 9008B L2 Frame.
| | ...
| | Set Suite Variable | ${10Ge_linerate_pps_64B} | 14880952
| | Set Suite Variable | ${10Ge_linerate_pps_68B} | 14204545
| | Set Suite Variable | ${10Ge_linerate_pps_72B} | 12755102
| | Set Suite Variable | ${10Ge_linerate_pps_78B} | 12755102
| | Set Suite Variable | ${10Ge_linerate_pps_1518B} | 812743
| | Set Suite Variable | ${10Ge_linerate_pps_1522B} | 810635
| | Set Suite Variable | ${10Ge_linerate_pps_1526B} | 808538
| | Set Suite Variable | ${10Ge_linerate_pps_9000B} | 138580
| | Set Suite Variable | ${10Ge_linerate_pps_9004B} | 138519
| | Set Suite Variable | ${10Ge_linerate_pps_9008B} | 138458

| Setup performance global Variables
| | [Documentation] | Setup performance global Variables
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - ${glob_loss_acceptance} - Loss acceptance treshold
| | ... | - ${glob_loss_acceptance_type} - Loss acceptance treshold type
| | ...
| | Set Suite Variable | ${glob_loss_acceptance} | 0.5
| | Set Suite Variable | ${glob_loss_acceptance_type} | percentage

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

| VPP interfaces in path are up
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
| | Set Test Message | (${nr_streams}x ${rate_per_stream} pps)
| | ...              | append=yes
| | Set Test Message | ${\n}FINAL_BANDWIDTH: ${bandwidth_total} Gbps (untagged)
| | ...              | append=yes

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
| | Set Test Message | (${nr_streams}x ${rate_per_stream} pps)
| | ...              | append=yes
| | Set Test Message | ${\n}FINAL_BANDWIDTH: ${bandwidth_total} Gbps (untagged)
| | ...              | append=yes
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
