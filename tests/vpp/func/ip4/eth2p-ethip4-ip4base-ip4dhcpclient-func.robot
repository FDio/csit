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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/features/dhcp_client.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Library | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *DHCPv4 Client related test cases*

*** Variables ***
| ${client_hostname}= | dhcp-client
| ${client_ip}= | 192.168.23.10
| ${client_mask}= | 255.255.255.0
| ${server_ip}= | 192.168.23.1
| ${own_xid}= | 11112222
| ${lease_time}= | ${15}

*** Test Cases ***
| TC01: VPP sends a DHCP DISCOVER
| | [Documentation] | Configure DHCPv4 client on interface to TG without
| | ... | hostname and check if DHCPv4 DISCOVER message contains all
| | ... | required fields with expected values.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | When Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | Then Verify DHCP DISCOVER header | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac}

| TC02: VPP sends a DHCPv4 DISCOVER with hostname
| | [Documentation] | Configure DHCPv4 client on interface to TG with hostname
| | ... | and check if DHCPv4 DISCOVER message contains all required
| | ... | fields with expected values.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | When Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${client_hostname}
| | Then Verify DHCP DISCOVER header | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac} | ${client_hostname}

| TC03: VPP sends DHCPv4 REQUEST after OFFER
| | [Documentation] | Configure DHCPv4 client on interface to TG and check if
| | ... | DHCPv4 REQUEST message contains all required fields.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| | ... | ${FALSE} | ${NONE}
| | When Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | Then Verify DHCP REQUEST after OFFER | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if1_mac} | ${server_ip}
| | ... | ${dut_to_tg_if1_mac} | ${client_ip} | ${client_mask}

| TC04: VPP doesn't send DHCPv4 REQUEST after OFFER with wrong XID
| | [ Tags ] | EXPECTED_FAILING
| | [Documentation] | Configure DHCPv4 client on interface to TG. If server
| | ... | sends DHCPv4 OFFER with different XID as in DHCPv4
| | ... | DISCOVER, DHCPv4 REQUEST message shouldn't be sent.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| | ... | ${FALSE} | ${NONE}
| | When Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | Then Run Keyword And Expect Error | DHCP REQUEST Rx timeout
| | ... | Verify DHCP REQUEST after OFFER | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if1_mac} | ${server_ip}
| | ... | ${dut_to_tg_if1_mac} | ${client_ip} | ${client_mask}
| | ... | offer_xid=${own_xid}

| TC05: VPP honors DHCPv4 lease time
| | [Documentation] | Send IP configuration to the VPP client via DHCPv4.
| | ... | Address is checked with ICMP echo request and there should
| | ... | be no reply for echo request when lease has expired.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | And VPP Route Add | ${dut_node} | 255.255.255.255 | 32 | ${NONE} | local
| | ... | ${FALSE} | ${NONE}
| | When Set DHCP client on Interface | ${dut_node} | ${dut_to_tg_if1}
| | And Configure IP on client via DHCP
| | ... | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tg_to_dut_if1_mac} | ${server_ip}
| | ... | ${client_ip} | ${client_mask}
| | ... | ${lease_time}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1} | ${server_ip}
| | ... | ${tg_to_dut_if1_mac}
| | Then Send ICMP echo request and verify answer
| | ... | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac} | ${client_ip}
| | ... | ${server_ip}
| | And Sleep | ${lease_time}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP echo request and verify answer | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac}
| | ... | ${client_ip} | ${server_ip}
