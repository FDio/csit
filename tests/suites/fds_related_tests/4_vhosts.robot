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
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/double_qemu_setup.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND | Qemu Teardown | ${dut1_node} | ${qemu_node1} | qemu_node1
| ...           | AND | Qemu Teardown | ${dut2_node} | ${qemu_node2} | qemu_node2
| Documentation | *Bridge domain test suite.*
| ...
| ... | Test suite uses 2-node topology TG - DUT1 - TG with two links
| ... | between nodes as well as 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes. Test packets are sent in both directions
| ... | and contain Ethernet header, IPv4 header and ICMP message. Ethernet
| ... | header MAC addresses are matching MAC addresses of the TG node.

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2
| ${shg1}= | 3
| ${shg2}= | 4
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2
| ${sock3}= | /tmp/sock3
| ${sock4}= | /tmp/sock4

| ${vni_blue}= | 23
| ${vni_red}= | 24

| ${bid_b}= | 23
| ${bid_r}= | 24

| ${vlan_red}= | 50
| ${vlan_blue}= | 60

| ${dut1_if_ip}= | 16.0.0.1
| ${dut2_if_ip}= | 16.0.0.2

| ${dut1_blue1}= | 16.0.10.1
| ${dut1_blue2}= | 16.0.10.2
| ${dut1_red1}= | 16.0.10.3
| ${dut1_red2}= | 16.0.10.4

| ${dut2_blue1}= | 16.0.20.1
| ${dut2_blue2}= | 16.0.20.2
| ${dut2_red1}= | 16.0.20.3
| ${dut2_red2}= | 16.0.20.4

| ${prefix_length}= | 16


*** Test Cases ***
| L2 test cases with tenant networks (VXLAN)
| | [Documentation] | Ping among all ports inside the same network should pass.
| | ...             | a) test l2 connectivity inside every network
| | ...             | b) test l2 connectivity between networks
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set Interface Address
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_if_ip} | 16
| | And Set Interface Address
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_if_ip} | 16
| | And Set Interface State | ${dut1_node} | ${dut1_to_dut2} | up
| | And Set Interface State | ${dut2_node} | ${dut2_to_dut1} | up
| | When VPP 4 Vhosts are created | ${dut1_node}
| | ...                           | ${sock1}
| | ...                           | ${sock2}
| | ...                           | ${sock3}
| | ...                           | ${sock4}
| | And VPP 4 Vhosts are created | ${dut2_node}
| | ...                           | ${sock1}
| | ...                           | ${sock2}
| | ...                           | ${sock3}
| | ...                           | ${sock4}
| | And Setup QEMU Vhost and Run | ${dut1_node}
| | ...                   | ${sock1}
| | ...                   | ${sock2}
| | ...                   | ${sock3}
| | ...                   | ${sock4}
| | ...                   | ${dut1_blue1}
| | ...                   | ${dut1_blue2}
| | ...                   | ${dut1_red1}
| | ...                   | ${dut1_red2}
| | ...                   | ${prefix_length}
| | ...                   | qemu_node1
| | ...                   | 04
| | And Setup QEMU Vhost and Run | ${dut2_node}
| | ...                   | ${sock1}
| | ...                   | ${sock2}
| | ...                   | ${sock3}
| | ...                   | ${sock4}
| | ...                   | ${dut2_blue1}
| | ...                   | ${dut2_blue2}
| | ...                   | ${dut2_red1}
| | ...                   | ${dut2_red2}
| | ...                   | ${prefix_length}
| | ...                   | qemu_node2
| | ...                   | 06
| | And Setup Vxlan and BD on Dut | ${dut1_node} | ${dut1_if_ip} | ${dut2_if_ip}
| | And Setup Vxlan and BD on Dut | ${dut2_node} | ${dut2_if_ip} | ${dut1_if_ip}
| | And Sleep | 10
| | Then Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.2 | nmspace1
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.1 | nmspace1
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.2 | nmspace1
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.1 | nmspace2
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.2 | nmspace2
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.4 | nmspace3
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.3 | nmspace3
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.4 | nmspace3
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.3 | nmspace4
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.4 | nmspace4
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.3 | nmspace1
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.4 | nmspace1
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.3 | nmspace1
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.4 | nmspace1
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.3 | nmspace2
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.4 | nmspace2
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.3 | nmspace2
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.4 | nmspace2
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.1 | nmspace3
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.2 | nmspace3
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.1 | nmspace4
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.2 | nmspace4

| Provider network test cases with provider physical networks (VLAN)
| | [Documentation] | Ping among all ports inside the same network should pass.
| | ...             | a) test l2 connectivity inside every network
| | ...             | b) test l2 connectivity between networks
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 3-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${dut1_if_ip} | 16
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${dut2_if_ip} | 16
| | And Set Interface State | ${dut1_node} | ${dut1_to_dut2} | up
| | And Set Interface State | ${dut2_node} | ${dut2_to_dut1} | up
| | When VPP 4 Vhosts are created | ${dut1_node}
| | ...                           | ${sock1}
| | ...                           | ${sock2}
| | ...                           | ${sock3}
| | ...                           | ${sock4}
| | And VPP 4 Vhosts are created | ${dut2_node}
| | ...                           | ${sock1}
| | ...                           | ${sock2}
| | ...                           | ${sock3}
| | ...                           | ${sock4}
| | And Setup QEMU Vhost and Run | ${dut1_node}
| | ...                   | ${sock1}
| | ...                   | ${sock2}
| | ...                   | ${sock3}
| | ...                   | ${sock4}
| | ...                   | ${dut1_blue1}
| | ...                   | ${dut1_blue2}
| | ...                   | ${dut1_red1}
| | ...                   | ${dut1_red2}
| | ...                   | ${prefix_length}
| | ...                   | qemu_node1
| | ...                   | 04
| | And Setup QEMU Vhost and Run | ${dut2_node}
| | ...                   | ${sock1}
| | ...                   | ${sock2}
| | ...                   | ${sock3}
| | ...                   | ${sock4}
| | ...                   | ${dut2_blue1}
| | ...                   | ${dut2_blue2}
| | ...                   | ${dut2_red1}
| | ...                   | ${dut2_red2}
| | ...                   | ${prefix_length}
| | ...                   | qemu_node2
| | ...                   | 06
| | And Setup Vlan and BD on Dut
| | ... | ${dut1_node} | ${dut1_if_ip} | ${dut2_if_ip} | ${dut1_to_dut2}
| | And Setup Vlan and BD on Dut
| | ... | ${dut2_node} | ${dut2_if_ip} | ${dut1_if_ip} | ${dut2_to_dut1}
| | And Sleep | 10
| | Then Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.2 | nmspace1
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.1 | nmspace1
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.2 | nmspace1
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.1 | nmspace2
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.2 | nmspace2
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.4 | nmspace3
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.3 | nmspace3
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.4 | nmspace3
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.3 | nmspace4
| | And Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.4 | nmspace4
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.3 | nmspace1
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.4 | nmspace1
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.3 | nmspace1
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.4 | nmspace1
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.3 | nmspace2
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.10.4 | nmspace2
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.3 | nmspace2
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.4 | nmspace2
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.1 | nmspace3
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.2 | nmspace3
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.1 | nmspace4
| | And Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | 16.0.20.2 | nmspace4




