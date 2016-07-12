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

*** Variables***
# Interface to run tests on.
| ${interface}= | ${node['interfaces']['port1']['name']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/access_control_lists.robot
| Variables | tests/suites/honeycomb/resources/acl.py
| Suite Teardown | Clear all ACL settings | ${node}
| Documentation | *Honeycomb access control lists test suite.*
| Force Tags | Honeycomb_sanity

*** Test Cases ***
| Honeycomb can create ACL classify table
| | [Documentation] | Check if Honeycomb API can create an ACL table.
| | Given ACL table from Honeycomb should not exist
| | ... | ${node} | ${hc_acl_table['name']}
| | And ACL table from VAT should not exist
| | ... | ${node} | ${table_index}
| | When Honeycomb creates ACL table
| | ... | ${node} | ${hc_acl_table}
| | Then ACL table from Honeycomb should be | ${node} | ${hc_acl_table}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index} | ${vat_acl_table}

| Honeycomb manages more than one ACL table
| | [Documentation] | Check if Honeycomb API can create another ACL table.
| | Given ACL table from Honeycomb should be | ${node} | ${hc_acl_table}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index} | ${vat_acl_table}
| | And Honeycomb creates ACL table | ${node} | ${hc_acl_table2}
| | Then ACL table from Honeycomb should be | ${node} | ${hc_acl_table}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index} | ${vat_acl_table}
| | And ACL table from Honeycomb should be | ${node} | ${hc_acl_table2}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index2} | ${vat_acl_table2}

| Honeycomb can add ACL session to table
| | [Documentation] | Check if Honeycomb API can add an ACL session to a table.
| | Given ACL table from Honeycomb should be | ${node} | ${hc_acl_table}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index} | ${vat_acl_table}
| | When Honeycomb adds ACL session
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session}
| | Then ACL session from Honeycomb should be
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session}
| | And ACL session from VAT should be
| | ... | ${node} | ${table_index} | ${session_index} | ${vat_acl_session}

| Honeycomb manages more than one ACL session on one table
| | [Documentation] | Check if Honeycomb API can add another ACL session\
| | ... | to a table.
| | Given ACL session from Honeycomb should be
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session}
| | And ACL session from VAT should be
| | ... | ${node} | ${table_index} | ${session_index} | ${vat_acl_session}
| | When Honeycomb adds ACL session
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session2}
| | Then ACL session from Honeycomb should be
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session}
| | And ACL session from VAT should be
| | ... | ${node} | ${table_index} | ${session_index} | ${vat_acl_session}
| | And ACL session from Honeycomb should be
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session2}
| | And ACL session from VAT should be
| | ... | ${node} | ${table_index} | ${session_index2} | ${vat_acl_session2}

| Honeycomb enables ACL on interface
| | [Documentation] | Check if Honeycomb API can enable ACL on an interface.
| | Given ACL table from Honeycomb should be | ${node} | ${hc_acl_table}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index} | ${vat_acl_table}
| | And ACL session from Honeycomb should be
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session}
| | And ACL session from VAT should be
| | ... | ${node} | ${table_index} | ${session_index} | ${vat_acl_session}
| | When Honeycomb enables ACL on interface
| | ... | ${node} | ${interface} | ${hc_acl_table['name']}
| | Then Interface ACL settings from Honeycomb should be
| | ... | ${node} | ${interface} | ${hc_acl_table['name']}
| | And Interface ACL settings from VAT should be
| | ... | ${node} | ${interface} | ${table_index}

| Honeycomb disables ACL on interface
| | [Documentation] | Check if Honeycomb API can disable ACL on an interface.
| | Given Interface ACL settings from Honeycomb should be
| | ... | ${node} | ${interface} | ${hc_acl_table['name']}
| | And Interface ACL settings from VAT should be
| | ... | ${node} | ${interface} | ${table_index}
| | When Honeycomb disables ACL on interface | ${node} | ${interface}
| | Then Interface ACL settings from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | And Interface ACL settings from VAT should be empty
| | ... | ${node} | ${interface}

| Honeycomb can remove ACL session
| | [Documentation] | Check if Honeycomb API can remove an ACL session.
| | Given ACL session from Honeycomb should be
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session}
| | And ACL session from VAT should be
| | ... | ${node} | ${table_index} | ${session_index} | ${vat_acl_session}
| | And ACL session from Honeycomb should be
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session2}
| | And ACL session from VAT should be
| | ... | ${node} | ${table_index} | ${session_index2} | ${vat_acl_session2}
| | When Honeycomb removes ACL session
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session2['match']}
| | Then ACL session from Honeycomb should be
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session}
| | And ACL session from VAT should be
| | ... | ${node} | ${table_index} | ${session_index} | ${vat_acl_session}
| | And ACL session from Honeycomb should not exist
| | ... | ${node} | ${hc_acl_table['name']} | ${hc_acl_session2['match']}
| | And ACL session from VAT should not exist
| | ... | ${node} | ${table_index} | ${session_index2}

| Honeycomb can remove ACL table
| | [Documentation] | Check if Honeycomb API can delete an ACL table.
| | Given ACL table from Honeycomb should be | ${node} | ${hc_acl_table}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index} | ${vat_acl_table}
| | And ACL table from Honeycomb should be | ${node} | ${hc_acl_table2}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index2} | ${vat_acl_table2}
| | When Honeycomb removes ACL table | ${node} | ${hc_acl_table2['name']}
| | Then ACL table from Honeycomb should be | ${node} | ${hc_acl_table}
| | And ACL table from VAT should be
| | ... | ${node} | ${table_index} | ${vat_acl_table}
| | And ACL table from Honeycomb should not exist
| | ... | ${node} | ${hc_acl_table2['name']}
| | And ACL table from VAT should not exist
| | ... | ${node} | ${table_index2}
