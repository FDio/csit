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
| | [Documentation] | Start the l2fwd with M worker threads without SMT
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
| | ... | skip_cnt=${1} | cpu_cnt=${cpu_cnt}
| | ${dut2_cpus}= | Cpu Range Per Node Str | ${dut2} | ${dut2_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${cpu_cnt}
| | Start the l2fwd test | ${dut1} | ${dut1_cpus} | ${nb_cores} | ${rxqueues}
| | ... | ${jumbo_frames}
| | Start the l2fwd test | ${dut2} | ${dut2_cpus} | ${nb_cores} | ${rxqueues}
| | ... | ${jumbo_frames}

| Start L2FWD '${m}' worker threads using SMT and rxqueues '${n}' with jumbo frames '${b}'
| | [Documentation] | Start the l2fwd with M worker threads with SMT
| | ... | and rxqueues N and B (yes or no) jumbo frames in all DUTs.
| | ...
| | ${m_int}= | Convert To Integer | ${m}
| | ${cpu_cnt}= | Evaluate | ${m_int}+1
| | ${nb_cores_int}= | Evaluate | ${m_int}*2
| | ${nb_cores}= | Convert to String | ${nb_cores_int}
| | ${rxqueues}= | Convert to String | ${n}
| | ${jumbo_frames}= | Convert to String | ${b}
| | ${dut1_numa}= | Get interfaces numa node | ${dut1}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${dut2_numa}= | Get interfaces numa node | ${dut2}
| | ... | ${dut2_if1} | ${dut2_if2}
| | ${dut1_cpus}= | Cpu Range Per Node Str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${cpu_cnt} | smt_used=${True}
| | ${dut2_cpus}= | Cpu Range Per Node Str | ${dut2} | ${dut2_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${cpu_cnt} | smt_used=${True}
| | Start the l2fwd test | ${dut1} | ${dut1_cpus} | ${nb_cores} | ${rxqueues}
| | ... | ${jumbo_frames}
| | Start the l2fwd test | ${dut2} | ${dut2_cpus} | ${nb_cores} | ${rxqueues}
| | ... | ${jumbo_frames}

| Start L3FWD '${m}' worker threads and rxqueues '${n}' with jumbo frames '${b}'
| | [Documentation] |  Start the l3fwd with M worker threads without HTT and rxqueues N
| | ...             |  and B(yes or no) jumbo frames in all DUTs
| | ${cpu_cnt}= | Convert To Integer | ${m}
| | ${nb_cores}= | Convert to String | ${m}
| | ${rxqueues}= | Convert to String | ${n}
| | ${jumbo_frames}= | Convert to String | ${b}
| | ${dut1_numa}= | Get interfaces numa node | ${dut1}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${dut2_numa}= | Get interfaces numa node | ${dut2}
| | ... | ${dut2_if1} | ${dut2_if2}
| | ${dut1_cpus}= | Cpu List Per Node Str | ${dut1} | ${dut1_numa}
| | ... | cpu_cnt=${cpu_cnt}
| | ${dut2_cpus}= | Cpu List Per Node Str | ${dut2} | ${dut2_numa}
| | ... | cpu_cnt=${cpu_cnt}
| | Start the l3fwd test | ${nodes} | ${dut1} | ${nb_cores} | ${dut1_cpus}
| | ... | ${rxqueues} | ${jumbo_frames}
| | Start the l3fwd test | ${nodes} | ${dut2} | ${nb_cores} | ${dut2_cpus}
| | ... | ${rxqueues} | ${jumbo_frames}
