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
| ... | NIC_Virtual | ETH | L2BD | BASE | 2TAP
| ...
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test | namespace
| Test Teardown | Tear down test | packet_trace | namespace | linux_bridge
| ...
| Test Template | Local Template
| ...
| Documentation | *Tap Interface Traffic Tests*
| ...
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG)
| ... | are set depending on test case; Namespaces (NM)
| ... | are set on DUT1 with attached linux-TAP.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets
| ... | are sent by TG on link to DUT1; On receipt TG verifies packets
| ... | for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${nic_name}= | virtual
| ${overhead}= | ${0}
| ${bid_TAP}= | tapBr

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Ver] Packet sent from TG is passed through all L2BD and received\
| | ... | back on TG. Then src_ip, dst_ip and MAC are checked.
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
| | And Set Max Rate And Jumbo And Handle Multi Seg
| | And Apply startup configuration on all VPP DUTs | with_trace=${True}
| | When Set interfaces in path up
| | ${int1}= | And Add Tap Interface | ${dut1} | tap0
| | ${int2}= | And Add Tap Interface | ${dut1} | tap1
| | And Set Interface State | ${dut1} | ${int1} | up
| | And Set Interface State | ${dut1} | ${int2} | up
| | And Create bridge domain | ${dut1} | 19 | learn=${TRUE}
| | And Create bridge domain | ${dut1} | 20 | learn=${TRUE}
| | And Linux Add Bridge | ${dut1} | ${bid_TAP} | tap0 | tap1
| | And Add interface to bridge domain | ${dut1} | ${int1} | 20 | 0
| | And Add interface to bridge domain | ${dut1} | ${dut1_if1} | 20 | 0
| | And Add interface to bridge domain | ${dut1} | ${int2} | 19 | 0
| | And Add interface to bridge domain | ${dut1} | ${dut1_if2} | 19 | 0
| | Then Send ICMP packet and verify received packet
| | ... | ${tg} | ${tg_if1} | ${tg_if2}

*** Test Cases ***
| tc01-64B-ethicmpv4-l2bdbasemaclrn-eth-2tap-dev
| | [Tags] | 64B
| | frame_size=${64} | phy_cores=${0}
