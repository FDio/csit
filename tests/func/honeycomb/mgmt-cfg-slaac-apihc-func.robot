# Copyright (c) 2017 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

*** Variables ***
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/slaac.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/traffic.robot
| Suite Teardown
| ... | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb and VPP | ${node}
| Force Tags | HC_FUNC
| Documentation | *Honeycomb SLAAC management test suite.*
| Variables | resources/test_data/honeycomb/slaac_variables.py

*** Test Cases ***
| TC01: Honeycomb can configure SLAAC
| | [Documentation] | Checks if Honeycomb can congigure SLAAC.
| | Given SLAAC Operational Data From Honeycomb Should Be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface IPv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data}
| | Then SLAAC Operational Data From Honeycomb Should Be | ${node}
| | ... | ${interface} | ${slaac_data}

| TC02: Honeycomb can disable SLAAC
| | [Documentation] | Checks if Honeycomb can disable SLAAC.
| | Given SLAAC Operational Data From Honeycomb Should Be | ${node}
| | ... | ${interface} | ${slaac_data}
| | When Honeycomb removes SLAAC configuration | ${node} | ${interface}
| | Then SLAAC Operational Data From Honeycomb Should Be empty | ${node}
| | ... | ${interface}

| TC03: Honeycomb can configure SLAAC with suppress link layer disabled
| | [Documentation] | Checks if Honeycomb can congigure SLAAC.
| | [Teardown] | SLAAC test teardown | ${node} | ${interface}
| | Given SLAAC Operational Data From Honeycomb Should Be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface IPv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data}
| | Then SLAAC Operational Data From Honeycomb Should Be | ${node}
| | ... | ${interface} | ${slaac_data}

| TC04: Honeycomb can configure SLAAC with sending RA packets disabled
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | SLAAC test teardown | ${node} | ${interface}
| | Given SLAAC Operational Data From Honeycomb Should Be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface IPv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_01}
| | Then SLAAC Operational Data From Honeycomb Should Be | ${node} | ${interface}
| | ... | ${slaac_data_01}

| TC05: Honeycomb can configure SLAAC with min interval values
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | SLAAC test teardown | ${node} | ${interface}
| | Given SLAAC Operational Data From Honeycomb Should Be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface IPv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_02}
| | Then SLAAC Operational Data From Honeycomb Should Be | ${node} | ${interface}
| | ... | ${slaac_data_02}

| TC06: Honeycomb can configure SLAAC with max interval values
| | [Documentation] | Checks if Honeycomb can configure SLAAC\
| | ... | with given settings.
| | [Teardown] | SLAAC test teardown | ${node} | ${interface}
| | Given SLAAC Operational Data From Honeycomb Should Be empty | ${node}
| | ... | ${interface}
| | And InterfaceAPI.Set Interface State | ${node} | ${interface} | up
| | And Honeycomb sets interface IPv6 address | ${node} | ${interface}
| | ... | ${address} | ${prefix}
| | When Honeycomb configures SLAAC | ${node} | ${interface} | ${slaac_data_03}
| | Then SLAAC Operational Data From Honeycomb Should Be | ${node} | ${interface}
| | ... | ${slaac_data_03}

| TC07: DUT retransmits RA on IPv6 enabled interface after a set interval
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Cfg] On DUT1 configure IPv6 interface on the link to TG.
| | ... | [Ver] Make TG wait for two IPv6 Router Advertisement packets\
| | ... | to be sent by DUT1 and verify the received RA packets are correct.
| | [Teardown] | SLAAC test teardown | ${dut_node} | ${dut_to_tg_if1}
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Honeycomb sets interface IPv6 address
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${address} | ${prefix}
| | And Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | When Honeycomb configures SLAAC | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${slaac_data}
| | :FOR | ${n} | IN RANGE | ${2}
| | | Then Receive and verify router advertisement packet
| | | ... | ${tg_node} | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac} | ${20}
