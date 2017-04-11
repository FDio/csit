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
| Resource | resources/libraries/robot/honeycomb/policer.robot
| Resource | resources/libraries/robot/honeycomb/access_control_lists.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/policer.robot
| Variables | resources/test_data/honeycomb/policer_variables.py
| Suite Teardown
| ... | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb and VPP | ${node}
| Force Tags | honeycomb_sanity | honeycomb_odl | test_policer
| Documentation | *Honeycomb Policer management test suite.*
| Variables | resources/test_data/honeycomb/policer_variables.py

*** Test Cases ***
| TC01: Honeycomb can configure Policer
| | [Documentation] | Checks if Honeycomb can congigure Policer.
| | Given Policer configuration from Honeycomb should be empty | ${node}
| | When Honeycomb configures Policer | ${node} | ${policer_data}
| | Then Policer configuration from Honeycomb should be | ${node}
| | ... | ${policer_data_compare}

| TC02: Honeycomb can disable Policer
| | [Documentation] | Checks if Honeycomb can disable Policer.
| | Given Policer configuration from Honeycomb should be | ${node}
| | ... | ${policer_data_compare}
| | When Honeycomb removes Policer configuration | ${node}
| | Then Policer configuration from Honeycomb should be empty | ${node}

| TC03: Honeycomb can configure Policer with suppress link layer disabled
| | [Documentation] | Checks if Honeycomb can congigure Policer with\
| | ... | suppresed link layer disabled.
| | [Teardown] | Policer test teardown | ${node}
| | Given Policer configuration from Honeycomb should be empty | ${node}
| | When Honeycomb configures Policer | ${node} | ${policer_data}
| | Then Policer configuration from Honeycomb should be | ${node}
| | ... | ${policer_data_compare}

| TC04: Honeycomb can configure Policer with increased values of CIR (900kbps)
| | [Documentation] | Checks if Honeycomb can configure Policer\
| | ... | with increased values of CIR.
| | [Teardown] | Policer test teardown | ${node}
| | Given Policer configuration from Honeycomb should be empty | ${node}
| | When Honeycomb configures Policer | ${node} | ${policer_data_2}
| | Then Policer configuration from Honeycomb should be | ${node}
| | ... | ${policer_data_compare_2}

| TC05: Honeycomb can configure Policer with increased values of CIR (1500kbps)
| | [Documentation] | Checks if Honeycomb can configure Policer\
| | ... | with increased values of CIR (600kbps).
| | [Teardown] | Policer test teardown | ${node}
| | Given Policer configuration from Honeycomb should be empty | ${node}
| | When Honeycomb configures Policer | ${node} | ${policer_data_3}
| | Then Policer configuration from Honeycomb should be | ${node}
| | ... | ${policer_data_compare_3}

| TC06: Configure Policer on Interface
| | Given Honeycomb configures Policer | ${node} | ${policer_data}
| | And ACL table from Honeycomb should not exist
| | ... | ${node} | ${acl_tables['hc_acl_table']['name']}
| | When Honeycomb creates ACL table
| | ... | ${node} | ${acl_tables['hc_acl_table']}
| | When Honeycomb adds ACL session
| | ... | ${node} | ${acl_tables['hc_acl_table']['name']}
| | ... | ${acl_tables['hc_acl_session']}
| | When Honeycomb enables policer on interface
| | ... | ${node} | ${interface} | ${acl_tables['hc_acl_table']['name']}

# TODO: TC07 - VPP policer 2R3C Color-aware marks packet