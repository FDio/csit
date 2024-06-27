# Copyright (c) 2023 Cisco and/or its affiliates.
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
| Compute Bandwidth
| | [Documentation]
| | ... | Compute (bidir) bandwidth from given (unidir) transaction rate.
| | ...
| | ... | This keyword reads \${ppta} and \${avg_aggregated_frame_size} set
| | ... | elsewhere. The implementation should work for both pps and cps rates.
| | ... |
| | ... | *Arguments:*
| | ... | - tps - Transaction rate (unidirectional) [tps]. Type: float
| | ...
| | ... | *Returns:*
| | ... | - Computed bandwidth in Gbps.
| | ... | - Computed aggregated packet rate in pps.
| |
| | ... | *Example:*
| |
| | ... | |\ \${bandwidth} \| \${pps} = \| Compute Bandwidth \| \${12345.67} \|
| |
| | [Arguments] | ${tps}
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${pps} = | Evaluate | ${tps} * ${ppta}
| | ${bandwidth} = | Evaluate | ${pps} * (${avg_aggregated_frame_size}+20)*8/1e9
| | Return From Keyword | ${bandwidth} | ${pps}

| Display Reconfig Test Message
| | [Documentation]
| | ... | Display the number of packets lost (bidirectionally)
| | ... | due to reconfiguration under traffic.
| |
| | ... | *Arguments:*
| | ... | - result - Result of MLRsearch invocation for one search goal.
| | ... | Type: StatInterval
| |
| | ... | *Example:*
| |
| | ... | \| Display Reconfig Test Message \| \${result} \|
| |
| | [Arguments] | ${result}
| |
| | ${bandwidth} | ${packet_rate}= | Compute Bandwidth | ${result.intended_load}
| | ${packet_loss} = | Set Variable | ${result.loss_count}
| | ${time_loss} = | Evaluate | ${packet_loss} / ${packet_rate}
| | Set Test Message | Packets lost due to reconfig: ${packet_loss}
| | Set Test Message | ${\n}Implied time lost: ${time_loss} | append=yes
| | Export Reconf Result | ${packet_rate} | ${packet_loss} | ${bandwidth * 1e9}

| Display result of NDRPDR search
| | [Documentation]
| | ... | Display result of NDR+PDR search, both quantities, aggregated,
| | ... | conditional throughput only, in units given by trasaction type,
| | ... | e.g. by default in packet per seconds and Gbps total bandwidth
| | ... | (for initial packet size).
| | ... | The lower bounds in the result are assumed to be valid.
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
| | ... | - result - Measured result data Tps. Type: List[TrimmedStat]
| | ... | *Returns:* NDR and PDR: Unidirectional intended load as tps float.
| |
| | ... | *Example:*
| |
| | ... | \| Display result of NDRPDR search \| \${result} \|
| |
| | [Arguments] | ${result}
| |
| | ${ndr} = | Convert To Number | ${result[0].relevant_lower_bound}
| | ${pdr} = | Convert To Number | ${result[1].relevant_lower_bound}
| | Display single bound | NDR | ${result[0].conditional_throughput}
| | Display single bound | PDR | ${result[1].conditional_throughput}
| | Return From Keyword | ${ndr} | ${pdr}

| Display result of soak search
| | [Documentation]
| | ... | Display result of soak search, avg+-stdev, as upper/lower bounds.
| | ... | See Display single bound for units used.
| | ... | The displayed values are bidirectional, based on conditional
| | ... | throughput. The returned
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| | ... | - transaction_type - String identifier to determine how to count
| | ... | transactions. Default is "packet".
| | ... | *Arguments:*
| | ... | - avg - Estimated average critical load [pps]. Type: float
| | ... | - stdev - Standard deviation of critical load [pps]. Type: float
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
| | ... |
| | ... | The bound to display is given as target transfer rate, it is assumed
| | ... | valid and in transactions per second. Bidirectional traffic
| | ... | transaction is understood as having 2 packets, for this purpose.
| | ... |
| | ... | Pps values are aggregated, in packet per seconds
| | ... | and Gbps total bandwidth (for initial packet size).
| | ... | If the latency string is present, it is displayed as well.
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
| | ... | - tps - Conditional throughput [tps]. Type: Union[float, DiscreteLoad]
| | ... | - latency - Latency data to display if non-empty. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Display single bound \| NDR \| \${12345.67} \
| | ... | \| latency=\${EMPTY} \|
| |
| | [Arguments] | ${text} | ${tps} | ${latency}=${EMPTY}
| |
| | ${tps} = | Convert To Number | ${tps}
| | ${transaction_type} = | Get Transaction Type
| | Run Keyword And Return If | """_cps""" in """${transaction_type}"""
| | ... | Display Single CPS Bound | ${text} | ${tps} | ${latency}
| | Run Keyword And Return
| | ... | Display Single PPS Bound | ${text} | ${tps} | ${latency}

| Display Single CPS Bound
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
| | ... | \| Display Single CPS Bound \| NDR lower bound \| \${12345.67} \
| | ... | \| latency=\${EMPTY} \|
| |
| | [Arguments] | ${text} | ${tps} | ${latency}=${EMPTY}
| |
| | Set Test Message | ${\n}${text}: ${tps} CPS | append=yes
| | ${bandwidth} | ${pps} = | Compute Bandwidth | ${tps}
| | Export Search Bound | ${text} | ${tps} | cps | ${bandwidth * 1e9}
| | Run Keyword If | """${latency}""" | Set Test Message
| | ... | ${\n}LATENCY [min/avg/max/hdrh] per stream: ${latency} | append=yes

| Display Single PPS Bound
| | [Documentation]
| | ... | Display one pps bound of NDR+PDR search, aggregated,
| | ... | in packet per seconds and Gbps total bandwidth
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
| | ... | \| Display Single PPS Bound \| NDR lower bound \| \${12345.67} \
| | ... | \| latency=\${EMPTY} \|
| |
| | [Arguments] | ${text} | ${tps} | ${latency}=${EMPTY}
| |
| | ${bandwidth} | ${pps} = | Compute Bandwidth | ${tps}
| | Set Test Message | ${\n}${text}: ${pps} pps, | append=yes
| | Set Test Message | ${bandwidth} Gbps (initial) | append=yes
| | Export Search Bound | ${text} | ${pps} | pps | ${bandwidth * 1e9}
| | Run Keyword If | """${latency}""" | Set Test Message
| | ... | ${\n}LATENCY [min/avg/max/hdrh] per stream: ${latency} | append=yes
