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
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Namespaces
| Library  | resources.libraries.python.Tap
| Library  | resources.libraries.python.Trace
| ...
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| ...
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV
| ... | FUNCTEST | IP4FWD | BASE | ETH | IP4BASE | TAP
| ...
| Suite Setup | Setup suite single link
| Test Setup | Setup test | namespace
| Test Teardown | Tear down test | packet_trace | namespace
| ...
| Documentation | *Tap Interface Traffic Tests*
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
| ${tap1_VPP_ip}= | 16.0.10.1
| ${tap1_NM_ip}= | 16.0.10.2
| ${tap1_NM_mac}= | 02:00:00:00:00:02
| ${tap_int1}= | tap0
| ${namespace1}= | nmspace1
| ${dut_ip_address}= | 192.168.0.1
| ${tg_ip_address}= | 192.168.0.2
| ${tg_ip_address_GW}= | 192.168.0.0
| ${prefix}= | 24

*** Test Cases ***
| tc01-eth2p-ethicmpv4-ip4base-device_tap-no-namespace
| | [Documentation]
| | ... | [Cfg] On DUT1 configure two interface addresses with IPv4 of which\
| | ... | one is TAP interface (dut_to_tg_if and TAP) and one is linux-TAP.
| | ... | [Ver] Packet sent from TG gets to the destination and ICMP-reply is\
| | ... | received on TG.
| | ...
| | Given Add PCI devices to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Configure path in 2-node circular topology | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1} |
| | And VPP Interface Set IP Address
| | ... | ${dut_node} | ${int1} | ${tap1_VPP_ip} | ${prefix}
| | And VPP Interface Set IP Address
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip_address} | ${prefix}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | And Set Linux Interface MAC | ${dut_node} | ${tap_int1} | ${tap1_NM_mac}
| | And Set Linux Interface IP | ${dut_node}
| | ... | ${tap_int1} | ${tap1_NM_ip} | ${prefix}
| | And Add Linux Route | ${dut_node}
| | ... | ${tg_ip_address_GW} | ${prefix} | ${tap1_VPP_ip}
| | And VPP Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${tg_ip_address} | ${tg_to_dut_if1_mac}
| | And VPP Add IP Neighbor | ${dut_node} | ${int1}
| | ... | ${tap1_NM_ip} | ${tap1_NM_mac}
| | Then Send ICMP echo request and verify answer | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap1_NM_ip} | ${tg_ip_address}

| tc02-eth2p-ethicmpv4-ip4base-device_tap-namespace
| | [Documentation]
| | ... | [Cfg] On DUT1 configure two interface addresses with IPv4 of which\
| | ... | one is TAP interface (dut_to_tg_if and TAP) and one is linux-TAP in\
| | ... | namespace.
| | ... | [Ver] Packet sent from TG gets to the destination and ICMP-reply is\
| | ... | received on TG.
| | ...
| | Given Add PCI devices to all DUTs
| | And Apply startup configuration on all VPP DUTs
| | And VPP Enable Traces On All Duts | ${nodes}
| | When Configure path in 2-node circular topology | ${nodes['TG']}
| | ... | ${nodes['DUT1']} | ${nodes['TG']}
| | And Set interfaces in 2-node circular topology up
| | ${int1}= | And Add Tap Interface | ${dut_node} | ${tap_int1} |
| | And VPP Interface Set IP Address
| | ... | ${dut_node} | ${int1} | ${tap1_VPP_ip} | ${prefix}
| | And VPP Interface Set IP Address
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_ip_address} | ${prefix}
| | And Set Interface State | ${dut_node} | ${int1} | up
| | When Create Namespace | ${dut_node} | ${namespace1}
| | And Attach Interface To Namespace | ${dut_node}
| | ... | ${namespace1} | ${tap_int1}
| | And Set Linux Interface MAC | ${dut_node}
| | ... | ${tap_int1} | ${tap1_NM_mac} | ${namespace1}
| | And Set Linux Interface IP | ${dut_node}
| | ... | ${tap_int1} | ${tap1_NM_ip} | ${prefix} | ${namespace1}
| | And VPP Add IP Neighbor | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${tg_ip_address} | ${tg_to_dut_if1_mac}
| | And VPP Add IP Neighbor | ${dut_node} | ${int1}
| | ... | ${tap1_NM_ip} | ${tap1_NM_mac}
| | And Add Linux Route | ${dut_node}
| | ... | ${tg_ip_address_GW} | ${prefix} | ${tap1_VPP_ip} | ${namespace1}
| | Then Send ICMP echo request and verify answer | ${tg_node}
| | ... | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac}
| | ... | ${tap1_NM_ip} | ${tg_ip_address}
