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
| Library | resources.libraries.python.IPv6Setup
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Test Setup | Set up functional test
| Test Teardown | Tear down functional test
| Documentation | *Bridge-domain with VXLAN test cases - IPv6*
| ...
| ... | *[Top] Network topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet encapsulations:* Eth-IPv6-VXLAN-Eth-IPv6-ICMPv6 on
| ... | DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for L2 switching of IPv6.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) switching combined with MAC learning enabled;
| ... | VXLAN tunnels are configured between L2BDs on DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv6 Echo Request packets are sent
| ... | in both directions by TG on links to DUT1 and DUT2; on receive TG
| ... | verifies packets for correctness and their IPv6 src-addr, dst-addr
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC7348.

*** Variables ***
| ${vni_1}= | 23

| ${bd_id1}= | 10

| ${ip6_addr1}= | 3ffe:64::1
| ${ip6_addr2}= | 3ffe:64::2
| ${ip6_prefix}= | 64

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2BD and VXLANoIPv6 tunnels switch ICMPv6 between TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG.[Enc] Eth-IPv6-VXLAN-Eth-IPv6-ICMPv6 on \
| | ... | DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn. [Cfg] On DUT1 and DUT2
| | ... | configure L2 bridge-domain (MAC learning enabled), each with one
| | ... | interface to TG and one VXLAN tunnel interface towards the other
| | ... | DUT. [Ver] Make TG send ICMPv6 Echo Req between two of its
| | ... | interfaces to be switched by DUT1 and DUT2; verify all packets
| | ... | are received. [Ref] RFC7348.
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set interfaces in 3-node circular topology up
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${ip6_addr1}
| | ...                       | ${ip6_prefix}
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${ip6_addr2}
| | ...                       | ${ip6_prefix}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${ip6_addr2}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${ip6_addr1}
| | And Vpp All RA Suppress Link Layer | ${nodes}
| | ${dut1s_vxlan}= | When Create VXLAN interface | ${dut1_node} | ${vni_1}
| | | ...                                         | ${ip6_addr1} | ${ip6_addr2}
| | And Add interfaces to L2BD | ${dut1_node} | ${bd_id1}
| | ...                            | ${dut1_to_tg} | ${dut1s_vxlan}
| | ${dut2s_vxlan}= | And Create VXLAN interface | ${dut2_node} | ${vni_1}
| | | ...                                        | ${ip6_addr2} | ${ip6_addr1}
| | And Add interfaces to L2BD | ${dut2_node} | ${bd_id1}
| | ...                            | ${dut2_to_tg} | ${dut2s_vxlan}
| | Then Send ICMPv6 bidirectionally and verify received packets
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
