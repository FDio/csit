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
| Variables | resources/libraries/python/Constants.py
|
| Documentation
| ... | Performance suite keywords - utilities to find and verify NDR and PDR.

*** Keywords ***
| Find NDR and PDR intervals using optimized search
| | [Documentation]
| | ... | Find boundaries for RFC2544 compatible NDR and PDR values
| | ... | using an optimized search algorithm.
| | ... | Display findings as a formatted test message.
| | ... | Fail if a resulting lower bound has too high loss fraction.
| | ... | Input rates are understood as uni-directional,
| | ... | reported result contains aggregate rates.
| | ... | Currently, the min_rate value is hardcoded to match test teardowns.
| |
| | ... | TODO: Should the trial duration of the additional
| | ... | measurements be configurable?
| |
| | ... | Some inputs are read from variables to streamline suites.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Arguments:*
| | ... | - packet_loss_ratio - Accepted loss during search. Type: float
| | ... | - final_relative_width - Maximal width multiple of upper. Type: float
| | ... | - final_trial_duration - Duration of final trials [s]. Type: float
| | ... | - initial_trial_duration - Duration of initial trials [s]. Type: float
| | ... | - intermediate phases - Number of intermediate phases [1]. Type: int
| | ... | - timeout - Fail if search duration is longer [s]. Type: float
| | ... | - doublings - How many doublings to do when expanding [1]. Type: int
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
| |
| | ... | *Example:*
| |
| | ... | \| Find NDR and PDR intervals using optimized search \| \${0.005} \
| | ... | \| \${0.005} \| \${30.0} \| \${1.0} \| \${2} \| \${600.0} \| \${2} \
| | ... | \| \${2} \|
| |
| | [Arguments] | ${packet_loss_ratio}=${0.005}
| | ... | ${final_relative_width}=${0.005} | ${final_trial_duration}=${30.0}
| | ... | ${initial_trial_duration}=${1.0}
| | ... | ${number_of_intermediate_phases}=${2} | ${timeout}=${720.0}
| | ... | ${doublings}=${2} | ${traffic_directions}=${2}
| |
| | ${result} = | Perform optimized ndrpdr search | ${frame_size}
| | ... | ${traffic_profile} | ${10000} | ${max_rate}
| | ... | ${packet_loss_ratio} | ${final_relative_width}
| | ... | ${final_trial_duration} | ${initial_trial_duration}
| | ... | ${number_of_intermediate_phases} | timeout=${timeout}
| | ... | doublings=${doublings} | traffic_directions=${traffic_directions}
| | Display result of NDRPDR search | ${result}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${packet_loss_ratio}
| | Check NDRPDR interval validity | ${result.ndr_interval}
| | Perform additional measurements based on NDRPDR result
| | ... | ${result} | ${frame_size} | ${traffic_profile}

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

| Find Throughput Using MLRsearch
| | [Documentation]
| | ... | Find and return lower bound PDR (zero PLR by default)
| | ... | aggregate throughput using MLRsearch algorithm.
| | ... | Input rates are understood as uni-directional.
| | ... | Currently, the min_rate value is hardcoded to match test teardowns.
| |
| | ... | TODO: Should the trial duration of the additional
| | ... | measurements be configurable?
| |
| | ... | Some inputs are read from variables to streamline suites.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Arguments:*
| | ... | - packet_loss_ratio - Accepted loss during search. Type: float
| | ... | - final_relative_width - Maximal width multiple of upper. Type: float
| | ... | - final_trial_duration - Duration of final trials [s]. Type: float
| | ... | - initial_trial_duration - Duration of initial trials [s]. Type: float
| | ... | - intermediate phases - Number of intermediate phases [1]. Type: int
| | ... | - timeout - Fail if search duration is longer [s]. Type: float
| | ... | - doublings - How many doublings to do when expanding [1]. Type: int
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
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
| | ... | ${doublings}=${2} | ${traffic_directions}=${2}
| |
| | ${result} = | Perform optimized ndrpdr search | ${frame_size}
| | ... | ${traffic_profile} | ${10000} | ${max_rate}
| | ... | ${packet_loss_ratio} | ${final_relative_width}
| | ... | ${final_trial_duration} | ${initial_trial_duration}
| | ... | ${number_of_intermediate_phases} | timeout=${timeout}
| | ... | doublings=${doublings} | traffic_directions=${traffic_directions}
| | Return From Keyword | ${result.pdr_interval.measured_low.transmit_rate}

| Find critical load using PLRsearch
| | [Documentation]
| | ... | Find boundaries for troughput (of given target loss ratio)
| | ... | using PLRsearch algorithm.
| | ... | Display results as formatted test message.
| | ... | Fail if computed lower bound is below minimal rate.
| | ... | Input rates are understood as uni-directional,
| | ... | reported result contains aggregate rates.
| | ... | Currently, the min_rate value is hardcoded to match test teardowns.
| | ... | Some inputs are read from variables to streamline suites.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Arguments:*
| | ... | - packet_loss_ratio - Accepted loss during search. Type: float
| | ... | - timeout - Stop when search duration is longer [s]. Type: float
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
| |
| | ... | *Example:*
| |
| | ... | \| Find critical load using PLR search \| \${1e-7} \| \${120} \
| | ... | \| \${2} \|
| |
| | [Arguments] | ${packet_loss_ratio}=${1e-7} | ${timeout}=${1800.0}
| | ... | ${traffic_directions}=${2}
| |
| | ${min_rate} = | Set Variable | ${10000}
| | ${average} | ${stdev} = | Perform soak search | ${frame_size}
| | ... | ${traffic_profile} | ${min_rate} | ${max_rate}
| | ... | ${packet_loss_ratio} | timeout=${timeout}
| | ... | traffic_directions=${traffic_directions}
| | ${lower} | ${upper} = | Display result of soak search
| | ... | ${average} | ${stdev}
| | Should Not Be True | ${lower} < ${min_rate}
| | ... | Lower bound ${lower} is below unidirectional minimum ${min_rate}.

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
| | ... | \| \${64} \| show_latency=\${EMPTY} \|
| |
| | [Arguments] | ${text} | ${rate_total} | ${frame_size} | ${latency}=${EMPTY}
| |
| | ${bandwidth_total} = | Evaluate | ${rate_total} * (${frame_size}+20)*8 / 1e9
| | Set Test Message | ${\n}${text}: ${rate_total} pps, | append=yes
| | Set Test Message | ${bandwidth_total} Gbps (initial) | append=yes
| | Return From Keyword If | not """${latency}"""
| | Set Test Message | ${\n}LATENCY [min/avg/max/hdrh] per stream: ${latency}
| | ... | append=yes

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
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
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
| | ... | ${result.ndr_interval.measured_low.transmit_rate} | ${frame_size}
| | ... | ${result.ndr_interval.measured_low.latency}
| | Display single bound | NDR_UPPER
| | ... | ${result.ndr_interval.measured_high.transmit_rate} | ${frame_size}
| | Display single bound | PDR_LOWER
| | ... | ${result.pdr_interval.measured_low.transmit_rate} | ${frame_size}
| | ... | ${result.pdr_interval.measured_low.latency}
| | Display single bound | PDR_UPPER
| | ... | ${result.pdr_interval.measured_high.transmit_rate} | ${frame_size}

| Display result of soak search
| | [Documentation]
| | ... | Display result of soak search, avg+-stdev, as upper/lower bounds,
| | ... | in aggregate packets per seconds
| | ... | and Gbps total bandwidth (for initial packet size).
| | ... | Througput is calculated as:
| | ... | Sum of measured rates over streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8)
| | ... | TODO: Do we want to report some latency data,
| | ... | even if not measured at the reported bounds?.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
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

| Perform additional measurements based on NDRPDR result
| | [Documentation]
| | ... | Perform any additional measurements which are not directly needed
| | ... | for determining NDR nor PDR, but which are needed for gathering
| | ... | additional data for debug purposes.
| | ... | Currently, just "Traffic should pass with no loss" is called.
| | ... | TODO: Move latency measurements from optimized search here.
| |
| | ... | *Arguments:*
| | ... | - result - Measured result data per stream [pps]. Type: NdrPdrResult
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | - traffic_profile - Topology profile. Type: string
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
| |
| | ... | *Example:*
| | ... | \| Perform additional measurements based on NDRPDR result \
| | ... | \| \${result} \| \${64} \| 3-node-IPv4 \| \${2} \|
| |
| | [Arguments] | ${result} | ${framesize} | ${traffic_profile}
| | ... | ${traffic_directions}=${2}
| |
| | ${duration}= | Set Variable | ${2.0}
| | ${rate_sum}= | Set Variable | ${result.ndr_interval.measured_low.target_tr}
| | ${rate_per_stream}= | Evaluate | ${rate_sum} / float(${traffic_directions})
| | Traffic should pass with no loss | ${duration} | ${rate_per_stream}pps
| | ... | ${framesize} | ${traffic_profile} | fail_on_loss=${False}
| | ... | traffic_directions=${traffic_directions}

| Traffic should pass with no loss
| | [Documentation]
| | ... | Send traffic at specified rate. No packet loss is accepted at loss
| | ... | evaluation.
| |
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - fail_on_loss - If True, the keyword fails if loss occurred.
| | ... | Type: boolean
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
| |
| | ... | *Example:*
| |
| | ... | \| Traffic should pass with no loss \| \${10} \| 4.0mpps \| \${64} \
| | ... | \| 3-node-IPv4 \| \${2} \|
| |
| | [Arguments] | ${duration} | ${rate} | ${frame_size} | ${traffic_profile}
| | ... | ${fail_on_loss}=${True} | ${traffic_directions}=${2}
| |
| | Send traffic at specified rate | ${duration} | ${rate} | ${frame_size}
| | ... | ${traffic_profile} | traffic_directions=${traffic_directions}
| | Run Keyword If | ${fail_on_loss} | No traffic loss occurred

| Traffic should pass with maximum rate
| | [Documentation]
| | ... | Send traffic at maximum rate.
| |
| | ... | Some inputs are read from variables to streamline suites.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Arguments:*
| | ... | - subsamples - How many trials in this measurement. Type: int
| | ... | - trial_duration - Duration of single trial [s]. Type: float
| | ... | - fail_no_traffic - Whether to fail on zero receive count. Type: boolean
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
| | ... | - tx_port - TX port of TG, default 0. Type: integer
| | ... | - rx_port - RX port of TG, default 1. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Traffic should pass with maximum rate \| \${1} \| \${10.0} \
| | ... | \| \${False} \| \${2} \| \${0} \| \${1} \|
| |
| | [Arguments] | ${trial_duration}=${PERF_TRIAL_DURATION}
| | ... | ${fail_no_traffic}=${True} | ${subsamples}=${PERF_TRIAL_MULTIPLICITY}
| | ... | ${traffic_directions}=${2} | ${tx_port}=${0} | ${rx_port}=${1}
| |
| | ${results} = | Send traffic at specified rate | ${trial_duration}
| | ... | ${max_rate}pps | ${frame_size} | ${traffic_profile} | ${subsamples}
| | ... | ${traffic_directions} | ${tx_port} | ${rx_port}
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
| | ... | The rate argument should be TRex friendly, so it should include "pps".
| |
| | ... | *Arguments:*
| | ... | - trial_duration - Duration of single trial [s]. Type: float
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - frame_size - L2 Frame Size [B]. Type: integer/string
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - subsamples - How many trials in this measurement. Type: int
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
| | ... | - tx_port - TX port of TG, default 0. Type: integer
| | ... | - rx_port - RX port of TG, default 1. Type: integer
| | ... | - pkt_trace - True to enable packet trace. Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Send traffic at specified rate \| \${1.0} \| 4.0mpps \| \${64} \
| | ... | \| 3-node-IPv4 \| \${10} \| \${2} \| \${0} | \${1} \| \${False}
| |
| | [Arguments] | ${trial_duration} | ${rate} | ${frame_size}
| | ... | ${traffic_profile} | ${subsamples}=${1} | ${traffic_directions}=${2}
| | ... | ${tx_port}=${0} | ${rx_port}=${1} | ${pkt_trace}=${False}
| |
| | Clear and show runtime counters with running traffic | ${trial_duration}
| | ... | ${rate} | ${frame_size} | ${traffic_profile}
| | ... | ${traffic_directions} | ${tx_port} | ${rx_port}
| | Run Keyword If | ${dut_stats}==${True}
| | ... | Clear statistics on all DUTs | ${nodes}
| | Run Keyword If | ${dut_stats}==${True} and ${pkt_trace}==${True}
| | ... | VPP Enable Traces On All DUTs | ${nodes} | fail_on_error=${False}
| | Run Keyword If | ${dut_stats}==${True}
| | ... | VPP enable elog traces on all DUTs | ${nodes}
| | ${results} = | Create List
| | FOR | ${i} | IN RANGE | ${subsamples}
| | | # The following line is skipping some default arguments,
| | | # that is why subsequent arguments have to be named.
| | | Send traffic on tg | ${trial_duration} | ${rate} | ${frame_size}
| | | ... | ${traffic_profile} | warmup_time=${0}
| | | ... | traffic_directions=${traffic_directions} | tx_port=${tx_port}
| | | ... | rx_port=${rx_port}
| | | ${rx} = | Get Received
| | | ${rr} = | Evaluate | ${rx} / ${trial_duration}
| | | Append To List | ${results} | ${rr}
| | END
| | Run Keyword If | ${dut_stats}==${True} | Show event logger on all DUTs
| | ... | ${nodes}
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
| |
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Unidirectional rate for sending packets. Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
| | ... | - tx_port - TX port of TG, default 0. Type: integer
| | ... | - rx_port - RX port of TG, default 1. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Clear and show runtime counters with running traffic \| \${10} \
| | ... | \| 4.0mpps \| \${64} \| 3-node-IPv4 \| \${2} \| \${0} \| \${1} \|
| |
| | [Arguments] | ${duration} | ${rate} | ${frame_size} | ${traffic_profile}
| | ... | ${traffic_directions}=${2} | ${tx_port}=${0} | ${rx_port}=${1}
| |
| | # Duration of -1 means we will stop traffic manually.
| | Send traffic on tg | ${-1} | ${rate} | ${frame_size} | ${traffic_profile}
| | ... | warmup_time=${0} | async_call=${True} | latency=${False}
| | ... | traffic_directions=${traffic_directions} | tx_port=${tx_port}
| | ... | rx_port=${rx_port}
| | Run Keyword If | ${dut_stats}==${True}
| | ... | VPP clear runtime counters on all DUTs | ${nodes}
| | Sleep | ${duration}
| | Run Keyword If | ${dut_stats}==${True}
| | ... | VPP show runtime counters on all DUTs | ${nodes}
| | Stop traffic on tg

| Start Traffic on Background
| | [Documentation]
| | ... | Start traffic at specified rate then return control to Robot.
| |
| | ... | This keyword is useful if the test needs to do something
| | ... | while traffic is running.
| | ... | Just a wrapper around L1 keyword.
| | ... |
| | ... | TODO: How to make sure the traffic is stopped on any failure?
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | *Arguments:*
| | ... | - rate - Unidirectional rate for sending packets. Type: string
| | ... | - traffic_directions - Bi- (2) or uni- (1) directional traffic.
| | ... | Type: int
| | ... | - tx_port - TX port of TG, default 0. Type: integer
| | ... | - rx_port - RX port of TG, default 1. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Start Traffic on Background \| 4.0mpps \| \${2} \| \${0} \
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
| | ... | Just a wrapper around L1 keyword.
| | ... |
| | ... | TODO: Tolerate if traffic was not started.
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
