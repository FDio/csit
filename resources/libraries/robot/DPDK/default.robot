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
| Library | resources.libraries.python.DPDK.L3fwdTest
| Library | Collections

*** Keywords ***
| Start L2FWD '${m}' worker threads and rxqueues '${n}' with jumbo frames '${b}'
| | [Documentation] | Start the l2fwd with M worker threads without HTT
| | ... | and rxqueues N and B (yes or no) jumbo frames in all DUTs.
| | ...
| | ${m_int}= | Convert To Integer | ${m}
| | ${cpu_cnt}= | Evaluate | ${m_int}+1
| | ${nb_cores}= | Convert to String | ${m}
| | ${rxqueues}= | Convert to String | ${n}
| | ${jumbo_frames}= | Convert to String | ${b}
| | ${dut1_numa}= | Get interfaces numa node | ${dut1}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${dut2_numa}= | Get interfaces numa node | ${dut2}
| | ... | ${dut2_if1} | ${dut2_if2}
| | ${dut1_cpus}= | Cpu Range Per Node Str | ${dut1} | ${dut1_numa}
| | ... | cpu_cnt=${cpu_cnt}
| | ${dut2_cpus}= | Cpu Range Per Node Str | ${dut2} | ${dut2_numa}
| | ... | cpu_cnt=${cpu_cnt}
| | Start the l2fwd test | ${dut1} | ${dut1_cpus} | ${nb_cores} | ${rxqueues}
| | ... | ${jumbo_frames}
| | Start the l2fwd test | ${dut2} | ${dut2_cpus} | ${nb_cores} | ${rxqueues}
| | ... | ${jumbo_frames}

| Start L3FWD '${m}' worker threads and rxqueues '${n}' with jumbo frames '${b}'
| | [Documentation] |  Start the l3fwd with M worker threads without HTT and rxqueues N
| | ...             |  and B(yes or no) jumbo frames in all DUTs
| | ${nb-cores}= | Catenate | ${m}
| | ${cpu}= | Run Keyword If | '${m}' == '1' | Catenate | 0x400
| | ...     | ELSE IF        | '${m}' == '2' | Catenate | 0xc00
| | ...     | ELSE IF        | '${m}' == '4' | Catenate | 0x3c00
| | ...     | ELSE IF        | '${m}' == '6' | Catenate | 0xfc00
| | ...     | ELSE IF        | '${m}' == '8' | Catenate | 0x3fc00
| | ...     | ELSE           | Fail | Not supported combination
| | ${lcores-list}= | Run Keyword If | '${m}' == '1' | Create List | 10
| | ...     | ELSE IF        | '${m}' == '2' | Create List | 10 | 11
| | ...     | ELSE IF        | '${m}' == '4' | Create List | 10 | 11 | 12 | 13
| | ...     | ELSE IF        | '${m}' == '6' | Create List | 10 | 11 | 12 | 13 | 14 | 15
| | ...     | ELSE IF        | '${m}' == '8' | Create List | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17
| | ...     | ELSE           | Fail | Not supported combination
| | ${rxqueues}= | Catenate | ${n}
| | ${jumbo_frames}= | Catenate | ${b}
| | Start l3fwd to all DUTs | ${cpu} | ${nb-cores} | ${lcores-list} | ${rxqueues} | ${jumbo_frames}

| Start l3fwd to all DUTs
| | [Documentation] | Setup worker threads and rxqueues in l3fwd startup
| | ...             | configuration to all DUTs
| | ...
| | ... | *Arguments:*
| | ... | - ${cpu} - CPU configuration. Type: string
| | ... | - ${nb-cores} - cores for the packet forwarding. Type: string
| | ... | - ${lcores-list} - the lcore list for the l3fwd routing. Type: list
| | ... | - ${rxqueues} - rxqueues configuration. Type: string
| | ... | - ${jumbo_frames} - Enable the jumbo frames or not. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Start l3fwd to all DUTs \| 0x402 \| 2 \| [1,10]
| | ... | \| 1 \| no
| | [Arguments] | ${cpu} | ${nb-cores} | ${lcores-list} | ${rxqueues} | ${jumbo_frames}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Start the l3fwd test | ${nodes} | ${nodes['${dut}']}
| | | ...            | ${cpu} | ${nb-cores} | ${lcores-list} | ${rxqueues} | ${jumbo_frames}
