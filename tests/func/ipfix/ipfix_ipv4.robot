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
| Resource | resources/libraries/robot/ipfix.robot
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.IPFIXSetup
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Show packet trace on all DUTs | ${nodes}
| ...           | AND          | Vpp Show Errors | ${nodes['DUT1']}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *IPFIX ipv4 test cases*
| ...
| ... | IPFIX tests use 3-node topology TG - DUT1 - DUT2 - TG with
| ... | one link between the nodes. DUT1 is configured with IPv4
| ... | routing and static routes. IPFIX is configured on DUT1 with
| ... | DUT1->TG interface as collector.Test packets are
| ... | sent from TG to or through DUT1. TG listens for flow report packets
| ... | and verifies that they contains flow records of test packets sent.

*** Variables ***
| ${dut1_to_tg_ip}= | 192.168.1.1
| ${dut2_to_dut1_ip}= | 192.168.2.1
| ${test_src_ip}= | 16.0.0.1
| ${test2_src_ip}= | 16.0.1.1
| ${prefix_length}= | 24
| ${ip_version}= | ip4

*** Test Cases ***
| TC01: DUT sends IPFIX template and data packets
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and any classify session.
| | ... | [Ver] Make TG listen for IPFIX template and data packets, verify
| | ... | that packet is received and correct.
| | ... | [Ref] RFC 7011
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${test_src_ip}
| | ... | ${tg_to_dut1_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ip4 | src
| | And VPP configures classify session L3 | ${dut1_node} | permit
| | ... | ${table_index} | ${skip_n} | ${match_n} | ip4 | src | ${test_src_ip}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=ip4
| | And setup IPFIX exporter | ${dut1_node} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index} | ip4
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | count=0

| TC02: DUT reports packet flow for traffic by source address
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add classify session with TG source address.
| | ... | [Ver] Make TG send a packet to DUT1, then listen for IPFIX template
| | ... | and data packets, verify that IPFIX reported the received packet.
| | ... | [Ref] RFC 7011
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${test_src_ip}
| | ... | ${tg_to_dut1_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ip4 | src
| | And VPP configures classify session L3 | ${dut1_node} | permit
| | ... | ${table_index} | ${skip_n} | ${match_n} | ip4 | src | ${test_src_ip}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=ip4
| | And setup IPFIX exporter | ${dut1_node} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index} | ip4
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | count=1

| TC03: DUT reports packet flow for traffic with local destination address
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add classify session with destination
| | ... | address of DUT1.
| | ... | [Ver] Make TG send a packet to DUT1, then listen for IPFIX template
| | ... | and data packets, verify that IPFIX reported the received packet.
| | ... | [Ref] RFC 7011
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${test_src_ip}
| | ... | ${tg_to_dut1_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ip4 | dst
| | And VPP configures classify session L3 | ${dut1_node} | permit
| | ... | ${table_index} | ${skip_n} | ${match_n} | ip4 | dst | ${dut1_to_tg_ip}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=ip4
| | And setup IPFIX exporter | ${dut1_node} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index} | ip4
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | count=1

| TC04: DUT reports packet flow for traffic with remote destination address
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add classify session with destination
| | ... | address of DUT2.
| | ... | [Ver] Make TG send a packet to DUT2 through DUT1, then listen
| | ... | for IPFIX template and data packets, verify that IPFIX reported
| | ... | the received packet.
| | ... | [Ref] RFC 7011
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set Interface Address | ${dut2_node}
| | ... | ${dut2_to_dut1} | ${dut2_to_dut1_ip} | ${prefix_length}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${test_src_ip}
| | ... | ${tg_to_dut1_mac}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip}
| | ... | ${dut2_to_dut1_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ip4 | dst
| | And VPP configures classify session L3 | ${dut1_node} | permit
| | ... | ${table_index} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | ${dut2_to_dut1_ip}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=ip4
| | And setup IPFIX exporter | ${dut1_node} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index} | ip4
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut2_node}
| | ... | ${tg_to_dut1} | ${dut2_to_dut1} | ${test_src_ip} | ${dut2_to_dut1_ip}
| | ... | count=1

| TC05: DUT reports packet flow through classifier wildcard table
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector, a chain of two classify tables and a classify
| | ... | session on the second table with TG source address.
| | ... | [Ver] Make TG send a packet to DUT1, then listen for IPFIX template
| | ... | and data packets, verify that the packet was classified and that
| | ... | IPFIX reported the received packet.
| | ... | [Ref] RFC 7011
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${test_src_ip}
| | ... | ${tg_to_dut1_mac}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ip4 | src
| | And VPP configures classify session generic | ${dut1_node} | hit-next 1
| | ... | ${table_index} | | | l3 ip4 src ${test_src_ip}
| | ${table_index2} | ${skip_n2} | ${match_n2}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ip4 | src dst
| | ... | next_table=${table_index}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index2} | ip_version=ip4
| | And setup IPFIX exporter | ${dut1_node} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index2} | ip4
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${test_src_ip} | ${dut1_to_tg_ip}
| | ... | count=1