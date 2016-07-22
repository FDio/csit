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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/netconf.robot
| Variables | resources/test_data/honeycomb/netconf/triggers.py
| Documentation | *Netconf test suite. Contains test cases that need to bypass\
| ... | REST API.*
| Force Tags | honeycomb_sanity

*** Test Cases ***
| Honeycomb can create and delete interfaces
| | [Documentation] | Repeatedly create and delete an interface through Netconf\
| | ... | and check the reply for any errors.
| | Given Netconf session is established | ${node}
| | :FOR | ${index} | IN RANGE | 20
| | | When Error trigger is sent | ${trigger_105}
| | | Then Replies should not contain RPC errors
