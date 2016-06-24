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
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *L2 bridge-domain test cases*
| ...
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes; TG-DUT1-DUT2-TG 3-node circular topology with
| ... | single links between nodes; TG=DUT1=DUT2=TG 3-node circular
| ... | topology with double parallel links and TG=DUT=VM 3-node topology
| ... | with VM and double parallel links.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply
| ... | to all links.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with L2
| ... | bridge-domain (L2BD) switching combined with static MACs; MAC
| ... | learning enabled and Split Horizon Groups (SHG) depending on
| ... | test case.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets
| ... | are sent in both directions by TG on links to DUT1 and DUT2; on
| ... | receive TG verifies packets for correctness and their IPv4 (IPv6)
| ... | src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2
| ${shg1}= | 3
| ${shg2}= | 4
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

*** Test Cases ***
| TC01: DUT reports active interfaces
| | [Documentation]
| | ... | [Top] TG=DUT1; TG-DUT1-DUT2-TG. [Enc] None. [Cfg] Discovered \
| | ... | active interfaces. [Ver] Report active interfaces on DUT. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | 3_NODE_SINGLE_LINK_TOPO
| | VPP reports interfaces on | ${nodes['DUT1']}

| TC02: DUT with L2BD (MAC learning) switch ICMPv4 between two TG links
| | [Documentation]
| | ... | [Top] TG=DUT1. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 configure \
| | ... | two i/fs into L2BD with MAC learning. [Ver] Make TG verify
| | ... | ICMPv4 Echo Req pkts are switched thru DUT1 in both directions
| | ... | and are correct on receive. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | When Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id1}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                     | ${tg_to_dut_if2}

| TC03: DUT1 and DUT2 with L2BD (MAC learning) switch between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 and DUT2 \
| | ... | configure two i/fs into L2BD with MAC learning. [Ver] Make TG
| | ... | verify ICMPv4 Echo Req pkts are switched thru DUT1 and DUT2 in
| | ... | both directions and are correct on receive. [Ref]
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_dut1}
| | ...                                     | ${bd_id2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut1}
| | ...                                          | ${tg_to_dut2}

| TC04: DUT1 and DUT2 with L2BD (static MACs) switch between two TG links
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 and \
| | ... | DUT2 configure two i/fs into L2BD with static MACs. [Ver] Make
| | ... | TG verify ICMPv4 Echo Req pkts are switched thru DUT1 and DUT2
| | ... | in both directions and are correct on receive. [Ref]
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | ...                                       | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut1}
| | ...                                                | ${dut1_node}
| | ...                                                | ${dut1_to_tg}
| | ...                                                | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut2}
| | ...                                                | ${dut1_node}
| | ...                                                | ${dut1_to_dut2}
| | ...                                                | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | ...                                      | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_dut1}
| | ...                                     | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut1}
| | ...                                                | ${dut2_node}
| | ...                                                | ${dut2_to_dut1}
| | ...                                                | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut2}
| | ...                                                | ${dut2_node}
| | ...                                                | ${dut2_to_tg}
| | ...                                                | ${bd_id2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut1}
| | ...                                          | ${tg_to_dut2}

| TC05: DUT1 and DUT2 with L2BD (MAC learn) and SHG switch between four TG links
| | [Documentation]
| | ... | [Top] TG=DUT1=DUT2=TG. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 and \
| | ... | DUT2 configure four i/fs into L2BD with MAC learning and the
| | ... | same SHG on i/fs towards TG. [Ver] Make TG verify ICMPv4 Echo
| | ... | Req pkts are switched thru DUT1 and DUT2 in both directions and
| | ... | are correct on receive; verify no pkts are switched thru SHG
| | ... | isolated interfaces. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Given Path for 3-node BD-SHG testing is set | ${nodes['TG']}
| | ...                                         | ${nodes['DUT1']}
| | ...                                         | ${nodes['DUT2']}
| | And Interfaces in 3-node BD-SHG testing are up
| | When Bridge domain on DUT node is created | ${dut1_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if1}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_tg_if2}
| | ...                                     | ${bd_id1} | ${shg1}
| | And Interface is added to bridge domain | ${dut1_node} | ${dut1_to_dut2}
| | ...                                     | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut2_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if1}
| | ...                                     | ${bd_id2} | ${shg2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_tg_if2}
| | ...                                     | ${bd_id2} | ${shg2}
| | And Interface is added to bridge domain | ${dut2_node} | ${dut2_to_dut1}
| | ...                                     | ${bd_id2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                          | ${tg_to_dut1_if1}
| | ...                                          | ${tg_to_dut2_if1}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if1}
| | ...                                         | ${tg_to_dut2_if2}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if1}
| | And Send and receive ICMPv4 bidirectionally | ${tg_node}
| | ...                                         | ${tg_to_dut1_if2}
| | ...                                         | ${tg_to_dut2_if2}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ...                              | Send and receive ICMPv4 bidirectionally
| | | ...                            | ${tg_node} | ${tg_to_dut1_if1}
| | | ...                            | ${tg_to_dut1_if2}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ...                              | Send and receive ICMPv4 bidirectionally
| | | ...                            | ${tg_node} | ${tg_to_dut2_if1}
| | | ...                            | ${tg_to_dut2_if2}

| TC06: DUT with two L2BDs (MAC learn) switches ICMPv4 between TG and VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 configure \
| | ... | two L2BDs with MAC learning, each with vhost-user i/f to local
| | ... | VM and i/f to TG; configure VM to loop pkts back betwen its two
| | ... | virtio i/fs. [Ver] Make TG verify ICMPv4 Echo Req pkts are
| | ... | switched thru DUT1 and VM in both directions and are correct on
| | ... | receive. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if1}
| | ...                                     | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if2}
| | ...                                     | ${bd_id2}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Show vpp trace dump on all DUTs
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}

| TC07: DUT with two L2BDs (MAC learn) switches ICMPv6 between TG and VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv6-ICMPv6. [Cfg] On DUT1 configure \
| | ... | two L2BDs with MAC learning, each with vhost-user i/f to local
| | ... | VM and i/f to TG; configure VM to loop pkts back betwen its two
| | ... | virtio i/fs. [Ver] Make TG verify ICMPv6 Echo Req pkts are
| | ... | switched thru DUT1 and VM in both directions and are correct on
| | ... | receive. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if1}
| | ...                                     | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if2}
| | ...                                     | ${bd_id2}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv6 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Show vpp trace dump on all DUTs
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}

| TC08: DUT with two L2BDs (static MACs) switches ICMPv4 between TG and VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 configure \
| | ... | two L2BDs with static MACs, each with vhost-user i/f to local VM
| | ... | and i/f to TG; configure VM to loop pkts back betwen its two
| | ... | virtio i/fs. [Ver] Make TG verify ICMPv4 Echo Req pkts are
| | ... | switched thru DUT1 and VM in both directions and are correct on
| | ... | receive. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | ...                                      | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if1}
| | ...                                     | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if1}
| | ...                                                | ${dut_node}
| | ...                                                | ${dut_to_tg_if1}
| | ...                                                | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if2}
| | ...                                                | ${dut_node}
| | ...                                                | ${vhost_if1}
| | ...                                                | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id2}
| | ...                                      | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if2}
| | ...                                     | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if2}
| | ...                                                | ${dut_node}
| | ...                                                | ${dut_to_tg_if2}
| | ...                                                | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if1}
| | ...                                                | ${dut_node}
| | ...                                                | ${vhost_if2}
| | ...                                                | ${bd_id2}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv4 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Show vpp trace dump on all DUTs
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}

| TC09: DUT with two L2BDs (static MACs) switches ICMPv6 between TG and VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv6-ICMPv6. [Cfg] On DUT1 configure \
| | ... | two L2BDs with static MACs, each with vhost-user i/f to local VM
| | ... | and i/f to TG; configure VM to loop pkts back betwen its two
| | ... | virtio i/fs. [Ver] Make TG verify ICMPv6 Echo Req pkts are
| | ... | switched thru DUT1 and VM in both directions and are correct on
| | ... | receive. [Ref]
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | When VPP Vhost interfaces for L2BD forwarding are setup | ${dut_node}
| | ...                                                     | ${sock1}
| | ...                                                     | ${sock2}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id1}
| | ...                                      | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if1}
| | ...                                     | ${bd_id1}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if1}
| | ...                                     | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if1}
| | ...                                                | ${dut_node}
| | ...                                                | ${dut_to_tg_if1}
| | ...                                                | ${bd_id1}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if2}
| | ...                                                | ${dut_node}
| | ...                                                | ${vhost_if1}
| | ...                                                | ${bd_id1}
| | And Bridge domain on DUT node is created | ${dut_node} | ${bd_id2}
| | ...                                      | learn=${FALSE}
| | And Interface is added to bridge domain | ${dut_node} | ${dut_to_tg_if2}
| | ...                                     | ${bd_id2}
| | And Interface is added to bridge domain | ${dut_node} | ${vhost_if2}
| | ...                                     | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if2}
| | ...                                                | ${dut_node}
| | ...                                                | ${dut_to_tg_if2}
| | ...                                                | ${bd_id2}
| | And Destination port is added to L2FIB on DUT node | ${tg_node}
| | ...                                                | ${tg_to_dut_if1}
| | ...                                                | ${dut_node}
| | ...                                                | ${vhost_if2}
| | ...                                                | ${bd_id2}
| | And VM for Vhost L2BD forwarding is setup | ${dut_node} | ${sock1}
| | ...                                       | ${sock2}
| | Then Send and receive ICMPv6 bidirectionally | ${tg_node} | ${tg_to_dut_if1}
| | ...                                          | ${tg_to_dut_if2}
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ...        | AND          | Show vpp trace dump on all DUTs
| | ...        | AND          | Stop and Clear QEMU | ${dut_node} | ${vm_node}
