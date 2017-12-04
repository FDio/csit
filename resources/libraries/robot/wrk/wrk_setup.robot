# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library  | resources.tools.wrk.wrk
| Resource | resources/libraries/robot/performance/performance_setup.robot
| ...
| Documentation | L2 keywords to set up wrk and to measure performance
| ... | parameters using wrk.

*** Keywords ***
| Install wrk on TG node
| | [Documentation]
| | ... | Install wrk on the TG node.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Install wrk on TG node \|
| | ...
| | Install wrk | ${tg}

| Measure throughput
| | [Documentation]
| | ... | Measure throughput using wrk.
| | ...
| | ... | *Arguments:*
| | ... | - ${profile} - THe name of the wrk traffic profile defining the
| | ... | traffic. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Measure throughput \| wrk-bw-1url-1core-50con \|
| | ...
| | [Arguments] | ${profile}
| | ...
| | ${output}= | Run wrk | ${tg} | ${profile}
| | Log to console | ${output}

| Measure requests per second
| | [Documentation]
| | ... | Measure number of requests per second using wrk.
| | ...
| | ... | *Arguments:*
| | ... | - ${profile} - THe name of the wrk traffic profile defining the
| | ... | traffic. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Measure requests per second \| wrk-bw-1url-1core-50con \|
| | ...
| | [Arguments] | ${profile}
| | ...
| | ${output}= | Run wrk | ${tg} | ${profile}
| | Log to console | ${output}

| Measure connections per second
| | [Documentation]
| | ... | Measure number of connections per second using wrk.
| | ...
| | ... | *Arguments:*
| | ... | - ${profile} - THe name of the wrk traffic profile defining the
| | ... | traffic. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Measure connections per second \| wrk-bw-1url-1core-50con \|
| | ...
| | [Arguments] | ${profile}
| | ...
| | ${output}= | Run wrk | ${tg} | ${profile}
| | Log to console | ${output}

| Set variables in 2-node topology
| | [Documentation]
| | ... | Compute path for testing on two given nodes in
| | ... | topology and set corresponding suite variables.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - 1st DUT interface towards TG.
| | ... | - dut1_if2 - 2nd DUT interface towards TG.
| | ...
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${tg_if1} | ${tg}= | First Interface
| | ${dut1_if1} | ${dut1}= | First Ingress Interface
| | ${dut1_if2} | ${dut1}= | Last Egress Interface
| | ${tg_if2} | ${tg}= | Last Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}

| Set variables in 2-node topology with DUT interface model
| | [Documentation]
| | ... | Compute path for testing on two given nodes in topology
| | ... | based on interface model provided as an argument and set
| | ... | corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - 1st DUT interface towards TG.
| | ... | - dut1_if2 - 2nd DUT interface towards TG.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set variables in 2-node topology with DUT interface model\
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
| | ${iface_model_list}= | Create list | ${iface_model}
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path | always_same_link=${False}
| | ${tg_if1} | ${tg}= | First Interface
| | ${dut1_if1} | ${dut1}= | First Ingress Interface
| | ${dut1_if2} | ${dut1}= | Last Egress Interface
| | ${tg_if2} | ${tg}= | Last Interface
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2}

# Suite setup

| Set up 2-node topology with wrk and DUT interface model
| | [Documentation]
| | ... | Suite preparation phase that setup default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and setup global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Installs the traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up 2-node topology with wrk and DUT interface model\
| | ... | \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
# Used for local testing. TODO: remove
#| | Set variables in 2-node topology
| | Set variables in 2-node topology with DUT interface model
| | ... | ${iface_model}
| | Install wrk on TG node

# Tests teardowns

| Tear down performance test with wrk
| | [Documentation] | Common test teardown for ndrdisc and pdrdisc performance \
| | ... | tests.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down performance test with wrk \|
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Show statistics on all DUTs | ${nodes}
