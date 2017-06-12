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
| ...
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| ...
| Test Setup | Set up TAP functional test
| ...
| Test Teardown | Tear down TAP functional test
| ...
| Documentation | *Tap Interface Traffic Tests*
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG)
| ... | are set depending on test case; Namespaces (NM)
| ... | are set on DUT1 with attached linux-TAP.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets
| ... | are sent by TG on link to DUT1; On receipt TG verifies packets
| ... | for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${tap1_NM_ip}= | 16.0.10.2
| ${tap2_NM_SHG}= | 16.0.10.3

| ${bd_id1}= | 21
| ${shg1}= | 2
| ${shg2}= | 3

| ${tap1_NM_mac}= | 02:00:00:00:00:02
| ${tap2_NM_mac}= | 02:00:00:00:00:04

| ${tap_int1}= | tap_int1
| ${tap_int2}= | tap_int2

| ${namespace1}= | nmspace1
| ${namespace2}= | nmspace2

| ${tg_ip_address_SHG}= | 16.0.10.20
| ${prefix}= | 24

*** Test Cases ***
| TC01: Tap Interface BD - Different Split Horizon
| | [Documentation]
| | ... | [Top] TG-DUT1-TG.
| | ... | [Enc] Eth-IPv4-ICMPv4.
| | ... | [Cfg] On DUT1 configure one if into L2BD with MAC learning. Add two\
| | ... | TAP interfaces into this L2BD and assign them different SHG. Setup\
| | ... | two namespaces and assign two linux-TAP interfaces to it respectively.
| | ... | [Ver] Packet is sent from TG to both linux-TAP interfaces and reply\
| | ... | is checked. Ping from First linux-TAP to another should pass.
| | ...
| | Given Configure path in 2-node circular topology | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
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
| | And Set Linux Interface IP | ${dut_node} | ${tap_int1}
| | ... | ${tap1_NM_ip} | ${prefix} | ${namespace1}
| | And Set Linux Interface IP | ${dut_node} | ${tap_int2}
| | ... | ${tap2_NM_SHG} | ${prefix} | ${namespace2}
| | And Set Linux Interface MAC | ${dut_node}
| | ... | ${tap_int1} | ${tap1_NM_mac} | ${namespace1}
| | And Set Linux Interface MAC | ${dut_node}
| | ... | ${tap_int2} | ${tap2_NM_mac} | ${namespace2}
| | And Set Linux Interface ARP | ${dut_node} | ${tap_int1}
| | ... | ${tg_ip_address_SHG} | ${tg_to_dut_if1_mac} | ${namespace1}
| | And Set Linux Interface ARP | ${dut_node} | ${tap_int2}
| | ... | ${tg_ip_address_SHG} | ${tg_to_dut_if1_mac} | ${namespace2}
| | And Create bridge domain | ${dut_node}
| | ... | ${bd_id1} | learn=${TRUE}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${int1}
| | ... | ${bd_id1} | ${shg1}
| | And Add interface to bridge domain | ${dut_node} | ${int2}
| | ... | ${bd_id1} | ${shg2}
| | Then Send ICMP echo request and verify answer | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tap1_NM_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap1_NM_ip} | ${tg_ip_address_SHG}
| | And Send ICMP echo request and verify answer | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tap2_NM_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap2_NM_SHG} | ${tg_ip_address_SHG}
| | And Send Ping From Node To Dst | ${dut_node} | ${tap1_NM_ip}
| | ... | namespace=${namespace2}
| | And Send Ping From Node To Dst | ${dut_node} | ${tap2_NM_SHG}
| | ... | namespace=${namespace1}

| TC02: Tap Interface BD - Same Split Horizon
| | [Documentation]
| | ... | [Top] TG-DUT1-TG.
| | ... | [Enc] Eth-IPv4-ICMPv4.
| | ... | [Cfg] On DUT1 configure one if into L2BD with MAC learning. Add two\
| | ... | TAP interfaces into this L2BD and assign them same SHG. Setup two\
| | ... | namespaces and assign two linux-TAP interfaces to it respectively.
| | ... | [Ver] Packet is sent from TG to both linux-TAP interfaces and reply\
| | ... | is checked. Ping from First linux-TAP to another should fail.
| | ...
| | Given Configure path in 2-node circular topology | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
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
| | And Set Linux Interface IP | ${dut_node} | ${tap_int1}
| | ... | ${tap1_NM_ip} | ${prefix} | ${namespace1}
| | And Set Linux Interface IP | ${dut_node} | ${tap_int2}
| | ... | ${tap2_NM_SHG} | ${prefix} | ${namespace2}
| | And Set Linux Interface MAC | ${dut_node}
| | ... | ${tap_int1} | ${tap1_NM_mac} | ${namespace1}
| | And Set Linux Interface MAC | ${dut_node}
| | ... | ${tap_int2} | ${tap2_NM_mac} | ${namespace2}
| | And Set Linux Interface ARP | ${dut_node} | ${tap_int1}
| | ... | ${tg_ip_address_SHG} | ${tg_to_dut_if1_mac} | ${namespace1}
| | And Set Linux Interface ARP | ${dut_node} | ${tap_int2}
| | ... | ${tg_ip_address_SHG} | ${tg_to_dut_if1_mac} | ${namespace2}
| | And Create bridge domain | ${dut_node}
| | ... | ${bd_id1} | learn=${TRUE}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${int1}
| | ... | ${bd_id1} | ${shg1}
| | And Add interface to bridge domain | ${dut_node} | ${int2}
| | ... | ${bd_id1} | ${shg1}
| | Then Send ICMP echo request and verify answer | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tap1_NM_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap1_NM_ip} | ${tg_ip_address_SHG}
| | And Send ICMP echo request and verify answer | ${tg_node} | ${tg_to_dut_if1}
| | ... | ${tap2_NM_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap2_NM_SHG} | ${tg_ip_address_SHG}
| | And Run Keyword And Expect Error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${dut_node} | ${tap2_NM_SHG}
| | ... | namespace=${namespace1}
| | And Run Keyword And Expect Error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${dut_node} | ${tap1_NM_ip}
| | ... | namespace=${namespace2}
