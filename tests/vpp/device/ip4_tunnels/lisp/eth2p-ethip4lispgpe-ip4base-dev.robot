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
| ...
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/overlay/lispgpe.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| ...
# Import configuration and test data:
#| Variables | resources/test_data/lisp/ipv4_lispgpe_ipv4/ipv4_lispgpe_ipv4.py
| Variables | resources/test_data/lisp/ipv4_lisp_ipv4/ipv4_lisp_ipv4.py
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | IP4FWD | LISP
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
| ...
| Test Template | Local Template
| ...
| Documentation | *ip4-lispgpe-ip4 encapsulation test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2,\
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4\
| ... | routing and static routes. LISPoIPv4 tunnel is configured between\
| ... | DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in\
| ... | both directions by TG on links to DUT1 and DUT2; on receive\
| ... | TG verifies packets for correctness and their IPv4 src-addr, dst-addr\
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${nic_name}= | virtual
| ${overhead}= | ${54}
| ${tg_if1_ip4}= | 6.0.0.2
| ${tg_if2_ip4}= | 6.0.1.2
| ${dut_if1_ip4}= | 6.0.0.1
| ${dut_if2_ip4}= | 6.0.1.1
| ${ip4_plen}= | ${24}
| ${src_ip4}= | 6.0.0.2
| ${dst_ip4}= | 6.0.2.2
| ${src_rloc4}= | ${dut_if2_ip4}
| ${dst_rloc4}= | ${tg_if2_ip4}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] On DUT1 configure LISP\
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
| | And Configure LISP GPE topology in 2-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid}
| | ... | ${dut1_to_tg_ip4_static_adjacency}
#| | Then Send packet and verify headers
| | Then Send packet and verify LISP encap
| | ... | ${tg} | ${tg1_ip4} | ${dst_ip4}
| | ... | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
| | ... | ${src_rloc4} | ${dst_rloc4}

*** Test Cases ***
| tc01-110B-ethip4lispgpe-ip4base-dev
| | [Tags] | 110B
| | frame_size=${110} | phy_cores=${0}
