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
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/l2/tagging.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_DOUBLE_LINK_TOPO | HW_ENV | VM_ENV | VPP_VM_ENV
| Test Setup | Set up functional test
| Test Teardown | Run Keywords  | Tear down functional test
| ... | AND | Stop and clear QEMU | ${dut_node}
| Documentation | *L2 bridge domain with VLAN tag over VM test cases*
| ...
| ... | *[Top] Network Topologies:* TG=DUT 2-node circular topology
| ... | with double links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-dot1q-IPv4-ICMPv4 or
| ... | Eth-dot1q-IPv6-ICMPv6 on TG=DUT and on DUT=VM.
| ... | *[Cfg] DUT configuration:* DUT is configured with two bridge domains
| ... | (L2BD) with MAC learning enabled; each one with added VLAN
| ... | sub-interface towards TG and vhost-user interface to local VM. Configure
| ... | linux bridge on VM to pass traffic between both vhost-user interfaces.
| ... | *[Ver] TG verification:* Make TG send ICMPv4/ICMPv6 Echo Req between two
| ... | of its interfaces to be switched by DUT via VM; verify packets are
| ... | switched between these TG interfaces; on receive TG verifies packets for
| ... | correctness and their IPv4 src-addr, dst-addr, MAC addresses and
| ... | VLAN tag.
| ... | *[Ref] Applicable standard specifications:* IEEE 802.1q.

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2

| ${vlan_id1}= | 110
| ${vlan_wrong}= | 150

| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

| ${ip4_1}= | 192.168.100.1
| ${ip4_2}= | 192.168.100.2

| ${ip6_1}= | 3ffe:63::1
| ${ip6_2}= | 3ffe:63::2

*** Test Cases ***
| TC01: eth2p-dot1q-l2bdbasemaclrn-eth-2vhost-1vm - ipv4
| | [Documentation]
| | ... | [Top] TG=DUT.
| | ... | [Enc] Eth-dot1q-IPv4-ICMPv4 on TG=DUT and on DUT=VM.
| | ... | [Cfg] On DUT configure two L2BDs (MAC learning enabled); first L2BD
| | ... | with Dot1Q tagged interface to TG-if1 and vhost-user interface to
| | ... | local VM, second one with vhost-user interface to local VM and Dot1Q
| | ... | tagged interface towards TG-if2. Configure linux bridge on VM to pass
| | ... | traffic between both vhost-user interfaces.
| | ... | [Ver] Make TG send ICMPv4 Echo Req tagged with one Dot1q tag
| | ... | from one of its interfaces to another one via DUT and VM; verify
| | ... | that packet is received.
| | ... | [Ref] IEEE 802.1q
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create vlan sub-interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Create vlan sub-interface
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${vlan_id1}
| | And Configure vhost interfaces for L2BD forwarding
| | ... | ${dut_node} | ${sock1} | ${sock2}
| | And Configure VM for vhost L2BD forwarding
| | ... | ${dut_node} | ${sock1} | ${sock2}
| | And Add interface to bridge domain | ${dut_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${vhost_if1}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${vlan2_index}
| | ...                                     | ${bd_id2}
| | And Add interface to bridge domain | ${dut_node} | ${vhost_if2}
| | ...                                     | ${bd_id2}
| | Then Send ICMP packet and verify received packet
| | ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2} | ${ip4_1} | ${ip4_2}
| | ... | encaps=Dot1q | vlan1=${vlan_id1} | encaps_rx=Dot1q
| | And Send ICMP packet and verify received packet
| | ... | ${tg_node} | ${tg_to_dut_if2} | ${tg_to_dut_if1} | ${ip4_2} | ${ip4_1}
| | ... | encaps=Dot1q | vlan1=${vlan_id1} | encaps_rx=Dot1q

| TC01: eth2p-dot1q-l2bdbasemaclrn-eth-2vhost-1vm - ipv6
| | [Documentation]
| | ... | [Top] TG=DUT.
| | ... | [Enc] Eth-dot1q-IPv6-ICMPv6 on TG=DUT and on DUT=VM.
| | ... | [Cfg] On DUT configure two L2BDs (MAC learning enabled); first L2BD
| | ... | with Dot1Q tagged interface to TG-if1 and vhost-user interface to
| | ... | local VM, second one with vhost-user interface to local VM and Dot1Q
| | ... | tagged interface towards TG-if2. Configure linux bridge on VM to pass
| | ... | traffic between both vhost-user interfaces.
| | ... | [Ver] Make TG send ICMPv6 Echo Req tagged with one Dot1q tag
| | ... | from one of its interfaces to another one via DUT and VM; verify
| | ... | that packet is received.
| | ... | [Ref] IEEE 802.1q
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | ${vlan1_name} | ${vlan1_index}= | When Create vlan sub-interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${vlan_id1}
| | ${vlan2_name} | ${vlan2_index}= | And Create vlan sub-interface
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${vlan_id1}
| | And Configure vhost interfaces for L2BD forwarding
| | ... | ${dut_node} | ${sock1} | ${sock2}
| | And Configure VM for vhost L2BD forwarding
| | ... | ${dut_node} | ${sock1} | ${sock2}
| | And Add interface to bridge domain | ${dut_node} | ${vlan1_index}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${vhost_if1}
| | ...                                     | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${vlan2_index}
| | ...                                     | ${bd_id2}
| | And Add interface to bridge domain | ${dut_node} | ${vhost_if2}
| | ...                                     | ${bd_id2}
| | Then Send ICMP packet and verify received packet
| | ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2} | ${ip6_1} | ${ip6_2}
| | ... | encaps=Dot1q | vlan1=${vlan_id1} | encaps_rx=Dot1q
| | And Send ICMP packet and verify received packet
| | ... | ${tg_node} | ${tg_to_dut_if2} | ${tg_to_dut_if1} | ${ip6_2} | ${ip6_1}
| | ... | encaps=Dot1q | vlan1=${vlan_id1} | encaps_rx=Dot1q




