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
| ${interface}= | ${node['interfaces']['port1']['name']}
| ${vhost_interface}= | test_vhost
| &{vhost_user_server}= | socket=/tmp/soc1 | role=server
| &{vhost_user_server_edit_1}= | socket=/tmp/soc12 | role=server
| &{vhost_user_server_edit_2}= | socket=/tmp/soc12 | role=client
| &{vhost_user_client}= | socket=/tmp/soc2 | role=client
| &{vhost_user_client_edit_1}= | socket=/tmp/soc22 | role=client
| &{vhost_user_client_edit_2}= | socket=/tmp/soc22 | role=server
| &{vhost_user_wrong}= | socket=/tmp/soc2 | role=wrong

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/vhost_user.robot
| Force Tags | honeycomb_sanity
| Suite Teardown | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Documentation | *Honeycomb vhost-user interface management test suite.*

*** Test Cases ***
| TC01: Honeycomb creates vhost-user interface - server
| | [Documentation] | Check if Honeycomb creates a vhost-user interface, role:\
| | ... | server.
| | ...
| | Given vhost-user configuration from Honeycomb should be empty
| | ... | ${node} | ${vhost_interface}
| | When Honeycomb creates vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
| | Then vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
| | And vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_server}

| TC02: Honeycomb modifies vhost-user interface - server
| | [Documentation] | Check if Honeycomb can modify properties of existing\
| | ... | vhost-user interface, role: server.
| | ...
| | Given vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
| | When Honeycomb configures vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server_edit_1}
| | Then vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server_edit_1}
| | And vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_server_edit_1}
| | When Honeycomb configures vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server_edit_2}
| | Then vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server_edit_2}
| | And vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_server_edit_2}
| | When Honeycomb configures vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
| | Then vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
| | And vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_server}

| TC03: Honeycomb deletes vhost-user interface - server
| | [Documentation] | Check if Honeycomb can delete an existing vhost-user\
| | ... | interface, role: server.
| | ...
| | Given vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_server}
| | When Honeycomb removes vhost-user interface
| | ... | ${node} | ${vhost_interface}
| | Then vhost-user configuration from Honeycomb should be empty
| | ... | ${node} | ${vhost_interface}
| | And vhost-user configuration from VAT should be empty
| | ... | ${node}

| TC04: Honeycomb creates vhost-user interface - client
| | [Documentation] | Check if Honeycomb creates a vhost-user interface, role:\
| | ... | client.
| | ...
| | Given vhost-user configuration from Honeycomb should be empty
| | ... | ${node} | ${vhost_interface}
| | When Honeycomb creates vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client}
| | Then vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client}
| | And vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_client}

| TC05: Honeycomb modifies vhost-user interface - client
| | [Documentation] | Check if Honeycomb can modify properties of existing\
| | ... | vhost-user interface, role: client.
| | ...
| | Given vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client}
| | When Honeycomb configures vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client_edit_1}
| | Then vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client_edit_1}
| | And vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_client_edit_1}
| | When Honeycomb configures vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client_edit_2}
| | Then vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client_edit_2}
| | And vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_client_edit_2}
| | When Honeycomb configures vhost-user interface
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client}
| | Then vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client}
| | And vhost-user configuration from VAT should be
| | ... | ${node} | ${vhost_user_client}

| TC06: Honeycomb deletes vhost-user interface - client
| | [Documentation] | Check if Honeycomb can delete an existing vhost-user\
| | ... | interface, role: client.
| | ...
| | Given vhost-user configuration from Honeycomb should be
| | ... | ${node} | ${vhost_interface} | ${vhost_user_client}
| | When Honeycomb removes vhost-user interface
| | ... | ${node} | ${vhost_interface}
| | Then vhost-user configuration from Honeycomb should be empty
| | ... | ${node} | ${vhost_interface}
| | And vhost-user configuration from VAT should be empty
| | ... | ${node}

| TC07: Honeycomb does not set vhost-user configuration on another interface type
| | [Documentation] | Check if Honeycomb refuses to set vhost-user\
| | ... | configuration for interface which is not v3po:vhost-user type.
| | ...
| | When Honeycomb fails setting vhost-user on different interface type
| | ... | ${node} | ${interface} | ${vhost_user_server}
| | Then vhost-user configuration from Honeycomb should be empty
| | ... | ${node} | ${interface}
| | And vhost-user configuration from VAT should be empty
| | ... | ${node}

| TC08: Honeycomb does not set invalid vhost-user configuration
| | [Documentation] | Check if Honeycomb refuses to set invalid parameters to\
| | ... | vhost-user interface.
| | ...
| | Given vhost-user configuration from Honeycomb should be empty
| | ... | ${node} | ${vhost_interface}
| | When Honeycomb fails setting invalid vhost-user configuration
| | ... | ${node} | ${vhost_interface} | ${vhost_user_wrong}
| | Then vhost-user configuration from Honeycomb should be empty
| | ... | ${node} | ${vhost_interface}
| | And vhost-user configuration from VAT should be empty
| | ... | ${node}
