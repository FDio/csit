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
| Resource | resources/libraries/robot/wrk/wrk_setup.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | POKUS
| ...
| Suite Setup | Set up 2-node topology with wrk and DUT interface model
| ... | Intel-X520-DA2
| ...
| Test Setup | Set up performance test
| Test Teardown | Tear down performance test with wrk
| ...
| Documentation | *Reference NDR throughput IPv4 whitelist verify test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT-TG 2-node topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 for IPv4 routing.
| ... | *[Cfg] DUT configuration:*
| ... | *[Ver] TG verification:*
| ... | *[Ref] Applicable standard specifications:*

*** Test Cases ***
| Example bw
| | [Documentation]
| | ... | Measure and report throughput using wrk.
| | ...
| | [Tags]
| | ...
| | Measure throughput | wrk-bw-1url-1core-50con

| Example cps
| | [Documentation]
| | ... | Measure number of connections per second using wrk.
| | ...
| | [Tags]
| | ...
| | Measure connections per second | wrk-cps-1url-1core-1con

| Example rps
| | [Documentation]
| | ... | Measure and report number of requests per second using wrk.
| | ...
| | [Tags]
| | ...
| | Measure requests per second | wrk-rps-1url-1core-50con
