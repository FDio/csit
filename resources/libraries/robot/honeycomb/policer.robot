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

*** Settings ***
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.honeycomb.Routing.RoutingKeywords
| ...     | WITH NAME | RoutingKeywordsAPI
| Variables | resources/test_data/honeycomb/policer_variables.py
| Documentation | Keywords used to test Policer using Honeycomb.

*** Keywords ***
| Honeycomb Configures Policer
| | [Documentation] | Uses Honeycomb API to configure Policer on the specified\
| | ... | interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - policer_data - data needed to configure Policer. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb Configures Policer \| ${node} \
| | ... | \| ${policer_data} \|
| | ...
| | [Arguments] | ${node} | ${policer_data}
| | Configure Policer
| | ... | ${node} | ${policer_data['name']} | ${policer_data}

| Policer Operational Data From Honeycomb Should Be
| | [Documentation] | Retrieves Policer operational data and verifies if\
| | ... | Policer is configured correctly.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - policer_data - data to compare configuration Policer with.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Policer Operational Data From Honeycomb Should Be \
| | ... | \| ${node} \| ${policer_data} \|
| | ...
| | [Arguments] | ${node} | ${policer_data}
| | ${data}= | Get Policer oper data | ${node} | ${policer_data['name']}
| | Compare data structures | ${data[0]} | ${policer_data}

| Policer Operational Data From Honeycomb Should Be empty
| | [Documentation] | Checks whether Policer configuration from Honeycomb \
| | ... | is empty.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Policer Operational Data From Honeycomb Should Be empty \
| | ... | \| ${node} \|
| | ...
| | [Arguments] | ${node}
| | Run keyword and expect error | HoneycombError*404*
| | ... | Get Policer oper data | ${node} | ${policer_data['name']}

| Honeycomb removes Policer configuration
| | [Documentation] | Uses Honeycomb API to remove Policer configuration\
| | ... | from the specified interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes Policer configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node}
| | Configure Policer | ${node} | ${policer_data['name']}

| Tear down policer test
| | [Documentation] | Uses Honeycomb API to remove Policer configuration\
| | ... | and reset interface state.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes Policer configuration \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node}
| | Honeycomb removes Policer configuration | ${node}

| Honeycomb enables Policer on interface
| | [Documentation] | Uses Honeycomb API to enable Policer on an interface.
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
| | ...
| | [Arguments] | ${node} | ${interface} | ${table_name}
| | Enable Policer on interface
| | ... | ${node} | ${interface} | ${table_name}

| Honeycomb disables Policer on interface
| | [Documentation] | Uses Honeycomb API to disable Policer on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the specified node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables Policer on interface \| ${nodes['DUT1']} \
| | ... | \| GigabithEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Disable Policer on interface
| | ... | ${node} | ${interface}

| Honeycomb Send packet and verify marking
| | [Documentation] | Send packet and verify DSCP of the received packet.
| | ...
| | ... | *Arguments:*
| | ... | - node - TG node. Type: dictionary
| | ... | - tx_if - TG transmit interface. Type: string
| | ... | - rx_if - TG receive interface. Type: string
| | ... | - src_mac - Packet source MAC. Type: string
| | ... | - dst_mac - Packet destination MAC. Type: string
| | ... | - src_ip - Packet source IP address. Type: string
| | ... | - dst_ip - Packet destination IP address. Type: string
| | ... | - dscp_num - DSCP value to verify. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| ${dscp}= \| DSCP AF22 \|
| | ... | \| Send packet and verify marking \| ${nodes['TG']} \| eth1 \| eth2 \
| | ... | \| 08:00:27:87:4d:f7 \| 52:54:00:d4:d8:22 \| 192.168.122.2 \
| | ... | \| 192.168.122.1 \| ${dscp} \|
| | ...
| | [Arguments] | ${node} | ${tx_if} | ${rx_if} | ${src_mac} | ${dst_mac}
| | ...         | ${src_ip} | ${dst_ip} | ${dscp_num}
| | ${tx_if_name}= | Get Interface Name | ${node} | ${tx_if}
| | ${rx_if_name}= | Get Interface Name | ${node} | ${rx_if}
| | ${args}= | Traffic Script Gen Arg | ${rx_if_name} | ${tx_if_name}
| | ...      | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${args}= | Set Variable | ${args} --dscp ${dscp_num}
| | Run Traffic Script On Node | policer.py | ${node} | ${args}
