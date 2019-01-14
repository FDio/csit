# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Suite Setup | Run Keywords | Setup performance global Variables
| ...         | AND          | Setup Framework | ${nodes}
| ...         | AND          | Install Vpp On All Duts | ${nodes}
| ...         | ${packages_dir} | ${vpp_rpm_pkgs} | ${vpp_deb_pkgs}
| ...         | AND          | Verify Vpp On All Duts | ${nodes}
| ...         | AND          | Verify UIO Driver on all DUTs | ${nodes}
| ...         | AND          | Setup All DUTs | ${nodes}
| ...         | AND          | Show Vpp Version On All Duts | ${nodes}
| ...         | AND          | Get CPU Layout from all nodes | ${nodes}
| ...         | AND          | Update All Interface Data On All Nodes
| ...                        | ${nodes} | skip_tg=${True} | numa_node=${True}
#| Suite Teardown | Cleanup Framework | ${nodes}

*** Keywords ***
| Setup performance global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - perf_pdr_loss_acceptance - Loss acceptance treshold
| | ... | - perf_pdr_loss_acceptance_type - Loss acceptance treshold type
| | ... | - perf_vm_image - Guest VM disk image
| | ... | - perf_qemu_path - Path prefix to QEMU binary
| | ... | - use_tuned_cfs - Switch to set scheduler policy
| | ... | - qemu_build - Whether Qemu will be built
| | ... | - pkt_trace - Switch to enable packet trace for test
| | ... | - dut_stats - Switch to enable DUT statistics
| | ... | - uio_driver - Default UIO driver
| | ... | - plugins_to_enable - List of plugins to be enabled for test
| | ...
| | Set Global Variable | ${perf_pdr_loss_acceptance} | 0.5
| | Set Global Variable | ${perf_pdr_loss_acceptance_type} | percentage
| | Set Global Variable | ${perf_vm_image} | /var/lib/vm/csit-nested-1.7.img
| | Set Global Variable | ${perf_qemu_path} | /opt/qemu-2.11.2
| | Set Global Variable | ${qemu_build} | ${True}
| | Set Global Variable | ${pkt_trace} | ${False}
| | Set Global Variable | ${dut_stats} | ${True}
| | @{plugins_to_enable}= | Create List | dpdk_plugin.so
| | Set Global Variable | @{plugins_to_enable}
| | Set Global Variable | ${packages_dir} | /tmp/install_dir/
| | @{vpp_rpm_pkgs}= | Create List | vpp | vpp-devel | vpp-lib | vpp-plugins
| | Set Global Variable | ${vpp_rpm_pkgs}
| | @{vpp_deb_pkgs}= | Create List | vpp | vpp-dbg | vpp-dev | vpp-lib
| | ... | vpp-plugins | vpp-api-python
| | Set Global Variable | ${vpp_deb_pkgs}
