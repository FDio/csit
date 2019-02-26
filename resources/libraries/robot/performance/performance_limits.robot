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
| Documentation | Performance suite keywords - Handling NIC and TG limits.
| Library | Collections
| Variables | ${CURDIR}/../../python/Constants.py

*** Keywords ***
| Get Average Frame Size
| | [Documentation]
| | ... | Framesize can be either integer in case of a single packet
| | ... | in stream, or set of packets in case of IMIX type or simmilar.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - Framesize. Type: integer or string
| | ...
| | ... | *Returns:*
| | ... | Average framesize. Type: float
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get Average Frame Size \| IMIX_v4_1 \|
| | ...
| | [Arguments] | ${framesize}
| | ...
| | Return From Keyword If | '${framesize}' == 'IMIX_v4_1' | ${353.83333}
| | ${framesize} = | Convert To Number | ${framesize}
| | Return From Keyword | ${framesize}

| Get Max Rate And Jumbo
| | [Documentation]
| | ... | Argument framesize can be either integer in case of a single packet
| | ... | in stream, or IMIX string defining mix of packets.
| | ... | For jumbo frames detection, the maximal packet size is relevant.
| | ... | For maximal transmit rate, the average packet size is relevant.
| | ... | In both cases, encapsulation overhead (if any) has effect.
| | ... | The maximal rate is computed from NIC name.
| | ... | The implementation works by mapping from exact
| | ... | whitelisted NIC names.
| | ... | The mapping is hardcoded in nic_limits.yaml
| | ... | TODO: Make the mapping from NIC names case insensistive.
| | ...
| | ... | TODO: Make pps limit also definable per NIC.
| | ...
| | ... | This keyword returns computed maximal unidirectional transmit rate
| | ... | and jumbo boolean (some suites need that).
| | ...
| | ... | *Arguments:*
| | ... | - nic_name - Name of bottleneck NIC. Type: string
| | ... | - framesize - Framesize in bytes or IMIX. Type: integer or string
| | ... | - overhead - Overhead in bytes. Default: 0. Type: integer
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
| | ... | \| Get Max Rate And Jumbo | Intel-X710 \| IMIX_v4_1 \
| | ... | \| overhead=\${40} \|
| | ...
| | [Arguments] | ${nic_name} | ${framesize} | ${overhead}=${0}
| | ...
| | ${pps_limit} = | Set Variable | ${18750000}
| | ${bps_limit} = | Get From Dictionary | ${NIC_NAME_TO_LIMIT} | ${nic_name}
| | ${avg_size} = | Get Average Frame Size | ${framesize}
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
| | # TODO: Can our code handle float rate? If yes, trop trunc.
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
| | ... | - nic_name - Name of bottleneck NIC. Type: string
| | ... | - framesize - Framesize in bytes. Type: integer or string
| | ... | - overhead - Overhead in bytes. Default: 0. Type: integer
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
| | ... | \| Get Max Rate And Jumbo And Handle Multi Seg | Intel-X710 \
| | ... | \| IMIX_v4_1 \| overhead=\${40} \|
| | ...
| | [Arguments] | ${nic_name} | ${framesize} | ${overhead}=${0}
| | ...
| | ${max_rate} | ${jumbo} = | Get Max Rate And Jumbo
| | ... | ${nic_name} | ${framesize} | ${overhead}
| | Run Keyword If | not ${jumbo} | Add no multi seg to all DUTs
| | Return From Keyword | ${max_rate} | ${jumbo}
