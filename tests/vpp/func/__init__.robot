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
| Suite Setup | Run Keywords | Setup Functional Global Variables
| ... | AND | Setup Framework | ${nodes}
| ... | AND | Install Vpp On All Duts | ${nodes} | ${VPP_PKG_DIR}
| ... | AND | Verify Vpp On All Duts | ${nodes}
| ... | AND | Setup All DUTs | ${nodes}
| ... | AND | Update All Interface Data On All Nodes | ${nodes}
| Suite Teardown | Cleanup Framework | ${nodes}

*** Keywords ***
| Setup Functional Global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across functional testing.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - vpp_pkg_dir - Path to directory where VPP packages are stored.
| | ...
| | Set Global Variable | ${VPP_PKG_DIR} | /scratch/vpp/
