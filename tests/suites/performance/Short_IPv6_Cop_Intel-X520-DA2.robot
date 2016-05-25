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
| Library | resources.libraries.python.Cop
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | PERFTEST_SHORT
| ...        | NIC_Intel-X520-DA2
| Suite Setup | 3-node Performance Suite Setup with DUT's NIC model
| ... | L3 | Intel-X520-DA2
| Suite Teardown | 3-node Performance Suite Teardown
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keyword | Remove startup configuration of VPP from all DUTs
| Documentation | Minimal throughput acceptance test cases

*** Test Cases ***
| 1core VPP passes 78B frames through IPv6 forwarding with COP at 2x 2.9Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 78B frames through IPv6 forwarding
| | ... | at 2x 2.9Mpps in 3-node topology with COP.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 78
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 2.9mpps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 1core VPP passes 1518B frames through IPv6 forwarding with COP at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 1518B frames through IPv6 forwarding
| | ... | at 2x 812,743pps (2x 10Gbps) in 3-node topology with COP.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 1core VPP passes 9000B frames through IPv6 forwarding with COP at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 1 core should pass 9000B frames through IPv6 forwarding
| | ... | at 2x138,580pps (2x 10Gbps) in 3-node topology with COP.
| | [Tags] | 1_THREAD_NOHTT_RSS_1 | SINGLE_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Add '1' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 2core VPP with rss 1 passes 78B frames through IPv6 forwarding with COP at 2x 4.9Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 78B frames through IPv6 forwarding
| | ... | at 2x 4.9Mpps in 3-node topology with COP.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 78
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 4.9mpps
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 2core VPP with rss 1 passes 1518B frames through IPv6 forwarding with COP at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 1518B frames through IPv6 forwarding
| | ... | at 2x 812,743pps (2x 10Gbps) in 3-node topology with COP.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 2core VPP with rss 1 passes 9000B frames through IPv6 forwarding with COP at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 2 cores should pass 9000B frames through IPv6 forwarding
| | ... | at 2x 138,580pps (2x 10Gbps) in 3-node topology with COP.
| | [Tags] | 2_THREAD_NOHTT_RSS_1 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Add '2' worker threads and rss '1' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 4core VPP with rss 2 passes 78B frames through IPv6 forwarding with COP at 2x 10.1Mpps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rss 2 should pass 78B frames through IPv6
| | ... | forwarding at 2x 10.1Mpps in 3-node topology with COP.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 78
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 10.1mpps
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 4core VPP with rss 2 passes 1518B frames through IPv6 forwarding with COP at 2x 812,743pps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rss 2 should pass 1518B frames through IPv6
| | ... | forwarding at 2x 812,743pps (2x 10Gbps) in 3-node topology with COP.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 1518
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 812743pps
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Add No Multi Seg to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6

| 4core VPP with rss 2 passes 9000B frames through IPv6 forwarding with COP at 2x 138,580pps in 3-node topology
| | [Documentation]
| | ... | VPP with 4 cores and rss 2 should pass 9000B frames through IPv6
| | ... | forwarding at 2x 138,580pps (2x 10Gbps) in 3-node topology with COP.
| | [Tags] | 4_THREAD_NOHTT_RSS_2 | MULTI_THREAD | NDR
| | ${framesize}= | Set Variable | 9000
| | ${duration}= | Set Variable | 10
| | ${rate}= | Set Variable | 138580pps
| | Given Add '4' worker threads and rss '2' without HTT to all DUTs
| | And   Add all PCI devices to all DUTs
| | And   Apply startup configuration on all VPP DUTs
| | When  IPv6 forwarding initialized in a 3-node circular topology
| | And   Add fib table | ${dut1} | 2001:1:: | 64 | 1 | local
| | And   Add fib table | ${dut2} | 2001:2:: | 64 | 1 | local
| | And   COP Add whitelist Entry | ${dut1} | ${dut1_if1} | ip6 | 1
| | And   COP Add whitelist Entry | ${dut2} | ${dut2_if2} | ip6 | 1
| | And   COP interface enable or disable | ${dut1} | ${dut1_if1} | enable
| | And   COP interface enable or disable | ${dut2} | ${dut2_if2} | enable
| | Then  Traffic should pass with no loss | ${duration} | ${rate}
| | ...                                    | ${framesize} | 3-node-IPv6
