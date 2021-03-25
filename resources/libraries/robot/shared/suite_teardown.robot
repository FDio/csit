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

"""Keywords used in suite teardowns."""

*** Settings ***
| Library | resources.libraries.python.DPDK.DPDKTools
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.NGINX.NGINXTools
| Library | resources.libraries.python.DUTSetup
|
| Documentation | Suite teardown keywords.

*** Keywords ***
| Tear down suite
| | [Documentation]
| | ... | Common suite teardown for tests.
| |
| | ... | *Arguments:*
| | ... | - ${actions} - Additional teardown action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Suite Tear Down Action For ${action}
| | END
| | Remove All Added VIF Ports On All DUTs From Topology | ${nodes}

| Additional Suite Tear Down Action For nginx
| | [Documentation]
| | ... | Additional teardown for suites which uses nginx.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Cleanup NGINX Framework
| | | ... | ${nodes['${dut}']}
| | END

| Additional Suite Tear Down Action For ab
| | [Documentation]
| | ... | Additional teardown for suites which uses ab.
| |
| | ${intf_name}= | Get Linux interface name | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | FOR | ${ip_addr} | IN | @{ab_ip_addrs}
| | | ${ip_addr_on_intf}= | Linux Interface Has IP | ${tg} | ${intf_name}
| | | ... | ${ip_addr} | ${ab_ip_prefix}
| | | Run Keyword If | ${ip_addr_on_intf}==${True} | Delete Linux Interface IP
| | | ... | ${tg} | ${intf_name} | ${ip_addr} | ${ab_ip_prefix}
| | END
| | Run Keyword And Ignore Error | PCI Driver Unbind
| | ... | ${tg} | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | Run Keyword And Ignore Error | PCI Driver Unbind
| | ... | ${tg} | ${tg['interfaces']['${tg_if2}']['pci_address']}

| Additional Suite Tear Down Action For performance
| | [Documentation]
| | ... | Additional teardown for suites which uses performance measurement.
| |
| | Run Keyword And Ignore Error | Teardown traffic generator | ${tg}

| Additional Suite Tear Down Action For dpdk
| | [Documentation]
| | ... | Additional teardown for suites which uses dpdk.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Cleanup DPDK Framework
| | | ... | ${nodes['${dut}']} | ${${dut}_${int}1}[0] | ${${dut}_${int}2}[0]
| | END

| Additional Suite Tear Down Action For hoststack
| | [Documentation]
| | ... | Additional teardown for suites which uses hoststack test programs.
| | ... | Ensure all hoststack test programs are no longer running on all DUTS.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Kill Program | ${nodes['${dut}']} | iperf3
| | | Kill Program | ${nodes['${dut}']} | vpp_echo
