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
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/telemetry/ipfix.robot
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.telemetry.IPFIXSetup
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO | EXPECTED_FAILING
| ...        | SKIP_VPP_PATCH
| Test Setup | Func Test Setup
| Test Teardown | Func Test Teardown
| Documentation | *IPFIX ipv4 test cases*
| ...
| ... | IPFIX tests use 3-node topology TG - DUT1 - DUT2 - TG with
| ... | one link between the nodes. DUT1 is configured with IPv4
| ... | routing and static routes. IPFIX is configured on DUT1 with
| ... | DUT1->TG interface as collector. Test packets are
| ... | sent from TG to DUT1. TG listens for flow report packets
| ... | and verifies that they contains flow record of test packets sent.

*** Variables ***
| ${dut1_to_tg_ip}= | 192.168.1.1
| ${tg_to_dut1_ip}= | 192.168.1.2
| ${prefix_length}= | 24
| ${ip_version}= | ip4
| ${sessions}= | 80

*** Test Cases ***
| TC01: DUT reports packet flow with a large number of packets
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add classify session with TG source address.
| | ... | [Ver] Make TG send packets to DUT1, then listen for IPFIX template
| | ... | and data packets, verify that IPFIX reported the received packets.
| | ... | [Ref] RFC 7011
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip}
| | ... | ${tg_to_dut1_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ${ip_version} | src
| | And VPP configures classify session L3 | ${dut1_node} | permit
| | ... | ${table_index} | ${skip_n} | ${match_n} | ${ip_version} | src
| | ... | ${tg_to_dut1_ip}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=${ip_version}
| | And setup IPFIX exporter | ${dut1_node} | ${tg_to_dut1_ip}
| | ... | ${dut1_to_tg_ip} | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index}
| | ... | ${ip_version}
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${tg_to_dut1_ip} | ${dut1_to_tg_ip}
| | ... | count=20000 | timeout=10

| TC02: DUT reports packet flow when multiple sessions are configured
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add several classify sessions with different
| | ... | ports.
| | ... | [Ver] Make TG send packets to DUT1 using a range of ports matching
| | ... | configured sessions, then listen for IPFIX template and data packets,
| | ... | verify that IPFIX reported the received packets for each session.
| | ... | [Ref] RFC 7011
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip}
| | ... | ${tg_to_dut1_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ${ip_version}
| | ... | src proto l4 src_port dst_port
| | :FOR | ${index} | IN RANGE | ${sessions}
| | | VPP configures classify session generic | ${dut1_node}
| | | ... | acl-hit-next permit | ${table_index} | ${skip_n} | ${match_n}
| | | ... | l3 ${ip_version} src ${tg_to_dut1_ip}
| | | ... | proto 6 l4 src_port ${index} dst_port ${index}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=${ip_version}
| | And setup IPFIX exporter | ${dut1_node} | ${tg_to_dut1_ip}
| | ... | ${dut1_to_tg_ip}
| | ... | mtu=1450 | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index}
| | ... | ${ip_version}
| | Then Send session sweep and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${tg_to_dut1_ip} | ${dut1_to_tg_ip}
| | ... | ${sessions} | timeout=10 | count=3

# TODO: DUT reports packet flow when ACL is configured with wildcards
