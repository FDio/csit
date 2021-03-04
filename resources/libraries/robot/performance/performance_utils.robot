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
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${runtime_duration} = | Get Runtime Duration
| | ${runtime_rate} = | Get Runtime Rate
| | ${traffic_directions} = | Get Traffic Directions
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
| | ... | async_call=${True}
| | ... | ppta=${ppta}
| | ... | use_latency=${use_latency}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | duration_limit=${0.0}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
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
| | ... | Input rates are unidirectional, in transaction per second.
| | ... | Reported result may contain aggregate pps rates, depending on test.
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
| | ${min_rate_soft} = | Get Min Rate Soft
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${resetter} = | Get Resetter
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | ${average} | ${stdev} = | Perform soak search
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | minimum_transmit_rate=${min_rate_soft}
| | ... | maximum_transmit_rate=${max_rate}
| | ... | plr_target=${1e-7}
| | ... | tdpt=${0.1}
| | ... | initial_count=${50}
| | ... | ppta=${ppta}
| | ... | resetter=${resetter}
| | ... | timeout=${1800.0}
| | ... | trace_enabled=${False}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${use_latency}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | ${lower} | ${upper} = | Display result of soak search
| | ... | ${average} | ${stdev}
| | Set Test Variable | \${rate for teardown} | ${lower}
| | Should Not Be True | 1.1 * ${min_rate_soft} > ${lower}
| | ... | Lower bound ${lower} too small for unidir minimum ${min_rate_soft}.

| Find NDR and PDR intervals using optimized search
| | [Documentation]
| | ... | Find boundaries for RFC2544 compatible NDR and PDR values
| | ... | using an optimized search algorithm.
| | ... | Display findings as a formatted test message.
| | ... | Fail if a resulting lower bound has too high loss fraction.
| | ... | Input rates are unidirectional, in transaction per second.
| | ... | Reported result may contain aggregate pps rates, depending on test.
| | ... | Additional latency measurements are performed for smaller loads,
| | ... | even if latency stream is disabled in search. Their results
| | ... | are also displayed.
| | ... | Finally, two measurements for runtime stats are done (not displayed).
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated maximal unidirectional transmit rate [tps].
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
| | ${min_rate_soft} = | Get Min Rate Soft
| | # \${packet_loss_ratio} is used twice so it is worth a variable.
| | ${packet_loss_ratio} = | Get Packet Loss Ratio
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${resetter} = | Get Resetter
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | ${result} = | Perform optimized ndrpdr search
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | minimum_transmit_rate=${min_rate_soft}
| | ... | maximum_transmit_rate=${max_rate}
| | ... | packet_loss_ratio=${packet_loss_ratio}
| | ... | final_relative_width=${0.005}
| | ... | final_trial_duration=${30.0}
| | ... | initial_trial_duration=${1.0}
| | ... | number_of_intermediate_phases=${2}
| | ... | timeout=${720.0}
| | ... | doublings=${2}
| | ... | ppta=${ppta}
| | ... | resetter=${resetter}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${use_latency}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | Display result of NDRPDR search | ${result}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${packet_loss_ratio}
| | Check NDRPDR interval validity | ${result.ndr_interval}
| | ${pdr} = | Set Variable | ${result.pdr_interval.measured_low.target_tr}
| | ${ndr} = | Set Variable | ${result.ndr_interval.measured_low.target_tr}
| | # We expect NDR and PDR to have different-looking stats.
| | Send traffic at specified rate
| | ... | rate=${pdr}
| | ... | trial_duration=${1.0}
| | ... | trial_multiplicity=${1}
| | ... | use_latency=${use_latency}
| | ... | duration_limit=${1.0}
| | Run Keyword If | ${ndr} != ${pdr}
| | ... | Send traffic at specified rate
| | ... | rate=${ndr}
| | ... | trial_duration=${1.0}
| | ... | trial_multiplicity=${1}
| | ... | use_latency=${use_latency}
| | ... | duration_limit=${1.0}
| | Return From Keyword If | ${disable_latency}
| | ${rate} = | Evaluate | 0.9 * ${pdr}
| | Measure and show latency at specified rate | Latency at 90% PDR: | ${rate}
| | ${rate} = | Evaluate | 0.5 * ${pdr}
| | Measure and show latency at specified rate | Latency at 50% PDR: | ${rate}
| | ${rate} = | Evaluate | 0.1 * ${pdr}
| | Measure and show latency at specified rate | Latency at 10% PDR: | ${rate}
| | Measure and show latency at specified rate | Latency at 0% PDR: | ${0.0}

| Find Throughput Using MLRsearch
| | [Documentation]
| | ... | Find and return lower bound NDR (zero PLR)
| | ... | throughput using MLRsearch algorithm.
| | ... | Input and output rates are understood as uni-directional, in tps.
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - traffic_profile - Name of module defining traffc for measurements.
| | ... | Type: string
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - max_rate - Calculated maximal unidirectional transmit rate [tps].
| | ... | Type: float
| | ... | - resetter - Callable to reset DUT state before each trial.
| | ... | - transaction_scale - Number of ASTF transaction (zero if unlimited).
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| |
| | ... | *Returns:*
| | ... | - Lower bound for uni-directional tps throughput at given PLR.
| | ... | Type: float
| |
| | ... | *Example:*
| |
| | ... | \| \${throughpt}= \| Find Throughput Using MLRsearch \|
| |
| | ${max_rate} = | Get Max Rate
| | ${min_rate_soft} = | Get Min Rate Soft
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${resetter} = | Get Resetter
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | ${result} = | Perform optimized ndrpdr search
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | minimum_transmit_rate=${min_rate_soft}
| | ... | maximum_transmit_rate=${max_rate}
| | ... | packet_loss_ratio=${0.0}
| | ... | final_relative_width=${0.001}
| | ... | final_trial_duration=${10.0}
| | ... | initial_trial_duration=${1.0}
| | ... | number_of_intermediate_phases=${1}
| | ... | timeout=${720}
| | ... | doublings=${2}
| | ... | ppta=${ppta}
| | ... | resetter=${resetter}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${use_latency}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${0.0}
| | Return From Keyword | ${result.pdr_interval.measured_low.target_tr}

| Measure and show latency at specified rate
| | [Documentation]
| | ... | Send traffic at specified rate, single trial.
| | ... | Extract latency information and append it to text message.
| | ... | The rate argument is float, so should not include "pps".
| | ... | If the given rate is too low, a safe value is used instead.
| | ... | Call \${resetter} (if defined) to reset DUT state before each trial.
| |
| | ... | *Arguments:*
| | ... | - message_prefix - Preface to test message addition. Type: string
| | ... | - rate - Unidirectional rate [tps] for sending packets.
| | ... | Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Measure and show latency at specified rate \| Latency at 90% NDR \
| | ... | \| ${10000000} \|
| |
| | [Arguments] | ${message_prefix} | ${rate}
| |
| | ${min_rate_hard} = | Get Min Rate Hard
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${real_rate} = | Evaluate | max(${rate}, ${min_rate_hard})
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | Call Resetter
| | Send traffic on tg
| | ... | duration=${PERF_TRIAL_LATENCY_DURATION}
| | ... | rate=${real_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | async_call=${False}
| | ... | duration_limit=${PERF_TRIAL_LATENCY_DURATION}
| | ... | ppta=${ppta}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${True}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | ${latency} = | Get Latency Int
| | Set Test Message | ${\n}${message_prefix} ${latency} | append=${True}

| Send ramp-up traffic
| | [Documentation]
| | ... | Fail unless positive ramp-up rate is specified.
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
| | ... | - ramp_up_rate - Suitable unidirectional transmit rate [tps].
| | ... | Type: float
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| |
| | ... | *Example:*
| |
| | ... | \| Send ramp-up traffic \|
| |
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | Run Keyword Unless | ${ramp_up_rate} > 0.0 | Fail | Ramp up rate missing!
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | Send traffic on tg
| | ... | duration=${ramp_up_duration}
| | ... | rate=${ramp_up_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | async_call=${False}
| | ... | duration_limit=${0.0}
| | ... | ppta=${ppta}
| | ... | use_latency=${use_latency}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | ... | ramp_up_only=${True}

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
| | ... | - rate - Target unidirectional transmit rate [tps]. Type: float
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
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${traffic_directions} = | Get Traffic Directions
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
| | | ${delay} = | Evaluate | (${i} - 5) / 100
| | | ${result} = | Send traffic on tg
| | | ... | duration=${trial_duration}
| | | ... | rate=${rate}
| | | ... | frame_size=${frame_size}
| | | ... | traffic_profile=${traffic_profile}
| | | ... | async_call=${False}
| | | ... | duration_limit=${duration_limit}
| | | ... | ppta=${ppta}
| | | ... | traffic_directions=${traffic_directions}
| | | ... | transaction_duration=${transaction_duration}
| | | ... | transaction_scale=${transaction_scale}
| | | ... | transaction_type=${transaction_type}
| | | ... | use_latency=${use_latency}
| | | ... | ramp_up_duration=${ramp_up_duration}
| | | ... | ramp_up_rate=${ramp_up_rate}
| | | ... | delay=${delay}
| | | # Out of several quantities for aborted traffic (duration stretching),
| | | # the approximated receive rate is the best estimate we have.
| | | Append To List | ${results} | ${result.approximated_receive_rate}
| | | Log To Console | Delay: ${delay}, unsent: ${result.unsent}
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
| | ... | - rate - Unidirectional rate [tps] for sending packets.
| | ... | Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Start Traffic on Background \| ${4000000.0} \|
| |
| | [Arguments] | ${rate}
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${traffic_directions} = | Get Traffic Directions
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
| | ... | async_call=${True}
| | ... | duration_limit=${0.0}
| | ... | ppta=${ppta}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | use_latency=${use_latency}
| | # TODO: Ramp-up?

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
| | ... | - max_rate - Calculated maximal transmit rate [tps].
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
| | ${unit} = | Set Variable If | """_cps""" in """${transaction_type}"""
| | ... | estimated connections per second | packets per second
| | Set Test Message | ${\n}Maximum Receive Rate trial results
| | Set Test Message | in ${unit}: ${results}
| | ... | append=yes
| | Fail if no traffic forwarded
