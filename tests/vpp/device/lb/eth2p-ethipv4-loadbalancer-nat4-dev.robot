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
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | ETH | IP4 | LOADBALANCER_NAT4 | DRV_VFIO_PCI
|
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local Template
|
| Documentation | *loadbalancer nat4 test cases*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP for LoadBalancer maglev \
| ... | *[Cfg] DUT configuration:* DUT1 is configured with LoadBalancer\
| ... | nat4 and one static IPv4 /24 route entries. DUT1 tested with\
| ... | ${nic_name}.
| ... | *[Ver] TG verification:* Test Eth-IPv4-UDP packet with IP \
| ... | protocol=17 is sent \
| ... | in one direction by TG on links to DUT1; on receive TG verifies packet \
| ... | for correctness of UDP or TCP header.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | lb_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}
| ${osi_layer}= | L3
| ${p1_src_port}= | 63
| ${p1_dst_port}= | 20000
| ${p2_src_port}= | 3307
| ${p2_dst_port}= | 63

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send Eth-IPv4-UDP packet routed over DUT1 interfaces.\
| | ... | Make TG verify Eth-IPv4-UDP packet is correct.
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| |
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| |
| | Set Test Variable | \${frame_size}
| |
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize loadbalancer nat4
| | Then Send TCP or UDP packet and verify received packet | ${tg}
| | ... | 192.168.50.74 | 90.1.2.1
| | ... | ${tg_if1} | ${tg_if1_mac}
| | ... | ${tg_if2} | ${dut1_if1_mac}
| | ... | UDP | ${p1_src_port} | ${p1_dst_port}
| | Then Send TCP or UDP packet and verify received packet | ${tg}
| | ... | 192.168.60.74 | 192.168.50.74
| | ... | ${tg_if2} | ${tg_if2_mac}
| | ... | ${tg_if1} | ${dut1_if2_mac}
| | ... | UDP | ${p2_src_port} | ${p2_dst_port}

*** Test Cases ***
| tc01-64B-ethipv4-loadbalancer-nat4-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
