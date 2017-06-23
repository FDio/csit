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
| ${interface}= | ${node['interfaces']['port1']['name']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/nat.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Variables | resources/test_data/honeycomb/nat.py | ${node} | ${interface}
| ...
| Documentation | *Honeycomb NAT test suite.*
| ...
| Suite Setup | Set Up Honeycomb Functional Test Suite | ${node}
| ...
| Suite Teardown | Tear Down Honeycomb Functional Test Suite | ${node}
| ...
| Force Tags | HC_FUNC

*** Test Cases ***
| TC01: Honeycomb configures NAT entry
| | [Documentation] | Honeycomb configures a static NAT entry.
| | ...
| | Given NAT Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${nat_empty}
| | When Honeycomb Configures NAT Entry | ${node} | ${entry1}
| | Then NAT Entries From Honeycomb Should Be | ${node} | ${entry1}

| TC02: Honeycomb removes NAT entry
| | [Documentation] | Honeycomb removes a configured static NAT entry.
| | ...
| | Given NAT Entries From Honeycomb Should Be | ${node} | ${entry1}
| | When Honeycomb Configures NAT Entry | ${node} | ${NONE}
| | Then NAT Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${nat_empty}

| TC03: Honeycomb configures multiple NAT entries
| | [Documentation] | Honeycomb configures two static NAT entries.
| | ...
| | [Teardown] | Honeycomb Configures NAT Entry | ${node} | ${NONE}
| | ...
| | Given NAT Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${nat_empty}
| | When Honeycomb Configures NAT Entry | ${node} | ${entry1} | ${0} | ${1}
| | And Honeycomb Configures NAT Entry | ${node} | ${entry2} | ${0} | ${2}
| | Then NAT Entries From Honeycomb Should Be
| | ... | ${node} | ${entry1_2_oper} | ${0}

| TC04: Honeycomb enables NAT on interface - inbound
| | [Documentation] | Honeycomb configures NAT on an interface\
| | ... | in inbound direction.
| | ...
| | Given NAT Interface Operational Data From Honeycomb Should Be Empty
| | ... | ${node} | ${interface} | inbound
| | And NAT Interface Operational Data From Honeycomb Should Be Empty
| | ... | ${node} | ${interface} | outbound
| | When Honeycomb Configures NAT On Interface
| | ... | ${node} | ${interface} | inbound
| | Then NAT Interface Operational Data From Honeycomb Should Be
| | ... | ${node} | ${interface} | inbound
| | And NAT Interface Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${interface} | outbound

| TC05: Honeycomb removes NAT interface configuration
| | [Documentation] | Honeycomb removes NAT configuration from an interface.
| | ...
| | Given NAT Interface Operational Data From Honeycomb Should Be
| | ... | ${node} | ${interface} | inbound
| | And NAT Interface Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${interface} | outbound
| | When Honeycomb removes NAT interface configuration
| | ... | ${node} | ${interface} | inbound
| | Then NAT Interface Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${interface} | inbound
| | And NAT Interface Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${interface} | outbound

| TC06: Honeycomb enables NAT on interface - outbound
| | [Documentation] | Honeycomb configures NAT on an interface\
| | ... | in outbound direction.
| | ...
| | [Teardown] | Honeycomb removes NAT interface configuration
| | ... | ${node} | ${interface} | outbound
| | ...
| | Given NAT Interface Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${interface} | inbound
| | And NAT Interface Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${interface} | outbound
| | When Honeycomb Configures NAT on Interface
| | ... | ${node} | ${interface} | outbound
| | Then NAT Interface Operational Data From Honeycomb Should Be empty
| | ... | ${node} | ${interface} | inbound
| | And NAT Interface Operational Data From Honeycomb Should Be
| | ... | ${node} | ${interface} | outbound
