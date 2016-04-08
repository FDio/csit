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
| Resource | resources/libraries/robot/counters.robot
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.LispSetup.LispSetup
| Library | resources.libraries.python.LispUtil

*** Keywords ***

| Test set Lisp locator_set params
| | [Documentation] | Test API, compare set and get Lisp locator_set params
| | [Arguments] | ${node}
| | ${set_locator_set}= | Get Lisp Locator Set Test Values | ${node}
| | Node Set Lisp Locator Set | ${node} | ${set_locator_set}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${node}
| | Compare Lisp Locator Set | ${set_locator_set} | ${show_locator_set}

| Test unset Lisp locator_set params
| | [Documentation] | Test unset all Lisp locator_set params
| | [Arguments] | ${node}
| | ${set_locator_set}= | Get Lisp Locator Set Test Values | ${node}
| | Node Unset Lisp Locator Set | ${node} | ${set_locator_set}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${node}
| | ${empty_list}= | Get Locator Empty List
| | Compare Lisp Locator Set | ${empty_list} | ${show_locator_set}

| Test reset Lisp locator_set
| | [Documentation] | Test reset lisp locator_set and then set it
| | [Arguments] | ${node}
| | ${set_locator_set}= | Get Lisp Locator Set Reset Test Values | ${node}
| | Node Set Lisp Locator Set | ${node} | ${set_locator_set}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${node}
| | Compare Lisp Locator Set | ${set_locator_set} | ${show_locator_set}

| Test unset reset Lisp locator_set
| | [Documentation] | Test unset all reset Lisp locator_set params
| | [Arguments] | ${node}
| | ${set_locator_set}= | Get Lisp Locator Set Reset Test Values | ${node}
| | Node Unset Lisp Locator Set | ${node} | ${set_locator_set}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${node}
| | ${empty_list}= | Get Locator Empty List
| | Compare Lisp Locator Set | ${empty_list} | ${show_locator_set}

| Test set Lisp local eid table
| | [Documentation] | Test API, compare set and get Lisp local eid table
| | [Arguments] | ${node}
| | ${set_eid} = | Get Lisp Local Eid Test Value
| | Node Set Lisp Eid Table | ${node} | ${set_eid}
| | ${show_eid}= | Vpp Show Lisp Local Eid Table | ${node}
| | Compare Lisp | ${set_eid} | ${show_eid}

| Test unset Lisp local eid table
| | [Documentation] | Test API, unset all Lisp local eid table
| | [Arguments] | ${node}
| |  ${set_eid} = | Get Lisp Local Eid Test Value
| | Node Unset Lisp Eid Table | ${node} | ${set_eid}
| | ${show_eid}= | Vpp Show Lisp Local Eid Table | ${node}
| | ${empty_list}= | Get Empty List
| | Compare Lisp | ${empty_list} | ${show_eid}

| Test set Lisp map resolver
| | [Documentation] | Test API, compare set and get Lisp map resolver
| | [Arguments] | ${node}
| | ${set_map_resolver} = | Get Lisp Map Resolver
| | Node Set Lisp Map Resolver | ${node} | ${set_map_resolver}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${node}
| | Compare Lisp | ${set_map_resolver} | ${show_map_resolver}

| Test unset Lisp map resolver
| | [Documentation] | Test API, unset all Lisp map resolver
| | [Arguments] | ${node}
| | ${set_map_resolver} = | Get Lisp Map Resolver
| | Node Unset Lisp Map Resolver | ${node} | ${set_map_resolver}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${node}
| | ${empty_list}= | Get Empty List
| | Compare Lisp | ${empty_list} | ${show_map_resolver}

| Set lisp gpe interface down and up
| | [Documentation] | Test API to set lisp gpe interface up and down
| | [Arguments] | ${node}
| | Node Lisp Gpe Interface Up | ${node}
| | Node Lisp Gpe Interface Down | ${node}
