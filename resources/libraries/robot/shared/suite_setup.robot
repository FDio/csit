# Copyright (c) 2020 Cisco and/or its affiliates.
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
| Variables | resources/libraries/python/Constants.py
| Resource | resources/libraries/robot/wrk/wrk_utils.robot
|
| Documentation | Suite setup keywords.

*** Keywords ***
| Setup suite topology interfaces
| | [Documentation]
| | ... | Common suite setup for single link tests.
| | ... |
| | ... | Compute path for testing on two given nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| |
| | ... | _NOTE:_ This KW sets topology suite variables:
| |
| | ... | *Arguments:*
| | ... | - ${actions} - Additional setup action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | ${nic_model_list}= | Create list | ${nic_name}
| | &{info}= | Compute Circular Topology
| | ... | ${nodes} | filter_list=${nic_model_list} | nic_pfs=${nic_pfs}
| | ${variables}= | Get Dictionary Keys | ${info}
| | FOR | ${variable} | IN | @{variables}
| | | ${value}= | Get From Dictionary | ${info} | ${variable}
| | | Set Suite Variable | ${${variable}} | ${value}
| | END
| | FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Suite setup Action For ${action}
| | END

| Setup suite single link no tg
| | [Documentation]
| | ... | Common suite setup for single link tests.
| | ... |
| | ... | Compute path for testing on two given nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| |
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - duts - List of DUT nodes
| | ... | - duts_count - Number of DUT nodes.
| | ... | - dut{n} - DUTx node
| | ... | - dut{n}_if1 - 1st DUT interface.
| | ... | - dut{n}_if1_mac - 1st DUT interface MAC address.
| | ... | - dut{n}_if2 - 2nd DUT interface.
| | ... | - dut{n}_if2_mac - 2nd DUT interface MAC address.
| |
| | ... | *Arguments:*
| | ... | - ${actions} - Additional setup action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | ${nic_model_list}= | Create list | ${nic_name}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | FOR | ${dut} | IN | @{duts}
| | | Append Node | ${nodes['${dut}']} | filter_list=${nic_model_list}
| | END
| | Append Node | ${nodes['@{duts}[0]']} | filter_list=${nic_model_list}
| | Compute Path | always_same_link=${TRUE}
| | FOR | ${i} | IN RANGE | 1 | ${DATAPATH_INTERFACES_MAX}
| | | ${dutx_if} | ${dutx}= | Next Interface
| | | Run Keyword If | '${dutx_if}' == 'None' | EXIT FOR LOOP
| | | ${dutx_if_mac}= | Get Interface MAC | ${dutx} | ${dutx_if}
| | | ${dutx_if_ip4_addr}= | Get Interface Ip4 | ${dutx} | ${dutx_if}
| | | ${dutx_if_ip4_prefix_length}= | Get Interface Ip4 Prefix Length
| | | ... | ${dutx} | ${dutx_if}
| | | ${dut_str}= | Get Keyname For DUT | ${dutx} | ${duts}
| | | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut_str}_if1}
| | | ${if_name}= | Set Variable If | '${if1_status}' == 'PASS'
| | | ... | if2 | if1
| | | Set Suite Variable | ${${dut_str}} | ${dutx}
| | | Set Suite Variable | ${${dut_str}_${if_name}} | ${dutx_if}
| | | Set Suite Variable | ${${dut_str}_${if_name}_mac} | ${dutx_if_mac}
| | | Set Suite Variable | ${${dut_str}_${if_name}_ip4_addr}
| | | ... | ${dutx_if_ip4_addr}
| | | Set Suite Variable | ${${dut_str}_${if_name}_ip4_prefix}
| | | ... | ${dutx_if_ip4_prefix_length}
| | END
| | Run Keyword If | ${i}>${DATAPATH_INTERFACES_MAX}
| | ... | Fatal Error | Datapath length exceeded
| | ${duts_count}= | Get Length | ${duts}
| | Set Suite Variable | ${duts}
| | Set Suite Variable | ${duts_count}
| | FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Suite setup Action For ${action}
| | END

| Additional Suite Setup Action For scapy
| | [Documentation]
| | ... | Additional Setup for suites which uses scapy as Traffic generator.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set Suite Variable | ${${dut}_vf1} | ${${dut}_${ilayer}1}
| | | Set Suite Variable | ${${dut}_vf2} | ${${dut}_${ilayer}2}
| | END
| | Set Interface State | ${tg} | ${TG_pf1}[0] | up
| | Set Interface State | ${tg} | ${TG_pf2}[0] | up

| Additional Suite Setup Action For dpdk
| | [Documentation]
| | ... | Additional Setup for suites which uses dpdk.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize DPDK Environment | ${nodes['${dut}']}
| | | ... | ${${dut}_${ilayer}1}[0] | ${${dut}_${ilayer}2}[0]
| | END

| Additional Suite Setup Action For performance vf
| | [Documentation]
| | ... | Additional Setup for suites which uses performance measurement for
| | ... | single DUT (inner loop).
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Additional Suite Setup Action For performance_dut \| DUT1 \|
| |
| | [Arguments] | ${dut}
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | ${_vf}=
| | | ... | Run Keyword | Init ${nic_driver} interface
| | | ... | ${nodes['${dut}']} | ${${dut}_pf${pf}}[0] | numvfs=${nic_vfs}
| | | ... | osi_layer=${osi_layer}
| | | ${_vlan}=
| | | ... | Create List | ${EMPTY}
| | | ${_mac}=
| | | ... | Create List | ${EMPTY}
| | | Set Suite Variable
| | | ... | ${${dut}_vf${pf}} | ${_vf}
| | | Set Suite Variable
| | | ... | ${${dut}_vf${pf}_ip4_addr} | ${${dut}_pf${pf}_ip4_addr}
| | | Set Suite Variable
| | | ... | ${${dut}_vf${pf}_ip4_prefix} | ${${dut}_pf${pf}_ip4_prefix}
| | | Set Suite Variable
| | | ... | ${${dut}_vf${pf}_mac} | ${_mac}
| | | Set Suite Variable
| | | ... | ${${dut}_vf${pf}_vlan} | ${_vlan}
| | | Set Suite Variable
| | | ... | ${ilayer} | vf
| | END

| Additional Suite Setup Action For performance
| | [Documentation]
| | ... | Additional Setup for suites which uses performance measurement.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword If | ${nic_vfs} > 0
| | | ... | Additional Suite Setup Action For performance vf | ${dut}
| | END
| | Initialize traffic generator
| | ... | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]
| | ... | ${dut1} | ${DUT1_${ilayer}1}[0]
| | ... | ${dut${duts_count}} | ${DUT${duts_count}_${ilayer}2}[0]
| | ... | ${osi_layer}

| Additional Suite Setup Action For ipsechw
| | [Documentation]
| | ... | Additional Setup for suites which uses QAT HW.
| |
| | ${numvfs}= | Set Variable If
| | ... | '${crypto_type}' == 'HW_DH895xcc' | ${32}
| | ... | '${crypto_type}' == 'HW_C3xxx' | ${16}
| | Configure crypto device on all DUTs | ${crypto_type} | numvfs=${numvfs}
| | ... | force_init=${True}
| | Configure kernel module on all DUTs | vfio_pci | force_load=${True}

| Additional Suite Setup Action For wrk
| | [Documentation]
| | ... | Additional Setup for suites which uses WRK TG.
| |
| | Verify Program Installed | ${tg} | wrk
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
| | FOR | ${ip_addr} | IN | @{wrk_ip_addrs}
| | | ${ip_addr_on_intf}= | Linux interface has IP | ${tg} | ${intf_name}
| | | ... | ${ip_addr} | ${wrk_ip_prefix}
| | | Run Keyword If | ${ip_addr_on_intf}==${False} | Set Linux interface IP
| | | ... | ${tg} | ${intf_name} | ${ip_addr} | ${wrk_ip_prefix}
| | END
| | Set Linux interface up | ${tg} | ${intf_name}
| | Check wrk | ${tg}
