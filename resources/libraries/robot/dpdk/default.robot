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

| Start L2FWD on all DUTs
| | [Documentation] | Start the l2fwd with M worker threads and rxqueues N and
| | ... | optional jumbo frames support on all DUTs.
| | ... | - jumbo_frames argument is a boolean.
| | ...
| | [Arguments] | ${cpu_cnt} | ${rx_queues} | ${jumbo_frames}
| | ...
| | ${cpu_count_int} | Convert to Integer | ${cpu_cnt}
| | ${thr_count_int} | Convert to Integer | ${cpu_cnt}
| | ${dp_cores}= | Evaluate | ${cpu_count_int}+1
| | ${nb_cores}= | Set Variable | ${cpu_count_int}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${numa}= | Get interfaces numa node | ${nodes['${dut}']}
| | | ... | ${${dut}_if1} | ${${dut}_if2}
| | | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | | ${cpus}= | Cpu Range Per Node Str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${1} | cpu_cnt=${dp_cores} | smt_used=${smt_used}
| | | Start the l2fwd test | ${nodes['${dut}']} | ${cpus} | ${nb_cores}
| | | ... | ${rxqueues} | ${jumbo_frames}
| | | ${thr_count_int}= | Run keyword if | ${smt_used} |
| | | ... | Evaluate | int(${cpu_count_int}*2) | ELSE | Set variable
| | | ... | ${thr_count_int}
| | | Run keyword if | ${thr_count_int} > 1
| | | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | | Set Tags | ${thr_count_int}T${cpu_count_int}C

| Start L3FWD on all DUTs
| | [Documentation] | Start the l3fwd with M worker threads and rxqueues N and
| | ... | optional jumbo frames support on all DUTs.
| | ... | - jumbo_frames argument is a boolean.
| | ...
| | [Arguments] | ${cpu_cnt} | ${rx_queues} | ${jumbo_frames}
| | ...
| | ${cpu_count_int} | Convert to Integer | ${cpu_cnt}
| | ${thr_count_int} | Convert to Integer | ${cpu_cnt}
| | ${dp_cores}= | Evaluate | ${cpu_count_int}+1
| | ${nb_cores}= | Set Variable | ${cpu_count_int}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${numa}= | Get interfaces numa node | ${nodes['${dut}']}
| | | ... | ${${dut}_if1} | ${${dut}_if2}
| | | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | | ${cpus}= | Cpu List Per Node Str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${1} | cpu_cnt=${nb_cores} | smt_used=${smt_used}
| | | Start the l3fwd test | ${nodes} | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ${${dut}_if2} | ${nb_cores} | ${cpus} | ${rxqueues}
| | | ... | ${jumbo_frames}
| | | ${thr_count_int}= | Run keyword if | ${smt_used} |
| | | ... | Evaluate | int(${cpu_count_int}*2) | ELSE | Set variable
| | | ... | ${thr_count_int}
| | | Run keyword if | ${thr_count_int} > 1
| | | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | | Set Tags | ${thr_count_int}T${cpu_count_int}C
