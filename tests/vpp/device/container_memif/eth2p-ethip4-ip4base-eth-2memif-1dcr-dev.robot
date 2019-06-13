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
| ...
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/memif.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | IP4FWD | BASE | ETH | MEMIF | DOCKER
| ...
| Test Setup | Set up VPP device test
| ...
| Test Teardown | Run Keywords
| ... | Tear down functional test with container
| ... | AND | Tear down VPP device test
| ... | AND | Show Memif on all DUTs | ${nodes}
| ...
| Documentation | *IPv4 routing test cases with memif interface*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology with \
| ... | single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for IPv4 routing on \
| ... | both links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and \
| ... | two static IPv4 /24 route entries. Container is connected to VPP via \
| ... | Memif interface. Container is running same VPP version as running on \
| ... | DUT.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in \
| ... | one direction by TG on links to DUT1 and via container; on receive TG \
| ... | verifies packets for correctness and their IPv4 src-addr, dst-addr and \
| ... | MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

*** Variables ***
# IP
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
# Memif
| ${sock_base}= | memif-DUT1_CNF
# Container
| ${container_engine}= | Docker
| ${container_chain_topology}= | chain_functional

# TODO: Add update of VPP PIDs after container creation
*** Test Cases ***
| tc01-eth2p-ethip4-ip4base-eth-2memif-1dcr-device
| | [Documentation]
| | ... | [Top] TG=DUT=DCR. [Enc] Eth-IPv4-ICMPv4. [Cfg] Configure two VRFs to \
| | ... | route IPv4 traffic through two memif interfaces. Both interfaces are \
| | ... | configured with IP addresses from the same network. [Ver] Make TG to \
| | ... | send ICMPv4 Echo Reqest form one TG interface to another one to be \
| | ... | switched by DUT1; verify header of received packet.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set up functional test with containers
| | And Configure interfaces in path up
| | When Set up memif interfaces on DUT node
| | ... | ${dut_node} | ${sock_base} | ${sock_base} | dcr_uuid=${dcr_uuid}
| | ... | memif_if1=memif_if1 | memif_if2=memif_if2 | rxq=${0} | txq=${0}
| | And Add Fib Table | ${dut_node} | ${fib_table_2}
| | And Assign Interface To Fib Table
| | ... | ${dut_node} | ${memif_if2} | ${fib_table_2}
| | And Assign Interface To Fib Table
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${fib_table_2}
| | And Configure IP addresses on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${net1_ip1} | ${prefix_length}
| | ... | ${dut_node} | ${memif_if1} | ${net2_ip1} | ${prefix_length}
| | ... | ${dut_node} | ${memif_if2} | ${net2_ip2} | ${prefix_length}
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${net3_ip1} | ${prefix_length}
| | ${memif_if2_key}= | Get interface by sw index | ${nodes['DUT1']}
| | ... | ${memif_if2}
| | ${memif_if2_mac}= | Get interface MAC | ${nodes['DUT1']} | ${memif_if2_key}
| | And Vpp Route Add
| | ... | ${dut_node} | ${net3} | ${prefix_length}
| | ... | gateway=${net2_ip2} | interface=${memif_if1}
| | And Vpp Route Add
| | ... | ${dut_node} | ${net1} | ${prefix_length}
| | ... | gateway=${net2_ip1} | interface=${memif_if2} | vrf=${fib_table_2}
| | VPP Add IP Neighbor
| | ... | ${dut_node} | ${memif_if1} | ${net2_ip2} | ${memif_if2_mac}
| | VPP Add IP Neighbor
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${net3_ip2} | ${tg_to_dut_if2_mac}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${net1_ip2} | ${net3_ip2}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac} | ${dut_to_tg_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac} | ${tg_to_dut_if2_mac}
