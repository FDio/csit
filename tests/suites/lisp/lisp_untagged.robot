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

*** Test Cases ***

| VPP lisp locator_set API test
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Test set Lisp locator_set params | ${nodes['${dut}']}
| | | Test unset Lisp locator_set params | ${nodes['${dut}']}

| VPP lisp locator_set API test reset
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Test reset Lisp locator_set | ${nodes['${dut}']}
| | | Test unset reset Lisp locator_set | ${nodes['${dut}']}

| VPP lisp local Eid Table API test
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Test set Lisp local eid table | ${nodes['${dut}']}
| | | Test unset Lisp local eid table | ${nodes['${dut}']}

| VPP lisp Map Resolver API Test
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Test set Lisp Map Resolver | ${nodes['${dut}']}
| | | Test unset Lisp map resolver | ${nodes['${dut}']}

| VPP lisp gpe interface up/down API Test
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Set lisp gpe interface down and up | ${nodes['${dut}']}
