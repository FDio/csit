# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.SetupFramework.CleanupFramework
| Library | resources.libraries.python.CpuUtils
| ...
| Suite Setup | Run Keywords | Setup performance global Variables
| ... | AND | Setup Framework | ${nodes}
| ... | AND | Setup Corekeeper on All Nodes | ${nodes}
| ... | AND | Install Vpp on All Duts | ${nodes} | ${packages_dir}
| ... | AND | Verify Vpp on All Duts | ${nodes}
| ... | AND | Verify UIO Driver on all DUTs | ${nodes}
| ... | AND | Show Vpp Version on All Duts | ${nodes}
| ... | AND | Get CPU Layout from All nodes | ${nodes}
| ... | AND | Update All Interface Data on All Nodes | ${nodes}
| ... | skip_tg=${True} | numa_node=${True}
| ...
| Suite Teardown | Cleanup Framework | ${nodes}

*** Keywords ***
| Setup performance global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - dut_stats - Switch to enable DUT statistics.
| | ... | - dcr_uuid - Docker unique identificator of NF container (empty if
| | ... | DUT runs on bare metal).
| | ... | - packages_dir - Directory with VPP binary packages.
| | ...
| | Set Global Variable | ${dut_stats} | ${True}
| | Set Global Variable | ${dcr_uuid} | ${EMPTY}
| | Set Global Variable | ${packages_dir} | /tmp/openvpp-testing/download_dir/
