# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/shared/traffic.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | IP4FWD | BASE | ETH | VHOST | 1VM
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | vhost
| ...
| Documentation | *IPv4 routing test cases with vhost user interface*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology with \
| ... | VM and single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for IPv4 routing on \
| ... | both links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with IPv4 routing and \
| ... | two static IPv4 /24 route entries. Qemu Guest is connected to VPP via \
| ... | vhost-user interfaces. Guest is running VPP ip4 interconnecting \
| ... | vhost-user interfaces.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in \
| ... | one direction by TG on links to DUT1; on receive TG verifies packets \
| ... | for correctness and their IPv4 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC791, RFC826, RFC792

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${nic_name}= | virtual
| ${nf_chains}= | ${1}
| ${nf_nodes}= | ${1}
| ${tg_if1_ip}= | 10.10.10.2
| ${tg_if2_ip}= | 20.20.20.2

*** Test Cases ***
| tc01-eth2p-ethip4-ip4base-eth-2vhost-1vm-device
| | [Documentation]
| | ... | Test uses two VRFs to route IPv4 traffic through two vhost-user \
| | ... | interfaces. Both interfaces are configured with IP addresses from \
| | ... | the same network. The VM is running VPP ip4 to pass packet \
| | ... | from one vhost-user interface to another one.
| | ...
| | Given Add PCI devices to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Initialize IPv4 forwarding with vhost in 2-node circular topology
| | ... | nf_nodes=${nf_nodes}
| | And Configure chains of NFs connected via vhost-user on single node
| | ... | DUT1 | nf_chains=${nf_chains} | nf_nodes=${nf_nodes}
| | ... | vnf=vpp_chain_ip4_noarp | pinning=${False}
| | ${dut1_if1_mac}= | Get Interface MAC | ${dut1} | ${dut1_if1}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | Then Send packet and verify headers
| | ... | ${tg} | ${tg_if1_ip} | ${tg_if2_ip}
| | ... | ${tg_if1} | ${tg_if1_mac} | ${dut1_if1_mac}
| | ... | ${tg_if2} | ${dut1_if2_mac} | ${tg_if2_mac}
