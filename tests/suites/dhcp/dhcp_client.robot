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
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *DHCP Client related test cases*

*** Variables ***
| ${client_hostname}= | dhcp-client
| ${client_ip}= | 192.168.23.10
| ${client_mask}= | 255.255.255.0
| ${server_ip}= | 192.168.23.1
| ${own_xid}= | 11112222
| ${lease_time}= | ${15}

*** Test Cases ***
| VPP sends a DHCP DISCOVER
| | [Documentation] | Configure DHCP client on interface to TG without hostname
| | ...             | and check if DHCP DISCOVER message contains all required
| | ...             | fields with expected values.
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | When  Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | Then  Check DHCP DISCOVER header | ${tg_node}
| |       ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}

| VPP sends a DHCP DISCOVER with hostname
| | [Documentation] | Configure DHCP client on interface to TG with hostname
| | ...             | and check if DHCP DISCOVER message contains all required
| | ...             | fields with expected values.
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
| | And   VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| |       ... | ${FALSE} | ${NONE}
| | When  Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | Then  Check DHCP REQUEST after OFFER | ${tg_node} | ${tg_to_dut_if1}
| |       ... | ${tg_to_dut_if1_mac} | ${server_ip}
| |       ... | ${dut_to_tg_if1_mac} | ${client_ip} | ${client_mask}

| VPP doesn't send DHCP REQUEST after OFFER with wrong XID
| | [ Tags ] | EXPECTED_FAILING
| | [Documentation] | Configure DHCP client on interface to TG. If server sends
| | ...             | DHCP OFFER with different XID as in DHCP DISCOVER,
| | ...             | DHCP REQUEST message shouldn't be sent.
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| |       ... | ${FALSE} | ${NONE}
| | When  Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | Then  Run Keyword And Expect Error | DHCP REQUEST Rx timeout
| |       ... | Check DHCP REQUEST after OFFER | ${tg_node} | ${tg_to_dut_if1}
| |       ... | ${tg_to_dut_if1_mac} | ${server_ip}
| |       ... | ${dut_to_tg_if1_mac} | ${client_ip} | ${client_mask}
| |       ... | offer_xid=${own_xid}

| VPP honors DHCPv4 lease time
| | [Documentation] | Send IP configuration to the VPP client via DHCP. Address
| | ...             | is checked with ICMP echo request and there should be no
| | ...             | reply for echo request when lease has expired.
| | ...
| | Given Path for 2-node testing is set
| |       ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And   Interfaces in 2-node path are up
| | And   VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| |       ... | ${FALSE} | ${NONE}
| | When  Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | And   Send IP configuration to client via DHCP
| |       ... | ${tg_node} | ${tg_to_dut_if1}
| |       ... | ${tg_to_dut_if1_mac} | ${server_ip}
| |       ... | ${client_ip} | ${client_mask}
| |       ... | ${lease_time}
| | And   Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1} | ${server_ip}
| |       ... | ${tg_to_dut_if1_mac}
| | Then  Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut_if1}
| |       ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac} | ${client_ip}
| |       ... | ${server_ip}
| | And   Sleep | ${lease_time}
| | And   Run Keyword And Expect Error | ICMP echo Rx timeout
| |       ... | Node replies to ICMP echo request | ${tg_node}
| |       ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac}
| |       ... | ${client_ip} | ${server_ip}
