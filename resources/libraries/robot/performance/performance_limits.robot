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
| Documentation | Performance suite keywords - Handling NIC and TG limits.
| Library | Collections
| Variables | ${CURDIR}/../../python/Constants.py

*** Keywords ***
| Get Average Frame Size
| | [Documentation]
| | ... | Framesize can be either integer in case of a single packet
| | ... | in stream, or set of packets in case of IMIX type or simmilar.
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize. Type: integer or string
| | ... | - overhead - Overhead in bytes; default value: ${0}. Type: integer
| |
| | ... | *Returns:*
| | ... | Average frame size including overhead. Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Get Average Frame Size \| IMIX_v4_1 \|
| |
| | [Arguments] | ${frame_size} | ${overhead}=${0}
| |
| | ${frame_size} = | Run Keyword If | '${frame_size}' == 'IMIX_v4_1'
| | ... | Set Variable | ${353.83333}
| | ... | ELSE
| | ... | Convert To Number | ${frame_size}
| | ${avg_frame_size} = | Evaluate | ${frame_size} + ${overhead}
| | Return From Keyword | ${avg_frame_size}

| Get Maximum Frame Size
| | [Documentation]
| | ... | Framesize can be either integer in case of a single packet
| | ... | in stream, or set of packets in case of IMIX type or simmilar.
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize. Type: integer or string
| | ... | - overhead - Overhead in bytes; default value: ${0}. Type: integer
| |
| | ... | *Returns:*
| | ... | Maximum frame size including overhead. Type: float
| |
| | ... | *Example:*
| |
| | ... | \| Get Maximum Frame Size \| IMIX_v4_1 \|
| |
| | [Arguments] | ${frame_size} | ${overhead}=${0}
| |
| | ${frame_size} = | Run Keyword If | '${frame_size}' == 'IMIX_v4_1'
| | ... | Set Variable | ${1518}
| | ... | ELSE
| | ... | Convert To Number | ${frame_size}
| | ${max_frame_size} = | Evaluate | ${frame_size} + ${overhead}
| | Return From Keyword | ${max_frame_size}

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
| | ... | TODO: Make pps limit also definable per NIC.
| |
| | ... | This keyword computes maximal unidirectional transmit rate
| | ... | and jumbo boolean (some suites need that for configuration decisions).
| | ... | To streamline suite autogeneration, both input and output values
| | ... | are communicated as test (or broader scope) variables,
| | ... | instead of explicit arguments and return values.
| |
| | ... | *Test (or broader scope) variables read:*
| | ... | - nic_name - Name of bottleneck NIC. Type: string
| | ... | - overhead - Overhead in bytes; default value: 0. Type: integer
| | ... | - frame_size - L2 Frame Size [B] or IMIX string. Type: integer or
| | ... | string
| |
| | ... | *Test variables set:*
| | ... | - max_rate - Calculated unidirectional maximal transmit rate [pps].
| | ... | Type: float
| | ... | - jumbo - Jumbo boolean, true if jumbo packet support has to be
| | ... | enabled. Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Set Test Variable \| \${frame_size} \| IMIX_v4_1 \|
| | ... | \| Set Max Rate And Jumbo \|
| |
| | # Negative overhead is possible, if DUT-DUT traffic is less encapsulated
| | # than TG-DUT traffic.
| | # TODO: Re-check overhead values in suites with both traffics encapsulated.
| | # TODO: Improve layered setup to detect encap/decap and update overhead.
| | ${overhead} = | Set Variable If | ${overhead} >= 0 | ${overhead} | ${0}
| | ${pps_limit} = | Get From Dictionary
| | ... | ${NIC_NAME_TO_PPS_LIMIT} | ${nic_name}
| | ${bps_limit} = | Get From Dictionary
| | ... | ${NIC_NAME_TO_BPS_LIMIT} | ${nic_name}
| | # swo := size_with_overhead
| | ${avg_swo} = | Get Average Frame Size | ${frame_size} | ${overhead}
| | ${rate} = | Evaluate | ${bps_limit} / ((${avg_swo} + 20.0) * 8)
| | ${max_rate} = | Set Variable If | ${rate} > ${pps_limit}
| | ... | ${pps_limit} | ${rate}
| | Set Test Variable | \${max_rate}
| | Set Jumbo

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
| | ... | \| Set Jumnbo \|
| |
| | ${overhead} = | Set Variable If | ${overhead} >= 0 | ${overhead} | ${0}
| | ${max_swo} = | Get Maximum Frame Size | ${frame_size} | ${overhead}
| | ${jumbo} = | Set Variable If | ${max_swo} < 1522
| | ... | ${False} | ${True}
| | Set Test Variable | \${jumbo}
