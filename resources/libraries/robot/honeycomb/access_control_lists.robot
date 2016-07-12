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
| Library | resources.libraries.python.Classify
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.honeycomb.HcAPIKwACL.ACLKeywords
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords
| ...     | WITH NAME | InterfaceAPI
| Documentation | Keywords used to manage ACLs.

*** Keywords ***
| Honeycomb creates ACL table
| | [Documentation] | Uses Honeycomb API to create an ACL table.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - settings - ACL table settings. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb creates ACL table \| ${nodes['DUT1']} \
| | ... | \| ${settings} \|
| | [Arguments] | ${node} | ${settings}
| | Add classify table | ${node} | ${settings}

| Honeycomb removes ACL table
| | [Documentation] | Uses Honeycomb API to remove and existing ACL table.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_name - name of an ACL table. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes ACL table \| ${nodes['DUT1']} \| table0 \|
| | [Arguments] | ${node} | ${table_name}
| | Remove classify table | ${node} | ${table_name}

| Honeycomb adds ACL session
| | [Documentation] | Uses Honeycomb API to create an ACL session.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_name - name of an ACL table. Type: string
| | ... | - settings - ACL session settings. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds ACL session \| ${nodes['DUT1']} \
| | ... | \| table0 \| ${settings} \|
| | [Arguments] | ${node} | ${table_name} | ${settings}
| | Add classify session | ${node} | ${table_name} | ${settings}

| Honeycomb removes ACL session
| | [Documentation] | Uses Honeycomb API to remove an ACL session.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_name - name of an ACL table. Type: string
| | ... | - match - ACL session match setting. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes ACL session \| ${nodes['DUT1']} \
| | ... | \| table0 \| 00:00:00:00:00:00:01:02:03:04:05:06:00:00:00:00 \|
| | [Arguments] | ${node} | ${table_name} | ${match}
| | Remove classify session | ${node} | ${table_name} | ${match}

| Honeycomb enables ACL on interface
| | [Documentation] | Uses Honeycomb API to enable ACL on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - table_name - name of an ACL table. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables ACL on interface \| ${nodes['DUT1']} \
| | ... | \| GigabithEthernet0/8/0 \| table0 \|
| | [Arguments] | ${node} | ${interface} | ${table_name}
| | InterfaceAPI.Enable ACL on interface
| | ... | ${node} | ${interface} | ${table_name}

| Honeycomb disables ACL on interface
| | [Documentation] | Uses Honeycomb API to disable ACL on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables ACL on interface \| ${nodes['DUT1']} \
| | ... | \| GigabithEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | InterfaceAPI.Disable ACL on interface | ${node} | ${interface}

| ACL table from Honeycomb should be
| | [Documentation] | Retrieves ACL table information from Honeycomb\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - settings - expected ACL table settings. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL table from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| ${settings} \|
| | [Arguments] | ${node} | ${settings}
| | ${data}= | Get classify table oper data | ${node} | ${settings['name']}
| | Compare data structures | ${data} | ${settings}

| ACL table from VAT should be
| | [Documentation] | Retrieves ACL table information from VAT\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_index - VPP internal index of an ACL table. Type: int
| | ... | - settings - expected ACL table settings. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL session from VAT should be \| ${nodes['DUT1']} \
| | ... | \| ${0} \| ${settings} \|
| | [Arguments] | ${node} | ${table_index} | ${settings}
| | ${data}= | Get classify table data | ${node} | ${table_index}
| | Compare data structures | ${data} | ${settings}

| ACL table from Honeycomb should not exist
| | [Documentation] | Retrieves ACL table information from Honeycomb\
| | ... | and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_name - name of an ACL table. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL table from Honeycomb should not exist \| ${nodes['DUT1']} \
| | ... | \| table0 \|
| | [Arguments] | ${node} | ${table_name}
| | Run keyword and expect error | ValueError: No JSON object could be decoded
| | ... | Get classify table oper data | ${node} | ${table_name}

| ACL table from VAT should not exist
| | [Documentation] | Retrieves ACL table information from VAT\
| | ... | and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_index - VPP internal index of an ACL table. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL table from VAT should not exist \| ${nodes['DUT1']} \
| | ... | \| ${0} \|
| | [Arguments] | ${node} | ${table_index}
| | Run keyword and expect error | No JSON data.
| | ... | Get classify table data | ${node} | ${table_index}

| ACL session from Honeycomb should be
| | [Documentation] | Retrieves ACL session information from Honeycomb\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_name - name of an ACL table. Type: string
| | ... | - settings - expected ACL session settings. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL session from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| table0 \| ${settings} \|
| | [Arguments] | ${node} | ${table_name} | ${settings}
| | ${data}= | Get classify session oper data
| | ... | ${node} | ${table_name} | ${settings['match']}
| | Compare data structures | ${data} | ${settings}

| ACL session from VAT should be
| | [Documentation] | Retrieves ACL session information from VAT\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_index - VPP internal index of an ACL table. Type: int
| | ... | - session_index - VPP internal index of an ACL session. Type: int
| | ... | - settings - expected ACL table settings. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL session from VAT should be \| ${nodes['DUT1']} \
| | ... | \| ${0} \| ${0} \| ${settings} \|
| | [Arguments] | ${node} | ${table_index} | ${session_index} | ${settings}
| | ${data}= | Get classify session data
| | ... | ${node} | ${table_index} | ${session_index}
| | Compare data structures | ${data} | ${settings}

| ACL session from Honeycomb should not exist
| | [Documentation] | Retrieves ACL session information from Honeycomb\
| | ... | and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_name - name of an ACL table. Type: string
| | ... | - session_match - ACL session match setting. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL session from Honeycomb should not exist \| ${nodes['DUT1']} \
| | ... | \| table0 \| 00:00:00:00:00:00:01:02:03:04:05:06:00:00:00:00 \|
| | [Arguments] | ${node} | ${table_name} | ${session_match}
| | Run keyword and expect error | *HoneycombError: *Status code: 404.
| | ... | Get classify session oper data
| | ... | ${node} | ${table_name} | ${session_match}

| ACL session from VAT should not exist
| | [Documentation] | Retrieves ACL session information from VAT\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_index - VPP internal index of an ACL table. Type: int
| | ... | - session_index - VPP internal index of an ACL session. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL session from VAT should not exist \| ${nodes['DUT1']} \
| | ... | \| ${0} \| ${0} \|
| | [Arguments] | ${node} | ${table_index} | ${session_index}
| | Run keyword and expect error | ValueError: No JSON object could be decoded
| | ... | Get classify session data
| | ... | ${node} | ${table_index} | ${session_index}

| Interface ACL settings from Honeycomb should be
| | [Documentation] | Retrieves ACL interface settings from Honeycomb\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - table_name - expected ACL table name. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ACL settings from Honeycomb should be \
| | ... | \| ${nodes['DUT1']} \| GigabithEthernet0/8/0 \| table0 \|
| | [Arguments] | ${node} | ${interface} | ${table_name}
| | ${data}= | InterfaceAPI.Get interface oper data | ${node} | ${interface}
| | Should be equal
| | ... | ${table_name} | ${data['v3po:acl']['l2-acl']['classify-table']}

| Interface ACL settings from VAT should be
| | [Documentation] | Retrieves ACL interface settings from VAT\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - table_index - VPP internal index of an ACL table. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ACL settings from VAT should be \| ${nodes['DUT1']} \
| | ... | \| GigabithEthernet0/8/0 \| ${0} \|
| | [Arguments] | ${node} | ${interface} | ${table_index}
| | ${data}= | Get interface classify table | ${node} | ${interface}
| | Should be equal | ${table_index} | ${data[0]['l2_table_id']}

| Interface ACL settings from Honeycomb should be empty
| | [Documentation] | Retrieves ACL interface settings from Honeycomb\
| | ... | and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ACL settings from Honeycomb should be empty \
| | ... | \| ${nodes['DUT1']} \| GigabithEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | ${data}= | InterfaceAPI.Get interface oper data | ${node} | ${interface}
| | Run keyword and expect error | KeyError*
| | ... | Set Variable | ${data['v3po:acl']['l2-acl']['classify-table']}

| Interface ACL settings from VAT should be empty
| | [Documentation] | Retrieves ACL interface settings from VAT\
| | ... | and expects to fail.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - table_index - VPP internal index of an ACL table. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ACL settings from Honeycomb should be empty \
| | ... | \| ${nodes['DUT1']} \| GigabithEthernet0/8/0 \| ${0} \|
| | [Arguments] | ${node} | ${interface} | ${table_index}
| | ${data}= | Get interface classify table | ${node} | ${interface}
| | Run keyword and expect error | No JSON object could be decoded
| | ... | Should be equal | ${table_index} | ${data[0]['l2_table_id']}

| Clear all ACL settings
| | [Documentation] | Removes all ACL sessions and tables from Honeycomb\
| | ... | configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Clear all ACL settings \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Remove all classify tables | ${node}
