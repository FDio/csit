# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Documentation | Performance suite keywords - Suite and test setups and
| ... | teardowns.

*** Keywords ***

# Keywords used in setups and teardowns

| Set variables in 3-node circular topology with DUT interface model with double link between DUTs
| | [Documentation]
| | ... | Compute path for testing on three given nodes in circular topology
| | ... | with double link between DUTs based on interface model provided as an
| | ... | argument and set corresponding suite variables.
| | ...
| | ... | *Arguments:*
| | ... | - iface_model - Interface model. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - tg - TG node
| | ... | - tg_if1 - 1st TG interface towards DUT.
| | ... | - tg_if1 - 1st TG interface MAC address.
| | ... | - tg_if2 - 2nd TG interface towards DUT.
| | ... | - tg_if2 - 2nd TG interface MAC address.
| | ... | - dut1 - DUT1 node
| | ... | - dut1_if1 - DUT1 interface towards TG.
| | ... | - dut1_if2_1 - DUT1 interface 1 towards DUT2.
| | ... | - dut1_if2_2 - DUT1 interface 2 towards DUT2.
| | ... | - dut2 - DUT2 node
| | ... | - dut2_if1_1 - DUT2 interface 1 towards DUT1.
| | ... | - dut2_if1_2 - DUT2 interface 2 towards DUT1.
| | ... | - dut2_if2 - DUT2 interface towards TG.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set variables in 3-node circular topology with DUT interface model\
| | ... | with double link between DUTs \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${iface_model}
| | ...
| | ${iface_model_list}= | Create list | ${iface_model}
| | # Compute path TG - DUT1 with single link in between
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if1} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | # Compute path TG - DUT2 with single link in between
| | Clear Path
| | Append Node | ${nodes['TG']}
| | Append Node | ${nodes['DUT2']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['TG']}
| | Compute Path
| | ${tg_if2} | ${tg}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | # Compute path DUT1 - DUT2 with double link in between
| | Clear Path
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['DUT2']} | filter_list=${iface_model_list}
| | Append Node | ${nodes['DUT1']} | filter_list=${iface_model_list}
| | Compute Path | always_same_link=${FALSE}
| | ${dut1_if2_1} | ${dut1}= | First Interface
| | ${dut1_if2_2} | ${dut1}= | Last Interface
| | ${dut2_if1_1} | ${dut2}= | First Ingress Interface
| | ${dut2_if1_2} | ${dut2}= | Last Egress Interface
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | # Set suite variables
| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${tg_if1}
| | Set Suite Variable | ${tg_if1_mac}
| | Set Suite Variable | ${tg_if2}
| | Set Suite Variable | ${tg_if2_mac}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut1_if1}
| | Set Suite Variable | ${dut1_if2_1}
| | Set Suite Variable | ${dut1_if2_2}
| | Set Suite Variable | ${dut2}
| | Set Suite Variable | ${dut2_if1_1}
| | Set Suite Variable | ${dut2_if1_2}
| | Set Suite Variable | ${dut2_if2}

# Suite setups

| Set up 3-node performance topology with DUT's NIC model with double link between DUTs
| | [Documentation]
| | ... | Suite preparation phase that sets the default startup configuration of
| | ... | VPP on all DUTs. Updates interfaces on all nodes and sets the global
| | ... | variables used in test cases based on interface model provided as an
| | ... | argument. Initializes traffic generator.
| | ...
| | ... | *Arguments:*
| | ... | - osi_layer - OSI Layer type to initialize TG with. Type: string
| | ... | - nic_name - Interface model. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up 3-node performance topology with DUT's NIC model with \
| | ... | double link between DUTs \| L2 \| Intel-X520-DA2 \|
| | ...
| | [Arguments] | ${osi_layer} | ${nic_name}
| | ...
| | Set variables in 3-node circular topology with DUT interface model with double link between DUTs
| | ... | ${nic_name}
| | Initialize traffic generator | ${tg} | ${tg_if1} | ${tg_if2}
| | ... | ${dut1} | ${dut1_if1} | ${dut2} | ${dut2_if2} | ${osi_layer}
