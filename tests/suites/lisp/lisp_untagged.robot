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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.LispUtil
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/lisp.robot

*** Variables ***
| ${locator_set_num}= | 3
| ${eid_ipv4_num}= | 4
| ${eid_ipv6_num}= | 3
| ${map_resolver_ipv4_num}= | 3
| ${map_resolver_ipv6_num}= | 2

*** Test Cases ***

| VPP can add and delete locator_set
| | Given Lisp locator_set data are prepare
| | ... | ${nodes['DUT1']} | ${locator_set_num}
| | When Lisp locator_set data are set | ${nodes['DUT1']}
| | Then Lisp locator_set are set correct | ${nodes['DUT1']}
| | When Delete all lisp locator_set from VPP | ${nodes['DUT1']}
| | Then Lisp locator_set should be unset | ${nodes['DUT1']}

| VPP can add, reset and delete locator_set
| | Given Lisp locator_set data use for test reset locator_set are prepare
| | ... | ${nodes['DUT1']} | ${locator_set_num}
| | When Lisp locator_set data are set | ${nodes['DUT1']}
| | Then Lisp locator_set are set correct | ${nodes['DUT1']}
| | When Delete all lisp locator_set from VPP | ${nodes['DUT1']}
| | Then Lisp locator_set should be unset | ${nodes['DUT1']}

| Vpp can add and delete eid address
| | Given Lisp eid address are prepare
| | ... | ${nodes['DUT1']} | ${eid_ipv4_num} | ${eid_ipv6_num}
| | When Lisp eid address are set | ${nodes['DUT1']}
| | Then Lisp eid address are set correct to eid table | ${nodes['DUT1']}
| | When Delete all lisp eid address form VPP | ${nodes['DUT1']}
| | Then Lisp eid table should be empty | ${nodes['DUT1']}

| Vpp can add and delete lisp map resolver address
| | Given Lisp map resolver address are prepare | ${nodes['DUT1']}
| | ... | ${map_resolver_ipv4_num} | ${map_resolver_ipv6_num}
| | When Lisp map resolver address are set | ${nodes['DUT1']}
| | Then Lisp map resolver address are set correct | ${nodes['DUT1']}
| | When Delete all lisp map resolver address from VPP | ${nodes['DUT1']}
| | Then Lip map resolver address should be empty | ${nodes['DUT1']}
