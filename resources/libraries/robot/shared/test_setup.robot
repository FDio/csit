# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""Keywords used in test setups."""

*** Settings ***
| Library | resources.libraries.python.PapiHistory
|
| Documentation | Test Setup keywords.

*** Keywords ***
| Setup test
| | [Documentation]
| | ... | Common test setup for VPP tests.
| |
| | ... | *Arguments:*
| | ... | - ${actions} - Additional setup action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | Start Test Export
| | Reset PAPI History On All DUTs | ${nodes}
| | ${int} = | Set Variable If | ${nic_vfs} > 0 | prevf | pf
| | Create base startup configuration of VPP on all DUTs
| | FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Test Setup Action For ${action}
| | END

| Additional Test Setup Action For namespace
| | [Documentation]
| | ... | Additional Setup for tests which uses namespace.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Clean Up Namespaces | ${nodes['${dut}']}
| | END

| Additional Test Setup Action For performance
| | [Documentation]
| | ... | Additional Setup for tests which uses namespace.
| |
| | ${trex_running}= | Is Trex Running | ${tg}
| | Run Keyword If | not ${trex_running} | Startup Trex | ${tg} | ${osi_layer}
| | Stop Vpp Service on All Duts | ${nodes}
