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
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | OFFLOADTEST | HW_ENV | SCAPY
| ... | NIC_Intel-E810CQ | ETH | FLOW | IP6_N_TUPLE | DRV_VFIO_PCI
| ... | RXQ_SIZE_0 | TXQ_SIZE_0
| ... | flow-ip6-ntuple
|
| Suite Setup | Setup suite topology interfaces | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Documentation | *IP6-N-TUPLE flow test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1 2-node topology with one link\
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IP6-TCP or Eth-IP6-UDP.
| ... | *[Cfg] DUT configuration:* DUT is configured with IP6-N-TUPLE flow.
| ... | *[Ver] TG verification:* Verify if the flow action is correct.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | Intel-E810CQ
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
| ${frame_size}= | ${0}
| ${phy_cores}= | ${0}
| ${src_ip}= | 2001:0db8:3c4d:0015:0000:0000:1a2f:1a2b
| ${dst_ip}= | 1011:2022:3033:4044:5055:6066:7077:8088
| ${src_port}= | ${100}
| ${dst_port}= | ${200}
| ${timeout}= | ${5}

*** Keywords ***
| Initialize Flow Test Configuration
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${8} | ${8}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface

*** Test Cases ***
| flow-ip6-ntuple-udp-action-redirect-to-queue
| | Initialize Flow Test Configuration
| | ${flow_index} = | Vpp Create Ip6 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=UDP | action=redirect-to-queue | value=${7}
| | Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Sleep | ${timeout}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | flow_type=IP6 | proto=UDP
| | ... | action=redirect-to-queue | action_value=${7}
| | Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Vpp Flow Del | ${dut1} | ${flow_index}

| flow-ip6-ntuple-udp-action-drop
| | Initialize Flow Test Configuration
| | ${flow_index} = | Vpp Create Ip6 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=UDP | action=drop
| | Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Sleep | ${timeout}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | flow_type=IP6 | proto=UDP
| | ... | action=drop
| | Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Vpp Flow Del | ${dut1} | ${flow_index}

| flow-ip6-ntuple-udp-action-mark
| | Initialize Flow Test Configuration
| | ${flow_index} = | Vpp Create Ip6 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=UDP | action=mark | value=${8}
| | Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Sleep | ${timeout}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | flow_type=IP6 | proto=UDP
| | ... | action=mark
| | Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Vpp Flow Del | ${dut1} | ${flow_index}

| flow-ip6-ntuple-tcp-action-redirect-to-queue
| | Initialize Flow Test Configuration
| | ${flow_index} = | Vpp Create Ip6 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=TCP | action=redirect-to-queue | value=${7}
| | Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Sleep | ${timeout}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | flow_type=IP6 | proto=TCP
| | ... | action=redirect-to-queue | action_value=${7}
| | Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Vpp Flow Del | ${dut1} | ${flow_index}

| flow-ip6-ntuple-tcp-action-drop
| | Initialize Flow Test Configuration
| | ${flow_index} = | Vpp Create Ip6 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=TCP | action=drop
| | Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Sleep | ${timeout}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | flow_type=IP6 | proto=TCP
| | ... | action=drop
| | Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Vpp Flow Del | ${dut1} | ${flow_index}

| flow-ip6-ntuple-tcp-action-mark
| | Initialize Flow Test Configuration
| | ${flow_index} = | Vpp Create Ip6 N Tuple Flow | ${dut1}
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | proto=TCP | action=mark | value=${8}
| | Vpp Flow Enable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Sleep | ${timeout}
| | Then Send flow packet and verify action
| | ... | ${tg} | ${TG_pf1}[0] | ${DUT1_${int}1_mac}[0]
| | ... | ${src_ip} | ${dst_ip} | ${src_port} | ${dst_port}
| | ... | flow_type=IP6 | proto=TCP
| | ... | action=mark
| | Vpp Flow Disable | ${dut1} | ${DUT1_${int}1}[0] | ${flow_index}
| | Vpp Flow Del | ${dut1} | ${flow_index}
