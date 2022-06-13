# Copyright (c) 2022 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.DPDK.TestpmdCheck
| Library | resources.libraries.python.DPDK.L3fwdTest
| Library | resources.libraries.python.DPDK.L3fwdCheck
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
| | ... | - rxd - Number of RX descriptors. Type: integer
| | ... | - txd - Number of TX descriptors. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Start testpmd on all DUTs \| ${1} \| ${1} \| ${False} \|
| |
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None} | ${jumbo_frames}=${False}
| | ... | ${rxd}=${None} | ${txd}=${None}
| |
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_cores}= | Evaluate | ${cpu_count_int}+1
| | FOR | ${dut} | IN | @{duts}
| | | &{compute_resource_info}= | Get Affinity Vswitch
| | | ... | ${nodes} | ${dut} | ${phy_cores} | rx_queues=${rx_queues}
| | | ... | rxd=${rxd} | txd=${txd}
| | | Set Test Variable | &{compute_resource_info}
| | | Create compute resources variables
| | | Start testpmd
| | | ... | ${nodes['${dut}']} | ${${dut}_pf1}[0] | ${${dut}_pf2}[0]
| | | ... | ${cpu_dp} | ${dp_count_int} | ${rxq_count_int} | ${jumbo_frames}
| | | ... | ${nic_rxq_size} | ${nic_txq_size}
| | | Check testpmd
| | | ... | ${nodes['${dut}']}
| | END

| Start l3fwd on all DUTs
| | [Documentation] | Start the l3fwd with M worker threads and rxqueues N and
| | ... | jumbo support frames on/off on all DUTs.
| |
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues - Number of RX queues. Type: integer
| | ... | - jumbo_frames - Jumbo frames on/off: boolean
| | ... | - rxd - Number of RX descriptors. Type: integer
| | ... | - txd - Number of TX descriptors. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Start l3fwd on all DUTs \| ${1} \| ${1} \| ${False} \|
| |
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None} | ${jumbo_frames}=${False}
| | ... | ${rxd}=${None} | ${txd}=${None}
| |
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_count_int} | Convert to Integer | ${phy_cores}
| | ${dp_cores}= | Evaluate | ${cpu_count_int}+1
| | FOR | ${dut} | IN | @{duts}
| | | &{compute_resource_info}= | Get Affinity Vswitch
| | | ... | ${nodes} | ${dut} | ${phy_cores} | rx_queues=${rx_queues}
| | | ... | rxd=${rxd} | txd=${txd}
| | | Set Test Variable | &{compute_resource_info}
| | | Create compute resources variables
| | | Start l3fwd
| | | ... | ${nodes} | ${nodes['${dut}']} | ${${dut}_pf1}[0] | ${${dut}_pf2}[0]
| | | ... | ${cpu_dp} | ${dp_count_int} | ${rxq_count_int} | ${jumbo_frames}
| | | Check l3fwd
| | | ... | ${nodes['${dut}']}
| | END
