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

"""Keywords used in suite setups."""

*** Settings ***
| Library | resources.libraries.python.DPDK.DPDKTools
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.tools.wrk.wrk
| ...
| Documentation | Suite setup keywords.

*** Keywords ***
| Setup suite single link
| | [Documentation]
| | ... | Common suite setup for single link tests.
| | ... |
| | ... | Compute path for testing on two given nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - duts - List of DUT nodes
| | ... | - duts_count - Number of DUT nodes.
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if1_mac - 1st TG interface MAC address.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - tg_if2_mac - 2nd TG interface MAC address.
| | ... | - dut{n} - DUTx node
| | ... | - dut{n}_if1 - 1st DUT interface.
| | ... | - dut{n}_if1_mac - 1st DUT interface MAC address.
| | ... | - dut{n}_if2 - 2nd DUT interface.
| | ... | - dut{n}_if2_mac - 2nd DUT interface MAC address.
| | ...
| | ... | *Arguments:*
| | ... | - ${actions} - Additional setup action. Type: list
| | ...
| | [Arguments] | @{actions}
| | ...
| | ${nic_model_list}= | Create list | ${nic_name}
| | Append Node | ${nodes['TG']}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Append Node | ${nodes['${dut}']} | filter_list=${nic_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_if1} | ${tg}= | Next Interface
| | :FOR | ${dut} | IN | @{duts}
| | | ${dutx_if1} | ${dutx}= | Next Interface
| | | ${dutx_if2} | ${dutx}= | Next Interface
| | | ${dutx_if1_mac}= | Get Interface MAC | ${dutx} | ${dutx_if1}
| | | ${dutx_if2_mac}= | Get Interface MAC | ${dutx} | ${dutx_if2}
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | Set Suite Variable | ${${dut_str}} | ${dutx}
| | | Set Suite Variable | ${${dut_str}_if1} | ${dutx_if1}
| | | Set Suite Variable | ${${dut_str}_if2} | ${dutx_if2}
| | | Set Suite Variable | ${${dut_str}_if1_mac} | ${dutx_if1_mac}
| | | Set Suite Variable | ${${dut_str}_if2_mac} | ${dutx_if2_mac}
| | ${tg_if2} | ${tg}= | Next Interface
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${duts_count}= | Get Length | ${duts}
| | Set Suite Variable | ${duts}
| | Set Suite Variable | ${duts_count}
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if1_mac}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${tg_if2_mac}
| | :FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Suite setup Action For ${action}

| Setup suite double link
| | [Documentation]
| | ... | Common suite setup for double link tests.
| | ... |
| | ... | Compute path for testing on three given nodes in circular topology
| | ... | with double link between DUTs based on interface model provided as an
| | ... | argument and set corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - ${actions} - Additional setup action. Type: list
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - duts - List of DUT nodes
| | ... | - duts_count - Number of DUT nodes.
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
| | [Arguments] | @{actions}
| | ...
| | ${nic_model_list}= | Create list | ${nic_name}
| | # Compute path TG - DUT1 with single link in between
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${nic_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | # Compute path TG - DUT2 with single link in between
| | Clear Path
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT2']} | filter_list=${nic_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if2} | ${tg}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | # Compute path DUT1 - DUT2 with double link in between
| | Clear Path
| | Append Node | ${nodes['DUT1']} | filter_list=${nic_model_list}
| | Append Node | ${nodes['DUT2']} | filter_list=${nic_model_list}
| | Append Node | ${nodes['DUT1']} | filter_list=${nic_model_list}
| | Compute Path | always_same_link=${FALSE}
| | ${dut1_if2_1} | ${dut1}= | First Interface
| | ${dut1_if2_2} | ${dut1}= | Last Interface
| | ${dut2_if1_1} | ${dut2}= | First Ingress Interface
| | ${dut2_if1_2} | ${dut2}= | Last Egress Interface
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${duts_count}= | Set Variable | 2
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | # Set suite variables
| | Set Suite Variable | ${duts}
| | Set Suite Variable | ${duts_count}
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
| | :FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Suite setup Action For ${action}

| Additional Suite Setup Action For performance
| | [Documentation]
| | ... | Additional Setup for suites which uses performance measurement.
| | ...
| | Run Keyword If | ${duts_count} == 1
| | ... | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${osi_layer}
| | Run Keyword If | ${duts_count} == 2
| | ... | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${osi_layer}

| Additional Suite Setup Action For scapy
| | [Documentation]
| | ... | Additional Setup for suites which uses scapy as Traffic generator.
| | ...
| | Set Interface State | ${tg} | ${tg_if1} | up
| | Set Interface State | ${tg} | ${tg_if2} | up

| Additional Suite Setup Action For dpdk
| | [Documentation]
| | ... | Additional Setup for suites which uses dpdk.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | Initialize DPDK Environment | ${nodes['${dut}']}
| | | ... | ${${dut_str}_if1} | ${${dut_str}_if2}

| Additional Suite Setup Action For performance_avf
| | [Documentation]
| | ... | Additional Setup for suites which uses performance measurement over
| | ... | SRIOV AVF.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_avf_arr}= | Init AVF interface | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | numvfs=${1} | osi_layer=${osi_layer}
| | | ${if2_avf_arr}= | Init AVF interface | ${nodes['${dut}']} | ${${dut}_if2}
| | | ... | numvfs=${1} | osi_layer=${osi_layer}
# Currently only one AVF is supported.
| | | Set Suite Variable | ${${dut}_if1_vf0} | ${if1_avf_arr[0]}
| | | Set Suite Variable | ${${dut}_if2_vf0} | ${if2_avf_arr[0]}
| | Run Keyword If | ${duts_count} == 1
| | ... | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1_vf0} | ${dut1} | ${dut1_if2_vf0} | ${osi_layer}
| | Run Keyword If | ${duts_count} == 2
| | ... | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1_vf0} | ${dut2} | ${dut2_if2_vf0} | ${osi_layer}

| Additional Suite Setup Action For avf
| | [Documentation]
| | ... | Additional Setup for suites which uses SRIOV AVF.
| | ...
| | :FOR | ${dut} | IN | @{duts}
# Currently only one AVF is supported.
| | | Set Suite Variable | ${${dut}_if1_vf0} | ${${dut}_if1}
| | | Set Suite Variable | ${${dut}_if2_vf0} | ${${dut}_if2}

| Additional Suite Setup Action For ipsechw
| | [Documentation]
| | ... | Additional Setup for suites which uses QAT HW.
| | ...
| | ${numvfs}= | Set Variable If
| | ... | '${crypto_type}' == 'HW_DH895xcc' | ${32}
| | ... | '${crypto_type}' == 'HW_C3xxx' | ${16}
| | Configure crypto device on all DUTs | ${crypto_type} | numvfs=${numvfs}
| | ... | force_init=${True}
| | Configure kernel module on all DUTs | vfio_pci | force_load=${True}

| Additional Suite Setup Action For wrk
| | [Documentation]
| | ... | Additional Setup for suites which uses WRK TG.
| | ...
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
