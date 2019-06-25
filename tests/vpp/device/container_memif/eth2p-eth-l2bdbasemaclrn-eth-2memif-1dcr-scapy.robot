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
| Resource | resources/libraries/robot/shared/default.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | ETH | L2BDMACLRN | BASE | MEMIF | DOCKER
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | container
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
| @{plugins_to_enable}= | dpdk_plugin.so | memif_plugin.so
| ${nic_name}= | virtual
| ${overhead}= | ${0}
| ${rxq_count_int}= | 1
# Container
| ${container_engine}= | Docker
| ${container_chain_topology}= | chain_functional

*** Test Cases ***
| tc01-eth2p-ethip4-l2bdbase-eth-2memif-1dcr-device
| | [Documentation]
| | ... | [Cfg] Configure two L2 bridge-domains (L2BD) with MAC learning\
| | ... | enabled on DUT1, each with one untagged interface to TG and untagged\
| | ... | interface to docker over memif
| | ...
| | Set Test Variable | ${frame_size} | ${64}
| | ...
| | Given Add PCI devices to all DUTs
| | And Set Max Rate And Jumbo And Handle Multi Seg
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Start containers for device test
| | And Initialize L2 Bridge Domain with memif pairs
| | Then Send ICMPv4 bidirectionally and verify received packets
| | ... | ${tg} | ${tg_if1} | ${tg_if2}

| tc02-eth2p-ethip6-l2bdbase-eth-2memif-1dcr-device
| | [Documentation]
| | ... | [Cfg] Configure two L2 bridge-domains (L2BD) with MAC learning\
| | ... | enabled on DUT1, each with one untagged interface to TG and untagged\
| | ... | interface to docker over memif
| | ...
| | Set Test Variable | ${frame_size} | ${78}
| | ...
| | Given Add PCI devices to all DUTs
| | And Set Max Rate And Jumbo And Handle Multi Seg
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Start containers for device test
| | And Initialize L2 Bridge Domain with memif pairs
| | Then Send ICMPv6 bidirectionally and verify received packets
| | ... | ${tg} | ${tg_if1} | ${tg_if2}
