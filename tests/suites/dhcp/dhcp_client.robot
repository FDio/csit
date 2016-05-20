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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/dhcp_client.robot
| Resource | resources/libraries/robot/ipv4.robot
| Library | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Documentation | *DHCP Client related test cases*

*** Variables ***
| ${client_hostname} | dhcp-client

*** Test Cases ***
| VPP sends a DHCP DISCOVER
| | [Documentation] | Configure DHCP client on interface to TG and check if
| | ...             | DHCP DISCOVER message contains all required fields.
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | When  Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | Then  Check DHCP DISCOVER header | ${tg_node}
| |       ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}

| VPP sends a DHCP DISCOVER with hostname
| | [Documentation] | Configure DHCP client on interface to TG and check if
| | ...             | DHCP DISCOVER message contains all required fields.
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | When  Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| |       ... | ${client_hostname}
| | Then  Check DHCP DISCOVER header | ${tg_node}
| |       ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac} | ${client_hostname}

| VPP sends DHCP REQUEST after OFFER
| | [Documentation] | Configure DHCP client on interface to TG and check if
| | ...             | DHCP REQUEST message contains all required fields.
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And Set Route | ${dut_node} | 255.255.255.255 | 32 | local | 255.255.255.255
| | When  Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | Then  Check DHCP REQUEST header | ${tg_node}
| |       ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}
