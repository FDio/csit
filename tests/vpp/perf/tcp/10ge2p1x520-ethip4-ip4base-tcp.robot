# Copyright (c) 2017 Cisco and/or its affiliates.
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

| Library  | resources.tools.wrk.wrk
| Resource | resources/libraries/robot/wrk/wrk_setup.robot
| Resource | resources/libraries/robot/tcp/tcp_setup.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | TCP
| ...
| Suite Setup | Set up 3-node performance topology with wrk and DUT's NIC model
| ... | Intel-XL710
| ...
| Test Setup | Set up performance test
| Test Teardown | Tear down performance test with wrk
| ...
| Documentation | *HTTP requests per seconds, connections per seconds and
| ... | throughput measurement.*
| ...
| ... | *[Top] Network Topologies:* TG-DUT-TG 2-node topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 for IPv4 routing.
| ... | *[Cfg] DUT configuration:*
| ... | *[Ver] TG verification:*
| ... | *[Ref] Applicable standard specifications:*

*** Test Cases ***
| tc01-1t1c-ethip4-ip4tcp-throughput
| | [Documentation]
| | ... | Measure and report throughput using wrk.
| | ...
| | [Tags] | 1T1C | TCP_THROUGHPUT
| | ...
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure throughput | wrk-bw-1url-1core-50con

| tc02-2t2c-ethip4-ip4tcp-throughput
| | [Documentation]
| | ... | Measure and report throughput using wrk.
| | ...
| | [Tags] | 2T2C | TCP_THROUGHPUT
| | ...
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure throughput | wrk-bw-1url-1core-50con

| tc03-4t4c-ethip4-ip4tcp-throughput
| | [Documentation]
| | ... | Measure and report throughput using wrk.
| | ...
| | [Tags] | 4T4C | TCP_THROUGHPUT
| | ...
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure throughput | wrk-bw-1url-1core-50con

| tc04-1t1c-ethip4-ip4tcp-cps
| | [Documentation]
| | ... | Measure number of connections per second using wrk.
| | ...
| | [Tags] | 1T1C | TCP_CPS
| | ...
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure connections per second | wrk-cps-1url-1core-1con

| tc05-2t2c-ethip4-ip4tcp-cps
| | [Documentation]
| | ... | Measure number of connections per second using wrk.
| | ...
| | [Tags] | 2T2C | TCP_CPS
| | ...
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure connections per second | wrk-cps-1url-1core-1con

| tc06-4t4c-ethip4-ip4tcp-cps
| | [Documentation]
| | ... | Measure number of connections per second using wrk.
| | ...
| | [Tags] | 4T4C | TCP_CPS
| | ...
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure connections per second | wrk-cps-1url-1core-1con

| tc07-1t1c-ethip4-ip4tcp-rps
| | [Documentation]
| | ... | Measure and report number of requests per second using wrk.
| | ...
| | [Tags] | 1T1C | TCP_RPS
| | ...
| | Given Add '1' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure requests per second | wrk-rps-1url-1core-50con

| tc08-2t2c-ethip4-ip4tcp-rps
| | [Documentation]
| | ... | Measure and report number of requests per second using wrk.
| | ...
| | [Tags] | 2T2C | TCP_RPS
| | ...
| | Given Add '2' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure requests per second | wrk-rps-1url-1core-50con

| tc09-4t4c-ethip4-ip4tcp-rps
| | [Documentation]
| | ... | Measure and report number of requests per second using wrk.
| | ...
| | [Tags] | 4T4C | TCP_RPS
| | ...
| | Given Add '4' worker threads and '2' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Apply startup configuration on all VPP DUTs
| | And Set up HTTP server on the VPP node | 192.168.10.2 | 24
| | Then Measure requests per second | wrk-rps-1url-1core-50con
