# Copyright (c) 2016 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/performance.robot
| Resource | resources/libraries/robot/tagging.robot
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_SHORT
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L2 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keyword | Remove startup configuration of VPP from all DUTs
| Documentation | Minimal throughput acceptance test cases

*** Variables ***
| ${subid}= | 10
| ${outer_vlan_id}= | 100
| ${inner_vlan_id}= | 200
| ${type_subif}= | two_tags
| ${tag_rewrite}= | pop-2

*** Test Cases ***
| 1core VPP passes 64B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x3.6Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 64B frames through VLAN dot1ad
| | ... | sub-interfaces inter-connected using L2 cross connect at 2x 2.9Mpps
| | ... | in 3-node topology. Tagging is applied between DUTs inserting 2x 4B
| | ... | VLAN ID into a packet header.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 2.9mpps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect

| 1core VPP passes 1514B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x 810,635pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 1514B frames through VLAN dot1ad
| | ... | sub-interfaces inter-connected using L2 cross connect at
| | ... | 2x 810,635pps in 3-node topology. Tagging is applied between DUTs
| | ... | inserting 2x 4B VLAN ID into a packet header.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 1514
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 810635pps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect

| 1core VPP passes 9000B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x 138,458pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 9000B frames through VLAN dot1ad
| | ... | sub-interfaces inter-connected using L2 cross connect at
| | ... | 2x 138,458pps in 3-node topology. Tagging is applied between DUTs
| | ... | inserting 2x 4B VLAN ID into a packet header.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138458pps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect

| 2core VPP with rss 1 passes 64B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x7.0Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 64B frames through VLAN dot1q
| | ... | sub-interfaces inter-connected using L2 cross connect at 2x 7.0Mpps
| | ... | in 3-node topology. Tagging is applied between DUTs inserting 2x 4B
| | ... | VLAN ID into a packet header.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 7.0mpps
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect

| 2core VPP with rss 1 passes 1514B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x 810,635pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 1514B frames through VLAN dot1ad
| | ... | sub-interfaces inter-connected using L2 cross connect at
| | ... | 2x 810,635pps in 3-node topology. Tagging is applied between DUTs
| | ... | inserting 2x 4B VLAN ID into a packet header.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1514
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 810635pps
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect

| 2core VPP with rss 1 passes 9000B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x 138,458pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 9000B frames through VLAN dot1ad
| | ... | sub-interfaces inter-connected using L2 cross connect at
| | ... | 2x 138,458pps in 3-node topology. Tagging is applied between DUTs
| | ... | inserting 2x 4B VLAN ID into a packet header.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138458pps
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect

| 4core VPP with rss 2 passes 64B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x8.0Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 64B frames through VLAN dot1q
| | ... | sub-interfaces inter-connected using L2 cross connect at 2x 8.0Mpps
| | ... | in 3-node topology. Tagging is applied between DUTs inserting 2x 4B
| | ... | VLAN ID into a packet header.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 8.0mpps
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect

| 4core VPP with rss 2 passes 1514B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x 810,635pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 1514B frames through VLAN dot1ad
| | ... | sub-interfaces inter-connected using L2 cross connect at
| | ... | 2x 810,635pps in 3-node topology. Tagging is applied between DUTs
| | ... | inserting 2x 4B VLAN ID into a packet header.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1514
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 810635pps
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect

| 4core VPP with rss 2 passes 9000B frames through VLAN dot1ad sub-interfaces inter-connected using L2 cross connect at 2x 138,458pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 9000B frames through VLAN dot1ad
| | ... | sub-interfaces inter-connected using L2 cross connect at
| | ... | 2x 138,458pps in 3-node topology. Tagging is applied between DUTs
| | ... | inserting 2x 4B VLAN ID into a packet header.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138458pps
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | ... | ${outer_vlan_id} | ${inner_vlan_id} | ${type_subif}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                   | ${framesize} | 3-node-xconnect
