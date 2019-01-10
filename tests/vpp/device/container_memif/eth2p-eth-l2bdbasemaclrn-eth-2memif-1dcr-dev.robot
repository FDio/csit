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
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/memif.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | L2BDMACLRN | BASE | ETH | MEMIF | DOCKER
| ...
| Test Setup | Set up VPP device test
| ...
| Test Teardown | Run Keywords
| ... | Tear down functional test with container
| ... | AND | Tear down VPP device test
| ... | AND | Show Memif on all DUTs | ${nodes}
| ...
| Documentation | *L2 bridge-domain test cases with memif interface*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of \
| ... | IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all \
| ... | links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with L2 bridge-domain \
| ... | switching. Container is connected to VPP via Memif interface. \
| ... | Container is running same VPP version as running on DUT.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets \
| ... | are sent in both directions by TG on links to DUT1 and via container; \
| ... | on receive TG verifies packets for correctness and their IPv4 (IPv6) \
| ... | src-addr, dst-addr and MAC addresses.pecifications:* RFC792

*** Variables ***
# L2BD
| ${bd_id1}= | 1
| ${bd_id2}= | 2
# Memif
| ${sock_base}= | memif-DUT1_CNF1
# Container
| ${container_engine}= | Docker
| ${container_chain_topology}= | chain_functional

# TODO: Add update of VPP PIDs after container creation
*** Test Cases ***
| tc01-eth2p-ethip4-l2bdbase-eth-2memif-1dcr-device
| | [Documentation]
| | ... | [Top] TG=DUT=DCR. [Enc] Eth-IPv4-ICMPv4. [Cfg] Configure two \
| | ... | L2 bridge-domains (L2BD) with MAC learning enabled on DUT1, each \
| | ... | with one untagged interface to TG and untagged i/f to docker over \
| | ... | memif. [Ver] Make TG send ICMPv4 Echo Req in both directions between \
| | ... | two of its interfaces to be switched by DUT1; verify all packets are \
| | ... | received.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set up functional test with containers
| | And Configure interfaces in path up
| | When Set up memif interfaces on DUT node | ${dut_node} | ${sock_base}
| | ... | ${sock_base} | dcr_uuid=${dcr_uuid}
| | ... | memif_if1=memif_if1 | memif_if2=memif_if2 | rxq=${0} | txq=${0}
| | And Create bridge domain | ${dut_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${memif_if1}
| | ... | ${bd_id1}
| | And Create bridge domain | ${dut_node} | ${bd_id2}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${bd_id2}
| | And Add interface to bridge domain | ${dut_node} | ${memif_if2}
| | ... | ${bd_id2}
| | Then Send ICMPv4 bidirectionally and verify received packets | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if2}

| tc02-eth2p-ethip6-l2bdbase-eth-2memif-1dcr-device
| | [Documentation]
| | ... | [Top] TG=DUT=DCR. [Enc] Eth-IPv6-ICMPv6. [Cfg] Configure two \
| | ... | L2 bridge-domains (L2BD) with MAC learning enabled on DUT1, each \
| | ... | with one untagged interface to TG and untagged i/f to docker over \
| | ... | memif. [Ver] Make TG send ICMPv4 Echo Req in both directions between \
| | ... | two of its interfaces to be switched by DUT1; verify all packets are \
| | ... | received.
| | ...
| | Given Configure path in 2-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set up functional test with containers
| | And Configure interfaces in path up
| | When Set up memif interfaces on DUT node | ${dut_node} | ${sock_base}
| | ... | ${sock_base} | dcr_uuid=${dcr_uuid}
| | ... | memif_if1=memif_if1 | memif_if2=memif_if2 | rxq=${0} | txq=${0}
| | And Create bridge domain | ${dut_node} | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${bd_id1}
| | And Add interface to bridge domain | ${dut_node} | ${memif_if1}
| | ... | ${bd_id1}
| | And Create bridge domain | ${dut_node} | ${bd_id2}
| | And Add interface to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ... | ${bd_id2}
| | And Add interface to bridge domain | ${dut_node} | ${memif_if2}
| | ... | ${bd_id2}
| | Then Send ICMPv6 bidirectionally and verify received packets
| | ... | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}
