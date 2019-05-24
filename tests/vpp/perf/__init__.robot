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
#| ... | AND | Install Vpp on All Duts | ${nodes} | ${packages_dir}
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
| | ... | - perf_vm_image - Guest VM disk image
| | ... | - perf_qemu_path - Path prefix to QEMU binary
| | ... | - use_tuned_cfs - Switch to set scheduler policy
| | ... | - qemu_build - Whether Qemu will be built
| | ... | - pkt_trace - Switch to enable packet trace for test
| | ... | - dut_stats - Switch to enable DUT statistics
| | ... | - uio_driver - Default UIO driver
| | ... | - plugins_to_enable - List of plugins to be enabled for test
| | ...
| | Set Global Variable | ${pkt_trace} | ${False}
| | Set Global Variable | ${dut_stats} | ${True}
| | @{plugins_to_enable}= | Create List | dpdk_plugin.so
| | Set Global Variable | @{plugins_to_enable}
| | Set Global Variable | ${packages_dir} | /tmp/openvpp-testing/download_dir/
