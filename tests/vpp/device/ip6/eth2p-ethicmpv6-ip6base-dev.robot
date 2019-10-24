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
| ... | NIC_Virtual | ETH | IP6FWD | BASE | IP6BASE | DRV_VFIO_PCI
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
| ...
| Test Template | Local Template
| ...
| Documentation | *IPv6 routing test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv6-ICMPv6 for IPv6 routing on \
| ... | both links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv6 routing and \
| ... | two static IPv6 /64 route entries.
| ... | *[Ver] TG verification:* Test ICMPv6 Echo Request packets are sent in \
| ... | one direction by TG on links to DUT1; on receive TG verifies packets \
| ... | for correctness and their IPv6 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC2460, RFC4443, RFC4861

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send ICMPv6 Echo Req routed over DUT1 interfaces;\
| | ... | Make TG verify ICMPv6 Echo Reply is correct.
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
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize IPv6 forwarding in circular topology
| | ... | remote_host1_ip=3ffe:5f::1 | remote_host2_ip=3ffe:5f::2
| | Then Send IPv6 echo request packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${dut1} | ${dut1_if2}
| | ... | 2001:1::2 | 2001:2::1 | ${dut1_if1_mac} | ${0}
| | Then Send IPv6 echo request packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${dut1} | ${dut1_if1}
| | ... | 2001:1::2 | 2001:1::1 | ${dut1_if1_mac} | ${0}
| | Then Send IPv6 echo request packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${tg} | ${tg_if2}
| | ... | 2001:1::2 | 2001:2::2 | ${dut1_if1_mac} | ${1} | ${dut1_if2_mac}
| | Then Send IPv6 echo request packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${tg} | ${tg_if2}
| | ... | 3ffe:5f::1 | 3ffe:5f::2 | ${dut1_if1_mac} | ${1} | ${dut1_if2_mac}

*** Test Cases ***
| tc01-78B-ethicmpv6-ip6base-dev
| | [Tags] | 78B
| | frame_size=${78} | phy_cores=${0}
