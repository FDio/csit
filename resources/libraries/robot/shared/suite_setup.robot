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

"""Keywords used in suite setups."""

*** Settings ***
| Library | resources.libraries.python.DPDK.DPDKTools
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.ab
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficGenerator
| Variables | resources/libraries/python/Constants.py
|
| Documentation | Suite setup keywords.
*** Keywords ***
| Create suite topology variables
| | [Documentation]
| | ... | Create suite topology variables
| |
| | ... | _NOTE:_ This KW sets various suite variables based on filtered
| | ... | topology. All variables are set with also backward compatibility
| | ... | format dut{m}_if{n} (where the value type is string).
| | ... | List type allows to access physical interfaces in same way as
| | ... | virtual interface (e.g. SRIOV). This keeps abstracted compatibility
| | ... | between existing L1 and L2 KWs library and underlaying physical
| | ... | topology.
| |
| | ... | - duts - List of DUT nodes (name as seen in topology file).
| | ... | - duts_count - Number of DUT nodes.
| | ... | - int - Interfacy type (layer).
| | ... | Type: string
| | ... | - dut{n} - DUTx node.
| | ... | Type: dictionary
| | ... | - dut{m}_pf{n} - Nth interface of Mth DUT.
| | ... | Type: list
| | ... | - dut{m}_pf{n}_mac - Nth interface of Mth DUT - MAC address.
| | ... | Type: list
| | ... | - dut{m}_pf{n}_vlan - Nth interface of Mth DUT - VLAN id.
| | ... | Type: list
| | ... | - dut{m}_pf{n}_pci - Nth interface of Mth DUT - PCI address.
| | ... | Type: list
| | ... | - dut{m}_pf{n}_ip4_addr - Nth interface of Mth DUT - IPv4 address.
| | ... | Type: list
| | ... | - dut{m}_pf{n}_ip4_prefix - Nth interface of Mth DUT - IPv4 prefix.
| | ... | Type: list
| |
| | ... | *Arguments:*
| | ... | - @{actions} - Additional setup action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | ${variables}= | Get Dictionary Keys | ${topology_info}
| | FOR | ${variable} | IN | @{variables}
| | | ${value}= | Get From Dictionary | ${topology_info} | ${variable}
| | | Set Suite Variable | ${${variable}} | ${value}
| | END
| | FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Suite setup Action For ${action}
| | END

| Setup suite topology interfaces
| | [Documentation]
| | ... | Common suite setup for one to multiple link tests.
| | ... |
| | ... | Compute path for testing on given topology nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| |
| | ... | *Arguments:*
| | ... | - ${actions} - Additional setup action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | ${nic_model_list}= | Create list | ${nic_name}
| | &{info}= | Compute Circular Topology
| | ... | ${nodes} | filter_list=${nic_model_list} | nic_pfs=${nic_pfs}
| | ... | always_same_link=${False} | topo_has_tg=${True}
| | Set suite variable | &{topology_info} | &{info}
| | Create suite topology variables | @{actions}

| Setup suite topology interfaces with no TG
| | [Documentation]
| | ... | Common suite setup for single link tests with no traffic generator
| | ... | node.
| | ... |
| | ... | Compute path for testing on given topology nodes in circular topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| |
| | ... | *Arguments:*
| | ... | - ${actions} - Additional setup action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | ${nic_model_list}= | Create list | ${nic_name}
| | &{info}= | Compute Circular Topology
| | ... | ${nodes} | filter_list=${nic_model_list} | nic_pfs=${nic_pfs}
| | ... | always_same_link=${True} | topo_has_tg=${False}
| | Set suite variable | &{topology_info} | &{info}
| | Create suite topology variables | @{actions}

| Additional Suite Setup Action For scapy
| | [Documentation]
| | ... | Additional Setup for suites which uses scapy as Traffic generator.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Set Suite Variable | ${${dut}_vf1} | ${${dut}_${int}1}
| | | Set Suite Variable | ${${dut}_vf2} | ${${dut}_${int}2}
| | END
| | Set Interface State | ${tg} | ${TG_pf1}[0] | up
| | Set Interface State | ${tg} | ${TG_pf2}[0] | up

| Additional Suite Setup Action For dpdk
| | [Documentation]
| | ... | Additional Setup for suites which uses dpdk.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Initialize DPDK Framework | ${nodes['${dut}']}
| | | ... | ${${dut}_${int}1}[0] | ${${dut}_${int}2}[0] | ${nic_driver}
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
| | | ${_mac}=
| | | ... | Create List | ${EMPTY}
| | | ${_ip4_addr}=
| | | ... | Create List | ${EMPTY}
| | | ${_ip4_prefix}=
| | | ... | Create List | ${EMPTY}
| | | ${_pci}=
| | | ... | Create List | ${EMPTY}
| | | ${_vlan}=
| | | ... | Create List | ${EMPTY}
| | | Set Suite Variable
| | | ... | ${${dut}_prevf${pf}} | ${_vf}
| | | Set Suite Variable
| | | ... | ${${dut}_prevf${pf}_ip4_addr} | ${_ip4_addr}
| | | Set Suite Variable
| | | ... | ${${dut}_prevf${pf}_ip4_prefix} | ${_ip4_prefix}
| | | Set Suite Variable
| | | ... | ${${dut}_prevf${pf}_mac} | ${_mac}
| | | Set Suite Variable
| | | ... | ${${dut}_prevf${pf}_pci} | ${_pci}
| | | Set Suite Variable
| | | ... | ${${dut}_prevf${pf}_vlan} | ${_vlan}
| | END
| | Set Suite Variable
| | ... | ${int} | prevf

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
| | ... | ${dut1} | ${DUT1_${int}1}[0]
| | ... | ${dut${duts_count}} | ${DUT${duts_count}_${int}2}[0]
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

| Additional Suite Setup Action For ab
| | [Documentation]
| | ... | Additional Setup for suites which uses ab TG.
| |
| | Verify Program Installed | ${tg} | ab
| | Iface update numa node | ${tg}
| | ${running}= | Is TRex running | ${tg}
| | Run keyword if | ${running}==${True} | Teardown traffic generator | ${tg}
| | ${curr_driver}= | Get PCI dev driver | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | Run keyword if | '${curr_driver}'!='${None}'
| | ... | PCI Driver Unbind | ${tg} |
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | ${driver}= | Get Variable Value | ${tg['interfaces']['${tg_if1}']['driver']}
| | PCI Driver Bind | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']} | ${driver}
| | ${intf_name}= | Get Linux interface name | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | FOR | ${ip_addr} | IN | @{ab_ip_addrs}
| | | ${ip_addr_on_intf}= | Linux interface has IP | ${tg} | ${intf_name}
| | | ... | ${ip_addr} | ${ab_ip_prefix}
| | | Run Keyword If | ${ip_addr_on_intf}==${False} | Set Linux interface IP
| | | ... | ${tg} | ${intf_name} | ${ip_addr} | ${ab_ip_prefix}
| | END
| | Set Linux interface up | ${tg} | ${intf_name}
| | Check ab | ${tg}
