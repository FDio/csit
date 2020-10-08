# Copyright (c) 2020 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.TrafficGenerator.OptimizedSearch
| Library | resources.libraries.python.TrafficGenerator.TGDropRateSearchImpl
| Library | resources.libraries.python.Trace
| Variables | resources/libraries/python/Constants.py
| Resource | resources/libraries/robot/performance/performance_actions.robot
| Resource | resources/libraries/robot/performance/performance_display.robot
| Resource | resources/libraries/robot/performance/performance_vars.robot
|
| Documentation
| ... | Performance suite keywords - utilities to find and verify NDR and PDR.
| ... | See performance_vars.robot for values accessed via there.

*** Variables ***
| # Variable holding multiplicator of main heap size. By default it is set to 1
| # that means the main heap size will be set to 2G. Some tests may require more
| # memory for IP FIB (e.g. nat44det tests with 4M or 16M sessions).
| ${heap_size_mult}= | ${1}

*** Keywords ***
| Clear and show runtime counters with running traffic
| | [Documentation]
| | ... | Start traffic at specified rate then clear runtime counters on all
| | ... | DUTs. Wait for specified amount of time and capture runtime counters
| | ... | on all DUTs. Finally stop traffic.
| |
| | ... | TODO: Support resetter if this is not the first trial-ish action?
| |
| | ... | *Example:*
| |
| | ... | \| Clear and show runtime counters with running traffic \|
| |
| | ${runtime_duration} = | Get Runtime Duration
| | ${runtime_rate} = | Get Runtime Rate
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_directions} = | Get Transaction Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | # Duration of -1 means we will stop traffic manually.
| | Send traffic on tg
| | ... | duration=${-1}
| | ... | rate=${runtime_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | warmup_time=${0}
| | ... | async_call=${True}
| | ... | use_latency=${use_latency}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_directions=${transaction_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | duration_limit=${0.0}
| | FOR | ${action} | IN | @{pre_run_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Sleep | ${runtime_duration}
| | FOR | ${action} | IN | @{post_run_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Stop traffic on tg

| Find critical load using PLRsearch
| | [Documentation]
| | ... | Find boundaries for troughput (of hardcoded target loss ratio)
| | ... | using PLRsearch algorithm.
| | ... | Display results as formatted test message.
| | ... | Fail if computed lower bound is 110% of the minimal rate or less.
| | ... | Input rates are understood as uni-directional,
| | ... | reported result contains aggregate rates.
| | ... | Currently, the min_rate value is hardcoded to match test teardowns.
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Find critical load using PLR search \|
| |
| | # Get values via performance_vars.
| | ${max_rate} = | Get Max Rate
| | ${min_rate} = | Get Min Rate
| | ${resetter} = | Get Resetter
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_directions} = | Get Transaction Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | ${average} | ${stdev} = | Perform soak search
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | minimum_transmit_rate=${min_rate}
| | ... | maximum_transmit_rate=${max_rate}
| | ... | plr_target=${1e-7}
| | ... | tdpt=${0.1}
| | ... | initial_count=${50}
| | ... | resetter=${resetter}
| | ... | timeout=${720.0}
| | ... | trace_enabled=${False}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_directions=${transaction_directions}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${use_latency}
| | ${lower} | ${upper} = | Display result of soak search
| | ... | ${average} | ${stdev}
| | Set Test Variable | \${rate for teardown} | ${lower}
| | Should Not Be True | 1.1*${min_rate} > ${lower}
| | ... | Lower bound ${lower} too small for unidirectional minimum ${min_rate}.

| Find NDR and PDR intervals using optimized search
| | [Documentation]
| | ... | Find boundaries for RFC2544 compatible NDR and PDR values
| | ... | using an optimized search algorithm.
| | ... | Display findings as a formatted test message.
| | ... | Fail if a resulting lower bound has too high loss fraction.
| | ... | Input rates are understood as uni-directional,
| | ... | reported result contains aggregate rates.
| | ... | Additional latency measurements are performed for smaller loads,
| | ... | even if latency stream is disabled in search. Their results
| | ... | are also displayed.
| | ... | Finally, two measurements for runtime stats are done (not displayed).
| | ... | Currently, the min_rate value is hardcoded to 90kpps,
| | ... | allowing measurement at 10% of the discovered rate
| | ... | without breaking latency streams.
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| | ... | - resetter - Callable to reset DUT state before each trial.
| | ... | - transaction_scale - Number of ASTF transaction (zero if unlimited).
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| | ... | - disable_latency - If true, skip anything related to latency.
| | ... | Useful if transaction_scale is high and TPS is low. Default: false.
| |
| | ... | *Example:*
| |
| | ... | \| Find NDR and PDR intervals using optimized search \|
| |
| | # Get values via performance_vars.
| | ${disable_latency} = | Get Disable Latency
| | ${max_rate} = | Get Max Rate
| | ${min_rate} = | Get Min Rate
| | # \${packet_loss_ratio} is used twice so it is worth a variable.
| | ${packet_loss_ratio} = | Get Packet Loss Ratio
| | ${resetter} = | Get Resetter
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_directions} = | Get Transaction Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | ${result} = | Perform optimized ndrpdr search
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | minimum_transmit_rate=${min_rate}
| | ... | maximum_transmit_rate=${max_rate}
| | ... | packet_loss_ratio=${packet_loss_ratio}
| | ... | final_relative_width=${0.005}
| | ... | final_trial_duration=${30.0}
| | ... | initial_trial_duration=${1.0}
| | ... | number_of_intermediate_phases=${2}
| | ... | timeout=${720.0}
| | ... | doublings=${2}
| | ... | resetter=${resetter}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_directions=${transaction_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${use_latency}
| | Display result of NDRPDR search | ${result}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${packet_loss_ratio}
| | Check NDRPDR interval validity | ${result.ndr_interval}
| | ${pdr_sum} = | Set Variable | ${result.pdr_interval.measured_low.target_tr}
| | ${pdr_per_dir} = | Evaluate | ${pdr_sum} / float(${transaction_directions})
| | ${ndr_sum} = | Set Variable | ${result.ndr_interval.measured_low.target_tr}
| | ${ndr_per_dir} = | Evaluate | ${ndr_sum} / float(${transaction_directions})
| | # We expect NDR and PDR to have different-looking stats.
| | Send traffic at specified rate
| | ... | rate=${pdr_per_dir}
| | ... | trial_duration=${1.0}
| | ... | trial_multiplicity=${1}
| | ... | use_latency=${use_latency}
| | ... | duration_limit=${1.0}
| | Run Keyword If | $ndr_per_dir != $pdr_per_dir
| | ... | Send traffic at specified rate
| | ... | rate=${ndr_per_dir}
| | ... | trial_duration=${1.0}
| | ... | trial_multiplicity=${1}
| | ... | use_latency=${use_latency}
| | ... | duration_limit=${1.0}
| | Return From Keyword If | ${disable_latency}
| | ${rate} = | Evaluate | 0.9 * ${pdr_per_dir}
| | Measure and show latency at specified rate | Latency at 90% PDR: | ${rate}
| | ${rate} = | Evaluate | 0.5 * ${pdr_per_dir}
| | Measure and show latency at specified rate | Latency at 50% PDR: | ${rate}
| | ${rate} = | Evaluate | 0.1 * ${pdr_per_dir}
| | Measure and show latency at specified rate | Latency at 10% PDR: | ${rate}
| | Measure and show latency at specified rate | Latency at 0% PDR: | ${0.0}

| Find Throughput Using MLRsearch
| | [Documentation]
| | ... | Find and return lower bound NDR (zero PLR)
| | ... | aggregate throughput using MLRsearch algorithm.
| | ... | Input rates are understood as uni-directional.
| | ... | Currently, the min_rate value is hardcoded to match test teardowns.
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| | ... | - resetter - Callable to reset DUT state before each trial.
| | ... | - transaction_scale - Number of ASTF transaction (zero if unlimited).
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| |
| | ... | *Returns:*
| | ... | - Lower bound for bi-directional throughput at given PLR. Type: float
| |
| | ... | *Example:*
| |
| | ... | \| \${throughpt}= \| Find Throughput Using MLRsearch \|
| |
| | ${max_rate} = | Get Max Rate
| | ${min_rate} = | Get Min Rate
| | ${resetter} = | Get Resetter
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_directions} = | Get Transaction Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | ${result} = | Perform optimized ndrpdr search
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | minimum_transmit_rate=${min_rate}
| | ... | maximum_transmit_rate=${max_rate}
| | ... | packet_loss_ratio=${0.0}
| | ... | final_relative_width=${0.001}
| | ... | final_trial_duration=${10.0}
| | ... | initial_trial_duration=${1.0}
| | ... | number_of_intermediate_phases=${1}
| | ... | timeout=${720}
| | ... | doublings=${2}
| | ... | resetter=${resetter}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_directions=${transaction_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${use_latency}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${0.0}
| | Return From Keyword | ${result.pdr_interval.measured_low.target_tr}

| Measure and show latency at specified rate
| | [Documentation]
| | ... | Send traffic at specified rate, single trial.
| | ... | Extract latency information and append it to text message.
| | ... | The rate argument is int, so should not include "pps".
| | ... | If the given rate is too low, a safe value is used instead.
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| |
| | ... | *Arguments:*
| | ... | - message_prefix - Preface to test message addition. Type: string
| | ... | - rate - Rate [pps] for sending packets in case of T-Rex stateless
| | ... | mode or multiplier of profile CPS in case of T-Rex astf mode.
| | ... | Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Measure and show latency at specified rate \| Latency at 90% NDR \
| | ... | \| ${10000000} \|
| |
| | [Arguments] | ${message_prefix} | ${rate}
| |
| | ${min_rate} = | Get Min Rate
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_directions} = | Get Transaction Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${real_rate} = | Evaluate | max(${rate}, ${min_rate})
| | Call Resetter
| | Send traffic on tg
| | ... | duration=${PERF_TRIAL_LATENCY_DURATION}
| | ... | rate=${real_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | warmup_time=${0.0}
| | ... | async_call=${False}
| | ... | duration_limit=${PERF_TRIAL_LATENCY_DURATION}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_directions=${transaction_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${True}
| | ${latency} = | Get Latency Int
| | Set Test Message | ${\n}${message_prefix} ${latency} | append=${True}

| Send ramp-up traffic
| | [Documentation]
| | ... | Do nothing unless positive ramp-up duration is specified.
| | ... | Else perform one trial with appropriate rate and duration.
| | ... | This is useful for tests that set DUT state via traffic.
| | ... | Rate has to bee low enough so packets are not lost,
| | ... | Duration has to be long enough to set all the state.
| | ... | The trial results are discarded.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffic for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - ramp_up_duration - Suitable traffic duration [s].
| | ... | Type: float
| | ... | - ramp_up_rate - Suitable unidirectional transmit rate [pps].
| | ... | Type: float
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| |
| | ... | *Example:*
| |
| | ... | \| Send ramp-up traffic \|
| |
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | Run Keyword Unless | ${ramp_up_duration} > 0.0 | Return From Keyword
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_directions} = | Get Transaction Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | Send traffic on tg
| | ... | duration=${ramp_up_duration}
| | ... | rate=${ramp_up_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | warmup_time=${0}
| | ... | async_call=${False}
| | ... | use_latency=${use_latency}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_directions=${transaction_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | duration_limit=${0.0}

| Send traffic at specified rate
| | [Documentation]
| | ... | Perform a warmup, show runtime counters during it.
| | ... | Then send traffic at specified rate, possibly multiple trials.
| | ... | Show various DUT stats, optionally also packet trace.
| | ... | Return list of measured receive rates.
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| |
| | ... | *Arguments:*
| | ... | - trial_duration - Duration of single trial [s]. Type: float
| | ... | - rate - Target aggregate transmit rate [pps] / Connections per second
| | ... | (CPS) for UDP/TCP flows. Type: float
| | ... | Type: string
| | ... | - trial_multiplicity - How many trials in this measurement.
| | ... | Type: boolean
| | ... | - use_latency - Use latency stream in search; default value: False.
| | ... | Type: boolean
| | ... | - duration_limit - Hard limit for trial duration, overriding duration
| | ... | computed from transaction_scale. Default 0.0 means no limit.
| |
| | ... | *Example:*
| |
| | ... | \| Send traffic at specified rate \| \${1.0} \| ${4000000.0} \
| | ... | \| \${10} \| ${False} \| ${1.0} \|
| |
| | [Arguments] | ${trial_duration} | ${rate} | ${trial_multiplicity}
| | ... | ${use_latency}=${False} | ${duration_limit}=${0.0}
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_directions} = | Get Transaction Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | Set Test Variable | \${rate_for_teardown} | ${rate}
| | FOR | ${action} | IN | @{pre_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | ${results} = | Create List
| | FOR | ${i} | IN RANGE | ${trial_multiplicity}
| | | Call Resetter
| | | Send traffic on tg
| | | ... | duration=${trial_duration}
| | | ... | rate=${rate}
| | | ... | frame_size=${frame_size}
| | | ... | traffic_profile=${traffic_profile}
| | | ... | warmup_time=${0}
| | | ... | async_call=${False}
| | | ... | duration_limit=0.0
| | | ... | traffic_directions=${traffic_directions}
| | | ... | transaction_directions=${transaction_directions}
| | | ... | transaction_duration=${transaction_duration}
| | | ... | transaction_scale=${transaction_scale}
| | | ... | transaction_type=${transaction_type}
| | | ... | use_latency=${use_latency}
| | | ${result}= | Get Measurement Result
| | | # Approximated rate is good if duration is good.
| | | # But for small scale CPS MRR tests, the traffic is way shorter than 1s,
| | | # and the profile waits for retransmits do not happen within duration.
| | | # Thus, approx rate is too low in that case. At least logging it here.
| | | Log | ${result.approximated_receive_rate}
| | | # Partial receive rate gives bad results at big duration stretching,
| | | # but profile driver should have stopped the measurement soon enough.
| | | # For extreme cases (CPS MRR) this gives the more reasonable estimate.
| | | ${receive_rate} = | Set Variable  | ${result.partial_receive_rate}
| | | # For UDP_PPS, the output unit does not match input unit,
| | | # and it is easier to convert here than in the parent keyword.
| | | ${converted_receive_rate} = | Evaluate | ${receive_rate} * ${ppta}
| | | ${receive_rate} = | Set Variable If | "_pps" in "${transaction_type}"
| | | ... | ${converted_receive_rate} | ${receive_rate}
| | | # Experimenting with possible outputs, only log the previous one.
| | | Log | ${receive_rate}
| | | Append To List | ${results} | ${result.receive_rate}
| | END
| | FOR | ${action} | IN | @{post_stats}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Return From Keyword | ${results}

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
| |
| | ... | *Example:*
| |
| | ... | \| Start Traffic on Background \| ${4000000.0} \|
| |
| | [Arguments] | ${rate}
| |
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_directions} = | Get Transaction Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | Call Resetter
| | # Duration of -1 means we will stop traffic manually.
| | Send traffic on tg
| | ... | duration=${-1}
| | ... | rate=${rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | warmup_time=${0.0}
| | ... | async_call=${True}
| | ... | duration_limit=${0.0}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_directions=${transaction_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${use_latency}

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

| Traffic should pass with maximum rate
| | [Documentation]
| | ... | Send traffic at maximum rate.
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| | ... | Fail if no packets were forwarded.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffic for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| |
| | ... | *Example:*
| |
| | ... | \| Traffic should pass with maximum rate \|
| |
| | ${max_rate} = | Get Max Rate
| | ${transaction_type} = | Get Transaction Type
| | ${trial_duration} = | Get Mrr Trial Duration
| | ${trial_multiplicity} = | Get Mrr Trial Multiplicity
| | ${use_latency} = | Get Use Latency
| | # The following also sets \${rate_for_teardown}
| | ${results} = | Send traffic at specified rate
| | ... | rate=${max_rate}
| | ... | trial_duration=${trial_duration}
| | ... | trial_multiplicity=${trial_multiplicity}
| | ... | use_latency=${use_latency}
| | ... | duration_limit=${0.0}
| | ${unit} = | Set Variable If | """${transaction_type}""" == """packet"""
| | ... | packets per second | estimated connections per second
| | Set Test Message | ${\n}Maximum Receive Rate trial results
| | Set Test Message | in ${unit}: ${results}
| | ... | append=yes
| | Fail if no traffic forwarded
