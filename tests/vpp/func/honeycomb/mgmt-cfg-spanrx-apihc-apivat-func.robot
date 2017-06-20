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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/honeycomb/port_mirroring.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/sub_interface.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/telemetry/span.robot
| Variables | resources/test_data/honeycomb/span.py
| ... | ${node['interfaces']['port1']['name']}
| ... | ${node['interfaces']['port3']['name']}
| ... | local0
| Variables | resources/test_data/honeycomb/sub_interfaces.py
| ...
| Force Tags | HC_FUNC
| ...
| Suite Setup | Run Keywords
| ... | Set Up Honeycomb Functional Test Suite | ${node} | AND
| ... | Add Interface local0 To Topology | ${node}
| ...
| Suite Teardown | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Documentation | *Honeycomb port mirroring test suite.*

*** Test Cases ***
| TC01: Honeycomb can configure SPAN on an interface - receive
| | [Documentation] | Honeycomb configures SPAN on interface and verifies
| | ... | against VPP SPAN dump in state receive.
| | ...
| | When Honeycomb configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_receive}
| | Then Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_receive}

| TC02: Honeycomb can configure SPAN on an interface - transmit
| | [Documentation] | Honeycomb configures SPAN on interface and verifies
| | ... | against VPP SPAN dump in state transmit.
| | ...
| | When Honeycomb configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_transmit}
| | Then Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_transmit}

| TC03: Honeycomb can configure SPAN on an interface - both
| | [Documentation] | Honeycomb configures SPAN on interface and verifies
| | ... | against VPP SPAN dump in state both.
| | ...
| | When Honeycomb configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_both}
| | Then Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_both}

| TC04: Honeycomb can configure SPAN on an interface with two source interfaces
| | [Documentation] | Honeycomb configures SPAN on interface and verifies
| | ... | against VPP SPAN dump in state both.
| | ...
| | When Honeycomb configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_both} | ${settings_if2}
| | Then Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_both} | ${settings_if2}

| TC05: Honeycomb can disable SPAN on interface
| | [Documentation] | Honeycomb removes existing SPAN configuration
| | ... | from interface.
| | ...
| | Given Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_both} | ${settings_if2}
| | When Honeycomb removes interface SPAN configuration
| | ... | ${node} | ${interface1}
| | Then Interface SPAN Operational Data from Honeycomb should be empty
| | ... | ${node} | ${interface1}

| TC06: Honeycomb can configure SPAN with two destination interfaces from the same source
| | [Documentation] | Honeycomb configures SPAN on two interfaces and verifies
| | ... | against VPP SPAN dump.
| | ...
| | [Teardown] | Run Keywords
| | ... | Honeycomb removes interface SPAN configuration
| | ... | ${node} | ${interface1} | AND
| | ... | Honeycomb removes interface SPAN configuration
| | ... | ${node} | ${interface2}
| | ...
| | When Honeycomb configures SPAN on interface
| | ... | ${node} | ${interface1} | ${settings_if2}
| | And Honeycomb configures SPAN on interface
| | ... | ${node} | ${interface2} | ${settings_if2}
| | Then Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${settings_if2}
| | Then Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface2} | ${settings_if2}

| TC07: DUT mirrors IPv4 packets from one interface to another
# Pending rework
| | [Tags] | EXPECTED_FAILING
| | [Documentation]
| | ... | [Top] TG=DUT1
| | ... | [Cfg] (using Honeycomb) On DUT1 configure IPv4 address and set SPAN\
| | ... | mirroring from one DUT interface to the other.
| | ... | [Ver] Make TG send an ARP packet to DUT through one interface,\
| | ... | then receive a copy of sent packet and of DUT's ARP reply\
| | ... | on the second interface.
| | ...
| | [Teardown] | Run Keywords
| | ... | Show Packet Trace on All DUTs | ${nodes} | AND
| | ... | Honeycomb clears all interface IPv4 neighbors
| | ... | ${dut_node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb removes interface IPv4 addresses
| | ... | ${dut_node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb removes interface SPAN configuration
| | ... | ${node} | ${dut_to_tg_if2}
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if1}
| | ... | up
| | And Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if2}
| | ... | up
| | And Honeycomb sets interface IPv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix}
| | And Honeycomb adds interface IPv4 neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${tg_to_dut_if1_ip} | ${tg_to_dut_if1_mac}
| | ${settings_5}= | create dictionary | state=both
| | ... | iface-ref=${dut_to_tg_if1}
| | And All Vpp Interfaces Ready Wait | ${nodes}
| | When Honeycomb configures SPAN on interface
| | ... | ${node} | ${dut_to_tg_if2} | ${settings_5}
| | Then Send Packet And Check Received Copies | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if2}
| | ... | ${tg_to_dut_if1_ip} | ${dut_to_tg_if1_ip} | ICMP

| TC08: Honeycomb can configure SPAN on a sub-interface - receive
| | [Documentation] | Honeycomb configures SPAN on sub-interface and verifies
| | ... | against VPP SPAN dump in state receive.
| | ...
| | Given Honeycomb creates sub-interface | ${node} | ${interface1}
| | ... | ${sub_if_1_match} | ${sub_if_1_tags} | ${sub_if_1_settings}
| | When Honeycomb Configures SPAN on sub-interface
| | ... | ${node} | ${interface1} | ${1} | ${settings_receive}
| | Then sub-Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | ${settings_receive}

| TC09: Honeycomb can configure SPAN on a sub-interface - transmit
| | [Documentation] | Honeycomb configures SPAN on sub-interface and verifies
| | ... | against VPP SPAN dump in state transmit.
| | ...
| | Given Sub-interface state from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | down | up
| | When Honeycomb Configures SPAN on sub-interface
| | ... | ${node} | ${interface1} | ${1} | ${settings_transmit}
| | Then sub-Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | ${settings_transmit}

| TC10: Honeycomb can configure SPAN on a sub-interface - both
| | [Documentation] | Honeycomb configures SPAN on sub-interface and verifies
| | ... | against VPP SPAN dump in state both.
| | ...
| | Given Sub-interface state from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | down | up
| | When Honeycomb Configures SPAN on sub-interface
| | ... | ${node} | ${interface1} | ${1} | ${settings_both}
| | Then sub-Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | ${settings_both}

| TC11: Honeycomb can configure SPAN on a sub-interface with two source interfaces
| | [Documentation] | Honeycomb configures SPAN on sub-interface and verifies
| | ... | against VPP SPAN dump in state both.
| | ...
| | Given Sub-interface state from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | down | up
| | When Honeycomb Configures SPAN on sub-interface
| | ... | ${node} | ${interface1} | ${1} | ${settings_both} | ${settings_if2}
| | Then sub-Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | ${settings_both} | ${settings_if2}

| TC12: Honeycomb can disable SPAN on interface
| | [Documentation] | Honeycomb removes existing SPAN configuration
| | ... | from sub-interface.
| | ...
| | Given Sub-interface state from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | down | up
| | Given sub-Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | ${settings_both} | ${settings_if2}
| | When Honeycomb removes sub-interface SPAN configuration
| | ... | ${node} | ${interface1} | ${1}
| | Then sub-Interface SPAN Operational Data from Honeycomb should be empty
| | ... | ${node} | ${interface1} | ${1}

| TC13: Honeycomb can configure SPAN with two destination sub-interfaces from the same source
| | [Documentation] | Honeycomb configures SPAN on two sub-interfaces
| | ... | and verifies against VPP SPAN dump.
| | ...
| | [Teardown] | Run Keywords
| | ... | Honeycomb removes sub-interface SPAN configuration
| | ... | ${node} | ${interface1} | ${1} | AND
| | ... | Honeycomb removes sub-interface SPAN configuration
| | ... | ${node} | ${interface2} | ${1}
| | ...
| | Given Honeycomb creates sub-interface | ${node} | ${interface2}
| | ... | ${sub_if_2_match} | ${sub_if_2_tags} | ${sub_if_2_settings}
| | When Honeycomb Configures SPAN on sub-interface
| | ... | ${node} | ${interface1} | ${1} | ${settings_if2}
| | And Honeycomb Configures SPAN on sub-interface
| | ... | ${node} | ${interface2} | ${1} | ${settings_if2}
| | Then Sub-Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface1} | ${1} | ${settings_if2}
| | Then Sub-Interface SPAN Operational Data from Honeycomb should be
| | ... | ${node} | ${interface2} | ${1} | ${settings_if2}

| TC14: DUT mirrors IPv4 packets from an interface to a sub-interface
# Pending rework
| | [Tags] | EXPECTED_FAILING
| | [Documentation]
| | ... | [Top] TG=DUT1
| | ... | [Cfg] (using Honeycomb) On DUT1 configure IPv4 address and set SPAN\
| | ... | mirroring from one DUT interface to a sub-interface on the other\
| | ... | interface.
| | ... | [Ver] Make TG send an ARP packet to DUT through one interface,\
| | ... | then receive a copy of sent packet and of DUT's ARP reply\
| | ... | on the sub-interface.
| | ...
| | [Teardown] | Show Packet Trace on All DUTs | ${nodes}
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Sub-interface state from Honeycomb should be
| | ... | ${dut_node} | ${interface1} | ${1} | down | up
| | And Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if1}
| | ... | up
| | And Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if2}
| | ... | up
| | And Honeycomb sets the sub-interface up
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${1}
| | And Honeycomb sets interface IPv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix}
| | And And Honeycomb adds interface IPv4 neighbor
| | ... | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${tg_to_dut_if2_ip} | ${tg_to_dut_if2_mac}
| | ${settings_5}= | create dictionary | state=both
| | ... | iface-ref=${dut_to_tg_if2}
| | And All Vpp Interfaces Ready Wait | ${nodes}
| | When Honeycomb Configures SPAN on sub-interface
| | ... | ${node} | ${dut_to_tg_if1} | ${1} | ${settings_5}
| | Then Send Packet And Check Received Copies | ${tg_node}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if2_mac}
| | ... | ${dut_to_tg_if2_mac} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2_ip} | ${dut_to_tg_if2_ip} | ICMP
