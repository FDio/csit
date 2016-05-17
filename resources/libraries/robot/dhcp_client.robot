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
| Library  | Collections
| Resource | resources/libraries/robot/default.robot
| Library  | resources.libraries.python.Dhcp.DhcpClient
| Library  | resources.libraries.python.TrafficScriptExecutor
| Documentation | DHCP Client specific keywords.

*** Keywords ***
| Check DHCP DISCOVER header
| | [Documentation] | Check if DHCP message contains all required fields.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - interface - TGs interface where listen for DHCP DISCOVER message.
| | ... |   Type: string
| | ... | - src_mac - DHCP clients MAC address. Type: string
| | ... | - hostname - DHCP clients hostname (Optional, Default="", if not
| | ... |   specified, the hostneme is not configured). Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Check DHCP DISCOVER header \| ${nodes['TG']} \
| | ... | \| eth2 \| 08:00:27:66:b8:57 \|
| | ... | \| Check DHCP DISCOVER header \| ${nodes['TG']} \
| | ... | \| eth2 \| 08:00:27:66:b8:57 \| client-hostname \|
| | ...
| | [Arguments] | ${tg_node} | ${interface} | ${src_mac} | ${hostname}=${EMPTY}
| | ${args}= | Run Keyword If | "${hostname}" == "" | Catenate
| |          | ...  | --rx_if | ${interface} | --rx_src_mac | ${src_mac}
| | ...      | ELSE | Catenate | --rx_if | ${interface} | --rx_src_mac
| |          | ...  | ${src_mac} | --hostname | ${hostname}
| | Run Traffic Script On Node | dhcp/check_dhcp_discover.py
| | ... | ${tg_node} | ${args}
