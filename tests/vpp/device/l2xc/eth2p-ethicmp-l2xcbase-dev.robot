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
| ... | NIC_Virtual | ETH | L2XCFWD | BASE | ICMP
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
| ...
| Documentation | *L2 cross-connect test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of \
| ... | IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all \
| ... | links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with L2 cross-connect \
| ... | switching.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets \
| ... | are sent in both directions by TG on links to DUT1; on receive TG \
| ... | verifies packets for correctness and their IPv4 (IPv6) src-addr, \
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC792

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${nic_name}= | virtual
| ${overhead}= | ${0}

*** Test Cases ***
| tc01-eth2p-ethicmpv4-l2xcbase-dev
| | [Documentation]
| | ... | [Ver] Make TG send ICMPv4 Echo Reqs in both directions between two\
| | ... | of its interfaces to be switched by DUT to and from docker; verify\
| | ... | all packets are received.
| | ...
| | Set Test Variable | ${frame_size} | ${42}
| | Set Test Variable | ${rxq_count_int} | ${1}
| | ...
| | Given Add PCI devices to all DUTs
| | And Set Max Rate And Jumbo And Handle Multi Seg
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Initialize L2 xconnect in 2-node circular topology
| | Then Send ICMPv4 bidirectionally and verify received packets
| | ... | ${tg} | ${tg_if1} | ${tg_if2}

| tc02-eth2p-ethicmpv6-l2xcbase-dev
| | [Documentation]
| | ... | [Ver] Make TG send ICMPv6 Echo Reqs in both directions between two\
| | ... | of its interfaces to be switched by DUT to and from docker; verify\
| | ... | all packets are received.
| | ...
| | Set Test Variable | ${frame_size} | ${62}
| | Set Test Variable | ${rxq_count_int} | ${1}
| | ...
| | Given Add PCI devices to all DUTs
| | And Set Max Rate And Jumbo And Handle Multi Seg
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Initialize L2 xconnect in 2-node circular topology
| | Then Send ICMPv6 bidirectionally and verify received packets
| | ... | ${tg} | ${tg_if1} | ${tg_if2}
