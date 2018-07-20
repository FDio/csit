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
| Library | resources.libraries.python.DUTSetup
| Library | resources.tools.wrk.wrk
| Resource | resources/libraries/robot/performance/performance_configuration.robot
| Resource | resources/libraries/robot/performance/performance_utils.robot
| Resource | resources/libraries/robot/tcp/tcp_setup.robot
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

| Set up SRIOV 2-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that sets default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ... | It configures PCI device with VFs on all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ... | - vf_driver - Virtual function driver. Type: string
| | ... | - numvfs - Number of VFs. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up SRIOV 2-node performance topology with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \| AVF \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model} | ${vf_driver}
| | ... | ${numvfs}=${1}
| | ...
| | Set variables in 2-node circular topology with DUT interface model
| | ... | ${nic_model}
| | Run Keyword If | '${vf_driver}' == 'AVF'
| | ... | Configure AVF interfaces on all DUTs | numvfs=${numvfs}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1_vf0} | ${dut1} | ${dut1_if2_vf0}
| | ... | ${topology_type}

| Set up SRIOV 3-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that sets default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ... | It configures PCI device with VFs on all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ... | - vf_driver - Virtual function driver. Type: string
| | ... | - numvfs - Number of VFs. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up SRIOV 3-node performance topology with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \| AVF \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model} | ${vf_driver}
| | ... | ${numvfs}=${1}
| | ...
| | Set variables in 3-node circular topology with DUT interface model
| | ... | ${nic_model}
| | Run Keyword If | '${vf_driver}' == 'AVF'
| | ... | Configure AVF interfaces on all DUTs | numvfs=${numvfs}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1_vf0} | ${dut2} | ${dut2_if2_vf0}
| | ... | ${topology_type}

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
| | ... | - crypto_type - Crypto device type - HW_cryptodev or SW_cryptodev
| | ... | (Optional). Type: string, default value: HW_cryptodev
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up IPSec performance test suite \| L2 \
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model} | ${crypto_type}=HW_cryptodev
| | ...
| | Set up 3-node performance topology with DUT's NIC model
| | ... | ${topology_type} | ${nic_model}
| | ${numvfs}= | Set Variable If
| | ... | '${crypto_type}' == 'HW_cryptodev' | ${32}
| | ... | '${crypto_type}' == 'SW_cryptodev' | ${0}
| | Configure crypto device on all DUTs | force_init=${True} | numvfs=${numvfs}
| | Run Keyword If | '${crypto_type}' == 'HW_cryptodev'
| | ... | Configure kernel module on all DUTs | igb_uio | force_load=${True}

| Set up performance topology with containers
| | [Documentation]
| | ... | Suite preparation phase that starts containers
| | ...
| | Set Suite Variable | @{container_groups} | @{EMPTY}
| | Construct VNF containers on all DUTs
| | Acquire all 'VNF' containers
| | Create all 'VNF' containers
| | Configure VPP in all 'VNF' containers
| | Install VPP in all 'VNF' containers

| Set up performance test suite with MEMIF
| | [Documentation]
| | ... | Append memif_plugin.so to the list of enabled plugins.
| | ...
| | Set Suite Variable | @{plugins_to_enable}
| | Append To List | ${plugins_to_enable} | memif_plugin.so

| Set up performance test suite with NAT
| | [Documentation]
| | ... | Append nat_plugin.so to the list of enabled plugins.
| | ...
| | Set Suite Variable | @{plugins_to_enable}
| | Append To List | ${plugins_to_enable} | nat_plugin.so

| Set up performance test suite with ACL
| | [Documentation]
| | ... | Append acl_plugin.so to the list of enabled plugins.
| | ...
| | Set Suite Variable | @{plugins_to_enable}
| | Append To List | ${plugins_to_enable} | acl_plugin.so

| Set up performance test suite with AVF driver
| | [Documentation]
| | ... | Append avf_plugin.so to the list of enabled plugins.
| | ...
| | Set Suite Variable | @{plugins_to_enable}
| | Append To List | ${plugins_to_enable} | avf_plugin.so

| Set up performance test suite with Static SRv6 proxy
| | [Documentation]
| | ... | Append srv6as_plugin.so to the list of enabled plugins.
| | ...
| | Set Suite Variable | @{plugins_to_enable}
| | Append To List | ${plugins_to_enable} | srv6as_plugin.so

| Set up performance test suite with Dynamic SRv6 proxy
| | [Documentation]
| | ... | Append srv6ad_plugin.so to the list of enabled plugins.
| | ...
| | Set Suite Variable | @{plugins_to_enable}
| | Append To List | ${plugins_to_enable} | srv6ad_plugin.so

| Set up performance test suite with Masquerading SRv6 proxy
| | [Documentation]
| | ... | Append srv6am_plugin.so to the list of enabled plugins.
| | ...
| | Set Suite Variable | @{plugins_to_enable}
| | Append To List | ${plugins_to_enable} | srv6am_plugin.so

| Set up performance test suite with LACP mode link bonding
| | [Documentation]
| | ... | Append lacp_plugin.so to the list of enabled plugins.
| | ...
| | Set Suite Variable | @{plugins_to_enable}
| | Append To List | ${plugins_to_enable} | lacp_plugin.so

| Set up 3-node performance topology with wrk and DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that setup default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Installs the traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up 3-node performance topology with wrk and DUT's NIC model\
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
| | Set variables in 3-node circular topology with DUT interface model
| | ... | ${iface_model}
| | Iface update numa node | ${tg}
# Make sure TRex is stopped
| | ${running}= | Is TRex running | ${tg}
| | Run keyword if | ${running}==${True} | Teardown traffic generator | ${tg}
| | ${curr_driver}= | Get PCI dev driver | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | Run keyword if | '${curr_driver}'!='${None}'
| | ... | PCI Driver Unbind | ${tg} |
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
# Bind tg_if1 to driver specified in the topology
| | ${driver}= | Get Variable Value | ${tg['interfaces']['${tg_if1}']['driver']}
| | PCI Driver Bind | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']} | ${driver}
# Set IP on tg_if1
| | ${intf_name}= | Get Linux interface name | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.10.1 | 24
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.20.1 | 24
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.30.1 | 24
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.40.1 | 24
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.50.1 | 24
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.60.1 | 24
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.70.1 | 24
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.80.1 | 24
| | Set Linux interface up | ${tg} | ${intf_name}
| | Install wrk | ${tg}

# Suite teardowns

| Tear down 2-node performance topology
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ...
| | Teardown traffic generator | ${tg}

| Tear down 2-node performance topology with container
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown and container
| | ... | destroy.
| | ...
| | Teardown traffic generator | ${tg}
| | :FOR | ${group} | IN | @{container_groups}
| | | Destroy all '${group}' containers

| Tear down 3-node performance topology
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ...
| | Teardown traffic generator | ${tg}

| Tear down 3-node performance topology with container
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown and container
| | ... | destroy.
| | ...
| | Teardown traffic generator | ${tg}
| | :FOR | ${group} | IN | @{container_groups}
| | | Destroy all '${group}' containers

# Tests setups

| Set up performance test
| | [Documentation] | Common test setup for performance tests.
| | ...
| | Reset VAT History On All DUTs | ${nodes}
| | Create base startup configuration of VPP on all DUTs

| Set up tcp performance test
| | [Documentation] | Common test setup for TCP performance tests.
| | ...
| | Reset VAT History On All DUTs | ${nodes}
| | Create base startup configuration of VPP for TCP tests on all DUTs

| Set up performance test with Ligato Kubernetes
| | [Documentation] | Common test setup for performance tests with Ligato \
| | ... | Kubernetes.
| | ...
| | Apply Kubernetes resource on all duts | ${nodes} | namespaces/csit.yaml
| | Apply Kubernetes resource on all duts | ${nodes} | pods/kafka.yaml
| | Apply Kubernetes resource on all duts | ${nodes} | pods/etcdv3.yaml
| | Apply Kubernetes resource on all duts | ${nodes}
| | ... | configmaps/vswitch-agent-cfg.yaml
| | Apply Kubernetes resource on all duts | ${nodes}
| | ... | configmaps/vnf-agent-cfg.yaml
| | Apply Kubernetes resource on all duts | ${nodes}
| | ... | pods/contiv-sfc-controller.yaml
| | Apply Kubernetes resource on all duts | ${nodes}
| | ... | pods/contiv-vswitch.yaml

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
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Set Test Variable | ${pkt_trace} | ${True}
| | Run Keyword If Test Failed
| | ... | Traffic should pass with no loss | ${perf_trial_duration} | ${rate}
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}

| Tear down performance ndrchk test
| | [Documentation] | Common test teardown for ndrchk performance tests.
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}

| Tear down performance pdrchk test
| | [Documentation] | Common test teardown for pdrchk performance tests.
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}

| Tear down performance mrr test
| | [Documentation] | Common test teardown for max-received-rate performance
| | ... | tests.
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}

| Tear down performance test with wrk
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance test with wrk \|
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Show statistics on all DUTs | ${nodes}

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
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Show VPP vhost on all DUTs | ${nodes}
| | Show statistics on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Traffic should pass with no loss | ${perf_trial_duration} | ${rate}
| | ... | ${framesize} | ${topology_type} | fail_on_loss=${False}
| | Run keyword unless | ${dut1_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut1} | ${dut1_vm_refs}
| | Run keyword unless | ${dut2_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut2} | ${dut2_vm_refs}

| Tear down mrr test with vhost and VM with dpdk-testpmd
| | [Documentation] | Common test teardown for mrr tests which use
| | ... | vhost(s) and VM(s) with dpdk-testpmd.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - Node where to clean qemu. Type: dictionary
| | ... | - dut1_vm_refs - VM references on node. Type: dictionary
| | ... | - dut2_node - Node where to clean qemu. Type: dictionary
| | ... | - dut2_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance test with vhost and VM with dpdk-testpmd \
| | ... | \| ${node['DUT1']} \| ${dut_vm_refs} \
| | ... | \| ${node['DUT2']} \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${dut1_node}=${None} | ${dut1_vm_refs}=${None}
| | ... | ${dut2_node}=${None} | ${dut2_vm_refs}=${None}
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Show VPP vhost on all DUTs | ${nodes}
| | Show statistics on all DUTs | ${nodes}
| | Run keyword unless | ${dut1_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut1} | ${dut1_vm_refs}
| | Run keyword unless | ${dut2_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut2} | ${dut2_vm_refs}

| Tear down performance test with vhost and VM with dpdk-testpmd and ACL
| | [Documentation] | Common test teardown for performance tests which use
| | ... | vhost(s) and VM(s) with ACL and dpdk-testpmd.
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
| | [Arguments] | ${rate} | ${framesize} | ${topology_type}
| | ... | ${dut1_node}=${None} | ${dut1_vm_refs}=${None}
| | ... | ${dut2_node}=${None} | ${dut2_vm_refs}=${None}
| | ...
| | Tear down performance test with vhost and VM with dpdk-testpmd
| | ... | ${rate} | ${framesize} | ${topology_type}
| | ... | ${dut1_node} | ${dut1_vm_refs}
| | ... | ${dut2_node} | ${dut2_vm_refs}
| | Vpp Log Plugin Acl Settings | ${dut1}
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Plugin Acl Interface Assignment | ${dut1}

| Tear down mrr test with vhost and VM with dpdk-testpmd and ACL
| | [Documentation] | Common test teardown for mrr tests which use
| | ... | vhost(s) and VM(s) with ACL and dpdk-testpmd.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - Node where to clean qemu. Type: dictionary
| | ... | - dut1_vm_refs - VM references on node. Type: dictionary
| | ... | - dut2_node - Node where to clean qemu. Type: dictionary
| | ... | - dut2_vm_refs - VM references on node. Type: dictionary
| | ...
| | [Arguments] | ${dut1_node}=${None} | ${dut1_vm_refs}=${None}
| | ... | ${dut2_node}=${None} | ${dut2_vm_refs}=${None}
| | ...
| | Tear down mrr test with vhost and VM with dpdk-testpmd
| | ... | ${dut1_node} | ${dut1_vm_refs}
| | ... | ${dut2_node} | ${dut2_vm_refs}
| | Vpp Log Plugin Acl Settings | ${dut1}
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Plugin Acl Interface Assignment | ${dut1}

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
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Show VPP vhost on all DUTs | ${nodes}
| | Show statistics on all DUTs | ${nodes}
| | Run keyword unless | ${dut1_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut1} | ${dut1_vm_refs}
| | Run keyword unless | ${dut2_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut2} | ${dut2_vm_refs}

| Tear down performance mrr test with vhost and VM with dpdk-testpmd
| | [Documentation] | Common test teardown for performance mrr tests which \
| | ... | use vhost(s) and VM(s) with dpdk-testpmd.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - Node where to clean qemu. Type: dictionary
| | ... | - dut1_vm_refs - VM references on node. Type: dictionary
| | ... | - dut2_node - Node where to clean qemu. Type: dictionary
| | ... | - dut2_vm_refs - VM references on node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance mrr test with vhost and VM with \
| | ... | dpdk-testpmd \| ${node['DUT1']} \| ${dut_vm_refs} \| ${node['DUT2']} \
| | ... | \| ${dut_vm_refs} \|
| | ...
| | [Arguments] | ${dut1_node}=${None} | ${dut1_vm_refs}=${None}
| | ... | ${dut2_node}=${None} | ${dut2_vm_refs}=${None}
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Show VPP vhost on all DUTs | ${nodes}
| | Run keyword unless | ${dut1_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut1} | ${dut1_vm_refs}
| | Run keyword unless | ${dut2_node}==${None}
| | ... | Tear down guest VM with dpdk-testpmd | ${dut2} | ${dut2_vm_refs}

| Tear down DPDK 2-node performance topology
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ... | Cleanup DPDK test environment.
| | ...
| | Teardown traffic generator | ${tg}
| | Cleanup DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Tear down DPDK 3-node performance topology
| | [Documentation]
| | ... | Suite teardown phase with traffic generator teardown.
| | ... | Cleanup DPDK test environment.
| | ...
| | Teardown traffic generator | ${tg}
| | Cleanup DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Cleanup DPDK Environment | ${dut2} | ${dut2_if1} | ${dut2_if2}

| Tear down performance discovery test with NAT
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests with NAT feature used.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - traffic_profile - Traffic profile. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance discovery test with NAT \| 100000pps \| 64 \
| | ... | \| ${traffic_profile} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${traffic_profile}
| | ...
| | Tear down performance discovery test | ${rate} | ${framesize}
| | ... | ${traffic_profile}
| | Show NAT verbose | ${dut1}
| | Show NAT verbose | ${dut2}

| Tear down mrr test with NAT
| | [Documentation] | Common test teardown for mrr performance \
| | ... | tests with NAT feature used.
| | ...
| | ... | \| Tear down mrr test with NAT \|
| | ...
| | Tear down performance mrr test
| | Show NAT verbose | ${dut1}
| | Show NAT verbose | ${dut2}

| Tear down performance test with ACL
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests with ACL feature used.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - traffic_profile - Traffic profile. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance test with ACL \| 100000pps \| 64 \
| | ... | \| ${traffic_profile} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${traffic_profile}
| | ...
| | Tear down performance discovery test | ${rate} | ${framesize}
| | ... | ${traffic_profile}
| | Vpp Log Plugin Acl Settings | ${dut1}
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Plugin Acl Interface Assignment | ${dut1}

| Tear down mrr test with ACL
| | [Documentation] | Common test teardown for mrr performance \
| | ... | tests with ACL feature used.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down mrr test with ACL \|
| | ...
| | Tear down performance mrr test
| | Vpp Log Plugin Acl Settings | ${dut1}
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Plugin Acl Interface Assignment | ${dut1}

| Tear down performance test with MACIP ACL
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests with MACIP ACL feature used.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer
| | ... | - traffic_profile - Traffic profile. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance test with MACIP ACL \| 100000pps \| 64 \
| | ... | \| ${traffic_profile} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${traffic_profile}
| | ...
| | Tear down performance discovery test | ${rate} | ${framesize}
| | ... | ${traffic_profile}
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Macip Acl Settings | ${dut1}
| | Run Keyword And Ignore Error
| | ... | Vpp Log Macip Acl Interface Assignment | ${dut1}

| Tear down mrr test with MACIP ACL
| | [Documentation] | Common test teardown for mrr performance \
| | ... | tests with MACIP ACL feature used.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down mrr test with MACIP ACL \|
| | ...
| | Tear down performance mrr test
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Macip Acl Settings | ${dut1}
| | Run Keyword And Ignore Error
| | ... | Vpp Log Macip Acl Interface Assignment | ${dut1}

| Tear down performance test with Ligato Kubernetes
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests with Ligato Kubernetes.
| | ...
| | Run Keyword If Test Failed
| | ... | Get Kubernetes logs on all DUTs | ${nodes} | csit
| | Run Keyword If Test Failed
| | ... | Describe Kubernetes resource on all DUTs | ${nodes} | csit
| | Delete Kubernetes resource on all DUTs | ${nodes} | csit

| Tear down performance test with SRv6 with encapsulation
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests with SRv6 with encapsulation feature used.
| | ...
| | ... | *Arguments:*
| | ... | - rate - Rate for sending packets. Type: string
| | ... | - framesize - L2 Frame Size [B]. Type: integer/string
| | ... | - traffic_profile - Traffic profile. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance test with SRv6 with encapsulation \
| | ... | \| 100000pps \| 64 \| ${traffic_profile} \|
| | ...
| | [Arguments] | ${rate} | ${framesize} | ${traffic_profile}
| | ...
| | Tear down performance discovery test | ${rate} | ${framesize}
| | ... | ${traffic_profile}
| | Run Keyword If Test Failed | Show SR Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Show SR Steering Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed | Show SR LocalSIDs on all DUTs | ${nodes}

| Tear down mrr test with SRv6 with encapsulation
| | [Documentation] | Common test teardown for mrr tests with SRv6 with \
| | ... | encapsulation feature used.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down mrr test with SRv6 with encapsulation \|
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Run Keyword If Test Failed | Show SR Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Show SR Steering Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed | Show SR LocalSIDs on all DUTs | ${nodes}
