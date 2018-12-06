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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.VPPUtil
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/vm/qemu.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | IP4FWD | BASE | ETH | VHOST | 1VM
| ...
| Test Setup | Set up VPP device test
| ...
| Test Teardown | Run Keywords
| ... | Stop and clear QEMU | ${dut_node} | ${vm_node}
| ... | AND | Tear down VPP device test
| ...
| Documentation | *IPv4 routing test cases with vhost user interface*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology with \
| ... | VM and single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for IPv4 routing on \
| ... | both links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and \
| ... | two static IPv4 /24 route entries. Qemu Guest is connected to VPP via \
| ... | vhost-user interfaces. Guest is configured with linux bridge \
| ... | interconnecting vhost-user interfaces.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in \
| ... | one direction by TG on links to DUT1; on receive TG verifies packets \
| ... | for correctness and their IPv4 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

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
| tc01-eth2p-ethip4-ip4base-eth-2vhost-1vm-device
| | [Documentation]
| | ... | Test uses two VRFs to route IPv4 traffic through two vhost-user \
| | ... | interfaces. Both interfaces are configured with IP addresses from \
| | ... | the same network. There is created linux bridge on VM to pass packet \
| | ... | from one vhost-user interface to another one.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Configure interfaces in path up
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
| | And Vpp Route Add | ${dut_node} | ${net3} | ${prefix_length} | ${net2_ip2}
| | ... | ${vhost1} | resolve_attempts=${NONE} | count=${NONE}
| | And Vpp Route Add | ${dut_node} | ${net1} | ${prefix_length} | ${net2_ip1}
| | ... | ${vhost2} | resolve_attempts=${NONE} | count=${NONE}
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
