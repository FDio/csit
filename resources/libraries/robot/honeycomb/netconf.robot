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
| Library | resources.libraries.python.honeycomb.Netconf
| Variables | resources/test_data/honeycomb/netconf/hello.py
| Documentation | Keywords for managing Netconf communication.

*** Keywords ***
| Netconf session is established
| | [Documentation] | Open a communication channel on the Netconf session\
| | ... | and exchange hello messages.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Netconf session is established \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Create session | ${node} | ${hello}

| Error trigger is sent
| | [Documentation] | Send the specified error trigger through the channel.
| | ...
| | ... | *Arguments:*
| | ... | - trigger - RPC sequence that triggers a specific error. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Error trigger is sent \| <rpc>_some data_</rpc>]]>]]> \|
| | [Arguments] | ${trigger}
| | Send | ${trigger}

| Replies should not contain RPC errors
| | [Documentation] | Read response received through the channel, and check if\
| | ... | it is an error report.
| | ...
| | ... | *Arguments:*
| | ... | none
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Replies should not contain RPC errors \|
| | ${resp}= | Get all responses
| | should not contain | ${resp} | rpc-error
