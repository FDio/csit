# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | L2BDFWD | BASE | ETH | ICMP
| ...
| Test Setup | Set up VPP device test
| ...
| Test Teardown | Tear down VPP device test
| ...
| Documentation | *L2 bridge-domain test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of\
| ... | IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all\
| ... | links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with L2 bridge-domain\
| ... | switching.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets\
| ... | are sent in both directions by TG on links to DUT1; on receive TG\
| ... | verifies packets for correctness and their IPv4 (IPv6) src-addr,\
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC792

*** Variables ***
| ${bd_id}= | 1

*** Test Cases ***
| tc01-eth2p-ethicmpv4-l2bdbase-device
| | [Documentation]
| | ... | [Top] TG-DUT1-TG. [Enc] Eth-IPv4-ICMPv4.
| | ... | [Cfg] Configure L2 bridge-domain (L2BD) with MAC learning enabled on\
| | ... | DUT1. Add both interfaces towards TG to this L2BD.
| | ... | [Ver] Make TG send ICMPv4 Echo Req in both directions between two of\
| | ... | its interfaces to be switched by DUT1; verify all packets are
| | ... | received.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in path up
| | And Create bridge domain | ${dut_node} | ${bd_id}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${bd_id}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${bd_id}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if2}

| tc02-eth2p-ethicmpv6-l2bdbase-device
| | [Documentation]
| | ... | [Top] TG-DUT1-TG. [Enc] Eth-IPv6-ICMPv6.
| | ... | [Cfg] Configure L2 bridge-domain (L2BD) with MAC learning enabled on\
| | ... | DUT1. Add both interfaces towards TG to this L2BD.
| | ... | [Ver] Make TG send ICMPv6 Echo Req in both directions between two of\
| | ... | its interfaces to be switched by DUT1; verify all packets are
| | ... | received.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in path up
| | And Create bridge domain | ${dut_node} | ${bd_id}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${bd_id}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${bd_id}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send ICMPv6 bidirectionally and verify received packets
| | ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
