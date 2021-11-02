# Copyright (c) 2021 Intel and/or its affiliates.
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
| ... | NIC_Intel-X710 | ETH | IP4FWD | FLOW | NTUPLE | TCP | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | ethip4-flow-ip4-ntuple-tcp
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | telemetry
|
| Test Template | Local Template
|
| Documentation | *IP4_N_TUPLE flow test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IP4-TCP.
| ... | *[Cfg] DUT configuration:* DUT is configured with IP4_N_TUPLE flow.
| ... | *[Ver] TG verification:* Verify if the flow action is correct.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
| ${src_ip}= | 1.1.1.1
| ${dst_ip}= | 2.2.2.2
| ${src_port}= | ${100}
| ${dst_port}= | ${200}
| ${rxq}= | ${4}
# Telemetry
| ${telemetry_profile}= | vpp_test_teardown

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Make TG send IP4 packet routed over DUT1 interfaces.\
| | ... | Make VPP verify flow packet is correct.
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues. Type: integer
| |
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${rxq}
| |
| | Set Test Variable | \${frame_size}
| |
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| |
| | Clear Packet Trace On Dut | ${dut1}
| | Vpp Enable Traces On Dut | ${dut1}
| | Vpp Show Flow Interface | ${dut1}
| | ${flow_index} = | And Vpp Create Ip4 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=TCP | action=drop
| | Vpp Show Flow Interface | ${dut1}
| | And Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | flow_type=IP4 | proto=TCP
| | ... | src_ip=${src_ip} | dst_ip=${dst_ip}
| | ... | src_port=${src_port} | dst_port=${dst_port}
| | ... | action=drop
| | Vpp Show Flow Interface | ${dut1}
| | And Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | And Vpp Flow Del | ${dut1} | ${flow_index}
| |
| | Clear Packet Trace On Dut | ${dut1}
| | Vpp Enable Traces On Dut | ${dut1}
| | ${flow_index} = | And Vpp Create Ip4 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=TCP | action=mark | value=${7}
| | And Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | flow_type=IP4 | proto=TCP
| | ... | src_ip=${src_ip} | dst_ip=${dst_ip}
| | ... | src_port=${src_port} | dst_port=${dst_port}
| | ... | action=mark
| | And Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | And Vpp Flow Del | ${dut1} | ${flow_index}
| |
| | Clear Packet Trace On Dut | ${dut1}
| | Vpp Enable Traces On Dut | ${dut1}
| | ${flow_index} = | And Vpp Create Ip4 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=TCP | action=redirect-to-queue | value=${${rxq}-1}
| | And Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | flow_type=IP4 | proto=TCP
| | ... | src_ip=${src_ip} | dst_ip=${dst_ip}
| | ... | src_port=${src_port} | dst_port=${dst_port}
| | ... | action=redirect-to-queue | action_value=${${rxq}-1}
| | And Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | And Vpp Flow Del | ${dut1} | ${flow_index}

*** Test Cases ***
| 64B-0c-ethip4-flow-ip4-ntuple-tcp-scapy
| | [Tags] | 64B | 0C
| | frame_size=${64} | phy_cores=${0}
