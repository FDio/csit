# Copyright (c) 2016 Cisco and/or its affiliates.
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
| Variables | resources/libraries/python/topology.py
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.TGSetup
| Library | resources.libraries.python.DPDK.L2fwdTest
| Library | Collections

*** Keywords ***
| Start L2FWD '${m}' worker threads and rxqueues '${n}' with jumbo frames '${b}'
| | [Documentation] |  Start the l2fwd with M worker threads without HTT
| | ...             |  and rxqueues N and B(yes or no) jumbo frames in all DUTs
| | ${nb-cores}= | Catenate | ${m}
| | ${cpu}= | Run Keyword If | '${m}' == '1' | Catenate | 0x3
| | ...     | ELSE IF        | '${m}' == '2' | Catenate | 0x403
| | ...     | ELSE IF        | '${m}' == '4' | Catenate | 0xc07
| | ...     | ELSE IF        | '${m}' == '6' | Catenate | 0x1c0f
| | ...     | ELSE IF        | '${m}' == '8' | Catenate | 0x3c1f
| | ...     | ELSE           | Fail | Not supported combination
| | ${rxqueues}= | Catenate | ${n}
| | ${jumbo_frames}= | Catenate | ${b}
| | Start l2fwd to all DUTs | ${cpu} | ${nb-cores}
| | ...     | ${rxqueues} | ${jumbo_frames}

| Start l2fwd to all DUTs
| | [Documentation] | Setup worker threads and rxqueues in l2fwd startup
| | ...             | configuration to all DUTs
| | ...
| | ... | *Arguments:*
| | ... | - ${cpu} - CPU configuration. Type: string
| | ... | - ${nb-cores} - cores for the packet forwarding. Type: string
| | ... | - ${rxqueues} - rxqueues configuration. Type: string
| | ... | - ${jumbo_frames} - Enable the jumbo frames or not. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Start l2fwd to all DUTs \| 0x403 \| 2 \
| | ... | \| 1 \| no
| | [Arguments] | ${cpu} | ${nb-cores} | ${rxqueues} | ${jumbo_frames}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Start the l2fwd test | ${nodes['${dut}']}
| | | ...            | ${cpu} | ${nb-cores} | ${rxqueues} | ${jumbo_frames}

