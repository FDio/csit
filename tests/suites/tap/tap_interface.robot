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
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/traffic.robot
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.Tap
| Library  | resources.libraries.python.Namespaces
| Library  | resources.libraries.python.IPUtil
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Clean Up Namespaces | ${nodes['DUT1']}
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...        | AND          | Clean Up Namespaces | ${nodes['DUT1']}
| Documentation | *Tap Interface Traffic Tests*
| ... | *(Top) Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *(Enc) Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4.
| ... | *(Cfg) DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG)
| ... | are set depending on test case; Namespaces (NM)
| ... | are set on DUT1 with attached linux-TAP.
| ... | *(Ver) TG verification:* Test ICMPv4 Echo Request packets
| ... | are sent by TG on link to DUT1; On receipt TG verifies packets
| ... | for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.
| ... | *(Ref) Applicable standard specifications:*

*** Variables ***
| ${tap1_VPP_ip}= | 16.0.10.1
| ${tap2_VPP_ip}= | 16.0.20.1

| ${tap1_NM_ip}= | 16.0.10.2
| ${tap2_NM_ip}= | 16.0.20.2
| ${tap2_NM_SHG}= | 16.0.10.3

| ${bid_from_TG}= | 19
| ${bid_to_TG}= | 20
| ${bid_NM}= | container1_br
| ${bd_id1}= | 21
| ${bd_id2}= | 22
| ${shg1}= | 2
| ${shg2}= | 3

| ${tap1_NM_mac}= | 02:00:00:00:00:02
| ${tap2_NM_mac}= | 02:00:00:00:00:04

| ${tap_int1}= | tap_int1
| ${tap_int2}= | tap_int2
| ${mod_tap_name}= | tap_int1MOD

| ${namespace1}= | nmspace1
| ${namespace2}= | nmspace2

| ${tg_ip_address}= | 192.168.0.2
| ${tg_ip_address_SHG}= | 16.0.10.20
| ${tg_ip_address_GW}= | 192.168.0.0

| ${prefix}= | 24

*** Test Cases ***
| TC01: Tap Interface Simple BD
| | [Documentation]
| | ... | (Top) TG-DUT1-TG.
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) On DUT1 configure two
| | ... | L2BD with two if's for each L2BD with MAC learning and one L2BD
| | ... | joining two linux-TAP interfaces created by VPP located in namespace.
| | ... | (Ver) Packet sent from TG is passed through all L2BD and received
| | ... | back on TG. Then src_ip, dst_ip and MAC are checked.
| | ... | (Ref)
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1}
| | ${int2}= | And Add Tap Interface | ${dut_node} | ${tap_int2}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | And Set Interface State | ${dut_node} | ${int2} | up
| | When Create Namespace | ${dut_node} | ${namespace1}
| | And Attach Interface To Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1}
| | And Attach Interface To Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int2}
| | And Set Int State In Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1} | up
| | And Set Int State In Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int2} | up
| | And Bridge domain on DUT node is created | ${dut_node}
| | ... | ${bid_from_TG} | learn=${TRUE}
| | And Bridge domain on DUT node is created | ${dut_node}
| | ... | ${bid_to_TG} | learn=${TRUE}
| | ${interfaces}= | Create List | ${tap_int1} | ${tap_int2}
| | And Create Bridge For Int In Namespace | ${dut_node}
| | ... | ${namespace1} | ${bid_NM} | ${interfaces}
| | And Interface is added to bridge domain | ${dut_node}
| | ... | ${int1} | ${bid_to_TG} | 0
| | And Interface is added to bridge domain | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${bid_to_TG} | 0
| | And Interface is added to bridge domain | ${dut_node}
| | ... | ${int2} | ${bid_from_TG} | 0
| | And Interface is added to bridge domain | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${bid_from_TG} | 0
| | Then Send and receive ICMP Packet | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if2}

| TC02: Tap Interface IP Ping
| | [Documentation]
| | ... | (Top) TG-DUT1-TG.
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) On DUT1 configure two interface addresses with IPv4 of which
| | ... | one is TAP interface ( dut_to_tg_if and TAP ).
| | ... | and one is linux-TAP in namespace.
| | ... | (Ver) Packet sent from TG gets to the destination and ICMP-reply is
| | ... | received on TG.
| | ... | (Ref)
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1} |
| | And Set Interface Address
| | ... | ${dut_node} | ${int1} | ${tap1_VPP_ip} | ${prefix}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | When Create Namespace | ${dut_node} | ${namespace1}
| | And Attach Interface To Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1}
| | And Set Int Mac In Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1} | ${tap1_NM_mac}
| | And Set Int Ip In Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1} | ${tap1_NM_ip} | ${prefix}
| | And Set Int State In Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1} | up
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${tg_ip_address} | ${tg_to_dut_if1_mac}
| | And Add Arp On Dut | ${dut_node} | ${int1}
| | ... | ${tap1_NM_ip} | ${tap1_NM_mac}
| | And Int Add Route In Namespace | ${dut_node} | ${namespace1}
| | ... | ${tg_ip_address_GW} | ${prefix} | ${tap1_VPP_ip}
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap1_NM_ip} | ${tg_ip_address}

| TC03: Tap Interface BD - Different Split Horizon
| | [Documentation]
| | ... | (Top) TG-DUT1-TG.
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) On DUT1
| | ... | configure one if into L2BD with MAC learning. Add two TAP interfaces
| | ... | into this L2BD and assign them different SHG. Setup two namespaces
| | ... | and assign two linux-TAP interfaces to it respectively.
| | ... | (Ver) Packet is sent from TG to both linux-TAP interfaces and reply
| | ... | is checked. Ping from First linux-TAP to another should pass.
| | ... | (Ref)
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1}
| | ${int2}= | And Add Tap Interface | ${dut_node} | ${tap_int2}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | And Set Interface State | ${dut_node} | ${int2} | up
| | When Create Namespace | ${dut_node} | ${namespace1}
| | And Attach Interface To Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1}
| | And Create Namespace | ${dut_node} | ${namespace2}
| | And Attach Interface To Namespace | ${dut_node}
| | ... | ${namespace2} | ${tap_int2}
| | And Set Int State In Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1} | up
| | And Set Int State In Namespace | ${dut_node}
| | ... | ${namespace2} | ${tap_int2} | up
| | And Set Int IP In Namespace | ${dut_node} | ${namespace1} | ${tap_int1}
| | ... | ${tap1_NM_ip} | ${prefix}
| | And Set Int IP In Namespace | ${dut_node} | ${namespace2} | ${tap_int2}
| | ... | ${tap2_NM_SHG} | ${prefix}
| | And Set Int Mac In Namespace | ${dut_node} | ${namespace1}
| | ... | ${tap_int1} | ${tap1_NM_mac}
| | And Set Int Mac In Namespace | ${dut_node} | ${namespace2}
| | ... | ${tap_int2} | ${tap2_NM_mac}
| | And Set Int Arp In Namespace | ${dut_node} | ${namespace1} | ${tap_int1}
| | ... | ${tg_ip_address_SHG} | ${tg_to_dut_if1_mac}
| | And Set Int Arp In Namespace | ${dut_node} | ${namespace2}
| | ... | ${tap_int2} | ${tg_ip_address_SHG} | ${tg_to_dut_if1_mac}
| | And  Bridge domain on DUT node is created | ${dut_node}
| | ... | ${bd_id1} | learn=${TRUE}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${int1}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Interface is added to bridge domain | ${dut_node} | ${int2}
| | ...                                     | ${bd_id1} | ${shg2}
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tap1_NM_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap1_NM_ip} | ${tg_ip_address_SHG}
| | And Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tap2_NM_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap2_NM_SHG} | ${tg_ip_address_SHG}
| | And Ping From Namespace | ${dut_node} | ${namespace2} | ${tap1_NM_ip}
| | And Ping From Namespace | ${dut_node} | ${namespace1} | ${tap2_NM_SHG}

| TC04: Tap Interface BD - Same Split Horizon
| | [Documentation]
| | ... | (Top) TG-DUT1-TG.
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) On DUT1
| | ... | configure one if into L2BD with MAC learning. Add two TAP interfaces
| | ... | into this L2BD and assign them same SHG. Setup two namespaces
| | ... | and assign two linux-TAP interfaces to it respectively.
| | ... | (Ver) Packet is sent from TG to both linux-TAP interfaces and reply
| | ... | is checked. Ping from First linux-TAP to another should fail.
| | ... | (Ref)
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1}
| | ${int2}= | And Add Tap Interface | ${dut_node} | ${tap_int2}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | And Set Interface State | ${dut_node} | ${int2} | up
| | When Create Namespace | ${dut_node} | ${namespace1}
| | And Attach Interface To Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1}
| | And Create Namespace | ${dut_node} | ${namespace2}
| | And Attach Interface To Namespace | ${dut_node}
| | ... | ${namespace2} | ${tap_int2}
| | And Set Int State In Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1} | up
| | And Set Int State In Namespace | ${dut_node}
| | ... | ${namespace2} | ${tap_int2} | up
| | And Set Int IP In Namespace | ${dut_node} | ${namespace1} | ${tap_int1}
| | ... | ${tap1_NM_ip} | ${prefix}
| | And Set Int IP In Namespace | ${dut_node} | ${namespace2} | ${tap_int2}
| | ... | ${tap2_NM_SHG} | ${prefix}
| | And Set Int Mac In Namespace | ${dut_node} | ${namespace1}
| | ... | ${tap_int1} | ${tap1_NM_mac}
| | And Set Int Mac In Namespace | ${dut_node} | ${namespace2}
| | ... | ${tap_int2} | ${tap2_NM_mac}
| | And Set Int Arp In Namespace | ${dut_node} | ${namespace1} | ${tap_int1}
| | ... | ${tg_ip_address_SHG} | ${tg_to_dut_if1_mac}
| | And Set Int Arp In Namespace | ${dut_node} | ${namespace2}
| | ... | ${tap_int2} | ${tg_ip_address_SHG} | ${tg_to_dut_if1_mac}
| | And  Bridge domain on DUT node is created | ${dut_node}
| | ... | ${bd_id1} | learn=${TRUE}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${int1}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Interface is added to bridge domain | ${dut_node} | ${int2}
| | ...                                     | ${bd_id1} | ${shg1}
| | Then Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tap1_NM_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap1_NM_ip} | ${tg_ip_address_SHG}
| | And Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tap2_NM_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap2_NM_SHG} | ${tg_ip_address_SHG}
| | And Run Keyword And Expect Error | Host Unreachable | Ping From Namespace
| | ... | ${dut_node} | ${namespace1} | ${tap2_NM_SHG}
| | And Run Keyword And Expect Error | Host Unreachable | Ping From Namespace
| | ... | ${dut_node} | ${namespace2} | ${tap1_NM_ip}

| TC05: Tap Interface Modify And Delete
| | [Documentation]
| | ... | (Top) TG-DUT1-TG.
| | ... | (Enc) Eth-IPv4-ICMPv4.
| | ... | (Cfg) Set two TAP interfaces.
| | ... | (Ver) Verify that TAP interface can be modified, deleted, and no other
| | ... | TAP interface is affected.
| | ... | (Ref)
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1}
| | ${int2}= | And Add Tap Interface | ${dut_node} | ${tap_int2}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | And Set Interface State | ${dut_node} | ${int2} | up
| | When Modify Tap Interface | ${dut_node} | ${int1} | ${mod_tap_name}
| | Then Check Tap Present | ${dut_node} | ${mod_tap_name}
| | When Delete Tap Interface | ${dut_node} | ${int1}
| | Then Run Keyword And Expect Error
| | ... | Tap interface :${mod_tap_name} does not exist
| | ... | Check Tap Present | ${dut_node} | ${mod_tap_name}
| | And Check Tap Present | ${dut_node} | ${tap_int2}
| | When Delete Tap Interface | ${dut_node} | ${int2}
| | Then Run Keyword And Expect Error
| | ... | ValueError: No JSON object could be decoded
| | ... | Check Tap Present | ${dut_node} | ${tap_int2}


