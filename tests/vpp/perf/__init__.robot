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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.CpuUtils
| Suite Setup | Run Keywords | Setup performance global Variables
| ...         | AND          | Setup Framework | ${nodes}
| ...         | AND          | Setup All DUTs | ${nodes}
| ...         | AND          | Show Vpp Version On All Duts | ${nodes}
| ...         | AND          | Get CPU Layout from all nodes | ${nodes}
| ...         | AND          | Update All Interface Data On All Nodes
| ...                        | ${nodes} | skip_tg=${True} | numa_node=${True}

*** Keywords ***
| Setup performance global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - perf_trial_duration - Duration of traffic run [s]
| | ... | - perf_pdr_loss_acceptance - Loss acceptance treshold
| | ... | - perf_pdr_loss_acceptance_type - Loss acceptance treshold type
| | ... | - perf_vm_image - Guest VM disk image
| | ... | - perf_qemu_path - Path prefix to QEMU binary
| | ... | - use_tuned_cfs - Switch to set scheduler policy
| | ... | - qemu_build - Whether Qemu will be built
| | ... | - pkt_trace - Switch to enable packet trace for test
| | ... | - plugins_to_disable - List of plugins to be disabled for test
| | ...
| | Set Global Variable | ${perf_trial_duration} | 10
| | Set Global Variable | ${perf_pdr_loss_acceptance} | 0.5
| | Set Global Variable | ${perf_pdr_loss_acceptance_type} | percentage
| | Set Global Variable | ${perf_vm_image} | /var/lib/vm/csit-nested-1.7.img
| | Set Global Variable | ${perf_qemu_path} | /opt/qemu-2.5.0
| | Set Global Variable | ${use_tuned_cfs} | ${False}
| | Set Global Variable | ${qemu_build} | ${True}
| | Set Global Variable | ${pkt_trace} | ${False}
| | @{plugins_to_disable}= | Create List
| | ... | acl_plugin.so
| | ... | cdp_plugin.so
| | ... | flowprobe_plugin.so
| | ... | gbp_plugin.so
| | ... | gtpu_plugin.so
| | ... | igmp_plugin.so
| | ... | ila_plugin.so
| | ... | ioam_plugin.so
| | ... | ixge_plugin.so
| | ... | kubeproxy_plugin.so
| | ... | l2e_plugin.so
| | ... | lb_plugin.so
| | ... | memif_plugin.so
| | ... | nat_plugin.so
| | ... | pppoe_plugin.so
| | ... | srv6ad_plugin.so
| | ... | srv6am_plugin.so
| | ... | srv6as_plugin.so
# | | ... | sixrd_plugin.so
| | ... | stn_plugin.so
| | ... | tlsmbedtls_plugin.so
| | ... | tlsopenssl_plugin.so
| | Set Global Variable | @{plugins_to_disable}
