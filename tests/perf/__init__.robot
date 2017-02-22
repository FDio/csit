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

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.CpuUtils
| Suite Setup | Run Keywords | Setup performance global Variables
| ...         | AND          | Setup Framework | ${nodes}
| ...         | AND          | Setup All DUTs | ${nodes}
| ...         | AND          | Get CPU Layout from all nodes | ${nodes}
| ...         | AND          | Update All Interface Data On All Nodes
| ...                        | ${nodes} | skip_tg=${True} | numa_node=${True}

*** Keywords ***
| Setup performance global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - perf_trial_duration - Duration of traffic run [s].
| | ... | - perf_pdr_loss_acceptance - Loss acceptance treshold
| | ... | - perf_pdr_loss_acceptance_type - Loss acceptance treshold type
| | ... | - perf_vm_image - Guest VM disk image
| | ...
| | Set Suite Variable | ${perf_trial_duration} | 10
| | Set Suite Variable | ${perf_pdr_loss_acceptance} | 0.5
| | Set Suite Variable | ${perf_pdr_loss_acceptance_type} | percentage
| | Set Suite Variable | ${perf_vm_image} | /var/lib/vm/csit-nested-1.6.img
