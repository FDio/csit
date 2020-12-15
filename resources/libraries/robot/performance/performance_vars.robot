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
| Documentation | Performance suite keywords - Handling of various values
| ... | to allow autodetection, computation and overriding by suite variables.
| Library | Collections
| Variables | ${CURDIR}/../../python/Constants.py

*** Variables ***
| ${extended_debug}= | ${EXTENDED_DEBUG}

*** Keywords ***
| Get Disable Latency
| | [Documentation]
| | ... | If Get Use Latency returns true, return false.
| | ... | Otherwise return value of \${disable_latency} variable,
| | ... | or \${False} if not defined.
| |
| | ... | The return value controls whether latency trials in NDRPDR tests
| | ... | are executed. For example, ASTF tests do not support latency
| | ... | measurements yet, so executing the trials just wastes time.
| | ... | Return type: bool.
| |
| | ... | *Example:*
| |
| | ... | \| \${disable_latency} = \| Get Disable Latency \|
| |
| | ${use_latency} = | Get Use Latency
| | Return From Keyword If | ${use_latency} | ${False}
| | ${disable_latency} = | Get Variable Value | \${disable_latency} | ${False}
| | Return From Keyword | ${disable_latency}

| Get Max Rate
| | [Documentation]
| | ... | Return value of \${max_rate} variable,
| | ... | fail if it is not defined.
| | ... | Call this just before calling a Python keyword,
| | ... | as those have restricted access to Robot variables.
| |
| | ... | The return value controls the maximal unidirectional packet rate.
| | ... | The value is also usable for minimal TPS value for ASTF tests.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${max_rate} = \| Get Max Rate \|
| |
| | ${max_rate} = | Get Variable Value | \${max_rate} | ${0.0}
| | Return From Keyword If | ${max_rate} | ${max_rate}
| | Fail | \${max_rate} is not defined. Call Set Max Rate And Jumbo keyword.

| Get Min Rate Hard
| | [Documentation]
| | ... | Return a hardcoded value.
| | ... | The return value controls the minimal unidirectional packet rate,
| | ... | to be used anywhere, including latency measurements at 0% load.
| | ... | The current value is the smallest one permitted
| | ... | by STL profiles with latency streams.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${min_rate_hard} = \| Get Min Rate Hard \|
| |
| | Return From Keyword | ${9001.0}

| Get Min Rate Soft
| | [Documentation]
| | ... | If ramp up rate is not defined, return the hard min value.
| | ... | If ramp up rate is defined, return that value.
| | ... | The reason is, ramp up rate should already guarantee no loss.
| |
| | ... | The return value controls the minimal unidirectional packet rate,
| | ... | to be used in various search algorithms.
| | ... | Latency measurements may want even lower loads, use hard min for that.
| |
| | ... | The value is also usable for minimal TPS value for ASTF tests.
| | ... | Return type: float.
| |
| | ... | Currently, undefined ramp up rate is reported as zero,
| | ... | so we return the maximum of ramp up rate and the hard min rate.
| |
| | ... | *Example:*
| |
| | ... | \| \${min_rate_soft} = \| Get Min Rate Soft \|
| |
| | ${min_rate_hard} = | Get Min Rate Hard
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${min_rate_soft} = | Evaluate | max(${ramp_up_rate}, ${min_rate_hard})
| | Return From Keyword | ${min_rate_soft}

| Get Mrr Trial Duration
| | [Documentation]
| | ... | Return value from Constants. This is an abstraction, useful in case
| | ... | we start allowing various other overrides or computations.
| | ... | Call this just before calling a Python keyword,
| | ... | as those have restricted access to Robot variables.
| |
| | ... | The return value controls the duration of main trial measurement
| | ... | for MRR type tests.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${mrr_trial_duration} = \| Get Mrr Trial Duration \|
| |
| | Return From Keyword | ${PERF_TRIAL_DURATION}

| Get Mrr Trial Multiplicity
| | [Documentation]
| | ... | Return value from Constants. This is an abstraction, useful in case
| | ... | we start allowing various other overrides or computations.
| | ... | Call this just before calling a Python keyword,
| | ... | as those have restricted access to Robot variables.
| |
| | ... | The return value controls the number of main trial measurement
| | ... | for (B)MRR type tests.
| | ... | Return type: integer.
| |
| | ... | *Example:*
| |
| | ... | \| \${mrr_trial_multiplicity} = \| Get Mrr Trial Multiplicity \|
| |
| | Return From Keyword | ${PERF_TRIAL_MULTIPLICITY}

| Get Packet Loss Ratio
| | [Documentation]
| | ... | Return a hardcoded value. This is an abstraction, useful in case
| | ... | we start allowing various other overrides or computations.
| | ... | Call this just before calling a Python keyword,
| | ... | as those have restricted access to Robot variables.
| |
| | ... | The return value controls the default packet loss ration for PDR
| | ... | in NDRPDR tests. Some other usages of MLRsearch (e.g. reconf tests)
| | ... | may use a different value.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${packet_loss_ratio} = \| Get Packet Loss Ratio \|
| |
| | Return From Keyword | ${0.005}

| Get Packets Per Transaction Aggregated
| | [Documentation]
| | ... | Return value of \${packets_per_transaction_aggregated};
| | ... | if not defined, assume traffic is symmetric and compute
| | ... | from unidirectional values.
| |
| | ... | The return value is used when reporting PPS values from TPS found
| | ... | by some search (e.g. NDRPDR).
| | ... | Return type: integer.
| |
| | ... | *Example:*
| |
| | ... | \| \${ppta} = \| Get Packets Per Transaction Aggregated \|
| |
| | ${ppta} = | Get Variable Value | \${packets_per_transaction_aggregated}
| | ... | ${0}
| | Return From Keyword If | "${ppta}" != "0" | ${ppta}
| | # TODO: Insert TCP computation from packet size here.
| | ${pptad} = | Get Packets Per Transaction And Direction
| | ${traffic_directions} = | Get Traffic Directions
| | # We do not support ASTF profiles with multiple transactions, yet.
| | ${ppta} = | Evaluate | ${pptad} * ${traffic_directions}
| | Return From Keyword | ${ppta}

| Get Packets Per Transaction And Direction
| | [Documentation]
| | ... | Return value of \${packets_per_transaction_and_direction},
| | ... | or ${1} if not defined.
| |
| | ... | The return value is used when computing max rate (TPS),
| | ... | so for asymmetric transaction use the more numerous direction.
| | ... | Return type: integer.
| |
| | ... | *Example:*
| |
| | ... | \| \${pptad} = \| Get Packets Per Transaction And Direction \|
| |
| | ${pptad} = | Get Variable Value | \${packets_per_transaction_and_direction}
| | ... | ${1}
| | Return From Keyword | ${pptad}

| Get Ramp Up Duration
| | [Documentation]
| | ... | Return value of \${ramp_up_duration},
| | ... | or ${0.0} if not defined.
| |
| | ... | The return value determines the required duration of ramp-up phase.
| | ... | Typically used to prepare a specific state on DUT.
| | ... | If the value is zero, ramp-up phase is either skipped or size-limited.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${ramp_up_duration} = \| Get Ramp Up Duration \|
| |
| | ${ramp_up_duration} = | Get Variable Value | \${ramp_up_duration} | ${0.0}
| | Return From Keyword | ${ramp_up_duration}

| Get Ramp Up Rate
| | [Documentation]
| | ... | Return value of \${ramp_up_rate},
| | ... | if not defined, return zero.
| |
| | ... | The return value determines the rate for ramp-up phase.
| | ... | Typically used to limit the rate when max rate
| | ... | would lose packets in the ramp up phase, thus not setting
| | ... | the DUT state correctly.
| | ... | If the value is zero, ramp-up phase should be skipped.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${ramp_up_rate} = \| Get Ramp Up Rate \|
| |
| | ${ramp_up_rate} = | Get Variable Value | \${ramp_up_rate} | ${0.0}
| | Return From Keyword | ${ramp_up_rate}

| Get Rate For Teardown
| | [Documentation]
| | ... | Return value of \${rate_for_teardown},
| | ... | if not defined (or zero) return the soft min rate.
| |
| | ... | The return value determines the rate for teardown trial,
| | ... | that is executed if a perf test fails.
| | ... | The \${rate_for_teardown} is usually not defined in suite,
| | ... | but search keywords set it in places where failure can occur,
| | ... | so the trial is done at the rate interesting for the failure.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${rate_for_teardown} = \| Get Rate For Teardown \|
| |
| | ${rate_for_teardown} = | Get Variable Value | \${rate_for_teardown} | ${0.0}
| | Return From Keyword If | ${rate_for_teardown} | ${rate_for_teardown}
| | Run Keyword And Return | Get Min Rate Soft

| Get Resetter
| | [Documentation]
| | ... | Return value of \${resetter} variable,
| | ... | or \${None} if not defined.
| |
| | ... | If not \${None}, the returned value is callable.
| | ... | Its use is to reset DUT to initial conditions,
| | ... | for example to remove NAT sessions created in the previous trial.
| |
| | ... | *Example:*
| |
| | ... | \| \${resetter} = \| Get Resetter \|
| |
| | ${resetter} = | Get Variable Value | \${resetter} | ${None}
| | Return From Keyword | ${resetter}

| Get Runtime Duration
| | [Documentation]
| | ... | Return value of \${runtime_duration} variable,
| | ... | if not defined return ${1.0}.
| |
| | ... | The return value controls the duration of runtime trial,
| | ... | which also acts as a warmup. Usually one second is enough,
| | ... | but some suites need longer time to set up state on DUT.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${runtime_duration} = \| Get Runtime Duration \|
| |
| | ${runtime_duration} = | Get Variable Value | \${runtime_duration} | ${1.0}
| | Return From Keyword | ${runtime_duration}

| Get Runtime Rate
| | [Documentation]
| | ... | Return value of \${runtime_rate} variable,
| | ... | if not defined return the max rate.
| |
| | ... | The return value controls the rate (TPS unidir) of runtime trial,
| | ... | which also acts as a warmup. No plans to ever use a different rate,
| | ... | but keywords look better if access to such values is uniform.
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${runtime_rate} = \| Get Runtime Rate \|
| |
| | ${runtime_rate} = | Get Variable Value | \${runtime_rate} | ${0.0}
| | Return From Keyword If | ${runtime_rate} | ${runtime_rate}
| | Run Keyword And Return | Get Max Rate

| Get Traffic Directions
| | [Documentation]
| | ... | Return value of \${traffic_directions},
| | ... | or ${2} if not defined.
| |
| | ... | The return value used when parsing for measurement results.
| | ... | This needs to be known already in profile driver,
| | ... | as bidirectional parsing may fail on unidirectional traffic.
| | ... | Return type: integer.
| |
| | ... | *Example:*
| |
| | ... | \| \${traffic_directions} = \| Get Traffic Directions \|
| |
| | ${traffic_directions} = | Get Variable Value | \${traffic_directions} | ${2}
| | Return From Keyword | ${traffic_directions}

| Get Transaction Duration
| | [Documentation]
| | ... | Return value of \${transaction_duration} variable,
| | ... | or \${0.0} if not defined.
| |
| | ... | The return value is the expected duration of single (ASTF) transaction
| | ... | if it is not negligible for overall trial duration computation.
| | ... | Most tests use very short transactions (without explicit delays),
| | ... | so the zero default works (and suite saves one line
| | ... | of Variables table).
| | ... | Return type: float.
| |
| | ... | *Example:*
| |
| | ... | \| \${transaction_duration} = \| Get Transaction Duration \|
| |
| | ${transaction_duration} = | Get Variable Value | \${transaction_duration}
| | ... | ${0.0}
| | Return From Keyword | ${transaction_duration}

| Get Transaction Scale
| | [Documentation]
| | ... | Return value of \${transaction_scale} variable,
| | ... | or \${0} if not defined.
| |
| | ... | Zero return value means the number of transactions is not limited,
| | ... | which is true for most STL TRex profiles (transaction is a packet).
| | ... | Nonzero return value means the number of transactions is fixed,
| | ... | for example in stateful NAT scale tests.
| | ... | Return type: integer.
| |
| | ... | *Example:*
| |
| | ... | \| \${transaction_scale} = \| Get Transaction Scale \|
| |
| | ${transaction_scale} = | Get Variable Value | \${transaction_scale} | ${0}
| | Return From Keyword | ${transaction_scale}

| Get Transaction Type
| | [Documentation]
| | ... | Return value of \${transaction_type} variable,
| | ... | or "packet" if not defined.
| |
| | ... | The return value describes the type of transaction
| | ... | the test is executed. For example "packet" means a transaction
| | ... | is just a single packet. For more sophisticated transactions,
| | ... | the logic to determine the number of passed transactions
| | ... | is different from merely counting the packets received from DUT.
| | ... | Return type: string.
| |
| | ... | *Example:*
| |
| | ... | \| \${transaction_type} = \| Get Transaction Type \|
| |
| | ${transaction_type} = | Get Variable Value | \${transaction_type} | packet
| | Return From Keyword | ${transaction_type}

| Get Use Latency
| | [Documentation]
| | ... | Return value of \${use_latency} variable,
| | ... | if not defined return the value from Constants.
| |
| | ... | The return value controls whether latency streams are active
| | ... | during the main search.
| | ... | Return type: bool.
| |
| | ... | *Example:*
| |
| | ... | \| \${use_latency} = \| Get Use Latency \|
| |
| | ${use_latency} = | Get Variable Value | ${use_latency} | ${PERF_USE_LATENCY}
| | Return From Keyword | ${use_latency}

| Set Jumbo
| | [Documentation]
| | ... | For jumbo frames detection, the maximal packet size is relevant,
| | ... | encapsulation overhead (if any) has effect.
| |
| | ... | This keyword computes jumbo boolean (some suites need that for
| | ... | configuration decisions).
| | ... | To streamline suite autogeneration, both input and output values
| | ... | are communicated as test (or broader scope) variables,
| | ... | instead of explicit arguments and return values.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - overhead - Overhead in bytes; default value: 0. Type: integer
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| |
| | ... | *Test variables set:*
| | ... | - jumbo - Jumbo boolean, true if jumbo packet support has to be
| | ... | enabled. Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Set Jumbo \|
| |
| | # Already called by Set Max Rate And Jumbo, but some suites (e.g. device)
| | # are calling this directly.
| | Set Numeric Frame Sizes
| | ${jumbo} = | Set Variable If | ${max_frame_size} < 1522
| | ... | ${False} | ${True}
| | Set Test Variable | \${jumbo}

| Set Max Rate And Jumbo
| | [Documentation]
| | ... | Input framesize can be either integer in case of a single packet
| | ... | in stream, or IMIX string defining mix of packets.
| | ... | For jumbo frames detection, the maximal packet size is relevant.
| | ... | For maximal transmit rate, the average packet size is relevant.
| | ... | In both cases, encapsulation overhead (if any) has effect.
| | ... | The maximal rate is computed from NIC name.
| | ... | The implementation works by mapping from exact
| | ... | whitelisted NIC names.
| | ... | The mapping is hardcoded in nic_limits.yaml
| | ... | TODO: Make the mapping from NIC names case insensistive.
| |
| | ... | This keyword computes maximal unidirectional transmit rate
| | ... | and jumbo boolean (some suites need that for configuration decisions).
| | ... | To streamline suite autogeneration, both input and output values
| | ... | are communicated as test (or broader scope) variables,
| | ... | instead of explicit arguments and return values.
| |
| | ... | If this keyword detects the test is interested in (unidirectional)
| | ... | transactons per second maximal rate (tps), that is returned (not pps).
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - nic_name - Name of bottleneck NIC. Type: string
| | ... | - overhead - Overhead in bytes; default value: 0. Type: integer
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - packets_per_transaction_and_direction - Pps-tps conversion.
| | ... | Optional, default 1.
| |
| | ... | *Test variables set:*
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | This never exceeds bandwidth on TG-DUT nor DUT-DUT links.
| | ... | Type: float
| | ... | - jumbo - Jumbo boolean, true if jumbo packet support has to be
| | ... | enabled. Type: boolean
| | ... | avg_frame_size - Average frame size including overhead. Type: float
| | ... | max_frame_size - Maximal frame size including overhead. Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Set Max Rate And Jumbo \|
| |
| | # TODO: Re-check overhead values in suites with both traffics encapsulated.
| | # TODO: Improve layered setup to detect encap/decap and update overhead.
| | ${pps_limit} = | Get From Dictionary
| | ... | ${NIC_NAME_TO_PPS_LIMIT} | ${nic_name}
| | ${bps_limit} = | Get From Dictionary
| | ... | ${NIC_NAME_TO_BPS_LIMIT} | ${nic_name}
| | Set Numeric Frame Sizes
| | ${rate} = | Evaluate | ${bps_limit} / ((${avg_frame_size} + 20.0) * 8)
| | ${max_rate} = | Set Variable If | ${rate} > ${pps_limit}
| | ... | ${pps_limit} | ${rate}
| | ${pptad} = | Get Packets Per Transaction And Direction
| | ${max_rate} = | Evaluate | ${max_rate} / ${pptad}
| | Set Test Variable | \${max_rate}
| | Set Jumbo

| Set Numeric Frame Sizes
| | [Documentation]
| | ... | Framesize can be either integer in case of a single packet
| | ... | in stream, or set of packets in case of IMIX type or simmilar.
| | ... | For jumbo decisions, we need a numeric size of the biggest packet.
| | ... | For max rate decisions, we need a numeric average packet size.
| | ... | This keyword computes both and sets them as test variables.
| |
| | ... | Each suite sets a value named \${overhead},
| | ... | which describes by how many bytes the frames on DUT-DUT link
| | ... | are larger (due to encapsulation) than those
| | ... | on the primary TG-DUT link. But for some suites that value
| | ... | can be negaive (if TG-DUT is encapsulated more heavily).
| | ... | For calculations in this keyword, we need largest sizes
| | ... | across links, so zero is used if \${overhead} is negative.
| |
| | ... | *Test variables read:*
| | ... | - frame_size - Framesize. Type: integer or string
| | ... | - overhead - Overhead in bytes; default value: ${0}. Type: integer
| |
| | ... | *Test variables set*
| | ... | avg_frame_size - Average frame size including overhead. Type: float
| | ... | max_frame_size - Maximal frame size including overhead. Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Set Numeric Frame Sizes \|
| |
| | ${max_overhead} = | Set Variable If | ${overhead} >= 0 | ${overhead} | ${0}
| | ${bare_avg_frame_size} = | Run Keyword If | '${frame_size}' == 'IMIX_v4_1'
| | ... | Set Variable | ${353.83333}
| | ... | ELSE
| | ... | Convert To Number | ${frame_size}
| | ${avg_frame_size} = | Evaluate | $bare_avg_frame_size + $max_overhead
| | Set Test Variable | \${avg_frame_size}
| | ${bare_max_frame_size} = | Run Keyword If | '${frame_size}' == 'IMIX_v4_1'
| | ... | Set Variable | ${1518}
| | ... | ELSE
| | ... | Convert To Number | ${frame_size}
| | ${max_frame_size} = | Evaluate | $bare_max_frame_size + $max_overhead
| | Set Test Variable | ${max_frame_size}

| Set Rates For Policer
| | [Documentation]
| | ... | Policer tests need these values,
| | ... | currently computed from \${avg_frame_size}.
| | ... | TODO: Verify the units match and computation is correct.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - avg_frame_size - Average L2 Frame Size [B]. Type: float
| | ... | Set by Set Max Rate And Jumbo keyword.
| |
| | ... | *Test variables set:*
| | ... | - eb - Excess burst rate for policer. Type: float
| | ... | - cb - Committed burst rate for policer. Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Set Rates For Policer \|
| |
| | Set Test Variable | \${eb} | ${avg_frame_size}
| | Set Test Variable | \${cb} | ${avg_frame_size}
