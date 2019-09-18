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
# Import configuration and test data:
| Variables | resources/test_data/lisp/lisp.py
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | IP4FWD | LISP_IP4o4
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
| ...
| Test Template | Local Template
| ...
| Documentation | *ip4-lisp-ip4 encapsulation test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node\
| ... | circular topology with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv4-ICMPv4\
| ... | on DUT1-TG, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing\
| ... | over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT is configured with IPv4\
| ... | routing and static routes. LISPoIPv4 tunnel is\
| ... | configured between DUT1 and TG2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets\
| ... | are sent by TG on if1 link to DUT1; on receive TG verifies\
| ... | packets for correctness and their IPv4 src-addr, dst-addr\
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${nic_name}= | virtual
| ${overhead}= | ${54}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure LISP.\
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
| | When Configure topology for IPv4 LISP testing
| | And Configure LISP in 2-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid}
| | ... | ${dut1_to_tg_ip4_static_adjacency}
| | Then Send packet and verify LISP encap
| | ... | ${tg} | ${tg_if1_ip4} | ${dst_ip4}
| | ... | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
| | ... | ${src_rloc4} | ${dst_rloc4}

*** Test Cases ***
| tc01-46B-ethip4lisp-ip4base-dev
| | [Tags] | 46B
| | frame_size=${46} | phy_cores=${0}
