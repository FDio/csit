# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.KubernetesUtils
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/container.robot
| Resource | resources/libraries/robot/shared/memif.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/l2/l2_xconnect.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/vm/qemu.robot
| Resource | resources/libraries/robot/l2/tagging.robot
| Documentation | Performance suite keywords - utilities to find and verify NDR
| ... | and PDR.

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
| | Return From Keyword If | '${framesize}' == 'IMIX_v4_1' | ${353.83333}
| | Return From Keyword | ${framesize}

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
| | ... | (Throughput * (L2 Frame Size + IPG) * 8) / Max bitrate of NIC
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
| | ... | (Throughput * (L2 Frame Size + IPG) * 8) / Max bitrate of NIC
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

| Display raw results
| | [Documentation]
| | ... | Display raw results from TG in total received/send packets over trial
| | ... | duration in seconds.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - results - Measured results. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Display raw results \| 64 \| results \|
| | ...
| | [Arguments] | ${framesize} | ${results}
| | ...
| | ${framesize}= | Get Frame Size | ${framesize}
| | @{tokens}= | Split String | ${results} | ,
| | @{received}= | Split String | @{tokens}[1] | =
| | @{sent}= | Split String | @{tokens}[2] | =
| | ${total_received} = | Set Variable | @{received}[1]
| | ${total_sent} = | Set Variable | @{sent}[1]
| | Set Test Message | MaxReceivedRate_Results [pkts/${perf_trial_duration}sec]:
| | Set Test Message | tx ${total_sent}, rx ${total_received} | append=yes

| Measure latency pps
| | [Documentation]
| | ... | Send traffic at specified rate. Measure min/avg/max latency
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: integer
| | ... | - framesize - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
| | ... | - topology_type - Topology type. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Measure latency \| 10 \| 4.0 \| 64 \| 3-node-IPv4 \|
| | ...
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ...
| | Return From Keyword If | ${rate} <= 10000 | ${-1}
| | Send traffic on tg | ${duration} | ${rate}pps | ${framesize}
| | ... | ${topology_type} | warmup_time=0
| | Run keyword and return | Get latency

| Traffic should pass with no loss
| | [Documentation]
| | ... | Send traffic at specified rate. No packet loss is accepted at loss
| | ... | evaluation.
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
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
| | Send traffic at specified rate | ${duration} | ${rate} | ${framesize}
| | ... | ${topology_type}
| | Run Keyword If | ${fail_on_loss} | No traffic loss occurred

| Traffic should pass with partial loss
| | [Documentation]
| | ... | Send traffic at specified rate. Partial packet loss is accepted
| | ... | within loss acceptance value specified as argument.
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
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
| | Send traffic at specified rate | ${duration} | ${rate} | ${framesize}
| | ... | ${topology_type}
| | Run Keyword If | ${fail_on_loss} | Partial traffic loss accepted
| | ... | ${loss_acceptance} | ${loss_acceptance_type}

| Traffic should pass with maximum rate
| | [Documentation]
| | ... | Send traffic at maximum rate.
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
| | ... | - topology_type - Topology type. Type: string
| | ... | Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Traffic should pass with no loss \| 10 \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \|
| | ...
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ...
| | ${results}= | Send traffic at specified rate | ${duration} | ${rate}
| | ... | ${framesize} | ${topology_type}
| | Display raw results | ${framesize} | ${results}

| Send traffic at specified rate
| | [Documentation]
| | ... | Send traffic at specified rate.
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer/string
| | ... | - topology_type - Topology type. Type: string
| | ... | Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send traffic at specific rate \| 10 \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \|
| | ...
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ...
| | Clear and show runtime counters with running traffic | ${duration}
| | ... | ${rate} | ${framesize} | ${topology_type}
| | Run Keyword If | ${dut_stats}==${True} | Clear all counters on all DUTs
| | Run Keyword If | ${dut_stats}==${True} and ${pkt_trace}==${True}
| | ... | VPP Enable Traces On All DUTs | ${nodes}
| | ${results} = | Send traffic on tg | ${duration} | ${rate} | ${framesize}
| | ... | ${topology_type} | warmup_time=0
| | Run Keyword If | ${dut_stats}==${True} | Show statistics on all DUTs | ${nodes}
| | Run Keyword If | ${dut_stats}==${True} and ${pkt_trace}==${True}
| | ... | Show Packet Trace On All Duts | ${nodes} | maximum=${100}
| | Return From Keyword | ${results}

| Clear and show runtime counters with running traffic
| | [Documentation]
| | ... | Start traffic at specified rate then clear runtime counters on all
| | ... | DUTs. Wait for specified amount of time and capture runtime counters
| | ... | on all DUTs. Finally stop traffic
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
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
| | Run Keyword If | ${dut_stats}==${True}
| | ... | Clear runtime counters on all DUTs | ${nodes}
| | Sleep | ${duration}
| | Run Keyword If | ${dut_stats}==${True}
| | ... | Show runtime counters on all DUTs | ${nodes}
| | Stop traffic on tg
