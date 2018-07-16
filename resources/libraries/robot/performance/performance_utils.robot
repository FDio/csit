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
| Library | resources.libraries.python.TrafficGenerator.OptimizedSearch
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
| Get Max Rate And Jumbo
| | [Documentation]
| | ... | Argument framesize can be either integer in case of a single packet
| | ... | in stream, or IMIX string defining mix of packets.
| | ... | For jumbo frames detection, the maximal packet size is relevant.
| | ... | For maximal transmit rate, the average packet size is relevant.
| | ... | In both cases, encapsulation overhead (if any) has effect.
| | ... | The maximal rate is computed from line limit bandwidth,
| | ... | but NICs also have an independent limit in packet rate.
| | ... | For some NICs, the limit is not reachable (bps limit is stricter),
| | ... | in those cases None is used (meaning no limiting).
| | ...
| | ... | This keyword returns computed maximal unidirectional transmit rate
| | ... | and jumbo boolean (some suites need that).
| | ...
| | ... | *Arguments:*
| | ... | - bps_limit - Line rate limit in bps. Type: integer
| | ... | - framesize - Framesize in bytes or IMIX. Type: integer or string
| | ... | - overhead - Overhead in bytes. Default: 0. Type: integer
| | ... | - pps_limit - NIC limit rate value in pps. Type: integer or None
| | ...
| | ... | *Returns:*
| | ... | - 2-tuple, consisting of:
| | ... |   - Calculated unidirectional maximal transmit rate.
| | ... |     Type: integer or float
| | ... |   - Jumbo boolean, true if jumbo packet support has to be enabled.
| | ... |     Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get Max Rate And Jumbo | \${10000000} \| IMIX_v4_1 \
| | ... | \| overhead=\${40} \| pps_limit=\${18750000} \|
| | ...
| | [Arguments] | ${bps_limit} | ${framesize}
| | ... | ${overhead}=${0} | ${pps_limit}=${None}
| | ...
| | ${avg_size} = | Set Variable If | '${framesize}' == 'IMIX_v4_1'
| | ... | ${353.83333} | ${framesize}
| | ${max_size} = | Set Variable If | '${framesize}' == 'IMIX_v4_1'
| | ... | ${1518} | ${framesize}
| | # swo := size_with_overhead
| | ${avg_swo} = | Evaluate | ${avg_size} + ${overhead}
| | ${max_swo} = | Evaluate | ${max_size} + ${overhead}
| | ${jumbo} = | Set Variable If | ${max_swo} < 1522
| | ... | ${False} | ${True}
| | # For testing None see: https://groups.google.com/\
| | #                       forum/#!topic/robotframework-users/XntFz0ocD9E
| | ${limit_set} = | Set Variable | ${pps_limit != None}
| | ${rate} = | Evaluate | (${bps_limit}/((${avg_swo}+20)*8)).__trunc__()
| | ${max_rate} = | Set Variable If | ${limit_set} and ${rate} > ${pps_limit}
| | ... | ${pps_limit} | ${rate}
| | Return From Keyword | ${max_rate} | ${jumbo}

| Get Max Rate And Jumbo And Handle Multi Seg
| | [Documentation]
| | ... | This keyword adds correct multi seg configuration,
| | ... | then returns the result of Get Max Rate And Jumbo keyword.
| | ...
| | ... | See Documentation of Get Max Rate And Jumbo for more details.
| | ...
| | ... | *Arguments:*
| | ... | - bps_limit - Line rate limit in bps. Type: integer
| | ... | - framesize - Framesize in bytes. Type: integer or string
| | ... | - overhead - Overhead in bytes. Default: 0. Type: integer
| | ... | - pps_limit - NIC limit rate value in pps. Type: integer or None
| | ...
| | ... | *Returns:*
| | ... | - 2-tuple, consisting of:
| | ... |   - Calculated unidirectional maximal transmit rate.
| | ... |     Type: integer or float
| | ... |   - Jumbo boolean, true if jumbo packet support has to be enabled.
| | ... |     Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get Max Rate And Jumbo And Handle Multi Seg | \${10000000} \
| | ... | \| IMIX_v4_1 \| overhead=\${40} \| pps_limit=\${18750000} \|
| | ...
| | [Arguments] | ${bps_limit} | ${framesize}
| | ... | ${overhead}=${0} | ${pps_limit}=${None}
| | ...
| | ${max_rate} | ${jumbo} = | Get Max Rate And Jumbo
| | ... | ${bps_limit} | ${framesize} | ${overhead} | ${pps_limit}
| | Run Keyword If | not ${jumbo} | Add no multi seg to all DUTs
| | Return From Keyword | ${max_rate} | ${jumbo}

| Calculate pps
| | [Documentation]
| | ... | Calculate pps for given rate and L2 frame size,
| | ... | additional 20B are added to L2 frame size as padding.
| | ...
| | ... | FIXME: Migrate callers to Get Max Rate And Jumbo
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
| | ... | FIXME: Migrate callers to Get Max Rate And Jumbo
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

| Find NDR and PDR intervals using optimized search
| | [Documentation]
| | ... | Find boundaries for RFC2544 compatible NDR and PDR values
| | ... | using an optimized search algorithm.
| | ... | Display results as formatted test message.
| | ... | Fail if a resulting lower bound has too high loss fraction.
| | ... | Proceed with Perform additional measurements based on NDRPDR result.
| | ... | Input rates are understood as uni-directional,
| | ... | reported results contain bi-directional rates.
| | ...
| | ... | TODO: Should the trial duration of the additional
| | ... | measurements be configurable?
| | ...
| | ... | *Arguments:*
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | - topology_type - Topology type. Type: string
| | ... | - minimum_transmit_rate - Lower limit of search [pps]. Type: float
| | ... | - maximum_transmit_rate - Upper limit of search [pps]. Type: float
| | ... | - packet_loss_ratio - Accepted loss during search. Type: float
| | ... | - final_relative_width - Maximal width multiple of upper. Type: float
| | ... | - final_trial_duration - Duration of final trials [s]. Type: float
| | ... | - initial_trial_duration - Duration of initial trials [s]. Type: float
| | ... | - intermediate phases - Number of intermediate phases [1]. Type: int
| | ... | - timeout - Fail if search duration is longer [s]. Type: float
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find NDR and PDR intervals using optimized search \| \${64} \| \
| | ... | 3-node-IPv4 \| \${100000} \| \${14880952} \| \${0.005} \| \${0.005} \
| | ... | \| \${30.0} \| \${1.0} \| \${2} \| ${600.0} \|
| | ...
| | [Arguments] | ${frame_size} | ${topology_type} | ${minimum_transmit_rate}
| | ... | ${maximum_transmit_rate} | ${packet_loss_ratio}=${0.005}
| | ... | ${final_relative_width}=${0.005} | ${final_trial_duration}=${30.0}
| | ... | ${initial_trial_duration}=${1.0}
| | ... | ${number_of_intermediate_phases}=${2} | ${timeout}=${600.0}
| | ...
| | ${result} = | Perform optimized ndrpdr search | ${frame_size}
| | ... | ${topology_type} | ${minimum_transmit_rate*2}
| | ... | ${maximum_transmit_rate*2} | ${packet_loss_ratio}
| | ... | ${final_relative_width} | ${final_trial_duration}
| | ... | ${initial_trial_duration} | ${number_of_intermediate_phases}
| | ... | timeout=${timeout}
| | Display result of NDRPDR search | ${result} | ${frame_size}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${packet_loss_ratio}
| | Check NDRPDR interval validity | ${result.ndr_interval}
| | Perform additional measurements based on NDRPDR result
| | ... | ${result} | ${frame_size} | ${topology_type}

| Display single bound
| | [Documentation]
| | ... | Display one bound of NDR+PDR search,
| | ... | in packet per seconds (total and per stream)
| | ... | and Gbps total bandwidth with untagged packet.
| | ... | Througput is calculated as:
| | ... | Measured rate per stream * Total number of streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8) / Max bitrate of NIC
| | ... | The given result should contain latency data as well.
| | ...
| | ... | *Arguments:*
| | ... | - text - Flavor text describing which bound is this. Type: string
| | ... | - rate_total - Total (not per stream) measured Tr [pps]. Type: float
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - latency - Latency data to display if non-empty. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Display single bound \| NDR lower bound \| \${12345.67} \
| | ... | \| \${64} \| show_latency=\${EMPTY} \|
| | ...
| | [Arguments] | ${text} | ${rate_total} | ${framesize} | ${latency}=${EMPTY}
| | ...
| | ${bandwidth_total}= | Evaluate | ${rate_total}*(${framesize}+20)*8/(10**9)
| | Set Test Message | ${\n}${text}: ${rate_total} pps, | append=yes
| | Set Test Message | ${bandwidth_total} Gbps (untagged) | append=yes
| | Return From Keyword If | not """${latency}"""
| | Set Test Message | ${\n}LATENCY usec [min/avg/max] per stream: ${latency}
| | ... | append=yes

| Display result of NDRPDR search
| | [Documentation]
| | ... | Display result of NDR+PDR search, both quantities, both bounds,
| | ... | in packet per seconds (total and per stream)
| | ... | and Gbps total bandwidth with untagged packet.
| | ... | Througput is calculated as:
| | ... | Measured rate per stream * Total number of streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8) / Max bitrate of NIC
| | ... | The given result should contain latency data as well.
| | ...
| | ... | *Arguments:*
| | ... | - result - Measured result data per stream [pps]. Type: NdrPdrResult
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Display result of NDRPDR search \| \${result} \| \${64} \|
| | ...
| | [Arguments] | ${result} | ${framesize}
| | ...
| | ${framesize}= | Get Frame Size | ${framesize}
| | Display single bound | NDR_LOWER
| | ... | ${result.ndr_interval.measured_low.transmit_rate} | ${framesize}
| | ... | ${result.ndr_interval.measured_low.latency}
| | Display single bound | NDR_UPPER
| | ... | ${result.ndr_interval.measured_high.transmit_rate} | ${framesize}
| | Display single bound | PDR_LOWER
| | ... | ${result.pdr_interval.measured_low.transmit_rate} | ${framesize}
| | ... | ${result.pdr_interval.measured_low.latency}
| | Display single bound | PDR_UPPER
| | ... | ${result.pdr_interval.measured_high.transmit_rate} | ${framesize}

| Check NDRPDR interval validity
| | [Documentation]
| | ... | Extract loss ratio of lower bound of the interval.
| | ... | Fail if it does not reach the allowed value.
| | ...
| | ... | *Arguments:*
| | ... | - interval - Measured interval. Type: ReceiveRateInterval
| | ... | - packet_loss_ratio - Accepted loss (0.0 for NDR). Type: float
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Check NDRPDR interval validity \| \${result.pdr_interval} \
| | ... | \| \${0.005} \|
| | ...
| | [Arguments] | ${interval} | ${packet_loss_ratio}=${0.0}
| | ...
| | ${lower_bound_lf} = | Set Variable | ${interval.measured_low.loss_fraction}
| | Return From Keyword If | ${lower_bound_lf} <= ${packet_loss_ratio}
| | ${message}= | Catenate | SEPARATOR=${SPACE}
| | ... | Minimal rate loss fraction ${lower_bound_lf}
| | ... | does not reach target ${packet_loss_ratio}.
| | ${message} = | Set Variable If | ${lower_bound_lf} >= 1.0
| | ... | ${message}${\n}Zero packets forwarded! | ${message}
| | Fail | ${message}

| Perform additional measurements based on NDRPDR result
| | [Documentation]
| | ... | Perform any additional measurements which are not directly needed
| | ... | for determining NDR nor PDR, but which are needed for gathering
| | ... | additional data for debug purposes.
| | ... | Currently, just "Traffic should pass with no loss" is called.
| | ... | TODO: Move latency measurements from optimized search here.
| | ...
| | ... | *Arguments:*
| | ... | - result - Measured result data per stream [pps]. Type: NdrPdrResult
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | - topology_type - Topology type. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Perform additional measurements based on NDRPDR result \
| | ... | \| \${result} \| ${64} \| 3-node-IPv4 \|
| | ...
| | [Arguments] | ${result} | ${framesize} | ${topology_type}
| | ...
| | ${duration}= | Set Variable | 5.0
| | ${rate_per_stream}= | Evaluate
| | ... | ${result.ndr_interval.measured_low.target_tr} / 2.0
| | Traffic should pass with no loss | ${duration} | ${rate_per_stream}pps
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}

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
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
| | ... | - topology_type - Topology type. Type: string
| | ... | - subsamples - How many trials in this measurement. Type:int
| | ... | - trial_duration - Duration of single trial [s]. Type: float
| | ... | - fail_no_traffic - Whether to fail on zero receive count. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Traffic should pass with maximum rate \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \| ${1} \| ${10.0} | ${False} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${topology_type}
| | ... | ${trial_duration}=${perf_trial_duration} | ${fail_no_traffic}=${True}
| | ... | ${subsamples}=${perf_trial_multiplicity}
| | ...
| | ${results} = | Send traffic at specified rate | ${trial_duration} | ${rate}
| | ... | ${framesize} | ${topology_type} | ${subsamples}
| | Set Test Message | ${\n}Maximum Receive Rate trial results
| | Set Test Message | in packets per second: ${results}
| | ... | append=yes
| | # TODO: Should we also report the percentage relative to transmit rate,
| | # so that people looking at console can decide how close to 100% it is?
| | Run Keyword If | ${fail_no_traffic} | Fail if no traffic forwarded

| Send traffic at specified rate
| | [Documentation]
| | ... | Send traffic at specified rate.
| | ... | Return list of measured receive rates.
| | ...
| | ... | *Arguments:*
| | ... | - trial_duration - Duration of single trial [s]. Type: float
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer/string
| | ... | - topology_type - Topology type. Type: string
| | ... | - subsamples - How many trials in this measurement. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send traffic at specified rate \| ${1.0} \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \| ${10} \|
| | ...
| | [Arguments] | ${trial_duration} | ${rate} | ${framesize}
| | ... | ${topology_type} | ${subsamples}=${1}
| | ...
| | Clear and show runtime counters with running traffic | ${trial_duration}
| | ... | ${rate} | ${framesize} | ${topology_type}
| | Run Keyword If | ${dut_stats}==${True} | Clear all counters on all DUTs
| | Run Keyword If | ${dut_stats}==${True} and ${pkt_trace}==${True}
| | ... | VPP Enable Traces On All DUTs | ${nodes}
| | ${results} = | Create List
| | :FOR | ${i} | IN RANGE | ${subsamples}
| | | Send traffic on tg | ${trial_duration} | ${rate} | ${framesize}
| | | ... | ${topology_type} | warmup_time=0
| | | ${rx} = | Get Received
| | | ${rr} = | Evaluate | ${rx} / ${trial_duration}
| | | Append To List | ${results} | ${rr}
| | Run Keyword If | ${dut_stats}==${True} | Show statistics on all DUTs
| | ... | ${nodes}
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
