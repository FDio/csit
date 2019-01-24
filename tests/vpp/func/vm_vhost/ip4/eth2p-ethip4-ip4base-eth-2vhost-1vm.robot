# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.VPPUtil
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.VhostUser
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/vm/qemu.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Force Tags | VM_ENV | HW_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *IPv4 routing test cases with vhost user interface*
| ...
| ... | RFC791 IPv4, RFC826 ARP, RFC792 ICMPv4. Encapsulations: Eth-IPv4-ICMPv4
| ... | on links TG=DUT1. IPv4 routing tests use circular 2-node
| ... | topology TG - DUT1 - TG with two link between the nodes. DUT is
| ... | configured with IPv4 routing and static routes. Test sends packets
| ... | by TG on links to DUT and received on TG link on the other side of
| ... | circular topology. On receive TG verifies packets IPv4 src-addr,
| ... | dst-addr and MAC addresses.

*** Variables ***
| ${net1}= | 10.0.1.0
| ${net3}= | 10.0.3.0
| ${net1_ip1}= | 10.0.1.1
| ${net1_ip2}= | 10.0.1.2
| ${net2_ip1}= | 10.0.2.1
| ${net2_ip2}= | 10.0.2.2
| ${net3_ip1}= | 10.0.3.1
| ${net3_ip2}= | 10.0.3.2
| ${prefix_length}= | 24
| ${fib_table_2}= | 20
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

*** Test Cases ***
| TC01: IPv4 forward via vhost to another VRF
| | [Documentation]
| | ... | Test uses VRF to route IPv4 traffic through 2 vhost user interfaces.
| | ... | Both have IP addresses from same network. On VM is set bridge to pass
| | ... | packet from a one vhost user interface to another one.
| | [Teardown] | Run Keywords
| | ... | Stop and clear QEMU | ${dut_node} | ${vm_node} | AND
| | ... | Tear down functional test
| |
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | ${vhost1}= | And Vpp Create Vhost User Interface | ${dut_node} | ${sock1}
| | ${vhost2}= | And Vpp Create Vhost User Interface | ${dut_node} | ${sock2}
| | And Set Interface State | ${dut_node} | ${vhost1} | up
| | And Set Interface State | ${dut_node} | ${vhost2} | up
| | And Add Fib Table | ${dut_node} | ${fib_table_2}
| | And Assign Interface To Fib Table | ${dut_node}
| | ... | ${vhost2} | ${fib_table_2}
| | And Assign Interface To Fib Table | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${fib_table_2}
| | And Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${net1_ip1} | ${prefix_length}
| | ... | ${dut_node} | ${vhost1} | ${net2_ip1} | ${prefix_length}
| | ... | ${dut_node} | ${vhost2} | ${net2_ip2} | ${prefix_length}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${net3_ip1} | ${prefix_length}
| | ${vhost2_mac}= | And Get Vhost User Mac By SW Index
| | ... | ${dut_node} | ${vhost2}
| | And Vpp Route Add | ${dut_node} | ${net3} | 24 | gateway=${net2_ip2}
| | ... | interface=${vhost1} | resolve_attempts=${NONE} | count=${NONE}
| | And Vpp Route Add | ${dut_node} | ${net1} | 24 | gateway=${net2_ip1}
| | ... | interface=${vhost2} | resolve_attempts=${NONE} | count=${NONE}
| | ... | vrf=${fib_table_2}
| | Add IP Neighbor | ${dut_node} | ${vhost1} | ${net2_ip2} | ${vhost2_mac}
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${net3_ip2}
| | ... | ${tg_to_dut_if2_mac}
| | When Configure VM for vhost L2BD forwarding
| | ... | ${dut_node} | ${sock1} | ${sock2}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${net1_ip2} | ${net3_ip2}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
