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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.DPDK.TestpmdTest
| Library | resources.libraries.python.DPDK.L3fwdTest
| Library | Collections

*** Keywords ***
| Start testpmd on all DUTs
| | [Documentation] | Start the testpmd with M worker threads and rxqueues N and
| | ... | jumbo support frames on/off on all DUTs.
| |
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues - Number of RX queues. Type: integer
| | ... | - jumbo_frames - Jumbo frames on/off: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Start testpmd on all DUTs \| ${1} \| ${1} \| ${False} \|
| |
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None} | ${jumbo_frames}=${False}
| |
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_cores}= | Evaluate | ${cpu_count_int}+1
| | FOR | ${dut} | IN | @{duts}
| | | ${numa}= | Get interfaces numa node | ${nodes['${dut}']}
| | | ... | ${${dut}_pf1}[0] | ${${dut}_pf2}[0]
| | | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | | ${cpus}= | Cpu List Per Node Str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${2} | cpu_cnt=${cpu_count_int} | smt_used=${smt_used}
| | | ${dp_count_int}= | Run keyword if | ${smt_used} |
| | | ... | Evaluate | int(${cpu_count_int}*2) | ELSE | Set variable
| | | ... | ${dp_count_int}
| | | ${rxq_ratio} = | Get Variable Value | \${rxq_ratio} | ${1}
| | | ${rxq_count_int}= | Run Keyword If | ${rx_queues}
| | | ... | Set variable | ${rx_queues}
| | | ... | ELSE | Evaluate | int(${dp_count_int}/${rxq_ratio})
| | | ${rxq_count_int}= | Run keyword if | ${rxq_count_int} == 0
| | | ... | Set variable | ${1}
| | | ... | ELSE | Set variable | ${rxq_count_int}
| | | Start testpmd
| | | ... | ${nodes['${dut}']} | ${${dut}_pf1}[0] | ${${dut}_pf2}[0]
| | | ... | ${cpus} | ${dp_count_int} | ${rxq_count_int} | ${jumbo_frames}
| | | ... | ${nic_rxq_size} | ${nic_txq_size}
| | | Run keyword if | ${dp_count_int} > 1
| | | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | | Set Tags | ${dp_count_int}T${cpu_count_int}C
| | END

| Start l3fwd on all DUTs
| | [Documentation] | Start the l3fwd with M worker threads and rxqueues N and
| | ... | jumbo support frames on/off on all DUTs.
| |
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues - Number of RX queues. Type: integer
| | ... | - jumbo_frames - Jumbo frames on/off: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Start l3fwd on all DUTs \| ${1} \| ${1} \| ${False} \|
| |
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None} | ${jumbo_frames}=${False}
| |
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_cores}= | Evaluate | ${cpu_count_int}+1
| | FOR | ${dut} | IN | @{duts}
| | | ${numa}= | Get interfaces numa node | ${nodes['${dut}']}
| | | ... | ${${dut}_pf1}[0] | ${${dut}_pf2}[0]
| | | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | | ${cpus}= | Cpu List Per Node Str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${2} | cpu_cnt=${cpu_count_int} | smt_used=${smt_used}
| | | ${dp_count_int}= | Run keyword if | ${smt_used} |
| | | ... | Evaluate | int(${cpu_count_int}*2) | ELSE | Set variable
| | | ... | ${dp_count_int}
| | | ${rxq_count_int}= | Run keyword if | ${rx_queues}
| | | ... | Set variable | ${rx_queues}
| | | ... | ELSE | Evaluate | int(${dp_count_int}/1)
| | | ${rxq_count_int}= | Run keyword if | ${rxq_count_int} == 0
| | | ... | Set variable | ${1}
| | | ... | ELSE | Set variable | ${rxq_count_int}
| | | Start l3fwd
| | | ... | ${nodes} | ${nodes['${dut}']} | ${${dut}_pf1}[0] | ${${dut}_pf2}[0]
| | | ... | ${cpus} | ${dp_count_int} | ${rxq_count_int} | ${jumbo_frames}
| | | Run keyword if | ${dp_count_int} > 1
| | | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | | Set Tags | ${dp_count_int}T${cpu_count_int}C
| | END
