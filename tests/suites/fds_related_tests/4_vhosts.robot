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
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
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

| ${VNI_BLUE}= | 23
| ${BID_BLUE}= | 23
| ${VNI_RED}= | 24
| ${BID_RED}= | 24

| ${DUT1_IF_IP}= | 16.0.0.1
| ${DUT2_IF_IP}= | 16.0.0.2

| ${BLUE_IP}= | 16.0.0.3
| ${RED_IP}= | 16.0.0.4

*** Test Cases ***
| L2 test cases with tenant networks (VXLAN)
| | [Documentation] | Ping among all ports inside the same network should pass.
| | ...             | interfaces and check packet forwarding through VM via two
| | ...             | L2 bridge domains with learning enabled.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 3-node testing is set | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${DUT1_IF_IP} | 24
| | Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${DUT2_IF_IP} | 24
| | Setup QEMU
| | Start QEMU on Dut | ${dut1_node} | ${BLUE_IP} | vm_dut1
| | Setup Vxlan and BD on Dut | ${dut1_node} | ${DUT1_IF_IP} | ${DUT2_IF_IP}
| | Start QEMU on Dut | ${dut2_node} | ${RED_IP} | vm_dut2
| | Setup Vxlan and BD on Dut | ${dut2_node} | ${DUT2_IF_IP} | ${DUT1_IF_IP}
| | Make Ping From To | ${vm_dut1} | 16.0.0.4
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Stop and Clear QEMU | ${dut1_node} | ${vm_dut1}
| | ...        | AND          | Stop and Clear QEMU | ${dut2_node} | ${vm_dut2}
*** Keywords ***
| Setup QEMU
| | When VPP 4 Vhosts are created | ${dut1_node}
| | ...                           | ${sock1}
| | ...                           | ${sock2}
| | ...                           | ${sock3}
| | ...                           | ${sock4}
| | When VPP 4 Vhosts are created | ${dut2_node}
| | ...                           | ${sock1}
| | ...                           | ${sock2}
| | ...                           | ${sock3}
| | ...                           | ${sock4}
| | Setup QEMU Vhost | ${sock1}
| | ...              | ${sock2}
| | ...              | ${sock3}
| | ...              | ${sock4}

| Setup Vxlan and BD on Dut
| | [Arguments] | ${dut} | ${src_ip} | ${dst_ip}
| | Bridge domain on DUT node is created | ${dut} | ${BID_BLUE} | learn=${TRUE}
| | Bridge domain on DUT node is created | ${dut} | ${BID_RED} | learn=${TRUE}
| | ${vlan1_if} | Create VXLAN interface     | ${dut} | ${VNI_BLUE}
| |                 | ...  | ${src_ip} | ${dst_ip}
| | ${vlan2_if} | Create VXLAN interface     | ${dut} | ${VNI_RED}
| |                 | ...  | ${src_ip} | ${dst_ip}
| | Interface is added to bridge domain | ${dut} | ${vlan1_if} | ${BID_BLUE} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if1} | ${BID_BLUE} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if2} | ${BID_BLUE} | 0
| | Interface is added to bridge domain | ${dut} | ${vlan2_if} | ${BID_RED} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if3} | ${BID_RED} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if4} | ${BID_RED} | 0
