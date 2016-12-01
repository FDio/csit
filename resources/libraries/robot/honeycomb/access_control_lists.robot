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
*** Variables ***
#TODO: update based on resolution of bug https://jira.fd.io/browse/HONEYCOMB-119

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
| | ... | - settings - expected ACL table settings. Type: dictionary
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
| | ... | - table_index - VPP internal index of an ACL table. Type: integer
| | ... | - settings - expected ACL table settings. Type: dictionary
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
| | ... | - table_index - VPP internal index of an ACL table. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL table from VAT should not exist \| ${nodes['DUT1']} \
| | ... | \| ${0} \|
| | [Arguments] | ${node} | ${table_index}
| | Run keyword and expect error | VAT: no JSON data.
| | ... | Get classify table data | ${node} | ${table_index}

| ACL session from Honeycomb should be
| | [Documentation] | Retrieves ACL session information from Honeycomb\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - table_name - name of an ACL table. Type: string
| | ... | - settings - expected ACL session settings. Type: dictionary
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
| | ... | - table_index - VPP internal index of an ACL table. Type: integer
| | ... | - session_index - VPP internal index of an ACL session. Type: integer
| | ... | - settings - expected ACL session settings. Type: dictionary
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
| | ... | - table_index - VPP internal index of an ACL table. Type: integer
| | ... | - session_index - VPP internal index of an ACL session. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ACL session from VAT should not exist \| ${nodes['DUT1']} \
| | ... | \| ${0} \| ${0} \|
| | [Arguments] | ${node} | ${table_index} | ${session_index}
| | Run keyword if | ${session_index} == 0
| | ... | Run keyword and expect error
| | ... | ValueError: No JSON object could be decoded
| | ... | Get classify session data
| | ... | ${node} | ${table_index} | ${session_index}
| | Run keyword if | ${session_index} > 0
| | ... | Run keyword and expect error
| | ... | IndexError: list index out of range
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
| | ... | ${table_name}
| | ... | ${data['v3po:acl']['ingress']['l2-acl']['classify-table']}
| | ... | ${data['v3po:acl']['ingress']['ip4-acl']['classify-table']}

| Interface ACL settings from VAT should be
| | [Documentation] | Retrieves ACL interface settings from VAT\
| | ... | and compares with expected settings.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ... | - table_index - VPP internal index of an ACL table. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Interface ACL settings from VAT should be \| ${nodes['DUT1']} \
| | ... | \| GigabithEthernet0/8/0 \| ${0} \|
| | [Arguments] | ${node} | ${interface} | ${table_index}
| | ${data}= | Get interface classify table | ${node} | ${interface}
| | Should be equal | ${table_index} | ${data['l2_table_id']}
| | Should be equal | ${table_index} | ${data['ip4_table_id']}

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
| | Run keyword and expect error | *KeyError: 'v3po:acl'
| | ... | Set Variable | ${data['v3po:acl']['l2-acl']['classify-table']}

| Interface ACL settings from VAT should be empty
| | [Documentation] | Retrieves ACL interface settings from VAT\
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
| | ${data}= | Get interface classify table | ${node} | ${interface}
| | Should be equal | ${data['l2_table_id']} | ${-1}
| | Should be equal | ${data['ip4_table_id']} | ${-1}

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

| Honeycomb creates ACL chain through ACL plugin
| | [Documentation] | Creates classify chain using the ACL plugin.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - acl_list_name - Name for the classify chain. Type: string
| | ... | - acl_list_settings - classify rules. Type: dictionary
| | ... | - macip - Use MAC+IP classifier. Optional. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb creates ACL chain through ACL plugin \
| | ... | \| ${nodes['DUT1']} \| acl_test \| ${settings} \|
| | [Arguments] | ${node} | ${acl_list_name} | ${acl_list_settings}
| | ... | ${macip}=${False}
| | Create ACL plugin classify chain
| | ... | ${node} | ${acl_list_name} | ${acl_list_settings} | ${macip}

| Honeycomb assigns plugin-ACL chain to interface
| | [Documentation] | Applies classification through the high-level\
| | ... | IETF-ACL node to an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Interface to assign classifier to. Type: string
| | ... | - acl_list_name - Name of the clasify chain. Type: string
| | ... | - direction - Classifier direction, ingress or egress. Type: string
| | ... | - macip - Use MAC+IP classifier. Optional. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb assigns plugin-ACL chain to interface \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| acl_test \| ingress \|
| | [Arguments]
| | ... | ${node} | ${interface} | ${acl_list_name} | ${direction}
| | ... | ${macip}=${False}
| | Set ACL plugin interface
| | ... | ${node} | ${interface} | ${acl_list_name} | ${direction} | ${macip}

| Clear plugin-ACL settings
| | [Documentation] | Removes ACl assignment from interface, then deletes\
| | ... | IETF-ACL chain.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - interface - Interface to clean classifiers from. | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Clear plugin-ACL settings | ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Delete interface plugin ACLs | ${node} | ${interface}
| | Delete ACL plugin classify chains | ${node}

| Read plugin-ACL configuration from VAT
| | [Documentation] | Obtains ACL-plugin configuration through VAT and logs\
| | ... | the reply.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Read plugin-ACL configuration from VAT \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | VPP log plugin acl settings | ${node}
| | VPP log plugin acl interface assignment | ${node}

| Send ICMP packet with type and code
| | [Documentation] | Sends an ICMP packet with specified code and type.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: integer
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: integer
| | ... | - tx_port - Source interface (TG-if1). Type: string
| | ... | - tx_mac - MAC address of source interface (TG-if1). Type: string
| | ... | - rx_port - Destionation interface (TG-if1). Type: string
| | ... | - rx_mac - MAC address of destination interface (TG-if1). Type: string
| | ... | - icmp_type - ICMP type to use. Type: int
| | ... | - icmp_code - ICMP code to use. Type: int
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send ICMP packet with type and code \| ${nodes['TG']} \
| | ... | \| 16.0.0.1 \| 32.0.0.1 \| eth2 \| 08:00:27:cc:4f:54 \
| | ... | \| eth4 \| 08:00:27:c9:6a:d5 \| ${1} \| ${1} \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_port} |
| | ... | ${tx_mac} | ${rx_port} | ${rx_mac} | ${icmp_type} | ${icmp_code}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --src_mac | ${tx_mac}
| | ...                 | --dst_mac | ${rx_mac}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --dst_ip | ${dst_ip}
| | ...                 | --tx_if | ${tx_port_name}
| | ...                 | --rx_if | ${rx_port_name}
| | ...                 | --icmp_type | ${icmp_type}
| | ...                 | --icmp_code | ${icmp_code}
| | Run Traffic Script On Node | send_icmp_type_code.py
| | ... | ${tg_node} | ${args}
