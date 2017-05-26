# Copyright (c) 2017 Cisco and/or its affiliates.
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

*** Variables***
# Honeycomb node to run tests on.
| ${node}= | ${nodes['DUT1']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/performance.robot
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.CpuUtils
| Suite Setup | Run Keywords
| ... | Setup performance global Variables
| ... | AND | Setup Framework | ${nodes}
| ... | AND | Setup All DUTs | ${nodes}
| ... | AND | Get CPU Layout from all nodes | ${nodes}
| ... | AND | Update All Interface Data On All Nodes
| ... | ${nodes} | skip_tg=${True} | numa_node=${True}
| ... | AND | 2-node HC Performance Suite Setup with DUT's NIC model
| ... | L3 | Intel-X520-DA2
| ... | AND | Blacklist VPP Interface | ${node} | ${dut_if1}
| ... | AND | Setup Honeycomb service on DUTs | ${node}
| ... | AND | Copy ODL client | ${node} | ${HC_ODL} | ~ | /tmp/install_dir
| ... | AND | Setup ODL Client Service On DUT | ${node}
| Suite Teardown | Run Keywords
| ... | Stop VPP Service on DUT | ${node}
| ... | AND | Undo Interface Blacklist | ${node} | ${interface}
| ... | AND | Stop honeycomb service on DUTs | ${node}
| ... | AND | Stop ODL service on DUT | ${node}

*** Keywords ***
| Setup performance global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - perf_trial_duration - Duration of traffic run [s]
| | ...
| | Set Global Variable | ${perf_trial_duration} | 10
