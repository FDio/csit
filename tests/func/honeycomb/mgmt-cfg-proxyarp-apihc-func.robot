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

*** Variables ***
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}
| &{proxyarp_settings_ipv4}= | vrf-id=${0}
| ... | low-addr=192.168.1.2 | high-addr=192.168.1.10
| ${tg_to_dut_ip}= | 192.168.1.100
| ${dut_to_tg_ip}= | 192.168.1.1
| ${prefix_length}= | ${24}
| ${test_ip}= | 192.168.1.5

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/proxyarp.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.Trace
| Suite Teardown
| ... | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Force Tags | honeycomb_sanity | honeycomb_test
| Documentation | *Honeycomb proxyARP management test suite.*

*** Test Cases ***
# TODO: Add operational data and VAT dump verification if/when avaliable
| TC01: Honeycomb can configure ipv4 proxyARP
| | [Documentation] | Check if Honeycomb can configure the proxyARP feature.
| | [Teardown] | Honeycomb removes proxyARP configuration | ${node}
| | Honeycomb configures proxyARP | ${node} | ${proxyarp_settings_ipv4}

| TC02: Honeycomb can enable proxyarp on an interface
| | [Documentation] | Check if Honeycomb can enable the proxyARP feature\
| | ... | on an interface.
| | [Teardown] | Honeycomb disables proxyARP on interface
| | ... | ${node} | ${interface}
| | Honeycomb enables proxyARP on interface | ${node} | ${interface}

| TC03: DUT sends ARP reply on behalf of another machine from the IP range
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC1027.
| | ... | [Cfg] On DUT1 configure interface IPv4 address and proxy ARP
| | ... | for IP range, using Honeycomb API.
| | ... | [Ver] Make TG send ARP request to DUT1 interface,
| | ... | verify if DUT1 sends correct ARP reply on behalf of machine whose
| | ... | IP is in the configured range.
| | [Teardown] | Run Keywords
| | ... | Honeycomb removes proxyARP configuration | ${node}
| | ... | AND | Honeycomb disables proxyARP on interface
| | ... | ${node} | ${interface}
| | ... | AND | Honeycomb sets interface state
| | ... | ${dut_node} | ${dut_to_tg_if1} | down
| | ... | AND | Honeycomb removes interface ipv4 addresses
| | ... | ${node} | ${interface}
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | ${tg_to_dut_if1_name}= | Get interface name | ${tg_node} | ${tg_to_dut_if1}
| | And Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | And Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_ip} | ${prefix_length}
| | When Honeycomb configures proxyARP | ${dut_node} | ${proxyarp_settings_ipv4}
| | And Honeycomb enables proxyARP on interface | ${node} | ${dut_to_tg_if1}
| | Then Send ARP Request | ${tg_node} | ${tg_to_dut_if1_name}
| | ...                   | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ...                   | ${tg_to_dut_ip} | ${test_ip}
