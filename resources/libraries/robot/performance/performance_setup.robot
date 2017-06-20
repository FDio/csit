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
| Resource | resources/libraries/robot/performance/performance_configuration.robot
| Resource | resources/libraries/robot/performance/performance_utils.robot
| Documentation | Performance suite keywords - Suite and test setups and
| ... | teardowns.

*** Keywords ***

# Keywords used in setups and teardowns

| Set variables in 2-node circular topology
| | [Documentation]
| | ... | Compute path for testing on two given nodes in circular
| | ... | topology and set corresponding suite variables.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - 1st DUT interface towards TG.
| | ... | - dut1_if2 - 2nd DUT interface towards TG.
| | ...
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_if1} | ${tg}= | First Interface
| | ${dut1_if1} | ${dut1}= | First Ingress Interface
| | ${dut1_if2} | ${dut1}= | Last Egress Interface
| | ${tg_if2} | ${tg}= | Last Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}

| Set variables in 3-node circular topology
| | [Documentation]
| | ... | Compute path for testing on three given nodes in circular
| | ... | topology and set corresponding suite variables.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - TG interface towards DUT1.
| | ... | - tg_if2 - TG interface towards DUT2.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2 - DUT2 node
| | ... | - dut2_if1 - DUT2 interface towards DUT1.
| | ... | - dut2_if2 - DUT2 interface towards TG.
| | ...
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ... | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}
| | Set Suite Variable | ${dut2}
| | Set Suite Variable | ${dut2_if1}
| | Set Suite Variable | ${dut2_if2}

| Set variables in 2-node circular topology with DUT interface model
| | [Documentation]
| | ... | Compute path for testing on two given nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - 1st DUT interface towards TG.
| | ... | - dut1_if2 - 2nd DUT interface towards TG.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set variables in 2-node circular topology with DUT interface model\
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
| | ${iface_model_list}= | Create list | ${iface_model}
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_if1} | ${tg}= | First Interface
| | ${dut1_if1} | ${dut1}= | First Ingress Interface
| | ${dut1_if2} | ${dut1}= | Last Egress Interface
| | ${tg_if2} | ${tg}= | Last Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}

| Set variables in 3-node circular topology with DUT interface model
| | [Documentation]
| | ... | Compute path for testing on three given nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - TG interface towards DUT1.
| | ... | - tg_if2 - TG interface towards DUT2.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2 - DUT2 node
| | ... | - dut2_if1 - DUT2 interface towards TG.
| | ... | - dut2_if2 - DUT2 interface towards DUT1.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set variables in 3-node circular topology with DUT interface model\
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
| | ${iface_model_list}= | Create list | ${iface_model}
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['DUT2']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${tg_if2} | ${tg}= | Next Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}
| | Set Suite Variable | ${dut2}
| | Set Suite Variable | ${dut2_if1}
| | Set Suite Variable | ${dut2_if2}

| Tear down guest VM with dpdk-testpmd
| | [Documentation]
| | ... | Stop all qemu processes with dpdk-testpmd running on ${dut_node}.
| | ... | Argument is dictionary of all qemu nodes running with its names.
| | ... | Dpdk-testpmd is stopped gracefully with printing stats.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dictionary
| | ... | - dut_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down guest VM with dpdk-testpmd \| ${node['DUT1']} \
| | ... | \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${dut_node} | ${dut_vm_refs}
| | ${vms_number}= | Get Length | ${dut_vm_refs}
| | ${index}= | Set Variable | ${0}
| | :FOR | ${vm_name} | IN | @{dut_vm_refs}
| | | ${vm}= | Get From Dictionary | ${dut_vm_refs} | ${vm_name}
| | | ${index}= | Evaluate | ${index} + 1
| | | Dpdk Testpmd Stop | ${vm}
| | | Run Keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | | Run Keyword | ${vm_name}.Qemu Clear Socks
| | | Run Keyword If | '${index}' == '${vms_number}' | ${vm_name}.Qemu Kill All

| Tear down guest VM
| | [Documentation]
| | ... | Stop all qemu processes running on ${dut_node}.
| | ... | Argument is dictionary of all qemu nodes running with its names.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dictionary
| | ... | - dut_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down guest VM \| ${node['DUT1']} \
| | ... | \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${dut_node} | ${dut_vm_refs}
| | ${vms_number}= | Get Length | ${dut_vm_refs}
| | ${index}= | Set Variable | ${0}
| | :FOR | ${vm_name} | IN | @{dut_vm_refs}
| | | ${vm}= | Get From Dictionary | ${dut_vm_refs} | ${vm_name}
| | | ${index}= | Evaluate | ${index} + 1
| | | Run Keyword | ${vm_name}.Qemu Set Node | ${dut_node}
| | | Run Keyword | ${vm_name}.Qemu Clear Socks
| | | Run Keyword If | '${index}' == '${vms_number}' | ${vm_name}.Qemu Kill All

# Suite setups

| Set up 2-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that setup default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 2-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | Show vpp version on all DUTs
| | Set variables in 2-node circular topology with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${topology_type}

| Set up 2-node-switched performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that setup default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ... | - tg_if1_dest_mac - Interface 1 destination MAC address. Type: string
| | ... | - tg_if2_dest_mac - Interface 2 destination MAC address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 2-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \
| | ... | \| 22:22:33:44:55:66 \| 22:22:33:44:55:55 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model} | ${tg_if1_dest_mac}
| | ... | ${tg_if2_dest_mac}
| | ...
| | Show vpp version on all DUTs
| | Set variables in 2-node circular topology with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${topology_type}
| | ... | ${tg_if1_dest_mac} | ${tg_if2_dest_mac}

| Set up 3-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that setup default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up 3-node performance topology with DUT's NIC model \| L2 \
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | Show vpp version on all DUTs
| | Set variables in 3-node circular topology with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${topology_type}

| Set up DPDK 2-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator. Initializes DPDK test
| | ... | environment.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up DPDK 2-node performance topology with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | Set variables in 2-node circular topology with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${topology_type}
| | Initialize DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Set up DPDK 3-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator. Initializes DPDK test
| | ... | environment.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 3-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | Set variables in 3-node circular topology with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${topology_type}
| | Initialize DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Initialize DPDK Environment | ${dut2} | ${dut2_if1} | ${dut2_if2}

| Set up IPSec performance test suite
| | [Documentation]
| | ... | Suite preparation phase that sets default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ... | Then it configures crypto device and kernel module on all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up IPSec performance test suite \| L2 \
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | Set up 3-node performance topology with DUT's NIC model
| | ... | ${topology_type} | ${nic_model}
| | Configure crypto device on all DUTs | force_init=${True}
| | Configure kernel module on all DUTs | igb_uio | force_load=${True}

# Suite teardowns

| Tear down 3-node performance topology
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ...
| | Teardown traffic generator | ${tg}

| Tear down 2-node performance topology
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ...
| | Teardown traffic generator | ${tg}

# Tests setups

| Set up performance test
| | [Documentation] | Common test setup for performance tests.
| | ...
| | Reset VAT History On All DUTs | ${nodes}
| | Create base startup configuration of VPP on all DUTs

# Tests teardowns

| Tear down performance discovery test
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance discovery test \| 4.0mpps \| 64 \
| | ... | \| 3-node-IPv4 \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${topology_type}
| | ...
| | Show VAT History On All DUTs | ${nodes}
| | Show statistics on all DUTs
| | Run Keyword If Test Failed
| | ... | Traffic should pass with no loss | ${perf_trial_duration} | ${rate}
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}

| Tear down performance ndrchk test
| | [Documentation] | Common test teardown for ndrchk performance tests.
| | ...
| | Show VAT History On All DUTs | ${nodes}
| | Show statistics on all DUTs

| Tear down performance pdrchk test
| | [Documentation] | Common test teardown for pdrchk performance tests.
| | ...
| | Show VAT History On All DUTs | ${nodes}
| | Show statistics on all DUTs

| Tear down performance test with vhost and VM with dpdk-testpmd
| | [Documentation] | Common test teardown for performance tests which use
| | ... | vhost(s) and VM(s) with dpdk-testpmd.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ... | - dut1_node - Node where to clean qemu. Type: dictionary
| | ... | - dut1_vm_refs - VM references on node. Type: dictionary
| | ... | - dut2_node - Node where to clean qemu. Type: dictionary
| | ... | - dut2_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance test with vhost and VM with dpdk-testpmd \
| | ... | \| 4.0mpps \| 64 \| 3-node-IPv4 \| ${node['DUT1']} \| ${dut_vm_refs} \
| | ... | \| ${node['DUT2']} \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${topology_type}
| | ... | ${dut1_node}=${None} | ${dut1_vm_refs}=${None}
| | ... | ${dut2_node}=${None} | ${dut2_vm_refs}=${None}
| | ...
| | Show VAT History On All DUTs | ${nodes}
| | Show VPP vhost on all DUTs
| | Show statistics on all DUTs
| | Run Keyword If Test Failed
| | ... | Traffic should pass with no loss | ${perf_trial_duration} | ${rate}
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}
| | Run keyword unless | ${dut1_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut1} | ${dut1_vm_refs}
| | Run keyword unless | ${dut2_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut2} | ${dut2_vm_refs}

| Tear down performance pdrchk test with vhost and VM with dpdk-testpmd
| | [Documentation] | Common test teardown for performance pdrchk tests which \
| | ... | use vhost(s) and VM(s) with dpdk-testpmd.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ... | - dut1_node - Node where to clean qemu. Type: dictionary
| | ... | - dut1_vm_refs - VM references on node. Type: dictionary
| | ... | - dut2_node - Node where to clean qemu. Type: dictionary
| | ... | - dut2_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance pdrchk test with vhost and VM with \
| | ... | dpdk-testpmd \| 4.0mpps \| 64 \| 3-node-IPv4 \| ${node['DUT1']} \
| | ... | \| ${dut_vm_refs} \| ${node['DUT2']} \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${topology_type}
| | ... | ${dut1_node}=${None} | ${dut1_vm_refs}=${None}
| | ... | ${dut2_node}=${None} | ${dut2_vm_refs}=${None}
| | ...
| | Show VAT History On All DUTs | ${nodes}
| | Show VPP vhost on all DUTs
| | Show statistics on all DUTs
| | Run keyword unless | ${dut1_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut1} | ${dut1_vm_refs}
| | Run keyword unless | ${dut2_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut2} | ${dut2_vm_refs}

| Tear down DPDK 3-node performance topology
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ... | Cleanup DPDK test environment.
| | ...
| | Teardown traffic generator | ${tg}
| | Cleanup DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Cleanup DPDK Environment | ${dut2} | ${dut2_if1} | ${dut2_if2}

| Tear down DPDK 2-node performance topology
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ... | Cleanup DPDK test environment.
| | ...
| | Teardown traffic generator | ${tg}
| | Cleanup DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Tear down performance discovery test with SNAT
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests with SNAT feature used.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - topology_type - Topology type. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance discovery test with SNAT \| 4.0mpps \| 64 \
| | ... | \| ${traffic_profile} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${traffic_profile}
| | ...
| | Tear down performance discovery test | ${rate}pps | ${framesize}
| | ... | ${traffic_profile}
| | Show SNAT verbose | ${dut1}
| | Show SNAT verbose | ${dut2}
