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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
|
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.SetupFramework.CleanupFramework
| Library | resources.libraries.python.CpuUtils
|
| Suite Setup | Run Keywords | Start Suite Setup Export
| ... | AND | Setup Global Variables
| ... | AND | Setup Framework | ${nodes}
| ... | AND | Get CPU Info from All Nodes | ${nodes}
| ... | AND | Update All Interface Data on All Nodes | ${nodes}
| ... | skip_tg=${True} | skip_vpp=${True}
| ... | AND | Finalize Suite Setup Export
|
| Suite Teardown | Run Keywords | Start Suite Teardown Export
| ... | AND | Cleanup Framework | ${nodes}
| ... | AND | Finalize Suite Teardown Export

*** Keywords ***
| Setup Global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| |
| | ${stat_runtime}= | Create List | noop
| | ${stat_pre_trial}= | Create List | noop
| | ${stat_post_trial}= | Create List | noop
| | Set Global Variable | ${stat_runtime}
| | Set Global Variable | ${stat_pre_trial}
| | Set Global Variable | ${stat_post_trial}
| | Set Global Variable | ${nodes}
