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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Library | resources.libraries.python.NodePath
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | HW_ENV | VM_ENV
| Test Setup | Setup all DUTs before test
| Suite Setup | Setup all TGs before traffic script
| Documentation | *L2 cross-connect test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology with
| ... | single links between nodes; TG=DUT1=DUT2=TG 3-node circular topology
| ... | with double parallel links and TG=DUT=VM 3-node topology with VM and
| ... | double parallel links.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of IPv4;
| ... | Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | cross-connect (L2XC) switching.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets are
| ... | sent in both directions by TG on links to DUT1 and DUT2; on receive TG
| ... | verifies packets for correctness and their IPv4 (IPv6) src-addr,
| ... | dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

*** Test Cases ***
| TC01: DUT1 and DUT2 with L2XC switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 and \
| | ... | DUT2 configure L2 cross-connect (L2XC), each with one interface
| | ... | to TG and one Ethernet interface towards the other DUT. [Ver]
| | ... | Make TG send ICMPv4 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref]
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And L2 setup xconnect on DUT
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send and receive ICMPv4 bidirectionally
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
| | [Teardown] | Run Keyword | Show vpp trace dump on all DUTs

| TC02: DUT1 and DUT2 with L2XC switch ICMPv6 between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv6-ICMPv6. [Cfg] On DUT1 and \
| | ... | DUT2 configure L2 cross-connect (L2XC), each with one interface
| | ... | to TG and one Ethernet interface towards the other DUT. [Ver]
| | ... | Make TG send ICMPv6 Echo Req in both directions between two of
| | ... | its interfaces to be switched by DUT1 and DUT2; verify all
| | ... | packets are received. [Ref]
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And L2 setup xconnect on DUT
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_dut2}
| | And L2 setup xconnect on DUT
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_tg}
| | When All Vpp Interfaces Ready Wait | ${nodes}
| | Then Send and receive ICMPv6 bidirectionally
| | ... | ${tg_node} | ${tg_to_dut1} | ${tg_to_dut2}
| | [Teardown] | Run Keyword | Show vpp trace dump on all DUTs

| TC03: DUT with two L2XCs switches ICMPv4 between TG and local VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT configure \
| | ... | two L2 cross-connects (L2XC), each with one untagged interface
| | ... | to TG and untagged i/f to local VM over vhost-user. [Ver] Make
| | ... | TG send ICMPv4 Echo Reqs in both directions between two of its
| | ... | i/fs to be switched by DUT to and from VM; verify all packets
| | ... | are received. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And L2 Setup Xconnect on DUT | ${dut_node} | ${dut_to_tg_if1} | ${vhost_if1}
| | And L2 Setup Xconnect on DUT | ${dut_node} | ${dut_to_tg_if2} | ${vhost_if2}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}
| | ...        | AND          | Show vpp trace dump on all DUTs

| TC04: DUT with two L2XCs switches ICMPv6 between TG and local VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv6-ICMPv6. [Cfg] On DUT configure \
| | ... | two L2 cross-connects (L2XC), each with one untagged i/f to TG
| | ... | and untagged i/f to local VM over vhost-user. [Ver] Make TG send
| | ... | ICMPv6 Echo Reqs in both directions between two of its i/fs to
| | ... | be switched by DUT to and from VM; verify all packets are
| | ... | received. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And L2 Setup Xconnect on DUT | ${dut_node} | ${dut_to_tg_if1} | ${vhost_if1}
| | And L2 Setup Xconnect on DUT | ${dut_node} | ${dut_to_tg_if2} | ${vhost_if2}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv6 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}
| | ...        | AND          | Show vpp trace dump on all DUTs

