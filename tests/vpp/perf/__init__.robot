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
| Library | resources.libraries.python.PapiExecutor.Disconnector
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.SetupFramework.CleanupFramework
| Library | resources.libraries.python.CpuUtils
|
| Suite Setup | Run Keywords | Start Suite Setup Export
| ... | AND | Setup Global Variables
| ... | AND | Setup Framework | ${nodes}
| ... | AND | Setup Corekeeper on All Nodes | ${nodes}
| ... | AND | Install Vpp on All Duts | ${nodes} | ${packages_dir}
| ... | AND | Verify Vpp on All Duts | ${nodes}
| ... | AND | Verify UIO Driver on all DUTs | ${nodes}
| ... | AND | Show Vpp Version on All Duts | ${nodes}
| ... | AND | Get CPU Info from All Nodes | ${nodes}
| ... | AND | Update All Interface Data on All Nodes | ${nodes}
| ... | skip_tg=${True}
| ... | AND | Finalize Suite Setup Export
|
| Suite Teardown | Run Keywords | Start Suite Teardown Export
| ... | AND | Disconnect All Papi Connections
| ... | AND | Cleanup Framework | ${nodes}
| ... | AND | Finalize Suite Teardown Export

*** Keywords ***
| Setup Global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| |
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - stat_runtime - Statistics actions within traffic trial.
| | ... | - stat_pre_trial - Statistics actions before traffic trials.
| | ... | - stat_post_trial - Statistics actions after traffic trials.
| | ... | - packages_dir - Path to directory where VPP packages are stored.
| |
| | ${stat_runtime}= | Create List
| | ... | vpp-runtime | bpf-runtime
| | ${stat_pre_trial}= | Create List
| | ... | vpp-clear-stats | vpp-enable-packettrace
| | ${stat_post_trial}= | Create List
| | ... | vpp-show-stats | vpp-show-packettrace
| | Set Global Variable | ${stat_runtime}
| | Set Global Variable | ${stat_pre_trial}
| | Set Global Variable | ${stat_post_trial}
| | Set Global Variable | ${packages_dir} | /tmp/openvpp-testing/download_dir/
| | Set Global Variable | ${nodes}
