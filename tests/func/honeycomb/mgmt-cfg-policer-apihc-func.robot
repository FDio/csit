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
| ${interface}= | ${node['interfaces']['port1']['name']}
| ${tg_to_dut_if1_ip}= | 192.168.122.1
| ${dut_to_tg_if1_ip}= | 192.168.122.2
| ${dut_to_tg_if2_ip}= | 192.168.123.1
| ${tg_to_dut_if2_ip}= | 192.168.123.2
| ${prefix_length}= | ${24}
| ${dscp_number}= | ${20}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/policer.robot
| Resource | resources/libraries/robot/honeycomb/access_control_lists.robot
| Resource | resources/libraries/robot/testing_path.robot
| Library | resources.libraries.python.Trace
| Variables | resources/test_data/honeycomb/policer_variables.py
| ...
| Suite Setup | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Force Tags | HC_FUNC
| ...
| Documentation | *Honeycomb Policer management test suite.*

*** Test Cases ***
| TC01: Honeycomb can configure Policer
| | [Documentation] | Checks if Honeycomb can configure Policer.
| | ...
| | Given Policer Operational Data From Honeycomb Should Be empty | ${node}
| | When Honeycomb configures Policer | ${node} | ${policer_data}
| | Then Policer Operational Data From Honeycomb Should Be | ${node}
| | ... | ${policer_data_oper}

| TC02: Honeycomb can disable Policer
| | [Documentation] | Checks if Honeycomb can disable Policer.
| | ...
| | Given Policer Operational Data From Honeycomb Should Be | ${node}
| | ... | ${policer_data_oper}
| | When Honeycomb removes Policer configuration | ${node}
| | Then Policer Operational Data From Honeycomb Should Be empty | ${node}

| TC03: Honeycomb can configure Policer with increased values of CIR (900kbps)
| | [Documentation] | Checks if Honeycomb can configure Policer\
| | ... | with increased values of CIR.
| | ...
| | [Teardown] | Tear down policer test | ${node}
| | ...
| | Given Policer Operational Data From Honeycomb Should Be empty | ${node}
| | When Honeycomb configures Policer | ${node} | ${policer_data_2}
| | Then Policer Operational Data From Honeycomb Should Be | ${node}
| | ... | ${policer_data_oper_2}

| TC04: Honeycomb can configure Packets-Per-Second Based Policer
| | [Documentation] | Checks if Honeycomb can configure Policer\
| | ... | based on rate-type measured in pps.
| | ...
| | [Teardown] | Tear down policer test | ${node}
| | ...
| | Given Policer Operational Data From Honeycomb Should Be empty | ${node}
| | When Honeycomb configures Policer | ${node} | ${policer_data_3}
| | Then Policer Operational Data From Honeycomb Should Be | ${node}
| | ... | ${policer_data_oper_3}

| TC05: Configure Policer on Interface
| | [Documentation] | Honeycomb can configure Policer on a given interface.
| | ...
| | [Teardown] | Run Keywords
| | ... | Honeycomb disables Policer on interface | ${node} | ${interface} | AND
| | ... | Honeycomb removes ACL session | ${node}
| | ... | ${acl_tables['hc_acl_table']['name']}
| | ... | ${acl_tables['hc_acl_session']['match']} | AND
| | ... | Honeycomb removes ACL table | ${node}
| | ... | ${acl_tables['hc_acl_table']['name']} | AND
| | ... | Tear down policer test | ${node}
| | ...
| | Given Honeycomb configures Policer | ${node} | ${policer_data}
| | And ACL table from Honeycomb should not exist
| | ... | ${node} | ${acl_tables['hc_acl_table']['name']}
| | When Honeycomb creates ACL table
| | ... | ${node} | ${acl_tables['hc_acl_table']}
| | And Honeycomb adds ACL session
| | ... | ${node} | ${acl_tables['hc_acl_table']['name']}
| | ... | ${acl_tables['hc_acl_session']}
| | Then Honeycomb enables policer on interface
| | ... | ${node} | ${interface} | ${acl_tables['hc_acl_table']['name']}

| TC06: VPP policer 2R3C Color-aware marks packet
# Pending rework
| | [Tags] | EXPECTED_FAILING
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Ref] RFC2474, RFC2698.
| | ... | [Cfg] Configure 2R3C color-aware policer on DUT1 on the first\
| | ... | interface.
| | ... | [Ver] TG sends IPv4 TCP packet on the first link to DUT1.\
| | ... | Packet on DUT1 is marked with DSCP tag. Verifies if DUT1 sends\
| | ... | correct IPv4 TCP packet with correct DSCP on the second link to TG.
| | ...
| | [Teardown] | Show Packet Trace on All DUTs | ${nodes}
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Honeycomb configures Policer | ${dut_node} | ${policer_data_3}
| | And ACL table from Honeycomb should not exist
| | ... | ${dut_node} | ${acl_tables['hc_acl_table']['name']}
| | When Honeycomb creates ACL table
| | ... | ${dut_node} | ${acl_tables['hc_acl_table']}
| | And Honeycomb adds ACL session
| | ... | ${dut_node} | ${acl_tables['hc_acl_table']['name']}
| | ... | ${acl_tables['hc_acl_session']}
| | And Honeycomb enables policer on interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_tables['hc_acl_table']['name']}
| | And Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if1}
| | ... | up
| | And Honeycomb configures interface state | ${dut_node} | ${dut_to_tg_if2}
| | ... | up
| | And Honeycomb sets interface IPv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | And Honeycomb sets interface IPv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | And Honeycomb adds interface IPv4 neighbor
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${tg_to_dut_if2_ip}
| | ... | ${tg_to_dut_if2_mac}
| | And VPP Node Interfaces Ready Wait | ${dut_node}
| | Then Honeycomb Send packet and verify marking | ${tg_node}
| | ... | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if2} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if1_ip} | ${tg_to_dut_if2_ip} | ${dscp_number}
