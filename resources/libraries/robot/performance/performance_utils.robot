# Copyright (c) 2021 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.PerfUtil
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.Iperf3
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.OptimizedSearch
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Library | resources.libraries.python.Trace
| Variables | resources/libraries/python/Constants.py
|
| Documentation
| ... | Performance suite keywords - utilities to find and verify NDR and PDR.

*** Variables ***
| ${trial_duration}= | ${PERF_TRIAL_DURATION}
| ${trial_multiplicity}= | ${PERF_TRIAL_MULTIPLICITY}
| ${extended_debug}= | ${EXTENDED_DEBUG}

*** Keywords ***
| Find NDR and PDR intervals using optimized search
| | [Documentation]
| | ... | Find boundaries for RFC2544 compatible NDR and PDR values
| | ... | using an optimized search algorithm.
| | ... | Display findings as a formatted test message.
| | ... | Fail if a resulting lower bound has too high loss fraction.
| | ... | Input rates are understood as uni-directional,
| | ... | reported result contains aggregate rates.
| | ... | Additional latency measurements are performed for smaller loads,
| | ... | their results are also displayed.
| | ... | Finally, two measurements for runtime stats are done (not displayed).
| | ... | Currently, the min_rate value is hardcoded to 90kpps,
| | ... | allowing measurement at 10% of the discovered rate
| | ... | without breaking latency streams.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Arguments:*
| | ... | - packet_loss_ratio - Accepted loss during search. Type: float
| | ... | - final_relative_width - Maximal width multiple of upper. Type: float
| | ... | - final_trial_duration - Duration of final trials [s]. Type: float
| | ... | - initial_trial_duration - Duration of initial trials [s]. Type: float
| | ... | - intermediate phases - Number of intermediate phases [1].
| | ... | Type: integer
| | ... | - timeout - Fail if search duration is longer [s]. Type: float
| | ... | - doublings - How many doublings to do when expanding [1].
| | ... | Type: integer
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - latency_duration - Duration for latency-specific trials. Type: float
| | ... | - latency - False to disable latency measurement; default value: True.
| | ... | Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Find NDR and PDR intervals using optimized search \| \${0.005} \
| | ... | \| \${0.005} \| \${30.0} \| \${1.0} \| \${2} \| \${600.0} \| \${2} \
| | ... | \| \${2} \| ${5.0} \|
| |
| | [Arguments] | ${packet_loss_ratio}=${0.005}
| | ... | ${final_relative_width}=${0.005} | ${final_trial_duration}=${30.0}
| | ... | ${initial_trial_duration}=${1.0}
| | ... | ${number_of_intermediate_phases}=${2} | ${timeout}=${720.0}
| | ... | ${doublings}=${2} | ${traffic_directions}=${2}
| | ... | ${latency_duration}=${PERF_TRIAL_LATENCY_DURATION}
| | ... | ${latency}=${True}
| |
| | ${result} = | Perform optimized ndrpdr search | ${frame_size}
| | ... | ${traffic_profile} | ${9000} | ${max_rate}
| | ... | ${packet_loss_ratio} | ${final_relative_width}
| | ... | ${final_trial_duration} | ${initial_trial_duration}
| | ... | ${number_of_intermediate_phases} | timeout=${timeout}
| | ... | doublings=${doublings} | traffic_directions=${traffic_directions}
| | ... | latency=${False}
| | Display result of NDRPDR search | ${result}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${packet_loss_ratio}
| | Check NDRPDR interval validity | ${result.ndr_interval}
| | ${pdr_sum}= | Set Variable | ${result.pdr_interval.measured_low.target_tr}
| | ${pdr_per_stream}= | Evaluate | ${pdr_sum} / float(${traffic_directions})
| | ${ndr_sum}= | Set Variable | ${result.ndr_interval.measured_low.target_tr}
| | ${ndr_per_stream}= | Evaluate | ${ndr_sum} / float(${traffic_directions})
| | ${rate}= | Evaluate | 0.9 * ${pdr_per_stream}
| | Run Keyword If | ${latency}
| | ... | Measure and show latency at specified rate | Latency at 90% PDR:
| | ... | ${latency_duration} | ${rate} | ${framesize}
| | ... | ${traffic_profile} | ${traffic_directions}
| | ${rate}= | Evaluate | 0.5 * ${pdr_per_stream}
| | Run Keyword If | ${latency}
| | ... | Measure and show latency at specified rate | Latency at 50% PDR:
| | ... | ${latency_duration} | ${rate} | ${framesize}
| | ... | ${traffic_profile} | ${traffic_directions}
| | ${rate}= | Evaluate | 0.1 * ${pdr_per_stream}
| | Run Keyword If | ${latency}
| | ... | Measure and show latency at specified rate | Latency at 10% PDR:
| | ... | ${latency_duration} | ${rate} | ${framesize}
| | ... | ${traffic_profile} | ${traffic_directions}
| | Run Keyword If | ${latency}
| | ... | Measure and show latency at specified rate | Latency at 0% PDR:
| | ... | ${latency_duration} | ${0} | ${framesize}
| | ... | ${traffic_profile} | ${traffic_directions}
| | # Finally, trials with runtime and other stats.
| | # We expect NDR and PDR to have different-looking stats.
| | Send traffic at specified rate
| | ... | ${1.0} | ${pdr_per_stream} | ${framesize} | ${traffic_profile}
| | ... | traffic_directions=${traffic_directions}
| | Send traffic at specified rate
| | ... | ${1.0} | ${ndr_per_stream} | ${framesize} | ${traffic_profile}
| | ... | traffic_directions=${traffic_directions}

| Find Throughput Using MLRsearch
| | [Documentation]
| | ... | Find and return lower bound PDR (zero PLR by default)
| | ... | aggregate throughput using MLRsearch algorithm.
| | ... | Input rates are understood as uni-directional.
| | ... | Currently, the min_rate value is hardcoded to match test teardowns.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Arguments:*
| | ... | - packet_loss_ratio - Accepted loss during search. Type: float
| | ... | - final_relative_width - Maximal width multiple of upper. Type: float
| | ... | - final_trial_duration - Duration of final trials [s]. Type: float
| | ... | - initial_trial_duration - Duration of initial trials [s]. Type: float
| | ... | - intermediate phases - Number of intermediate phases [1].
| | ... | Type: integer
| | ... | - timeout - Fail if search duration is longer [s]. Type: float
| | ... | - doublings - How many doublings to do when expanding [1].
| | ... | Type: integer
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - latency - True to enable latency measurement; default value: False.
| | ... | Type: boolean
| |
| | ... | *Returns:*
| | ... | - Lower bound for bi-directional throughput at given PLR. Type: float
| |
| | ... | *Example:*
| |
| | ... | \| \${throughpt}= \| Find Throughput Using MLRsearch \| \${0} \
| | ... | \| \${0.001} \| \${10.0}\| \${1.0} \| \${1} \| \${720.0} \| \${2} \
| | ... | \| \${2} \|
| |
| | [Arguments] | ${packet_loss_ratio}=${0.0}
| | ... | ${final_relative_width}=${0.001} | ${final_trial_duration}=${10.0}
| | ... | ${initial_trial_duration}=${1.0}
| | ... | ${number_of_intermediate_phases}=${1} | ${timeout}=${720.0}
| | ... | ${doublings}=${2} | ${traffic_directions}=${2} | ${latency}=${False}
| |
| | ${result} = | Perform optimized ndrpdr search | ${frame_size}
| | ... | ${traffic_profile} | ${10000} | ${max_rate}
| | ... | ${packet_loss_ratio} | ${final_relative_width}
| | ... | ${final_trial_duration} | ${initial_trial_duration}
| | ... | ${number_of_intermediate_phases} | timeout=${timeout}
| | ... | doublings=${doublings} | traffic_directions=${traffic_directions}
| | ... | latency=${latency}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${packet_loss_ratio}
| | Return From Keyword | ${result.pdr_interval.measured_low.target_tr}

| Find critical load using PLRsearch
| | [Documentation]
| | ... | Find boundaries for troughput (of given target loss ratio)
| | ... | using PLRsearch algorithm.
| | ... | Display results as formatted test message.
| | ... | Fail if computed lower bound 110% of the minimal rate or less.
| | ... | Input rates are understood as uni-directional,
| | ... | reported result contains aggregate rates.
| | ... | Currently, the min_rate value is hardcoded to match test teardowns.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Arguments:*
| | ... | - packet_loss_ratio - Accepted loss during search. Type: float
| | ... | - timeout - Stop when search duration is longer [s]. Type: float
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - latency - True to enable latency measurement; default value: False.
| | ... | Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Find critical load using PLR search \| \${1e-7} \| \${120} \
| | ... | \| \${2} \|
| |
| | [Arguments] | ${packet_loss_ratio}=${1e-7} | ${timeout}=${1800.0}
| | ... | ${traffic_directions}=${2} | ${latency}=${False}
| |
| | ${min_rate} = | Set Variable | ${10000}
| | ${average} | ${stdev} = | Perform soak search | ${frame_size}
| | ... | ${traffic_profile} | ${min_rate} | ${max_rate}
| | ... | ${packet_loss_ratio} | timeout=${timeout}
| | ... | traffic_directions=${traffic_directions} | latency=${latency}
| | ${lower} | ${upper} = | Display result of soak search
| | ... | ${average} | ${stdev}
| | Should Not Be True | 1.1 * ${traffic_directions} * ${min_rate} > ${lower}
| | ... | Lower bound ${lower} too small for unidirectional minimum ${min_rate}.

| Display single bound
| | [Documentation]
| | ... | Display one bound of NDR+PDR search,
| | ... | in packet per seconds (total and per stream)
| | ... | and Gbps total bandwidth (for initial packet size).
| | ... | Througput is calculated as:
| | ... | Sum of measured rates over streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8)
| | ... | The given result should contain latency data as well.
| |
| | ... | *Arguments:*
| | ... | - text - Flavor text describing which bound is this. Type: string
| | ... | - rate_total - Total (not per stream) measured Tr [pps]. Type: float
| | ... | - frame_size - L2 Frame Size [B]. Type: integer
| | ... | - latency - Latency data to display if non-empty. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Display single bound \| NDR lower bound \| \${12345.67} \
| | ... | \| \${64} \| latency=\${EMPTY} \|
| |
| | [Arguments] | ${text} | ${rate_total} | ${frame_size} | ${latency}=${EMPTY}
| |
| | ${bandwidth_total} = | Evaluate | ${rate_total} * (${frame_size}+20)*8 / 1e9
| | Set Test Message | ${\n}${text}: ${rate_total} pps, | append=yes
| | Set Test Message | ${bandwidth_total} Gbps (initial) | append=yes
| | Return From Keyword If | not """${latency}"""
| | Set Test Message | ${\n}LATENCY [min/avg/max/hdrh] per stream: ${latency}
| | ... | append=yes

| Display Reconfig Test Message
| | [Documentation]
| | ... | Display the number of packets lost (bidirectionally)
| | ... | due to reconfiguration under traffic.
| |
| | ... | *Arguments:*
| | ... | - result - Result of bidirectional measurtement.
| | ... | Type: ReceiveRateMeasurement
| |
| | ... | *Example:*
| |
| | ... | \| Display Reconfig Test Message \| \${result} \|
| |
| | [Arguments] | ${result}
| |
| | Set Test Message | Packets lost due to reconfig: ${result.loss_count}
| | ${time_lost} = | Evaluate | ${result.loss_count} / ${result.target_tr}
| | Set Test Message | ${\n}Implied time lost: ${time_lost} | append=yes

| Display result of NDRPDR search
| | [Documentation]
| | ... | Display result of NDR+PDR search, both quantities, both bounds,
| | ... | aggregate in packet per seconds
| | ... | and Gbps total bandwidth (for initial packet size).
| | ... | Througput is calculated as:
| | ... | Sum of measured rate over streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8)
| | ... | The given result should contain latency data as well.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | *Arguments:*
| | ... | - result - Measured result data per stream [pps]. Type: NdrPdrResult
| |
| | ... | *Example:*
| |
| | ... | \| Display result of NDRPDR search \| \${result} \|
| |
| | [Arguments] | ${result}
| |
| | ${frame_size} = | Get Average Frame Size | ${frame_size}
| | Display single bound | NDR_LOWER
| | ... | ${result.ndr_interval.measured_low.target_tr} | ${frame_size}
| | ... | ${result.ndr_interval.measured_low.latency}
| | Display single bound | NDR_UPPER
| | ... | ${result.ndr_interval.measured_high.target_tr} | ${frame_size}
| | Display single bound | PDR_LOWER
| | ... | ${result.pdr_interval.measured_low.target_tr} | ${frame_size}
| | ... | ${result.pdr_interval.measured_low.latency}
| | Display single bound | PDR_UPPER
| | ... | ${result.pdr_interval.measured_high.target_tr} | ${frame_size}

| Display result of soak search
| | [Documentation]
| | ... | Display result of soak search, avg+-stdev, as upper/lower bounds,
| | ... | in aggregate packets per seconds
| | ... | and Gbps total bandwidth (for initial packet size).
| | ... | Througput is calculated as:
| | ... | Sum of measured rates over streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8)
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | *Arguments:*
| | ... | - avg - Estimated average critical load [pps]. Type: float
| | ... | - stdev - Standard deviation of critical load [pps]. Type: float
| |
| | ... | *Returns:*
| | ... | - Lower and upper bound of critical load [pps]. Type: 2-tuple of float
| |
| | ... | *Example:*
| |
| | ... | \| Display result of soak search \| \${100000} \| \${100} \|
| |
| | [Arguments] | ${avg} | ${stdev}
| |
| | ${frame_size} = | Get Average Frame Size | ${frame_size}
| | ${avg} = | Convert To Number | ${avg}
| | ${stdev} = | Convert To Number | ${stdev}
| | ${lower} = | Evaluate | ${avg} - ${stdev}
| | ${upper} = | Evaluate | ${avg} + ${stdev}
| | Display single bound | PLRsearch lower bound | ${lower} | ${frame_size}
| | Display single bound | PLRsearch upper bound | ${upper} | ${frame_size}
| | Return From Keyword | ${lower} | ${upper}

| Check NDRPDR interval validity
| | [Documentation]
| | ... | Extract loss ratio of lower bound of the interval.
| | ... | Fail if it does not reach the allowed value.
| |
| | ... | *Arguments:*
| | ... | - interval - Measured interval. Type: ReceiveRateInterval
| | ... | - packet_loss_ratio - Accepted loss (0.0 for NDR). Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Check NDRPDR interval validity \| \${result.pdr_interval} \
| | ... | \| \${0.005} \|
| |
| | [Arguments] | ${interval} | ${packet_loss_ratio}=${0.0}
| |
| | ${lower_bound} = | Set Variable | ${interval.measured_low}
| | ${lower_bound_lf} = | Set Variable | ${lower_bound.loss_fraction}
| | Return From Keyword If | ${lower_bound_lf} <= ${packet_loss_ratio}
| | ${message}= | Catenate | SEPARATOR=${SPACE}
| | ... | Minimal rate loss fraction ${lower_bound_lf}
| | ... | does not reach target ${packet_loss_ratio}.
| | ${message_zero} = | Set Variable | Zero packets forwarded!
| | ${message_other} = | Set Variable | ${lower_bound.loss_count} packets lost.
| | ${message} = | Set Variable If | ${lower_bound_lf} >= 1.0
| | ... | ${message}${\n}${message_zero} | ${message}${\n}${message_other}
| | Fail | ${message}

| Traffic should pass with maximum rate
| | [Documentation]
| | ... | Send traffic at maximum rate.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffic for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Arguments:*
| | ... | - trial_duration - Duration of single trial [s]. Type: float
| | ... | - fail_no_traffic - Whether to fail on zero receive count;
| | ... | default value: True. Type: boolean
| | ... | - trial_multiplicity - How many trials in this measurement.
| | ... | Type: integer
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic;
| | ... | default value: 2. Type: integer
| | ... | - tx_port - TX port of TG; default value: 0. Type: integer
| | ... | - rx_port - RX port of TG; default value: 1. Type: integer
| | ... | - latency - True to enable latency measurement; default value: False.
| | ... | Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Traffic should pass with maximum rate \| \${1} \| \${False} \
| | ... | \| \${10.0} \| \${2} \| \${0} \| \${1} \| \${True} \|
| |
| | [Arguments] | ${trial_duration}=${trial_duration}
| | ... | ${fail_no_traffic}=${True}
| | ... | ${trial_multiplicity}=${trial_multiplicity}
| | ... | ${traffic_directions}=${2} | ${tx_port}=${0} | ${rx_port}=${1}
| | ... | ${latency}=${False}
| |
| | ${results}= | Send traffic at specified rate
| | ... | ${trial_duration} | ${max_rate} | ${frame_size}
| | ... | ${traffic_profile} | ${trial_multiplicity}
| | ... | ${traffic_directions} | ${tx_port} | ${rx_port} | latency=${latency}
| | Set Test Message | ${\n}Maximum Receive Rate trial results
| | Set Test Message | in packets per second: ${results}
| | ... | append=yes
| | Run Keyword If | ${fail_no_traffic} | Fail if no traffic forwarded

| Send traffic at specified rate
| | [Documentation]
| | ... | Perform a warmup, show runtime counters during it.
| | ... | Then send traffic at specified rate, possibly multiple trials.
| | ... | Show various DUT stats, optionally also packet trace.
| | ... | Return list of measured receive rates.
| |
| | ... | *Arguments:*
| | ... | - trial_duration - Duration of single trial [s]. Type: float
| | ... | - rate - Target aggregate transmit rate [pps] / Connections per second
| | ... | (CPS) for UDP/TCP flows. Type: float
| | ... | - frame_size - L2 Frame Size [B]. Type: integer or string
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - trial_multiplicity - How many trials in this measurement.
| | ... | Type: integer
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - tx_port - TX port of TG; default value: 0. Type: integer
| | ... | - rx_port - RX port of TG; default value: 1. Type: integer
| | ... | - extended_debug - True to enable extended debug.
| | ... | Type: boolean
| | ... | - latency - True to enable latency measurement; default value: False.
| | ... | Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Send traffic at specified rate \| \${1.0} \| ${4000000.0} \
| | ... | \| \${64} \| 3-node-IPv4 \| \${10} \| \${2} \| \${0} \| \${1} \
| | ... | \| ${False} \| ${True} \|
| |
| | [Arguments] | ${trial_duration} | ${rate} | ${frame_size}
| | ... | ${traffic_profile} | ${trial_multiplicity}=${trial_multiplicity}
| | ... | ${traffic_directions}=${2} | ${tx_port}=${0} | ${rx_port}=${1}
| | ... | ${extended_debug}=${extended_debug} | ${latency}=${False}
| |
| | Set Test Variable | ${extended_debug}
| | # Following setting of test variables is needed for some pre_stats actions.
| | Set Test Variable | ${rate}
| | Set Test Variable | ${traffic_directions}
| | Set Test Variable | ${tx_port}
| | Set Test Variable | ${rx_port}
| |
| | FOR | ${action} | IN | @{pre_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | ${results} = | Create List
| | FOR | ${i} | IN RANGE | ${trial_multiplicity}
| | | # The following line is skipping some default arguments,
| | | # that is why subsequent arguments have to be named.
| | | Send traffic on tg
| | | ... | ${trial_duration} | ${rate} | ${frame_size} | ${traffic_profile}
| | | ... | warmup_time=${0} | traffic_directions=${traffic_directions}
| | | ... | tx_port=${tx_port} | rx_port=${rx_port} | latency=${latency}
| | | ${rx} = | Get Received
| | | ${rr} = | Evaluate | ${rx} / ${trial_duration}
| | | Append To List | ${results} | ${rr}
| | END
| | FOR | ${action} | IN | @{post_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Return From Keyword | ${results}

| Clear and show runtime counters with running iperf3
| | [Documentation]
| | ... | Start traffic at specified rate then clear runtime counters on all
| | ... | DUTs. Wait for specified amount of time and capture runtime counters
| | ... | on all DUTs. Finally stop traffic.
| |
| | ... | *Example:*
| |
| | ... | \| Clear and show runtime counters with running traffic \|
| |
| | ${runtime_duration} = | Get Runtime Duration
| | ${pids}= | iPerf Client Start Remote Exec
| | | ... | ${nodes['${iperf_client_node}']}
| | | ... | duration=${-1}
| | | ... | rate=${None}
| | | ... | frame_size=${None}
| | | ... | async_call=True
| | | ... | warmup_time=0
| | | ... | traffic_directions=${1}
| | | ... | namespace=${iperf_client_namespace}
| | | ... | udp=${iperf_client_udp}
| | | ... | host=${iperf_server_bind}
| | | ... | bind=${iperf_client_bind}
| | | ... | affinity=${iperf_client_affinity}
| | FOR | ${action} | IN | @{pre_run_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Sleep | ${runtime_duration}
| | FOR | ${action} | IN | @{post_run_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | iPerf Client Stop Remote Exec | ${nodes['${iperf_client_node}']} | ${pids}

| Traffic should pass with maximum rate on iPerf3
| | [Documentation]
| | ... | Send traffic at maximum rate on iPerf3.
| |
| | ... | *Arguments:*
| | ... | - trial_duration - Duration of single trial [s].
| | ... | Type: float
| | ... | - trial_multiplicity - How many trials in this measurement.
| | ... | Type: integer
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic;
| | ... | Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Traffic should pass with maximum rate on iPerf3 \| \${1} \| \
| | ... | \| \${10.0} \| \${2} \|
| |
| | [Arguments] | ${trial_duration}=${trial_duration}
| | ... | ${trial_multiplicity}=${trial_multiplicity}
| | ... | ${traffic_directions}=${1}
| |
| | ${results}= | Send iPerf3 traffic at specified rate
| | ... | ${trial_duration} | ${None} | ${None}
| | ... | ${trial_multiplicity} | ${traffic_directions}
| | Set Test Message | ${\n}iPerf3 trial results
| | Set Test Message | in Gbits per second: ${results}
| | ... | append=yes

| Send iPerf3 traffic at specified rate
| | [Documentation]
| | ... | Perform a warmup, show runtime counters during it.
| | ... | Then send traffic at specified rate, possibly multiple trials.
| | ... | Show various DUT stats, optionally also packet trace.
| | ... | Return list of measured receive rates.
| |
| | ... | *Arguments:*
| | ... | - trial_duration - Duration of single trial [s].
| | ... | Type: float
| | ... | - rate - Target aggregate transmit rate [bps] / Bits per second
| | ... | Type: float
| | ... | - frame_size - L2 Frame Size [B].
| | ... | Type: integer or string
| | ... | - trial_multiplicity - How many trials in this measurement.
| | ... | Type: integer
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - extended_debug - True to enable extended debug.
| | ... | Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Send iPerf3 traffic at specified rate \| \${1.0} \| ${4000000.0} \
| | ... | \| \${64} \| \${10} \| \${1} \| ${False} \|
| |
| | [Arguments] | ${trial_duration} | ${rate} | ${frame_size}
| | ... | ${trial_multiplicity}=${trial_multiplicity}
| | ... | ${traffic_directions}=${1} | ${extended_debug}=${extended_debug}
| |
| | Set Test Variable | ${extended_debug}
| | Set Test Variable | ${rate}
| | Set Test Variable | ${traffic_directions}
| |
| | ${smt_used}= | Is SMT enabled | ${nodes['${iperf_server_node}']['cpuinfo']}
| | ${vm_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Get Library Instance | vnf_manager
| | ${vth}= | Evaluate | (${thr_count_int} + 1)
| | ${cpu_skip_cnt}= | Set Variable If | '${vm_status}' == 'PASS'
| | ... | ${CPU_CNT_SYSTEM}
| | ... | ${${CPU_CNT_SYSTEM} + ${CPU_CNT_MAIN} + ${cpu_count_int} + ${vth}}
| |
| | Initialize iPerf Server
| | ... | ${nodes['${iperf_server_node}']}
| | ... | pf_key=${iperf_server_pf_key}
| | ... | interface=${iperf_server_interface}
| | ... | bind=${iperf_server_bind}
| | ... | bind_gw=${iperf_server_bind_gw}
| | ... | bind_mask=${iperf_server_bind_mask}
| | ... | namespace=${iperf_server_namespace}
| | ... | cpu_skip_cnt=${cpu_skip_cnt}
| | Run Keyword If | '${iperf_client_namespace}' is not '${None}'
| | ... | Set Linux Interface IP
| | ... | ${nodes['${iperf_client_node}']}
| | ... | interface=${iperf_client_interface}
| | ... | ip_addr=${iperf_client_bind}
| | ... | prefix=${iperf_client_bind_mask}
| | ... | namespace=${iperf_client_namespace}
| | Run Keyword If | '${iperf_client_namespace}' is not '${None}'
| | ... | Add Default Route To Namespace
| | ... | ${nodes['${iperf_client_node}']}
| | ... | namespace=${iperf_client_namespace}
| | ... | default_route=${iperf_client_bind_gw}
| | ${pre_stats}= | Create List
| | ... | clear-show-runtime-with-iperf3
| | ... | vpp-clear-stats | vpp-enable-packettrace | vpp-enable-elog
| | FOR | ${action} | IN | @{pre_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | ${results} = | Create List
| | FOR | ${i} | IN RANGE | ${trial_multiplicity}
| | | ${rr} = | iPerf Client Start Remote Exec
| | | ... | ${nodes['${iperf_client_node}']}
| | | ... | duration=${trial_duration}
| | | ... | rate=${rate}
| | | ... | frame_size=${frame_size}
| | | ... | async_call=False
| | | ... | warmup_time=0
| | | ... | traffic_directions=${traffic_directions}
| | | ... | namespace=${iperf_client_namespace}
| | | ... | udp=${iperf_client_udp}
| | | ... | host=${iperf_server_bind}
| | | ... | bind=${iperf_client_bind}
| | | ... | affinity=${iperf_client_affinity}
| | | ${conv} = | Convert To Number | ${rr['sum_received']['bits_per_second']}
| | | ${conv} = | Evaluate | ${conv} / ${1000} / ${1000} / ${1000}
| | | ${conv} = | Evaluate | "{:.3f}".format(${conv})
| | | Append To List
| | | ... | ${results} | ${conv}
| | END
| | FOR | ${action} | IN | @{post_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Return From Keyword | ${results}

| Measure and show latency at specified rate
| | [Documentation]
| | ... | Send traffic at specified rate, single trial.
| | ... | Extract latency information and append it to text message.
| | ... | The rate argument is int, so should not include "pps".
| | ... | If the given rate is too low, a safe value is used instead.
| |
| | ... | *Arguments:*
| | ... | - message_prefix - Preface to test message addition. Type: string
| | ... | - trial_duration - Duration of single trial [s]. Type: float
| | ... | - rate - Rate [pps] for sending packets in case of T-Rex stateless
| | ... | mode or multiplier of profile CPS in case of T-Rex astf mode.
| | ... | Type: float
| | ... | - frame_size - L2 Frame Size [B]. Type: integer or string
| | ... | - traffic_profile - Name of module defining traffic for measurements.
| | ... | Type: string
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - tx_port - TX port of TG; default value: 0. Type: integer
| | ... | - rx_port - RX port of TG; default value: 1. Type: integer
| | ... | - safe_rate - To apply if rate is below this, as latency pps is fixed.
| | ... | In pps. Type: integer.
| |
| | ... | *Example:*
| |
| | ... | \| Measure and show latency at specified rate \| Latency at 90% NDR \
| | ... | \| \${1.0} \| ${10000000} \| \${64} \| 3-node-IPv4 \| \${2} \
| | ... | \| \${0} \| \${1} \| ${9500} \|
| |
| | [Arguments] | ${message_prefix} | ${trial_duration} | ${rate}
| | ... | ${frame_size} | ${traffic_profile} | ${traffic_directions}=${2}
| | ... | ${tx_port}=${0} | ${rx_port}=${1} | ${safe_rate}=${9001}
| |
| | ${real_rate} = | Evaluate | max(${rate}, ${safe_rate})
| | # The following line is skipping some default arguments,
| | # that is why subsequent arguments have to be named.
| | Send traffic on tg | ${trial_duration} | ${real_rate} | ${frame_size}
| | ... | ${traffic_profile} | warmup_time=${0}
| | ... | traffic_directions=${traffic_directions} | tx_port=${tx_port}
| | ... | rx_port=${rx_port} | latency=${True}
| | ${latency} = | Get Latency Int
| | Set Test Message | ${\n}${message_prefix} ${latency} | append=${True}

| Clear and show runtime counters with running traffic
| | [Documentation]
| | ... | Start traffic at specified rate then clear runtime counters on all
| | ... | DUTs. Wait for specified amount of time and capture runtime counters
| | ... | on all DUTs. Finally stop traffic
| |
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate [pps] for sending packets in case of T-Rex stateless
| | ... | mode or multiplier of profile CPS in case of T-Rex astf mode.
| | ... | Type: float
| | ... | - frame_size - L2 Frame Size [B] or IMIX_v4_1. Type: integer or string
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - tx_port - TX port of TG; default value: 0. Type: integer
| | ... | - rx_port - RX port of TG, default value: 1. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Clear and show runtime counters with running traffic \| \${10} \
| | ... | \| ${4000000.0} \| \${64} \| 3-node-IPv4 \| \${2} \| \${0} \| \${1} \|
| |
| | [Arguments] | ${duration} | ${rate} | ${frame_size} | ${traffic_profile}
| | ... | ${traffic_directions}=${2} | ${tx_port}=${0} | ${rx_port}=${1}
| |
| | # Duration of -1 means we will stop traffic manually.
| | Send traffic on tg | ${-1} | ${rate} | ${frame_size} | ${traffic_profile}
| | ... | warmup_time=${0} | async_call=${True} | latency=${False}
| | ... | traffic_directions=${traffic_directions} | tx_port=${tx_port}
| | ... | rx_port=${rx_port}
| | FOR | ${action} | IN | @{pre_run_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Sleep | ${duration}
| | FOR | ${action} | IN | @{post_run_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Stop traffic on tg

| Send ramp-up traffic
| | [Documentation]
| | ... | Start ramp-up traffic at specified rate for defined duration.
| |
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate [pps] for sending packets in case of T-Rex stateless
| | ... | mode or multiplier of profile CPS in case of T-Rex astf mode.
| | ... | Type: float
| | ... | - frame_size - L2 Frame Size [B] or IMIX_v4_1. Type: integer or string
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - tx_port - TX port of TG; default value: 0. Type: integer
| | ... | - rx_port - RX port of TG, default value: 1. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Send ramp-up traffic \| \${10} \| ${400000.0} \| ${64} \
| | ... | \| ${2} \| ${0} \| ${1} \|
| |
| | [Arguments] | ${duration}=${ramp_up_duration} | ${rate}=${ramp_up_rate}
| | ... | ${frame_size}=${frame_size} | ${traffic_profile}=${traffic_profile}
| | ... | ${traffic_directions}=${2} | ${tx_port}=${0} | ${rx_port}=${1}
| |
| | Send traffic on tg
| | ... | ${duration} | ${rate} | ${frame_size} | ${traffic_profile}
| | ... | warmup_time=${0} | traffic_directions=${traffic_directions}
| | ... | tx_port=${tx_port} | rx_port=${rx_port} | latency=${False}

| Start Traffic on Background
| | [Documentation]
| | ... | Start traffic at specified rate then return control to Robot.
| | ... | This keyword is useful if the test needs to do something
| | ... | while traffic is running.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | *Arguments:*
| | ... | - rate - Rate [pps] for sending packets in case of T-Rex stateless
| | ... | mode or multiplier of profile CPS in case of T-Rex astf mode.
| | ... | Type: float
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: integer
| | ... | - tx_port - TX port of TG; default value: 0. Type: integer
| | ... | - rx_port - RX port of TG; default value: 1. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Start Traffic on Background \| ${4000000.0} \| \${2} \| \${0} \
| | ... | \| \${1} \|
| |
| | [Arguments] | ${rate} | ${traffic_directions}=${2} | ${tx_port}=${0}
| | ... | ${rx_port}=${1}
| |
| | # Duration of -1 means we will stop traffic manually.
| | Send traffic on tg | ${-1} | ${rate} | ${frame_size} | ${traffic_profile}
| | ... | warmup_time=${0} | async_call=${True} | latency=${False}
| | ... | traffic_directions=${traffic_directions} | tx_port=${tx_port}
| | ... | rx_port=${rx_port}

| Stop Running Traffic
| | [Documentation]
| | ... | Stop the running traffic, return measurement result.
| | ... | For bidirectional traffic, the reported values are bi-directional.
| |
| | ... | *Returns:*
| | ... | - Measurement result. Type: ReceiveRateMeasurement
| |
| | ... | *Example:*
| |
| | ... | \${result}= \| Stop Running Traffic \|
| |
| | ${result}= | Stop traffic on tg
| | Return From Keyword | ${result}

| Additional Statistics Action For vpp-clear-stats
| | [Documentation]
| | ... | Additional Statistics Action for clear VPP statistics.
| |
| | Clear Statistics On All DUTs | ${nodes}

| Additional Statistics Action For vpp-show-stats
| | [Documentation]
| | ... | Additional Statistics Action for show VPP statistics.
| |
| | Show Statistics On All DUTs | ${nodes}

| Additional Statistics Action For vpp-clear-runtime
| | [Documentation]
| | ... | Additional Statistics Action for clear VPP runtime.
| |
| | VPP Clear Runtime On All DUTs | ${nodes}

| Additional Statistics Action For vpp-show-runtime
| | [Documentation]
| | ... | Additional Statistics Action for show VPP runtime.
| |
| | VPP Show Runtime On All DUTs | ${nodes}

| Additional Statistics Action For vpp-enable-packettrace
| | [Documentation]
| | ... | Additional Statistics Action for enable VPP packet trace.
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | VPP Enable Traces On All DUTs | ${nodes} | fail_on_error=${False}

| Additional Statistics Action For vpp-show-packettrace
| | [Documentation]
| | ... | Additional Statistics Action for show VPP packet trace.
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | Show Packet Trace On All Duts | ${nodes} | maximum=${100}

| Additional Statistics Action For vpp-enable-elog
| | [Documentation]
| | ... | Additional Statistics Action for enable VPP elog trace.
| |
| | VPP Enable Elog Traces On All DUTs | ${nodes}

| Additional Statistics Action For vpp-show-elog
| | [Documentation]
| | ... | Additional Statistics Action for show VPP elog trace.
| |
| | Show Event Logger On All DUTs | ${nodes}

| Additional Statistics Action For bash-perf-stat
| | [Documentation]
| | ... | Additional Statistics Action for bash command "perf stat".
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | Perf Stat On All DUTs | ${nodes} | cpu_list=${cpu_alloc_str}

| Additional Statistics Action For clear-show-runtime-with-traffic
| | [Documentation]
| | ... | Additional Statistics Action for clear and show runtime counters with
| | ... | running traffic.
| |
| | Clear and show runtime counters with running traffic
| | ... | ${trial_duration} | ${rate}
| | ... | ${frame_size} | ${traffic_profile} | ${traffic_directions}
| | ... | ${tx_port} | ${rx_port}

| Additional Statistics Action For noop
| | [Documentation]
| | ... | Additional Statistics Action for no operation.
| |
| | No operation
