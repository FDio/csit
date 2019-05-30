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
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/telemetry/ipfix.robot
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.telemetry.IPFIXSetup
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *IPFIX ipv6 test cases*
| ...
| ... | IPFIX tests use 3-node topology TG - DUT1 - DUT2 - TG with
| ... | one link between the nodes. DUT1 is configured with IPv4 and IPV6
| ... | routing and static routes. IPFIX is configured on DUT1 with
| ... | DUT1->TG interface as collector.Test packets are
| ... | sent from TG to or through DUT1. TG listens for flow report packets
| ... | and verifies that they contains flow records of test packets sent.

*** Variables ***
| ${dut1_to_tg_ip}= | 10::10
| ${dut2_to_dut1_ip}= | 11::10
| ${tg_to_dut1_ip}= | 12::10
| ${prefix_length}= | 64
| ${ip_version}= | ip6
| ${port}= | 80

# IPv4 addresses used for IPFIX exporter. Export over IPv6 not (yet?) supported.
| ${dut1_to_tg_ip4}= | 192.168.1.1
| ${tg_to_dut1_ip4}= | 192.168.1.2

*** Test Cases ***
| TC01: DUT reports packet flow for traffic by source address
| | [Tags] | EXPECTED_FAILING
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add classify session with TG source address.
| | ... | [Ver] Make TG send a packet to DUT1, then listen for IPFIX template
| | ... | and data packets, verify that IPFIX reported the received packet.
| | ... | [Ref] RFC 7011
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Set VPP Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set VPP Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${24}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip4}
| | ... | ${tg_to_dut1_mac}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip}
| | ... | ${tg_to_dut1_mac}
| | And VPP RA suppress link layer | ${dut1_node} | ${dut1_to_tg}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ${ip_version} | src
| | And VPP configures classify session L3 | ${dut1_node} | permit
| | ... | ${table_index} | ${skip_n} | ${match_n} | ${ip_version} | src
| | ... | ${tg_to_dut1_ip}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=${ip_version}
| | And setup IPFIX exporter | ${dut1_node} | ${tg_to_dut1_ip4}
| | ... | ${dut1_to_tg_ip4} | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index}
| | ... | ${ip_version}
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${tg_to_dut1_ip} | ${dut1_to_tg_ip}

| TC02: DUT reports packet flow for traffic with local destination address
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add classify session with destination
| | ... | address of DUT1.
| | ... | [Ver] Make TG send a packet to DUT1, then listen for IPFIX template
| | ... | and data packets, verify that IPFIX reported the received packet.
| | ... | [Ref] RFC 7011
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Set VPP Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set VPP Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${24}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip4}
| | ... | ${tg_to_dut1_mac}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip}
| | ... | ${tg_to_dut1_mac}
| | And VPP RA suppress link layer | ${dut1_node} | ${dut1_to_tg}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ${ip_version} | dst
| | And VPP configures classify session L3 | ${dut1_node} | permit
| | ... | ${table_index} | ${skip_n} | ${match_n} | ${ip_version} | dst
| | ... | ${dut1_to_tg_ip}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=${ip_version}
| | And setup IPFIX exporter | ${dut1_node} | ${tg_to_dut1_ip4}
| | ... | ${dut1_to_tg_ip4} | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index}
| | ... | ${ip_version}
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${tg_to_dut1_ip} | ${dut1_to_tg_ip}

| TC03: DUT reports packet flow for traffic with remote destination address
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add classify session with destination
| | ... | address of DUT2.
| | ... | [Ver] Make TG send a packet to DUT2 through DUT1, then listen
| | ... | for IPFIX template and data packets, verify that IPFIX reported
| | ... | the received packet.
| | ... | [Ref] RFC 7011
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Set VPP Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set VPP Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${24}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip4}
| | ... | ${tg_to_dut1_mac}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip}
| | ... | ${tg_to_dut1_mac}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip}
| | ... | ${dut2_to_dut1_mac}
| | And VPP RA suppress link layer | ${dut1_node} | ${dut1_to_tg}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ${ip_version} | dst
| | And VPP configures classify session L3 | ${dut1_node} | permit
| | ... | ${table_index} | ${skip_n} | ${match_n} | ${ip_version} | dst
| | ... | ${dut2_to_dut1_ip}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=${ip_version}
| | And setup IPFIX exporter | ${dut1_node} | ${tg_to_dut1_ip4}
| | ... | ${dut1_to_tg_ip4} | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index}
| | ... | ${ip_version}
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${tg_to_dut1_ip}
| | ... | ${dut2_to_dut1_ip}

| TC04: DUT reports packet flow for traffic by source and destination port
| | [Tags] | SKIP_VPP_PATCH
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Cfg] On DUT1 configure IPFIX with TG interface
| | ... | address as collector and add classify session with TG source address
| | ... | and source and destination ports.
| | ... | [Ver] Make TG send a packet to DUT1, then listen for IPFIX template
| | ... | and data packets, verify that IPFIX reported the received packet.
| | ... | [Ref] RFC 7011
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Set VPP Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Set VPP Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${24}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip4}
| | ... | ${tg_to_dut1_mac}
| | And Add ARP on DUT | ${dut1_node} | ${dut1_to_tg} | ${tg_to_dut1_ip}
| | ... | ${tg_to_dut1_mac}
| | And VPP RA suppress link layer | ${dut1_node} | ${dut1_to_tg}
| | ${table_index} | ${skip_n} | ${match_n}=
| | ... | And VPP creates classify table L3 | ${dut1_node} | ${ip_version}
| | ... | src proto l4 src_port dst_port
| | And VPP configures classify session generic | ${dut1_node}
| | ... | acl-hit-next permit | ${table_index} | ${skip_n} | ${match_n}
| | ... | l3 ${ip_version} src ${tg_to_dut1_ip}
| | ... | proto 6 l4 src_port ${port} dst_port ${port}
| | When Assign interface to flow table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${table_index} | ip_version=${ip_version}
| | And setup IPFIX exporter | ${dut1_node} | ${tg_to_dut1_ip4}
| | ... | ${dut1_to_tg_ip4} | interval=5
| | And Set IPFIX stream | ${dut1_node} | ${1}
| | And Assign classify table to exporter | ${dut1_node} | ${table_index}
| | ... | ${ip_version}
| | Then Send packets and verify IPFIX | ${tg_node} | ${dut1_node}
| | ... | ${tg_to_dut1} | ${dut1_to_tg} | ${tg_to_dut1_ip} | ${dut1_to_tg_ip}
| | ... | port=${port}

# TODO: DUT reports packet flow when ACL is configured with wildcards
