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
| Discover NDR or PDR for IPv4 forwarding with VXLAN and ACL
| | [Arguments] | ${num_of_threads} | ${rxq} | ${pkt_framesize} | ${search_type}
| | [Documentation]
| | ... | [Cfg] DUT runs IP4 VXLAN w/ ACL whitelist on VXLAN endpoints with\
| | ... | required number of threads, phy cores and receive queues per NIC port.
| | ... | [Ver] Find NDR or PDR for defined frame size using binary search\
| | ... | start at 10GE linerate with specified step.
| | ...
| | ... | *Arguments:*
| | ... | - num_of_threads - Number of worker threads to be used. Type: integer
| | ... | - rxq - Number of Rx queues to be used. Type: integer
| | ... | - pkt_framesize - L2 Frame Size [B]. Type: integer
| | ... | - search_type - Type of the search - non drop rate (NDR) or partial
| | ... | drop rare (PDR). Type: string
| | ${max_pkt_size}= | Set Variable If | '${pkt_framesize}' == 'IMIX_v4_1' |
| | ... | ${1500 + ${vxlan_overhead}} | ${pkt_framesize + ${vxlan_overhead}}
| | ${max_rate}= | Calculate pps | ${s_limit} | ${max_pkt_size}
| | ${binary_min}= | Set Variable | ${min_rate}
| | ${binary_max}= | Set Variable | ${max_rate}
| | ${threshold}= | Set Variable | ${min_rate}
| | Set Suite Variable | ${framesize} | ${pkt_framesize}
| | Given Add '${num_of_threads}' worker threads and '${rxq}' rxqueues in 3-node single-link circular topology
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
| | Run Keyword If | '${search_type}' == 'NDR'
| | ... | Find NDR using binary search and pps
| | ... | ${pkt_framesize} | ${binary_min} | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ELSE IF | '${search_type}' == 'PDR'
| | ... | Find PDR using binary search and pps
| | ... | ${pkt_framesize} | ${binary_min} | ${binary_max} | ${traffic_profile}
| | ... | ${min_rate} | ${max_rate} | ${threshold}
| | ... | ${perf_pdr_loss_acceptance} | ${perf_pdr_loss_acceptance_type}


*** Settings ***
| Test Template | Discover NDR or PDR for IPv4 forwarding with VXLAN and ACL


*** Test Cases ***   num_of_threads | rxq | pkt_framesize | search_type
| tc01-64B-1t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-ndrdisc
| | ...             | 1             | 1   | ${64}         | NDR
| tc02-64B-2t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-ndrdisc
| | ...             | 2             | 1   | ${64}         | NDR
| tc03-64B-3t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-ndrdisc
| | ...             | 3             | 1   | ${64}         | NDR
| tc04-64B-1t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-pdrdisc
| | ...             | 1             | 1   | ${64}         | PDR
| tc05-64B-2t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-pdrdisc
| | ...             | 2             | 1   | ${64}         | PDR
| tc06-64B-3t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-pdrdisc
| | ...             | 3             | 1   | ${64}         | PDR
| tc07-IMIX-1t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-ndrdisc
| | ...             | 1             | 1   | IMIX_v4_1     | NDR
| tc08-IMIX-2t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-ndrdisc
| | ...             | 2             | 1   | IMIX_v4_1     | NDR
| tc09-IMIX-3t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-ndrdisc
| | ...             | 3             | 1   | IMIX_v4_1     | NDR
| tc10-IMIX-1t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-pdrdisc
| | ...             | 1             | 1   | IMIX_v4_1     | PDR
| tc11-IMIX-2t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-pdrdisc
| | ...             | 2             | 1   | IMIX_v4_1     | PDR
| tc12-IMIX-3t1c-ethip4vxlan-l2bdbasemaclrn-iacldstbase-pdrdisc
| | ...             | 3             | 1   | IMIX_v4_1     | PDR

