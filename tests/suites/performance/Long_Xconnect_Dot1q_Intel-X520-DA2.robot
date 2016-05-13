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
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_LONG
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L2 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keyword | Remove startup configuration of VPP from all DUTs
| Documentation | *Throughput search suite (based on RFC2544).*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG, with one link
| ... | between nodes. Traffic profile contain 2 L2 streams (1 stream per
| ... | direction). Packets contain Ethernet header, IPv4 header,
| ... | IP protocol=61 and random payload. Ethernet header MAC addresses are
| ... | matching MAC addresses of the TG node. DUT nodes are interconnected
| ... | with VLAN dot1q configured interfaces with VLAN 10.

*** Variables ***
| ${subid}= | 10
| ${tag_rewrite}= | pop-1

*** Test Cases ***
| Find NDR by using RFC2544 binary search and 64B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate by using binary search with
| | ... | threshold 0.1Mpps. Frames from and to TG are 64B long. Tagging is
| | ... | applied between DUTs inserting 4B VLAN ID into a packet header.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_68B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 64B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate by using binary search with
| | ... | threshold 0.1Mpps. Frames from and to TG are 64B long. Tagging is
| | ... | applied between DUTs inserting 4B VLAN ID into a packet header. Loss
| | ... | acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | PDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_68B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 1518B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate by using binary search with
| | ... | threshold 10,000pps. Frames from and to TG are 1518B long. Tagging is
| | ... | applied between DUTs inserting 4B VLAN ID into a packet header.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1522B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 1518B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate by using binary search with
| | ... | threshold 10,000pps. Frames from and to TG are 1518B long. Tagging is
| | ... | applied between DUTs inserting 4B VLAN ID into a packet header. Loss
| | ... | acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | PDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1522B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR by using RFC2544 binary search and 9000B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate by using binary search with
| | ... | threshold 5,000pps. Frames from and to TG are 9000B long. Tagging is
| | ... | applied between DUTs inserting 4B VLAN ID into a packet header.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9004B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR by using RFC2544 binary search and 9000B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate by using binary search with
| | ... | threshold 5,000pps. Frames from and to TG are 9000B long. Tagging is
| | ... | applied between DUTs inserting 4B VLAN ID into a packet header. Loss
| | ... | acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | PDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9004B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rss 1 by using RFC2544 binary search and 64B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate by using binary search
| | ... | with threshold 0.1Mpps. Frames from and to TG are 64B long. Tagging
| | ... | is applied between DUTs inserting 4B VLAN ID into a packet header.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_68B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rss 1 by using RFC2544 binary search and 64B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate by using binary
| | ... | search with threshold 0.1Mpps. Frames from and to TG are 64B long.
| | ... | Tagging is applied between DUTs inserting 4B VLAN ID into a packet
| | ... | header. Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_68B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rss 1 by using RFC2544 binary search and 1518B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate by using binary search
| | ... | with threshold 10,000pps. Frames from and to TG are 1518B long.
| | ... | Tagging is applied between DUTs inserting 4B VLAN ID into a packet
| | ... | header.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1522B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rss 1 by using RFC2544 binary search and 1518B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate by using binary
| | ... | search with threshold 10,000pps. Frames from and to TG are 1518B long.
| | ... | Tagging is applied between DUTs inserting 4B VLAN ID into a packet
| | ... | header. Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1522B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 2 cores and rss 1 by using RFC2544 binary search and 9000B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate by using binary search
| | ... | with threshold 5,000pps. Frames from and to TG are 9000B long.
| | ... | Tagging is applied between DUTs inserting 4B VLAN ID into a packet
| | ... | header.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9004B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 2 cores and rss 1 by using RFC2544 binary search and 9000B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate by using binary
| | ... | search with threshold 5,000pps. Frames from and to TG are 9000B long.
| | ... | Tagging is applied between DUTs inserting 4B VLAN ID into a packet
| | ... | header. Loss acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9004B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rss 2 by using RFC2544 binary search and 64B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with non drop rate by using
| | ... | binary search with threshold 0.1Mpps. Frames from and to TG are 64B
| | ... | long. Tagging is applied between DUTs inserting 4B VLAN ID into a
| | ... | packet header.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_68B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rss 2 by using RFC2544 binary search and 64B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with partial drop rate by using
| | ... | binary search with threshold 0.1Mpps. Frames from and to TG are 64B
| | ... | long. Tagging is applied between DUTs inserting 4B VLAN ID into a
| | ... | packet header. Loss acceptance is set to 0.5 percent of transmitted
| | ... | packets.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 100000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_68B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rss 2 by using RFC2544 binary search and 1518B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with non drop rate by using
| | ... | binary search with threshold 10,000pps. Frames from and to TG are
| | ... | 1518B long. Tagging is applied between DUTs inserting 4B VLAN ID into
| | ... | a packet header.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1522B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rss 2 by using RFC2544 binary search and 1518B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with partial drop rate by using
| | ... | binary search with threshold 10,000pps. Frames from and to TG are
| | ... | 1518B long. Tagging is applied between DUTs inserting 4B VLAN ID into
| | ... | a packet header. Loss acceptance is set to 0.5 percent of transmitted
| | ... | packets.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1522B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find NDR with 4 cores and rss 2 by using RFC2544 binary search and 9000B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with non drop rate by using
| | ... | binary search with threshold 5,000pps. Frames from and to TG are
| | ... | 9000B long. Tagging is applied between DUTs inserting 4B VLAN ID into
| | ... | a packet header.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9004B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find PDR with 4 cores and rss 2 by using RFC2544 binary search and 9000B frames through VLAN dot1q sub-interfaces inter-connected using L2 cross connect in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with partial drop rate by using
| | ... | binary search with threshold 5,000pps. Frames from and to TG are
| | ... | 9000B long. Tagging is applied between DUTs inserting 4B VLAN ID into
| | ... | a packet header. Loss acceptance is set to 0.5 percent of transmitted
| | ... | packets.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9004B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | And   VPP interfaces in path are up
| | When VLAN dot1q subinterfaces initialized on 3-node topology
| | ... | ${dut1} | ${dut1_if2} | ${dut2} | ${dut2_if1} | ${subid}
| | And L2 tag rewrite method setup on interfaces
| | ... | ${dut1} | ${subif_index_1} | ${dut2} | ${subif_index_2}
| | ... | ${tag_rewrite}
| | And Interfaces and VLAN sub-interfaces inter-connected using L2-xconnect
| | ... | ${dut1} | ${dut1_if1} | ${subif_index_1}
| | ... | ${dut2} | ${dut2_if2} | ${subif_index_2}
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-xconnect
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}
