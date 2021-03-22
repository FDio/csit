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
| Documentation
| ... | Performance suite keywords - Displaying results as test messages.
| ... | This includes checks to fail test.

*** Keywords ***
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
| | ${lower_bound_lr} = | Set Variable | ${lower_bound.loss_ratio}
| | Return From Keyword If | ${lower_bound_lr} <= ${packet_loss_ratio}
| | Set Test Variable | \${rate_for_teardown} | ${lower_bound_lr}
| | ${message}= | Catenate | SEPARATOR=${SPACE}
| | ... | Minimal rate loss ratio ${lower_bound_lr}
| | ... | does not reach target ${packet_loss_ratio}.
| | ${message_zero} = | Set Variable | Zero packets forwarded!
| | ${message_other} = | Set Variable | ${lower_bound.loss_count} packets lost.
| | ${message} = | Set Variable If | ${lower_bound_lr} >= 1.0
| | ... | ${message}${\n}${message_zero} | ${message}${\n}${message_other}
| | Fail | ${message}

| Display Reconfig Test Message
| | [Documentation]
| | ... | Display the number of packets lost (bidirectionally)
| | ... | due to reconfiguration under traffic.
| |
| | ... | *Arguments:*
| | ... | - result - Result of bidirectional measurement.
| | ... | Type: ReceiveRateMeasurement
| |
| | ... | *Example:*
| |
| | ... | \| Display Reconfig Test Message \| \${result} \|
| |
| | [Arguments] | ${result}
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${packet_rate} = | Evaluate | ${result.target_tr} * ${ppta}
| | ${packet_loss} = | Set Variable | ${result.loss_count}
| | ${time_loss} = | Evaluate | ${packet_loss} / ${packet_rate}
| | Set Test Message | Packets lost due to reconfig: ${packet_loss}
| | Set Test Message | ${\n}Implied time lost: ${time_loss} | append=yes

| Display result of NDRPDR search
| | [Documentation]
| | ... | Display result of NDR+PDR search, both quantities, both bounds,
| | ... | aggregate in units given by trasaction type, e.g. by default
| | ... | in packet per seconds and Gbps total bandwidth
| | ... | (for initial packet size).
| | ... |
| | ... | The bound to display is encoded as target rate, it is assumed
| | ... | it is in transactions per second. Bidirectional traffic
| | ... | transaction is understood as having 2 packets, for this purpose.
| | ... |
| | ... | Througput is calculated as:
| | ... | Sum of measured rate over streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8)
| | ... | If the results contain latency data, display them for lower bounds.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - frame_size_num - L2 Frame Size [B]. Type: integer or float
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| | ... | *Arguments:*
| | ... | - result - Measured result data. Aggregate rate, tps or pps.
| | ... | Type: NdrPdrResult
| |
| | ... | *Example:*
| |
| | ... | \| Display result of NDRPDR search \| \${result} \|
| |
| | [Arguments] | ${result}
| |
| | Display single bound | NDR_LOWER
| | ... | ${result[0].measured_low.target_tr}
| | ... | ${result[0].measured_low.latency}
| | Display single bound | NDR_UPPER
| | ... | ${result[0].measured_high.target_tr}
| | Display single bound | PDR_LOWER
| | ... | ${result[1].measured_low.target_tr}
| | ... | ${result[1].measured_low.latency}
| | Display single bound | PDR_UPPER
| | ... | ${result[1].measured_high.target_tr}

| Display result of soak search
| | [Documentation]
| | ... | Display result of soak search, avg+-stdev, as upper/lower bounds.
| | ... | See Display single bound for units used.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
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
| | ${avg} = | Convert To Number | ${avg}
| | ${stdev} = | Convert To Number | ${stdev}
| | ${lower} = | Evaluate | ${avg} - ${stdev}
| | ${upper} = | Evaluate | ${avg} + ${stdev}
| | Display single bound | PLRsearch lower bound | ${lower}
| | Display single bound | PLRsearch upper bound | ${upper}
| | Return From Keyword | ${lower} | ${upper}

| Display single bound
| | [Documentation]
| | ... | Compute and display one bound of NDR+PDR (or soak) search result.
| | ... | If the latency string is present, it is displayed as well.
| | ... |
| | ... | The bound to display is given as target transfer rate, it is assumed
| | ... | it is in transactions per second. Bidirectional traffic
| | ... | transaction is understood as having 2 packets, for this purpose.
| | ... |
| | ... | Pps values are aggregate in packet per seconds,
| | ... | and Gbps total bandwidth (for initial packet size).
| | ... |
| | ... | Througput is calculated as:
| | ... | Sum of measured rate over streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8)
| | ... | If the results contain latency data, display them for lower bounds.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| | ... | *Arguments:*
| | ... | - text - Flavor text describing which bound is this. Type: string
| | ... | - tps - Transaction rate [tps]. Type: float
| | ... | - latency - Latency data to display if non-empty. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Display single bound \| NDR lower bound \| \${12345.67} \
| | ... | \| latency=\${EMPTY} \|
| |
| | [Arguments] | ${text} | ${tps} | ${latency}=${EMPTY}
| |
| | ${transaction_type} = | Get Transaction Type
| | Run Keyword And Return If | """_cps""" in """${transaction_type}"""
| | ... | Display single cps bound | ${text} | ${tps} | ${latency}
| | Display single pps bound | ${text} | ${tps} | ${latency}

| Display single cps bound
| | [Documentation]
| | ... | Display one bound of NDR+PDR search for CPS tests.
| | ... | The bounds are expressed as transactions per second.
| | ... | If the latency string is present, it is displayed as well.
| |
| | ... | *Arguments:*
| | ... | - text - Flavor text describing which bound is this. Type: string
| | ... | - tps - Transaction rate [tps]. Type: float
| | ... | - latency - Latency data to display if non-empty. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Display single cps bound \| NDR lower bound \| \${12345.67} \
| | ... | \| latency=\${EMPTY} \|
| |
| | [Arguments] | ${text} | ${tps} | ${latency}=${EMPTY}
| |
| | Set Test Message | ${\n}${text}: ${tps} CPS | append=yes
| | Return From Keyword If | not """${latency}"""
| | Set Test Message | ${\n}LATENCY [min/avg/max/hdrh] per stream: ${latency}
| | ... | append=yes

| Display single pps bound
| | [Documentation]
| | ... | Display one pps bound of NDR+PDR search,
| | ... | aggregate in packet per seconds and Gbps total bandwidth
| | ... | (for initial packet size).
| | ... |
| | ... | The bound to display is given as target transfer rate, it is assumed
| | ... | it is in transactions per second. Bidirectional traffic
| | ... | transaction is understood as having 2 packets, for this purpose.
| | ... |
| | ... | Througput is calculated as:
| | ... | Sum of measured rates over streams
| | ... | Bandwidth is calculated as:
| | ... | (Throughput * (L2 Frame Size + IPG) * 8)
| | ... | If the latency string is present, it is displayed as well.
| |
| | ... | *Arguments:*
| | ... | - text - Flavor text describing which bound is this. Type: string
| | ... | - tps - Transaction rate [tps]. Type: float
| | ... | - latency - Latency data to display if non-empty. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Display single pps bound \| NDR lower bound \| \${12345.67} \
| | ... | \| latency=\${EMPTY} \|
| |
| | [Arguments] | ${text} | ${tps} | ${latency}=${EMPTY}
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${pps} = | Evaluate | ${tps} * ${ppta}
| | ${bandwidth} = | Evaluate | ${pps} * (${avg_frame_size}+20)*8 / 1e9
| | Set Test Message | ${\n}${text}: ${pps} pps, | append=yes
| | Set Test Message | ${bandwidth} Gbps (initial) | append=yes
| | Return From Keyword If | not """${latency}"""
| | Set Test Message | ${\n}LATENCY [min/avg/max/hdrh] per stream: ${latency}
| | ... | append=yes
