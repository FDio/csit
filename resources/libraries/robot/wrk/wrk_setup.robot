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
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.DUTSetup
| Library  | resources.libraries.python.TrafficGenerator
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

# Suite setup

| Set up 3-node performance topology with wrk and DUT's NIC model
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
| | Set variables in 3-node circular topology with DUT interface model
| | ... | ${iface_model}
# Make sure TRex is stopped
| | ${running}= | Is TRex running | ${tg}
| | Run keyword if | ${running}==${True} | Teardown traffic generator | ${tg}
| | ${curr_driver}= | Get PCI dev driver | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | Run keyword if | '${curr_driver}'!='${None}'
| | ... | PCI Driver Unbind | ${tg} |
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
# Bind tg_if1 to driver specified in the topology
| | ${driver}= | Get Variable Value | ${tg['interfaces']['${tg_if1}']['driver']}
| | PCI Driver Bind | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']} | ${driver}
# Set IP on tg_if1
| | ${intf_name}= | Get Linux interface name | ${tg}
| | ... | ${tg['interfaces']['${tg_if1}']['pci_address']}
| | Set Linux interface IP | ${tg} | ${intf_name} | 192.168.10.1 | 24
| | Set Linux interface up | ${tg} | ${intf_name}
| | Install wrk on TG node

# Tests teardown

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
