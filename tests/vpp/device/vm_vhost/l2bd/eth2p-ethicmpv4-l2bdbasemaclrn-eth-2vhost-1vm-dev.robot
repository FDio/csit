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
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | NIC_Virtual | ETH | L2BDMACLRN | BASE | ICMP | VHOST | 1VM
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace | vhost
| ...
| Test Template | Local Template
| ...
| Documentation | *L2 bridge-domain test cases with vhost user interface*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology with \
| ... | VM and single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of \
| ... | IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with two L2 \
| ... | bridge-domains (L2BD) switching combined with MAC learning enabled. \
| ... | Qemu Guest is connected to VPP via vhost-user interfaces. Guest is \
| ... | configured with VPP l2 cross-connect interconnecting vhost-user \
| ... | interfaces.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in \
| ... | both directions by TG on links to DUT1 via VM; on receive TG verifies \
| ... | packets for correctness and their IPv4 src-addr, dst-addr and MAC \
| ... | addresses.
| ... | *[Ref] Applicable standard specifications:* RFC792

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${nic_name}= | virtual
| ${nf_chains}= | ${1}
| ${nf_nodes}= | ${1}
| ${nf_dtc} | ${1}
| ${nf_dtcr} | ${1}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 configure \
| | ... | two L2BDs with MAC learning, each with vhost-user i/f to local \
| | ... | VM and i/f to TG; configure VPP in VM to loop pkts back betwen its \
| | ... | two virtio i/fs. [Ver] Make TG verify ICMPv4 Echo Req pkts are \
| | ... | switched thru DUT1 and VM in both directions and are correct on \
| | ... | receive. [Ref]
| | ...
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer. Type: integer
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| | ...
| | Set Test Variable | \${frame_size}
| | ...
| | Given Add worker threads and rxqueues to all DUTs | ${phy_cores} | ${rxq}
| | And Add PCI devices to all DUTs
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Initialize layer interface
| | ... | count=${nf_chains}
| | And Initialize L2 bridge domains with Vhost-User | nf_nodes=${nf_nodes}
| | And Configure chains of NFs connected via vhost-user
| | ... | nf_chains=${nf_chains} | nf_nodes=${nf_nodes} | vnf=vpp_chain_l2xc
| | ... | pinning=${False}
| | Then Send ICMPv4 bidirectionally and verify received packets | ${tg}
| | ... | ${tg_if1} | ${tg_if2}

*** Test Cases ***
| tc01-64B-ethicmpv4-l2bdbasemaclrn-eth-2vhost-1vm-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
