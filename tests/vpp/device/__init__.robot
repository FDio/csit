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
| Suite Setup | Run Keywords | Setup Global Variables
| ... | AND | Setup Framework | ${nodes}
| ... | AND | Install Vpp On All Duts | ${nodes} | ${packages_dir}
| ... | AND | Verify Vpp On All Duts | ${nodes}
| ... | AND | Get CPU Layout from all nodes | ${nodes}
| ... | AND | Update All Interface Data On All Nodes | ${nodes}
| ...       | skip_tg_udev=${True}
| ...
| Suite Teardown | Cleanup Framework | ${nodes}

*** Keywords ***
| Setup Global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across device testing.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - pkt_trace - Switch to enable packet trace for test
| | ... | - dut_stats - Switch to enable DUT statistics
| | ... | - vm_image - Guest VM disk image.
| | ... | - packages_dir - Path to directory where VPP packages are stored.
| | ... | - vpp_rpm_pkgs - Package list for CentOS based system.
| | ... | - vpp_deb_pkgs - Package list for Debian based system.
| | ...
| | Set Global Variable | ${pkt_trace} | ${False}
| | Set Global Variable | ${dut_stats} | ${True}
| | Set Global Variable | ${vm_image} | /var/lib/vm/csit-nested-1.7.img
| | Set Global Variable | ${packages_dir} | /tmp/openvpp-testing/download_dir/
