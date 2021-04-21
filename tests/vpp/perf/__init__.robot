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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
|
| Library | resources.libraries.python.PapiExecutor.Disconnector
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.SetupFramework.CleanupFramework
| Library | resources.libraries.python.CpuUtils
|
| Suite Setup | Run Keywords | Setup Global Variables
| ... | AND | Setup Framework | ${nodes}
| ... | AND | Setup Corekeeper on All Nodes | ${nodes}
| ... | AND | Install Vpp on All Duts | ${nodes} | ${packages_dir}
| ... | AND | Verify Vpp on All Duts | ${nodes}
| ... | AND | Verify UIO Driver on all DUTs | ${nodes}
| ... | AND | Show Vpp Version on All Duts | ${nodes}
| ... | AND | Get CPU Info from All Nodes | ${nodes}
| ... | AND | Update All Interface Data on All Nodes | ${nodes}
| ... | skip_tg=${True}
|
| Suite Teardown | Run Keywords | Disconnect All Papi Connections
| ... | AND | Cleanup Framework | ${nodes}

*** Keywords ***
| Setup Global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| |
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - pre_stats - Statistics actions before traffic.
| | ... | - post_stats - Statistics actions after traffic.
| | ... | - pre_run_stats - Statistics actions during traffic before timer.
| | ... | - post_run_stats - Statistics actions during traffic after timer.
| | ... | - packages_dir - Path to directory where VPP packages are stored.
| |
| | ${pre_stats}= | Create List
| | ... | clear-show-runtime-with-traffic | vpp-clear-stats
| | ... | vpp-enable-packettrace | vpp-enable-elog
| | ${post_stats}= | Create List
| | ... | vpp-show-stats | vpp-show-packettrace | vpp-show-elog
| | ${pre_run_stats}= | Create List
| | ... | vpp-show-threads | vpp-clear-runtime
| | ${post_run_stats}= | Create List
| | ... | vpp-show-runtime | bash-perf-stat
| | Set Global Variable | ${pre_stats}
| | Set Global Variable | ${post_stats}
| | Set Global Variable | ${pre_run_stats}
| | Set Global Variable | ${post_run_stats}
| | Set Global Variable | ${packages_dir} | /tmp/openvpp-testing/download_dir/
| | Set Global Variable | ${nodes}
