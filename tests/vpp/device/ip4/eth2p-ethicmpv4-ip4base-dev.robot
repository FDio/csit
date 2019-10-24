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
| ... | NIC_Virtual | ETH | IP4FWD | BASE | IP4BASE | DRV_VFIO_PCI
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
| ...
| Test Template | Local Template
| ...
| Documentation | *IPv4 routing test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for IPv4 routing on \
| ... | both links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and \
| ... | two static IPv4 /24 route entries.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in \
| ... | one direction by TG on links to DUT1; on receive TG verifies packets \
| ... | for correctness and their IPv4 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send ICMPv4 Echo Req routed over DUT1 interfaces.\
| | ... | Make TG verify ICMPv4 Echo Reply is correct.
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
| | And Initialize IPv4 forwarding in circular topology
| | ... | remote_host1_ip=192.168.0.1 | remote_host2_ip=192.168.0.2
| | Then Send IPv4 ping packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${dut1} | ${dut1_if2}
| | ... | 10.10.10.2 | 20.20.20.1 | ${dut1_if1_mac} | ${0}
| | Then Send IPv4 ping packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${dut1} | ${dut1_if1}
| | ... | 10.10.10.2 | 10.10.10.1 | ${dut1_if1_mac} | ${0}
| | Then Send IPv4 ping packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${tg} | ${tg_if2}
| | ... | 10.10.10.2 | 20.20.20.2 | ${dut1_if1_mac} | ${1}
| | Then Send IPv4 ping packet and verify headers
| | ... | ${tg} | ${tg_if1} | ${tg} | ${tg_if2}
| | ... | 192.168.0.1 | 192.168.0.2 | ${dut1_if1_mac} | ${1}

*** Test Cases ***
| tc01-64B-ethicmpv4-ip4base-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
