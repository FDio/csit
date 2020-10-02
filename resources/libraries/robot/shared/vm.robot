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
| Library | resources.libraries.python.InterfaceUtil
|
| Documentation | Keywords related to vm lifecycle management

*** Keywords ***
| Configure chains of NFs connected via vhost-user
| | [Documentation]
| | ... | Start 1..N chains of 1..N QEMU guests (VNFs) with two vhost-user\
| | ... | interfaces and interconnecting NF.
| |
| | ... | *Arguments:*
| | ... | - nf_chains - Number of chains of NFs. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ... | - jumbo - Jumbo frames are used (True) or are not used (False)
| | ... | in the test. Type: boolean
| | ... | - perf_qemu_qsz - Virtio Queue Size. Type: integer
| | ... | - use_tuned_cfs - Set True if CFS RR should be used for Qemu SMP.
| | ... | Type: boolean
| | ... | - auto_scale - Whether to use same amount of RXQs for memif interface
| | ... | in containers as vswitch, otherwise use single RXQ. Type: boolean
| | ... | - fixed_auto_scale - Enable fixed auto_scale (nf_dtc). Type: boolean
| | ... | - vnf - Network function as a payload. Type: string
| | ... | - pinning - Whether to pin QEMU VMs to specific cores
| |
| | ... | *Example:*
| |
| | ... | \| Configure chains of VMs connected via vhost-user
| | ... | \| 1 \| 1 \| False \| 1024 \| False \| False \| vpp \| True \|
| |
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${jumbo}=${False}
| | ... | ${perf_qemu_qsz}=${1024} | ${use_tuned_cfs}=${False}
| | ... | ${auto_scale}=${True} | ${fixed_auto_scale}=${False} | ${vnf}=vpp
| | ... | ${pinning}=${True}
| |
| | ${enable_gso} = | Get Variable Value | ${enable_gso} | ${False}
| | ${enable_csum} = | Get Variable Value | ${enable_csum} | ${False}
| | ${virtio_feature_mask}= | Create Virtio feature mask
| | ... | gso=${enable_gso} | csum=${enable_csum}
| | Import Library | resources.libraries.python.QemuManager | ${nodes}
| | ... | WITH NAME | vnf_manager
| | Run Keyword | vnf_manager.Construct VMs on all nodes
| | ... | nf_chains=${nf_chains} | nf_nodes=${nf_nodes} | jumbo=${jumbo}
| | ... | perf_qemu_qsz=${perf_qemu_qsz} | use_tuned_cfs=${use_tuned_cfs}
| | ... | auto_scale=${auto_scale} | fixed_auto_scale=${fixed_auto_scale}
| | ... | vnf=${vnf} | tg_pf1_mac=${TG_pf1_mac}[0] | tg_pf2_mac=${TG_pf2_mac}[0]
| | ... | vs_dtc=${cpu_count_int} | nf_dtc=${nf_dtc} | nf_dtcr=${nf_dtcr}
| | ... | rxq_count_int=${rxq_count_int}
| | ... | virtio_feature_mask=${virtio_feature_mask}
| | ${cpu_wt}= | Run Keyword | vnf_manager.Start All VMs | pinning=${pinning}
| | ${cpu_alloc_str}= | Catenate | SEPARATOR=, | ${cpu_alloc_str} | ${cpu_wt}
| | Set Test Variable | ${cpu_alloc_str}
| | All VPP Interfaces Ready Wait | ${nodes} | retries=${300}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=Virtual

| Configure chains of NFs connected via vhost-user on single node
| | [Documentation]
| | ... | Start 1..N chains of 1..N QEMU guests (VNFs) with two vhost-user\
| | ... | interfaces and interconnecting NF on single DUT node.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node. Type: dictionary
| | ... | - nf_chains - Number of chains of NFs. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ... | - jumbo - Jumbo frames are used (True) or are not used (False)
| | ... | in the test. Type: boolean
| | ... | - perf_qemu_qsz - Virtio Queue Size. Type: integer
| | ... | - use_tuned_cfs - Set True if CFS RR should be used for Qemu SMP.
| | ... | Type: boolean
| | ... | - auto_scale - Whether to use same amount of RXQs for memif interface
| | ... | in containers as vswitch, otherwise use single RXQ. Type: boolean
| | ... | - fixed_auto_scale - Enable override auto_scale. Type: boolean
| | ... | - vnf - Network function as a payload. Type: string
| | ... | - pinning - Whether to pin QEMU VMs to specific cores
| | ... | - validate - Validate interfaces are up. Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Configure chains of NFs connected via vhost-user on single node
| | ... | \| DUT1 \| 1 \| 1 \| False \| 1024 \| False \| False \| vpp \|
| | ... | True \|
| |
| | [Arguments] | ${node} | ${nf_chains}=${1} | ${nf_nodes}=${1}
| | ... | ${jumbo}=${False} | ${perf_qemu_qsz}=${1024}
| | ... | ${use_tuned_cfs}=${False} | ${auto_scale}=${True}
| | ... | ${fixed_auto_scale}=${False} | ${vnf}=vpp | ${pinning}=${True}
| | ... | ${validate}=${True}
| |
| | ${enable_gso}= | Get Variable Value | ${enable_gso} | ${False}
| | ${enable_csum}= | Get Variable Value | ${enable_csum} | ${False}
| | ${virtio_feature_mask}= | Create Virtio feature mask
| | ... | gso=${enable_gso} | csum=${enable_csum}
| | Import Library | resources.libraries.python.QemuManager | ${nodes}
| | ... | WITH NAME | vnf_manager
| | Run Keyword | vnf_manager.Initialize
| | Run Keyword | vnf_manager.Construct VMs on node
| | ... | node=${node}
| | ... | nf_chains=${nf_chains} | nf_nodes=${nf_nodes} | jumbo=${jumbo}
| | ... | perf_qemu_qsz=${perf_qemu_qsz} | use_tuned_cfs=${use_tuned_cfs}
| | ... | auto_scale=${auto_scale} | fixed_auto_scale=${fixed_auto_scale}
| | ... | vnf=${vnf} | tg_pf1_mac=${TG_pf1_mac}[0] | tg_pf2_mac=${TG_pf2_mac}[0]
| | ... | vs_dtc=${cpu_count_int} | nf_dtc=${nf_dtc} | nf_dtcr=${nf_dtcr}
| | ... | rxq_count_int=${rxq_count_int}
| | ... | virtio_feature_mask=${virtio_feature_mask}
| | ${cpu_wt}= | Run Keyword | vnf_manager.Start All VMs | pinning=${pinning}
| | ${cpu_alloc_str}= | Catenate | SEPARATOR=, | ${cpu_alloc_str} | ${cpu_wt}
| | Set Test Variable | ${cpu_alloc_str}
| | Run Keyword If | ${validate}
| | ... | All VPP Interfaces Ready Wait | ${nodes} | retries=${300}
| | VPP round robin RX placement on all DUTs | ${nodes} | prefix=Virtual

| Configure chains of NFs connected via passtrough
| | [Documentation]
| | ... | Start 1..N chains of 1..N QEMU guests (VNFs) with two pci passtrough\
| | ... | interfaces and interconnecting NF.
| |
| | ... | *Arguments:*
| | ... | - nf_chains - Number of chains of NFs. Type: integer
| | ... | - nf_nodes - Number of NFs nodes per chain. Type: integer
| | ... | - jumbo - Jumbo frames are used (True) or are not used (False)
| | ... | in the test. Type: boolean
| | ... | - perf_qemu_qsz - Virtio Queue Size. Type: integer
| | ... | - use_tuned_cfs - Set True if CFS RR should be used for Qemu SMP.
| | ... | Type: boolean
| | ... | - auto_scale - Whether to use same amount of RXQs for memif interface
| | ... | in containers as vswitch, otherwise use single RXQ. Type: boolean
| | ... | - fixed_auto_scale - Enable override auto_scale. Type: boolean
| | ... | - vnf - Network function as a payload. Type: string
| | ... | - pinning - Whether to pin QEMU VMs to specific cores
| |
| | ... | *Example:*
| |
| | ... | \| Configure chains of VMs connected via passtrough
| | ... | \| 1 \| 1 \| False \| 1024 \| False \| False \| vpp \| True \|
| |
| | [Arguments] | ${nf_chains}=${1} | ${nf_nodes}=${1} | ${jumbo}=${False}
| | ... | ${perf_qemu_qsz}=${1024} | ${use_tuned_cfs}=${False}
| | ... | ${auto_scale}=${True} | ${fixed_auto_scale}=${False} | ${vnf}=vpp
| | ... | ${pinning}=${True}
| |
| | ${enable_gso} = | Get Variable Value | ${enable_gso} | ${False}
| | ${enable_csum} = | Get Variable Value | ${enable_csum} | ${False}
| | ${virtio_feature_mask}= | Create Virtio feature mask
| | ... | gso=${enable_gso} | csum=${enable_csum}
| | Import Library | resources.libraries.python.QemuManager | ${nodes}
| | ... | WITH NAME | vnf_manager
| | Run Keyword | vnf_manager.Construct VMs on all nodes
| | ... | nf_chains=${nf_chains} | nf_nodes=${nf_nodes} | jumbo=${jumbo}
| | ... | perf_qemu_qsz=${perf_qemu_qsz} | use_tuned_cfs=${use_tuned_cfs}
| | ... | auto_scale=${auto_scale} | fixed_auto_scale=${fixed_auto_scale}
| | ... | vnf=${vnf} | tg_pf1_mac=${TG_pf1_mac}[0] | tg_pf2_mac=${TG_pf2_mac}[0]
| | ... | vs_dtc=${cpu_count_int} | nf_dtc=${nf_dtc} | nf_dtcr=${nf_dtcr}
| | ... | rxq_count_int=${rxq_count_int}
| | ... | virtio_feature_mask=${virtio_feature_mask}
| | ... | if1=${DUT1_${int}1}[0] | if2=${DUT1_${int}2}[0]
| | ${cpu_wt}= | Run Keyword | vnf_manager.Start All VMs | pinning=${pinning}
| | ${cpu_alloc_str}= | Catenate | SEPARATOR=, | ${cpu_alloc_str} | ${cpu_wt}
| | Set Test Variable | ${cpu_alloc_str}
