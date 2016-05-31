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
| Library | resources.libraries.python.NodePath
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_LONG
| ...        | VHOST_BRIDGE | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L2 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Remove startup configuration of VPP from all DUTs
| ...           | AND          | Qemu Teardown | ${dut1} | ${vm1} | VM1
| ...           | AND          | Qemu Teardown | ${dut2} | ${vm2} | VM2
| Documentation | *Throughput search suite (based on RFC2544).*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG, with one link
| ... | between nodes. Traffic profile contain 2 L2 streams (1 stream per
| ... | direction). Packets contain Ethernet header, IPv4 header,
| ... | IP protocol=61 and random payload. Ethernet header MAC addresses are
| ... | matching MAC addresses of the TG node. Traffic on each DUT is passed
| ... | through separate bridge domains (in learning mode) interconnected via
| ... | vhost-user and VM running Linux Bridge.

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2
| ${sock1}= | /tmp/sock-1-${bd_id1}
| ${sock2}= | /tmp/sock-1-${bd_id2}

*** Test Cases ***
| Find RFC2544:NDR with binary search and 64B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search and 64B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | PDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find RFC2544:NDR with binary search and 1518B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 1518B frames by using
| | ... | binary search with threshold 10,000pps.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1518B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search and 1518B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 1518B frames by using
| | ... | binary search with threshold 10,000pps. Loss acceptance is set to 0.5
| | ... | percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | PDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1518B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find RFC2544:NDR with binary search and 9000B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput with non drop rate for 9000B frames by using
| | ... | binary search with threshold of 5,000pps.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search and 9000B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput with partial drop rate for 9000B frames by using
| | ... | binary search with threshold of 5,000pps. Loss acceptance is set to
| | ... | 0.5 percent of transmitted packets.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | PDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find RFC2544:NDR with binary search with 2 cores and rss 1 and 64B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 64B frames by using
| | ... | binary search with threshold 0.1Mpps.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search with 2 cores and rss 1 and 64B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 64B frames by
| | ... | using binary search with threshold 0.1Mpps. Loss acceptance is set to
| | ... | 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find RFC2544:NDR with binary search with 2 cores and rss 1 and 1518B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 1518B frames by
| | ... | using binary search with threshold 10,000pps.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1518B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search with 2 cores and rss 1 and 1518B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 1518B frames by
| | ... | using binary search with threshold 10,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1518B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find RFC2544:NDR with binary search with 2 cores and rss 1 and 9000B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with non drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search with 2 cores and rss 1 and 9000B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 2 cores with partial drop rate for 9000B frames by
| | ... | using binary search with threshold 5,000pps. Loss acceptance is set
| | ... | to 0.5 percent of transmitted packets.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find RFC2544:NDR with binary search with 4 cores and rss 2 and 64B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with non drop rate for 64B
| | ... | frames by using binary search with threshold 0.1Mpps.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search with 4 cores and rss 2 and 64B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with partial drop rate for 64B
| | ... | frames by using binary search with threshold 0.1Mpps. Loss acceptance
| | ... | is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 64
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_64B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find RFC2544:NDR with binary search with 4 cores and rss 2 and 1518B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with non drop rate for 1518B
| | ... | frames by using binary search with threshold 10,000pps.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1518B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search with 4 cores and rss 2 and 1518B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with partial drop rate for 1518B
| | ... | frames by using binary search with threshold 10,000pps. Loss
| | ... | acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 1518
| | ${min_rate}= | Set Variable | 10000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_1518B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

| Find RFC2544:NDR with binary search with 4 cores and rss 2 and 9000B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with non drop rate for 9000B
| | ... | frames by using binary search with threshold 5,000pps.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find NDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}

| Find RFC2544:PDR with binary search with 4 cores and rss 2 and 9000B frames through BD-VM-BD in 3-node topology
| | [Documentation]
| | ... | Find throughput on 4 cores and rss 2 with partial drop rate for 9000B
| | ... | frames by using binary search with threshold 5,000pps. Loss
| | ... | acceptance is set to 0.5 percent of transmitted packets.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | PDR
| | ${framesize}= | Set Variable | 9000
| | ${min_rate}= | Set Variable | 5000
| | ${max_rate}= | Set Variable | ${10Ge_linerate_pps_9000B}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  L2 bridge domains initialized in a 3-node circular topology with Vhost-User
| | ...   | ${bd_id1} | ${bd_id2} | ${sock1} | ${sock2}
| | ${vm1}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut1} | ${sock1} | ${sock2} | VM1
| | ${vm2}= | And VM with Linux Bridge for Vhost L2BD forwarding is setup
| | ...     | ${dut2} | ${sock1} | ${sock2} | VM2
| | Then Find PDR using binary search and pps | ${framesize} | ${binary_min}
| | ...                                       | ${binary_max} | 3-node-bridge
| | ...                                       | ${min_rate} | ${max_rate}
| | ...                                       | ${threshold}
| | ...                                       | ${glob_loss_acceptance}
| | ...                                       | ${glob_loss_acceptance_type}

