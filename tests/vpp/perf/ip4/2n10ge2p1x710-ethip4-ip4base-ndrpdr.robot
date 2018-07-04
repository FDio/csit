# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/performance/performance_setup.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | NDRPDR
| ... | NIC_Intel-X710 | ETH | IP4FWD | BASE | IP4BASE
| ...
| Suite Setup | Set up 2-node performance topology with DUT's NIC model
| ... | L3 | Intel-X710
| Suite Teardown | Tear down 2-node performance topology
| ...
| Test Setup | Set up performance test
| Test Teardown | Tear down performance discovery test | ${min_rate}pps
| ... | ${framesize} | ${traffic_profile}
| ...
| Test Template | Discover NDRPDR for ethip4-ip4base
| ...
| Documentation | FIXME

*** Variables ***
# X710 bandwidth limit
| ${s_limit}= | ${10000000000}
# Traffic profile:
| ${traffic_profile}= | trex-sl-2n-ethip4-ip4src253

*** Keywords ***
| Discover NDRPDR for ethip4-ip4base
| | ...
| | [Documentation]
| | ... | FIXME
| | ...
| | [Arguments] | ${wt} | ${rxq} | ${framesize}
| | ...
| | # Test Variables required for test execution and test teardown
| | Set Test Variable | ${framesize}
| | Set Test Variable | ${worker_threads} | ${wt}
| | Set Test Variable | ${rx_queues} | ${rxq}
| | Set Test Variable | ${min_rate} | ${20000}
| | ${get_framesize}= | Get Frame Size | ${framesize}
| | ${max_uniditrectional_rate}= | Calculate pps | ${s_limit} | ${get_framesize}
| | ${max_rate}= | Evaluate | 2*${max_uniditrectional_rate}
| | ...
| | Given Add worker threads and rxqueues to all DUTs
| | And Add PCI devices to all DUTs
| | And Run Keyword If | ${get_framesize} < ${1522}
| | ... | Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize IPv4 forwarding in 2-node circular topology
| | Then Find NDR and PDR intervals using optimized search
| | ... | ${framesize} | ${traffic_profile} | ${min_rate} | ${max_rate}

*** Test Cases ***
| tc01-64B-1t1c-ethip4-ip4base-ndrpdr
| | [Documentation]
| | ... | FIXME
| | ...
| | [Tags] | 64B | 1T1C | STHREAD
| | ...
| | wt=1 | rxq=1 | framesize=${64}
