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
| ... | NIC_Virtual | ETH | IP4FWD | FEATURE | COPWHLIST
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
| ...
| Test Template | Local Template
| ...
| Documentation | *COP Security IPv4 whitelist test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 on all links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and
| ... | static routes. COP security white-lists are applied on DUT1 ingress
| ... | interface from TG.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in
| ... | one direction by TG on link to DUT1; on receive TG verifies packets for
| ... | correctness and drops as applicable.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${nic_name}= | virtual
| ${overhead}= | ${0}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send ICMPv4 Echo Req on its interface to DUT1; \
| | ... | verify received ICMPv4 Echo Req pkts are correct.
| | ...
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| | ...
| | Set Test Variable | \${frame_size}
| | ...
| | Given Add worker threads and rxqueues to all DUTs | ${phy_cores} | ${rxq}
| | And Add PCI devices to all DUTs
| | And Set Max Rate And Jumbo And Handle Multi Seg
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize IPv4 forwarding in circular topology
| | And COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip4 | 1
| | And COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | Then Send IPv4 ping packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${tg} | ${tg_if2}
| | ... | 10.10.10.2 | 20.20.20.2 | ${dut1_if1_mac} | ${1}

*** Test Cases ***
| tc01-64B-ethicmpv4-ip4base-copwhtlistbase-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
