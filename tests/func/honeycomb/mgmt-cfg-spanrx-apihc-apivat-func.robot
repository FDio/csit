# Copyright (c) 2016 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/port_mirroring.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/telemetry/span.robot
| Variables | resources/test_data/honeycomb/spanrx-apihc-apivat.py | ${node}
| Force Tags | honeycomb_sanity | honeycomb_test
| Suite Setup | Add Interface local0 To Topology | ${node}
| Suite Teardown | Restart Honeycomb and VPP | ${node}
| Documentation | *Honeycomb port mirroring test suite.*

*** Test Cases ***
| TC01: Honeycomb can configure SPAN on an interface receive
| | [Documentation] | Honeycomb configures SPAN on interface and verifies/
| | ... | against VPP SPAN dump in state receive.
| | ...
| | When Honeycomb Configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_1}
| | Then Interface SPAN configuration from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_1}

| TC02: Honeycomb can configure SPAN on an interface transmit
| | [Documentation] | Honeycomb configures SPAN on interface and verifies/
| | ... | against VPP SPAN dump in state transmit.
| | ...
| | When Honeycomb Configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_2}
| | Then Interface SPAN configuration from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_2}

| TC03: Honeycomb can configure SPAN on an interface both
| | [Documentation] | Honeycomb configures SPAN on interface and verifies/
| | ... | against VPP SPAN dump in state both.
| | ...
| | When Honeycomb Configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_3}
| | Then Interface SPAN configuration from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_3}

| TC04: Honeycomb can configure SPAN on two interfaces
| | [Documentation] | Honeycomb configures SPAN on interface and verifies/
| | ... | against VPP SPAN dump in state both.
| | ...
| | When Honeycomb Configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_2} | ${settings_4}
| | Then Interface SPAN configuration from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_2} | ${settings_4}

| TC05: Honeycomb can disable SPAN on interface
| | [Documentation] | Honeycomb removes existing SPAN configuration\
| | ... | on interface.
| | ...
| | Given Interface SPAN configuration from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_2} | ${settings_4}
| | When Honeycomb removes interface SPAN configuration
| | ... | ${node} | ${interface1}
| | Then Interface SPAN configuration from Honeycomb should be empty
| | ... | ${node} | ${interface1}

| TC06: DUT mirrors IPv4 packets from one interface to another
| | [TearDown] | Show Packet Trace on All DUTs | ${nodes}
| | [Documentation]
| | ... | [Top] TG=DUT1
| | ... | [Cfg] (using Honeycomb) On DUT1 configure IPv4 address and set SPAN\
| | ... | mirroring from one DUT interface to the other.
| | ... | [Ver] Make TG send an ARP packet to DUT through one interface,\
| | ... | then receive a copy of sent packet and of DUT's ARP reply\
| | ... | on the second interface.
| | ...
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix}
| | Add ARP on DUT
| | ... | ${node} | ${dut_to_tg_if1} | ${tg_to_dut_if1_ip}
| | ... | ${tg_to_dut_if1_mac}
| | ${settings_5}= | create dictionary | state=both
| | ... | iface-ref=${dut_to_tg_if1}
| | InterfaceCLI.All Vpp Interfaces Ready Wait | ${nodes}
| | When Honeycomb Configures SPAN on interface
| | ... | ${node} | ${dut_to_tg_if2} | ${settings_5}
| | Then Send Packet And Check Received Copies | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if1_ip} | ${dut_to_tg_if1_ip} | ICMP
