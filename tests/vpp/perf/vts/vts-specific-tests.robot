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
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT1']}
| ... | WITH NAME | dut1_v4
| Library | resources.libraries.python.IPv4Setup.Dut | ${nodes['DUT2']}
| ... | WITH NAME | dut2_v4
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | NDRPDRDISC
| ... | NIC_Intel-X520-DA2 | ETH | IP4FWD | FEATURE | IACLDST
| ... | L2BDMACLRN | ENCAP | VXLAN | L2OVRLAY | IP4UNRLAY
| ...
| Suite Setup | Set up 3-node performance topology with DUT's NIC model
| ... | L2 | Intel-X520-DA2
| Suite Teardown | Tear down 3-node performance topology
| ...
| Test Setup | Set up performance test
| ...
| Test Teardown | Tear down performance discovery test | ${min_rate}pps
| ... | ${framesize} | ${traffic_profile}
| ...

*** Variables ***
# X520-DA2 bandwidth limit
| ${s_limit} | ${10000000000}
| ${vxlan_overhead} | ${50}
# Traffic profile:
| ${traffic_profile} | trex-sl-3n-ethip4-ip4src254
| ${min_rate} | ${100000}

*** Keywords ***
| vxlan with acl on ${num_of_threads} threads with packetsize ${pkt_framesize}
| | [Documentation]
| | ${max_pkt_size}= | Set Variable If | '${pkt_framesize}' == 'IMIX_v4_1' | ${1500 + ${vxlan_overhead}} |
| | ... | ${pkt_framesize + ${vxlan_overhead}}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${max_pkt_size}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Set Suite Variable | ${framesize} | ${pkt_framesize}
| | Given Add '${num_of_threads}' worker threads and '1' rxqueues in 3-node single-link circular topology
| | And Add PCI devices to DUTs in 3-node single link topology
| | And Add no multi seg to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | And Initialize L2 bridge domain with VXLANoIPv4 in 3-node circular topology
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 172.16.0.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${dut1_if2} | ip4 | ${table_idx}
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut2} | ip4 | dst
| | And Vpp Configures Classify Session L3
| | ... | ${dut2} | permit | ${table_idx} | ${skip_n} | ${match_n}
| | ... | ip4 | dst | 172.16.0.1
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${dut2_if1} | ip4 | ${table_idx}
| | Then Find NDR using binary search and pps | ${pkt_framesize} | ${binary_min}
| | ... | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}

*** Test Cases ***
| tc01-vxlan-acl-1-thread-min-pkt
| | vxlan with acl on 1 threads with packetsize ${64}

| tc02-vxlan-acl-2-thread-min-pkt
| | vxlan with acl on 2 threads with packetsize ${64}

| tc03-vxlan-acl-3-thread-min-pkt
| | vxlan with acl on 3 threads with packetsize ${64}

| tc01-vxlan-acl-1-thread-imix-pkt
| | vxlan with acl on 1 threads with packetsize IMIX_v4_1

| tc01-vxlan-acl-2-thread-imix-pkt
| | vxlan with acl on 2 threads with packetsize IMIX_v4_1

| tc01-vxlan-acl-3-thread-imix-pkt
| | vxlan with acl on 3 threads with packetsize IMIX_v4_1

