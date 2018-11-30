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
| Resource | resources/libraries/robot/performance/performance_setup.robot
| Library | resources.libraries.python.QemuUtils
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | SOAK
| ... | NIC_Intel-X710 | ETH | L2XCFWD | BASE | VHOST | 1VM | VHOST_256
| ...
| Suite Setup | Set up 3-node performance topology with DUT's NIC model
| ... | L2 | Intel-X710
| Suite Teardown | Tear down 3-node performance topology
| ...
| Test Setup | Set up performance test
| Test Teardown | Tear down performance mrr test with vhost and VM with dpdk-testpmd
| ... | dut1_node=${dut1} | dut1_vm_refs=${dut1_vm_refs}
| ... | dut2_node=${dut2} | dut2_vm_refs=${dut2_vm_refs}
| ...
| Test Template | Local Template
| ...
| Documentation | *Raw results L2XC test cases with vhost*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 for L2 switching of IPv4. 802.1q
| ... | tagging is applied on link between DUT1 and DUT2.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2 cross-
| ... | connect. Qemu Guest is connected to VPP via vhost-user interfaces.
| ... | Guest is running DPDK testpmd interconnecting vhost-user interfaces
| ... | using 5 cores pinned to cpus 5-9 and 2048M memory. Testpmd is using
| ... | socket-mem=1024M (512x2M hugepages), 5 cores (1 main core and 4 cores
| ... | dedicated for io), forwarding mode is set to io, rxd/txd=256,
| ... | burst=64. DUT1, DUT2 are tested with 2p10GE NIC X710 by Intel.
| ... | *[Ver] TG verification:* Perform PLRsearch to find critical load.

*** Variables ***
# X710 bandwidth limit
| ${s_limit}= | ${10000000000}
# Traffic profile:
| ${traffic_profile}= | trex-sl-3n-ethip4-ip4src254

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT runs L2XC switching config.
| | ... | Each DUT uses ${phy_cores} physical core(s) for worker threads.
| | ... | [Ver] Perform PLRsearch to find critical load.
| | ...
| | ... | *Arguments:*
| | ... | - framesize - Framesize in Bytes in integer or string (IMIX_v4_1).
| | ... | Type: integer, string
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${framesize} | ${phy_cores} | ${rxq}=${None}
| | ...
| | ${dut1_vm_refs}= | Create Dictionary
| | ${dut2_vm_refs}= | Create Dictionary
| | Set Test Variable | ${dut1_vm_refs}
| | Set Test Variable | ${dut2_vm_refs}
| | ...
| | Given Add worker threads and rxqueues to all DUTs | ${phy_cores} | ${rxq}
| | And Add PCI devices to all DUTs
| | ${max_rate} | ${jumbo} = | Get Max Rate And Jumbo And Handle Multi Seg
| | ... | ${s_limit} | ${framesize}
| | And Apply startup configuration on all VPP DUTs
| | When Initialize L2 xconnect with Vhost-User | vm_count=${1}
| | And Configure guest VMs with dpdk-testpmd connected via vhost-user
| | ... | vm_count=${1} | jumbo=${jumbo} | perf_qemu_qsz=${256}
| | ... | use_tuned_cfs=${False}
| | Then Find critical load using PLRsearch
| | ... | ${framesize} | ${traffic_profile} | ${10000} | ${max_rate}

*** Test Cases ***
| tc01-64B-1c-eth-l2xcbase-eth-2vhostvr256-1vm-soak
| | [Tags] | 64B | 1C
| | framesize=${64} | phy_cores=${1}
