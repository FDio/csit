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
| Library | resources.libraries.python.DUTSetup
| Library | resources.tools.wrk.wrk
| Resource | resources/libraries/robot/performance/performance_configuration.robot
| Resource | resources/libraries/robot/performance/performance_limits.robot
| Resource | resources/libraries/robot/performance/performance_utils.robot
| Resource | resources/libraries/robot/tcp/tcp_setup.robot
| Documentation | Performance suite keywords - Suite and test setups and
| ... | teardowns.

*** Keywords ***

# Keywords used in setups and teardowns

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
| | ... | - tg_if1 - 1st TG interface MAC address.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface MAC address.
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
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if1_mac}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${tg_if2_mac}
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
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if1 - 1st TG interface MAC address.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface MAC address.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2 - DUT1 interface towards DUT2.
| | ... | - dut2 - DUT2 node
| | ... | - dut2_if1 - DUT2 interface towards DUT1.
| | ... | - dut2_if2 - DUT2 interface towards TG.
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
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if1_mac}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${tg_if2_mac}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}
| | Set Suite Variable | ${dut2}
| | Set Suite Variable | ${dut2_if1}
| | Set Suite Variable | ${dut2_if2}

| Set variables in 3-node circular topology with DUT interface model with double link between DUTs
| | [Documentation]
| | ... | Compute path for testing on three given nodes in circular topology
| | ... | with double link between DUTs based on interface model provided as an
| | ... | argument and set corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if1 - 1st TG interface MAC address.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface MAC address.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2_1 - DUT1 interface 1 towards DUT2.
| | ... | - dut1_if2_2 - DUT1 interface 2 towards DUT2.
| | ... | - dut2 - DUT2 node
| | ... | - dut2_if1_1 - DUT2 interface 1 towards DUT1.
| | ... | - dut2_if1_2 - DUT2 interface 2 towards DUT1.
| | ... | - dut2_if2 - DUT2 interface towards TG.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set variables in 3-node circular topology with DUT interface model\
| | ... | with double link between DUTs \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
| | ${iface_model_list}= | Create list | ${iface_model}
| | # Compute path TG - DUT1 with single link in between
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | # Compute path TG - DUT2 with single link in between
| | Clear Path
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT2']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if2} | ${tg}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | # Compute path DUT1 - DUT2 with double link in between
| | Clear Path
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['DUT2']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Compute Path | always_same_link=${FALSE}
| | ${dut1_if2_1} | ${dut1}= | First Interface
| | ${dut1_if2_2} | ${dut1}= | Last Interface
| | ${dut2_if1_1} | ${dut2}= | First Ingress Interface
| | ${dut2_if1_2} | ${dut2}= | Last Egress Interface
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | # Set suite variables
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if1_mac}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${tg_if2_mac}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2_1}
| | Set Suite Variable | ${dut1_if2_2}
| | Set Suite Variable | ${dut2}
| | Set Suite Variable | ${dut2_if1_1}
| | Set Suite Variable | ${dut2_if1_2}
| | Set Suite Variable | ${dut2_if2}

# Suite setups

| Set up 2-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that sets the default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets the global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 2-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name}
| | ...
| | Setup suite | ${nic_name}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${osi_layer}

| Set up 2-node-switched performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that sets the default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets the global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ... | - tg_if1_dest_mac - Interface 1 destination MAC address. Type: string
| | ... | - tg_if2_dest_mac - Interface 2 destination MAC address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 2-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \
| | ... | \| 22:22:33:44:55:66 \| 22:22:33:44:55:55 \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name} | ${tg_if1_dest_mac}
| | ... | ${tg_if2_dest_mac}
| | ...
| | Setup suite | ${nic_name}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${osi_layer}
| | ... | ${tg_if1_dest_mac} | ${tg_if2_dest_mac}

| Set up 3-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that sets the default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets the global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up 3-node performance topology with DUT's NIC model \| L2 \
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name}
| | ...
| | Setup suite | ${nic_name}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${osi_layer}

| Set up 3-node performance topology with DUT's NIC model with double link between DUTs
| | [Documentation]
| | ... | Suite preparation phase that sets the default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets the global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up 3-node performance topology with DUT's NIC model with \
| | ... | double link between DUTs \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name}
| | ...
| | Set variables in 3-node circular topology with DUT interface model with double link between DUTs
| | ... | ${nic_name}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${osi_layer}

| Set up DPDK 2-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Updates interfaces on all nodes and sets the global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator. Initializes DPDK test
| | ... | environment.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up DPDK 2-node performance topology with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name}
| | ...
| | Setup suite | ${nic_name}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${osi_layer}
| | Initialize DPDK Environment | ${dut1} | ${dut1_if1} | ${dut1_if2}

| Set up DPDK 3-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Updates interfaces on all nodes and sets the global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator. Initializes DPDK test
| | ... | environment.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| 3-node Performance Suite Setup \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name}
| | ...
| | Setup suite | ${nic_name}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${osi_layer}
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
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ... | - vf_driver - Virtual function driver. Type: string
| | ... | - numvfs - Number of VFs. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up SRIOV 2-node performance topology with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \| AVF \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name} | ${vf_driver}
| | ... | ${numvfs}=${1}
| | ...
| | Setup suite | ${nic_name}
| | Run Keyword If | '${vf_driver}' == 'AVF'
| | ... | Configure AVF interfaces on all DUTs | numvfs=${numvfs}
| | ... | osi_layer=${osi_layer}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1_vf0} | ${dut1} | ${dut1_if2_vf0}
| | ... | ${osi_layer}

| Set up SRIOV 3-node performance topology with DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that sets default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ... | It configures PCI device with VFs on all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ... | - vf_driver - Virtual function driver. Type: string
| | ... | - numvfs - Number of VFs. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up SRIOV 3-node performance topology with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \| AVF \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name} | ${vf_driver}
| | ... | ${numvfs}=${1}
| | ...
| | Setup suite | ${nic_name}
| | Run Keyword If | '${vf_driver}' == 'AVF'
| | ... | Configure AVF interfaces on all DUTs | numvfs=${numvfs}
| | ... | osi_layer=${osi_layer}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1_vf0} | ${dut2} | ${dut2_if2_vf0}
| | ... | ${osi_layer}

| Set up IPSec performance test suite
| | [Documentation]
| | ... | Suite preparation phase that sets default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ... | Then it configures crypto device and kernel module on all DUTs.
| | ...
| | ... | TODO CSIT-1481: Crypto HW should be read from topology file instead.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ... | - crypto_type - Crypto device type - HW_DH895xcc or HW_C3xxx or
| | ... |   SW_cryptodev. Type: string, default value: HW_DH895xcc
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up IPSec performance test suite \| L2 \
| | ... | \| Intel-X520-DA2 \| HW_DH895xcc \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name} | ${crypto_type}=HW_DH895xcc
| | ...
| | Set up 3-node performance topology with DUT's NIC model
| | ... | ${osi_layer} | ${nic_name}
| | Return From Keyword If | '${crypto_type}' == 'SW_cryptodev'
| | ${numvfs}= | Set Variable If
| | ... | '${crypto_type}' == 'HW_DH895xcc' | ${32}
| | ... | '${crypto_type}' == 'HW_C3xxx' | ${16}
| | Configure crypto device on all DUTs | ${crypto_type} | numvfs=${numvfs}
| | ... | force_init=${True}
| | Configure kernel module on all DUTs | vfio_pci | force_load=${True}

| Set up 3-node performance topology with wrk and DUT's NIC model
| | [Documentation]
| | ... | Suite preparation phase that sets the default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets the global
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
| | Setup suite | ${iface_model}
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
