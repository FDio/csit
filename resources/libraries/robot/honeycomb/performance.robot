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
| Library | resources.libraries.python.honeycomb.Performance
| Library | resources.libraries.python.InterfaceUtil
| Documentation | Keywords used in Honeycomb performance testing.

*** Keywords ***
| 2-node HC Performance Suite Setup with DUT's NIC model
| | [Documentation]
| | ... | Updates interfaces on node and sets up global variables used in test
| | ... | cases based on interface model provided as an argument. Initializes
| | ... | traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - topology_type - Topology type. Type: string
| | ... | - nic_model - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| DPDK 2-node Performance Suite Setup with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${topology_type} | ${nic_model}
| | ...
| | 2-node circular Topology Variables Setup with DUT interface model
| | ... | ${nic_model}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut1} | ${dut1_if2} | ${topology_type}

| Blacklist VPP Interface
| | [Documentation] | Blacklist and interface by assigning it an IP address.
| | ...
| | ... | *Arguments:*
| | ... | - node - Honeycomb node. Type: dict
| | ... | - interface - Name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| DPDK 2-node Performance Suite Setup with DUT's NIC model \
| | ... | \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Stop VPP Service on DUT | ${node}
| | Blacklist interface | ${node} | ${interface}
| | Setup DUT | ${node}

| Undo interface blacklist
| | [Documentation] | bcd
| | [Arguments] | ${node} | ${interface}
| | Blacklist interface | ${node} | ${interface} | remove=${TRUE}
