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

| Find NDR and PDR intervals using optimized search
| | [Documentation]
| | ... | Find boundaries for RFC2544 compatible NDR and PDR values
| | ... | using an optimized search algorithm.
| | ... | Display results as formatted test message.
| | ... | Fail if a resulting lower bound has too high loss fraction.
| | ... | Proceed with Perform additional measurements based on NDRPDR result.
| | ... | Input rates are understood as uni-directional,
| | ... | reported result contains bi-directional rates.
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
| | ... | - doublings - How many doublings to do when expanding [1]. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find NDR and PDR intervals using optimized search \| \${64} \| \
| | ... | 3-node-IPv4 \| \${100000} \| \${14880952} \| \${0.005} \| \${0.005} \
| | ... | \| \${30.0} \| \${1.0} \| \${2} \| ${600.0} \| ${2} \|
| | ...
| | [Arguments] | ${frame_size} | ${topology_type} | ${minimum_transmit_rate}
| | ... | ${maximum_transmit_rate} | ${packet_loss_ratio}=${0.005}
| | ... | ${final_relative_width}=${0.005} | ${final_trial_duration}=${30.0}
| | ... | ${initial_trial_duration}=${1.0}
| | ... | ${number_of_intermediate_phases}=${2} | ${timeout}=${720.0}
| | ... | ${doublings}=${2}
| | ...
| | ${result} = | Perform optimized ndrpdr search | ${frame_size}
| | ... | ${topology_type} | ${minimum_transmit_rate*2}
| | ... | ${maximum_transmit_rate*2} | ${packet_loss_ratio}
| | ... | ${final_relative_width} | ${final_trial_duration}
| | ... | ${initial_trial_duration} | ${number_of_intermediate_phases}
| | ... | timeout=${timeout} | doublings=${doublings}
| | Display result of NDRPDR search | ${result} | ${frame_size}
| | Check NDRPDR interval validity | ${result.pdr_interval}
| | ... | ${packet_loss_ratio}
| | Check NDRPDR interval validity | ${result.ndr_interval}
| | Perform additional measurements based on NDRPDR result
| | ... | ${result} | ${frame_size} | ${topology_type}

| Find critical load using PLRsearch
| | [Documentation]
| | ... | Find boundaries for troughput (of given target loss ratio)
| | ... | using PLRsearch algorithm.
| | ... | Display results as formatted test message.
| | ... | Fail if computed lower bound is below minimal rate.
| | ... | Input rates are understood as uni-directional,
| | ... | reported result contains bi-directional rates.
| | ... | TODO: Any additional measurements for debug purposes?
| | ...
| | ... | *Arguments:*
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: int or str
| | ... | - topology_type - Topology type. Type: string
| | ... | - minimum_transmit_rate - Lower limit of search [pps]. Type: float
| | ... | - maximum_transmit_rate - Upper limit of search [pps]. Type: float
| | ... | - packet_loss_ratio - Accepted loss during search. Type: float
| | ... | - timeout - Stop when search duration is longer [s]. Type: float
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Find critical load usingPLR search \| \${64} \| \
| | ... | 3-node-IPv4 \| \${100000} \| \${14880952} \| \${1e-7} \| \${1800} \
| | ...
| | [Arguments] | ${frame_size} | ${topology_type} | ${minimum_transmit_rate}
| | ... | ${maximum_transmit_rate} | ${packet_loss_ratio}=${1e-7}
| | ... | ${timeout}=${1800.0}
| | ...
| | ${min_rate} = | Set Variable | ${minimum_transmit_rate*2}
| | ${average} | ${stdev} = | Perform soak search | ${frame_size}
| | ... | ${topology_type} | ${min_rate} | ${maximum_transmit_rate*2}
| | ... | ${packet_loss_ratio} | timeout=${timeout}
| | ${lower} | ${upper} = | Display result of soak search
| | ... | ${average} | ${stdev} | ${frame_size}
| | Should Not Be True | ${lower} < ${min_rate}
| | ... | Lower bound ${lower} is below bidirectional minimum ${min_rate}.

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
| | ${bandwidth_total} = | Evaluate | ${rate_total} * (${framesize}+20)*8 / 1e9
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
| | ${framesize} = | Get Frame Size | ${framesize}
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

| Display result of soak search
| | [Documentation]
| | ... | Display result of soak search, avg+-stdev, as upper/lower bounds,
| | ... | in packet per seconds (total and per stream)
| | ... | and Gbps total bandwidth with untagged packet.
| | ... | Througput is calculated as:
| | ... | Measured rate per stream * Total number of streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8) / Max bitrate of NIC
| | ... | TODO: Do we want to report some latency data,
| | ... | even if not measured at the reported bounds?.
| | ...
| | ... | *Arguments:*
| | ... | - avg - Estimated average critical load [pps]. Type: float
| | ... | - stdev - Standard deviation of critical load [pps]. Type: float
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ...
| | ... | *Returns:*
| | ... | - Lower and upper bound of critical load [pps]. Type: 2-tuple of float
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Display result of soak search \| \${100000} \| \${100} \| \${64} \|
| | ...
| | [Arguments] | ${avg} | ${stdev} | ${framesize}
| | ...
| | ${framesize} = | Get Frame Size | ${framesize}
| | ${avg} = | Convert To Number | ${avg}
| | ${stdev} = | Convert To Number | ${stdev}
| | ${lower} = | Evaluate | ${avg} - ${stdev}
| | ${upper} = | Evaluate | ${avg} + ${stdev}
| | Display single bound | PLRsearch lower bound: | ${lower} | ${framesize}
| | Display single bound | PLRsearch upper bound: | ${upper} | ${framesize}
| | Return From Keyword | ${lower} | ${upper}

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
| | # TODO: Remove this keyword, or suport unidirectional traffic.
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
| | ... | - unidirection - False if traffic is bidirectional. Type: boolean
| | ... | - tx_port - TX port of TG, default 0. Type: integer
| | ... | - rx_port - RX port of TG, default 1. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Traffic should pass with maximum rate \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \| ${1} \| ${10.0} \| ${False}
| | ... | \| ${False} \| ${0} | ${1} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${topology_type}
| | ... | ${trial_duration}=${perf_trial_duration} | ${fail_no_traffic}=${True}
| | ... | ${subsamples}=${perf_trial_multiplicity}
| | ... | ${unidirection}=${False} | ${tx_port}=${0} | ${rx_port}=${1}
| | ...
| | ${results} = | Send traffic at specified rate | ${trial_duration} | ${rate}
| | ... | ${framesize} | ${topology_type} | ${subsamples} | ${unidirection}
| | ... | ${tx_port} | ${rx_port}
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
| | ... | - unidirection - False if traffic is bidirectional. Type: boolean
| | ... | - tx_port - TX port of TG, default 0. Type: integer
| | ... | - rx_port - RX port of TG, default 1. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send traffic at specified rate \| ${1.0} \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \| ${10} \| ${False} \| ${0} | ${1} \|
| | ...
| | [Arguments] | ${trial_duration} | ${rate} | ${framesize}
| | ... | ${topology_type} | ${subsamples}=${1} | ${unidirection}=${False}
| | ... | ${tx_port}=${0} | ${rx_port}=${1}
| | ...
| | Clear and show runtime counters with running traffic | ${trial_duration}
| | ... | ${rate} | ${framesize} | ${topology_type}
| | ... | ${unidirection} | ${tx_port} | ${rx_port}
| | Run Keyword If | ${dut_stats}==${True} | Clear all counters on all DUTs
| | Run Keyword If | ${dut_stats}==${True} and ${pkt_trace}==${True}
| | ... | VPP Enable Traces On All DUTs | ${nodes}
| | Run Keyword If | ${dut_stats}==${True}
| | ... | VPP enable elog traces on all DUTs | ${nodes}
| | ${results} = | Create List
| | :FOR | ${i} | IN RANGE | ${subsamples}
| | | # The following line is skipping some default arguments,
| | | # that is why subsequent arguments have to be named.
| | | Send traffic on tg | ${trial_duration} | ${rate} | ${framesize}
| | | ... | ${topology_type} | warmup_time=${0} | unidirection=${unidirection}
| | | ... | tx_port=${tx_port} | rx_port=${rx_port}
| | | ${rx} = | Get Received
| | | ${rr} = | Evaluate | ${rx} / ${trial_duration}
| | | Append To List | ${results} | ${rr}
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
| | ...
| | ... | *Arguments:*
| | ... | - duration - Duration of traffic run [s]. Type: integer
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B] or IMIX_v4_1. Type: integer/string
| | ... | - topology_type - Topology type. Type: string
| | ... | - unidirection - False if traffic is bidirectional. Type: boolean
| | ... | - tx_port - TX port of TG, default 0. Type: integer
| | ... | - rx_port - RX port of TG, default 1. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Clear and show runtime counters with running traffic \| 10 \
| | ... | \| 4.0mpps \| 64 \| 3-node-IPv4 \| ${False} \| ${0} | ${1} \|
| | ...
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | ... | ${unidirection}=${False} | ${tx_port}=${0} | ${rx_port}=${1}
| | ...
| | Send traffic on tg | ${-1} | ${rate} | ${framesize} | ${topology_type}
| | ... | warmup_time=${0} | async_call=${True} | latency=${False}
| | ... | unidirection=${unidirection} | tx_port=${tx_port} | rx_port=${rx_port}
| | Run Keyword If | ${dut_stats}==${True}
| | ... | Clear runtime counters on all DUTs | ${nodes}
| | Sleep | ${duration}
| | Run Keyword If | ${dut_stats}==${True}
| | ... | Show runtime counters on all DUTs | ${nodes}
| | Stop traffic on tg

| Create network function CPU list
| | [Documentation]
| | ... | Create list of CPUs allocated for network function base on SUT/DUT
| | ... | placement and other network functions placement.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: dictionary
| | ... | - chains: Total number of chains. Type: integer
| | ... | - nodeness: Total number of nodes per chain. Type: integer
| | ... | - chain_id - Network function chain ID. Type: integer
| | ... | - node_id - Network function node ID within chain. Type: integer
| | ... | - mtcr - Main thread to core ratio. Type: integer
| | ... | - dtcr - Dataplane thread to core ratio. Type: integer
| | ... | - auto_scale - If True, use same amount of Dataplane threads for
| | ... |   network function as DUT, otherwise use single physical core for
| | ... |   every network function. Type: boolean
| | ...
| | ... | *Note:*
| | ... | KW uses test variables \${cpu_count_int} set by
| | ... | "Add worker threads and rxqueues to all DUTs"
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create network function CPU list \| ${nodes['DUT1']} \
| | ... | \| 1 \| 1 \| 1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${chains}=${1} | ${nodeness}=${1} | ${chain_id}=${1}
| | ... | ${node_id}=${1} | ${mtcr}=${2} | ${dtcr}=${1} | ${auto_scale}=${False}
| | ...
| | ${sut_sc}= | Set Variable | ${1}
| | ${dut_mc}= | Set Variable | ${1}
| | ${dut_dc}= | Set Variable | ${cpu_count_int}
| | ${skip}= | Evaluate | ${sut_sc} + ${dut_mc} + ${dut_dc}
| | ${dtc}= | Set Variable If | ${auto_scale} | ${cpu_count_int} | ${1}
| | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${${dut}_if1}
| | @{if_list}= | Run Keyword If | '${if1_status}' == 'PASS'
| | ... | Create List | ${${dut}_if1}
| | ... | ELSE | Create List | ${${dut}_if1_1} | ${${dut}_if1_2}
| | ${if2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${${dut}_if2}
| | Run Keyword If | '${if2_status}' == 'PASS'
| | ... | Append To List | ${if_list} | ${${dut}_if2}
| | ... | ELSE | Append To List | ${if_list} | ${${dut}_if2_1} | ${${dut}_if2_2}
| | ${dut_numa}= | Get interfaces numa node | ${nodes['${dut}']} | @{if_list}
| | ${nf_cpus}= | Cpu slice of list for NF | node=${nodes['${dut}']}
| | ... | cpu_node=${dut_numa} | chains=${chains} | nodeness=${nodeness}
| | ... | chain_id=${chain_id} | node_id=${node_id} | mtcr=${mtcr}
| | ... | dtcr=${dtcr} | dtc=${dtc} | skip_cnt=${skip}
| | Return From Keyword | ${nf_cpus}
