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

| Lisp locator_set data are prepare
| | [Documentation] | *Generate lisp locator_set data for testing LISP API.*
| | ...
| | ... | _Set testcase variables with lisp
| | ... | - ${locator_set_values}
| | ...
| | [Arguments] | ${DUT1} | ${locator_set_number}
| | ${locator_set_values}= | Generate Lisp Locator Set Data |
| | ...                    | ${DUT1} | ${locator_set_number}
| | Set Test Variable | ${locator_set_values}

| Lisp locator_set data are set
| | [Documentation] | *Set the lisp locator_set in node.*
| | ...
| | [Arguments] | ${DUT1}
| | Vpp Set Lisp Locator Set | ${DUT1} | ${locator_set_values}

| Lisp locator_set are set correct
| | [Documentation] | *Test if the locator_set are set correct on VPP.*
| | ...
| | [Arguments] | ${DUT1}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${DUT1}
| | Lisp Locator S Should Be Equal
| | ... | ${locator_set_values} | ${show_locator_set}

| Delete all lisp locator_set from VPP
| | [Documentation] | *Delete all lisp locator_set on node.*
| | ...
| | [Arguments] | ${DUT1}
| | Vpp Unset Lisp Locator Set | ${DUT1} | ${locator_set_values}

| Lisp locator_set should be unset
| | [Documentation] | *Test if locator_set are unset.*
| | ...
| | [Arguments] | ${DUT1}
| | ${show_locator_set}= | Vpp Show Lisp Locator Set | ${DUT1}
| | Lisp Is Empty | ${show_locator_set}

| Lisp locator_set data use for test reset locator_set are prepare
| | [Documentation] | *Generate lisp special type of locator_set data.*
| | ... | It will be use for test reset locator_set.
| | ...
| | ... | _Set testcase variables with lisp
| | ... | - ${locator_set_values}
| | ...
| | [Arguments] | ${DUT1} | ${locator_set_number}
| | ${locator_set_values}= | Generate Lisp Locator Set Reset Data |
| | ...                    | ${DUT1} | ${locator_set_number}
| | Set Test Variable | ${locator_set_values}

| Lisp eid address are prepare
| | [Documentation] | *Generate lisp eid address for testing LISP API.*
| | ...
| | ... | _Set testcase variables with lisp
| | ... | - ${set_eid}
| | ...
| | [Arguments] | ${DUT1} | ${eid_ipv4_num} | ${eid_ipv6_num}
| | ${set_eid} = | Generate Lisp Local Eid Data
| | ... | ${eid_ipv4_num} | ${eid_ipv6_num}
| | Set Test Variable | ${set_eid}

| Lisp eid address are set
| | [Documentation] | *Set the lisp eid address in node.*
| | ...
| | [Arguments] | ${DUT1}
| | Vpp Set Lisp Eid Table | ${DUT1} | ${set_eid}

| Lisp eid address are set correct to eid table
| | [Documentation] | *Test if the locator_set are set correct on VPP.*
| | ...
| | [Arguments] | ${DUT1}
| | ${show_eid}= | Vpp Show Lisp Local Eid Table | ${DUT1}
| | Lisp Should Be Equal | ${set_eid} | ${show_eid}

| Delete all lisp eid address form VPP
| | [Documentation] | *Delete all lisp eid address on node.*
| | ...
| | [Arguments] | ${DUT1}
| | Vpp Unset Lisp Eid Table | ${DUT1} | ${set_eid}

| Lisp eid table should be empty
| | [Documentation] | *Test if the eid table are empty.*
| | ...
| | [Arguments] | ${DUT1}
| | ${show_eid}= | Vpp Show Lisp Local Eid Table | ${DUT1}
| | Lisp Is Empty | ${show_eid}

| Lisp map resolver address are prepare
| | [Documentation] | *Generate map resolver address for testing LISP API.*
| | ...
| | ... | _Set testcase variables with lisp
| | ... | - ${set_map_resolver}
| | ...
| | [Arguments] | ${DUT1} | ${map_resolver_ipv4_num} | ${map_resolver_ipv6_num}
| | ${set_map_resolver} = | Generate Lisp Map Resolver Data
| | ... | ${map_resolver_ipv4_num} | ${map_resolver_ipv6_num}
| | Set Test Variable | ${set_map_resolver}

| Lisp map resolver address are set
| | [Documentation] | *Set the lisp map resolver address address in node.*
| | ...
| | [Arguments] | ${DUT1}
| | Vpp Set Lisp Map Resolver | ${DUT1} | ${set_map_resolver}

| Lisp map resolver address are set correct
| | [Documentation] | *Test if the map resolver address are set correct on VPP.*
| | ...
| | [Arguments] | ${DUT1}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${DUT1}
| | Lisp Should Be Equal | ${set_map_resolver} | ${show_map_resolver}

| Delete all lisp map resolver address from VPP
| | [Documentation] | *Delete all lisp map resolver address on node.*
| | ...
| | [Arguments] | ${DUT1}
| | Vpp Unset Lisp Map Resolver | ${DUT1} | ${set_map_resolver}

| Lip map resolver address should be empty
| | [Documentation] | *Test if the map resolver are empty.*
| | ...
| | [Arguments] | ${DUT1}
| | ${show_map_resolver}= | Vpp Show Lisp Map Resolver | ${DUT1}
| | Lisp Is Empty | ${show_map_resolver}
