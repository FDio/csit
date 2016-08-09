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
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Setup all DUTs before test
| Documentation | *Basic VPP test cases*
| ...
| ... | to do...

*** Variables ***
| ${iterations}= | ${100}

*** Test Cases ***
| TC03: Restart VPP
| | [Documentation]
| | ... | [Top] TG=DUT1; TG-DUT1-DUT2-TG. [Enc] None. [Cfg] Discovered \
| | ... | active interfaces. [Ver] Report active interfaces on DUT. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | 3_NODE_SINGLE_LINK_TOPO | TEST
| | ${failures}= | Set Variable | ${0}
| | :FOR | ${index} | IN RANGE | ${iterations}
| | | ${stat} | ${exe_time}= | Restart VPP on DUT | ${nodes['DUT1']}
| | | ${incr}= | Set Variable If | "${stat}" == "PASS" | ${0} | ${1}
| | | ${failures}= | Evaluate | $failures + $incr
| | | ${time}= | Run Keyword If | "${stat}" == "PASS" | Convert To Number | ${exe_time} | 3
| | | ${restart_time}= | Set Variable If | "${stat}" == "PASS" | ${time} s | None
| | | Log To Console | Iteration: ${index} \| status: ${stat} \| VPP restart time: ${restart_time}
| | ${log_message}= | Set Variable If | ${failures} == 0 | All ${iterations} VPP restarts successfull. | VPP failed to restart: ${failures} times
| | Run Keyword If | ${failures} == 0 | Log | ${log_message} | INFO
| | ... | ELSE | FAIL | ${log_message}
