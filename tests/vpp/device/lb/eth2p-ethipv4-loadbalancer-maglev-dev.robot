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
| ... | NIC_Virtual | ETH | IP4 | LOADBALANCER_MAGLEV | DRV_VFIO_PCI
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
| ...
| Test Template | Local Template
| ...
| Documentation | *loadbalancer maglev test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-UDP for LoadBalancer maglev \
| ... | *[Cfg] DUT configuration:* DUT1 is configured with LoadBalancer\
| ... | maglev and one static IPv4 /24 route entries. DUT1 tested with\
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
| ${src_port}= | 63 
| ${dst_port}= | 20000

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send Eth-IPv4-UPD packet routed over DUT1 interfaces.\
| | ... | Make TG verify Eth-IPv4-UDP packet is correct.
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
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Initialize loadbalancer maglev
| | Then Send TCP or UDP packet and verify received packet | ${tg}
| | ... | 192.168.50.74 | 90.1.2.1 
| | ... | ${tg_if1} | ${tg_if1_mac}
| | ... | ${tg_if2} | ${dut1_if1_mac}
| | ... | UDP | ${src_port} | ${dst_port}

*** Test Cases ***
| tc01-64B-ethipv4-loadbalancer-maglev-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}

