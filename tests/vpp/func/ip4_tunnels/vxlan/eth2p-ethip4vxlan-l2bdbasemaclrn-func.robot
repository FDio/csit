# Copyright (c) 2016 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/overlay/vxlan.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Resource | resources/libraries/robot/vm/qemu.robot
| Resource | resources/libraries/robot/vm/double_qemu_setup.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV | SKIP_VPP_PATCH
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *Bridge-domain with VXLAN test cases - IPv4*
| ...
| ... | *[Top] Network topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on
| ... | DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for L2 switching of IPv4.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) switching combined with MAC learning enabled;
| ... | VXLAN tunnels are configured between L2BDs on DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent
| ... | in both directions by TG on links to DUT1 and DUT2; on receive TG
| ... | verifies packets for correctness and their IPv4 src-addr, dst-addr
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC7348.

*** Variables ***
| ${vni_1}= | 23
| ${vni_2}= | 35

| ${bd_id1}= | 10
| ${bd_id2}= | 20
| ${bd_id3}= | 30
| ${shg1}= | 1
| ${shg2}= | 2

| ${ip4_addr1}= | 172.16.0.1
| ${ip4_addr2}= | 172.16.0.2
| ${ip4_prefix}= | 24

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2BD and VXLANoIPv4 tunnels switch ICMPv4 between TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv4-VXLAN-Eth-IPv4-ICMPv4 on \
| | ... | DUT1-DUT2; Eth-IPv4-ICMPv4 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure two i/fs into L2BD with MAC learning. [Ver] Make TG
| | ... | verify ICMPv4 Echo Req pkts are switched thru DUT1 and DUT2 in
| | ... | both directions and are correct on receive. [Ref] RFC7348.
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | ${dut1_to_dut2_name}= | Get interface name | ${dut1_node} | ${dut1_to_dut2}
| | ${dut2_to_dut1_name}= | Get interface name | ${dut2_node} | ${dut2_to_dut1}
| | And Configure IP addresses and neighbors on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2_name} | ${NONE} | ${dut2_node}
| | ... | ${dut2_to_dut1_name} | ${NONE}
| | ${dut1s_vxlan}= | When Create VXLAN interface     | ${dut1_node} | ${vni_1}
| |                 | ... | ${dut1s_ip_address} | ${dut2s_ip_address}
| | And Add interfaces to L2BD
| | ... | ${dut1_node} | ${bd_id1} | ${dut1_to_tg} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| |                 | ... | ${dut2s_ip_address} | ${dut1s_ip_address}
| | And Add interfaces to L2BD
| | ... | ${dut2_node} | ${bd_id1} | ${dut2_to_tg} | ${dut2s_vxlan}
| | Then Send ICMPv4 bidirectionally and verify received packets
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
