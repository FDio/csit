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
| Force Tags | 3_NODE_DOUBLE_LINK_TOPO | HW_ENV | VM_ENV | VPP_VM_ENV
| Test Setup | Func Test Setup
| Test Teardown | Func Test Teardown
| Documentation | *L2 bridge-domain test cases*
| ...
| ... | *[Top] Network Topologies:* TG=DUT=VM 3-node topology with VM
| ... | and double parallel links.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-ICMPv4 for L2 switching of
| ... | IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply
| ... | to all links.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with two L2 bridge-domains
| ... | (L2BD) switching combined with static MACs.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets
| ... | are sent in both directions by TG on links to DUT1 via VM; on
| ... | receive TG verifies packets for correctness and their IPv4 (IPv6)
| ... | src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2

| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2

*** Test Cases ***
| TC01: DUT with two L2BDs (static MACs) switches ICMPv4 between TG and VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv4-ICMPv4. [Cfg] On DUT1 configure \
| | ... | two L2BDs with static MACs, each with vhost-user i/f to local VM
| | ... | and i/f to TG; configure VM to loop pkts back betwen its two
| | ... | virtio i/fs. [Ver] Make TG verify ICMPv4 Echo Req pkts are
| | ... | switched thru DUT1 and VM in both directions and are correct on
| | ... | receive. [Ref]
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
| | ... | AND | Show vpp trace dump on all DUTs
| | ... | AND | Stop and Clear QEMU | ${dut_node} | ${vm_node}
| | ... | AND | Check VPP PID in Teardown

| TC02: DUT with two L2BDs (static MACs) switches ICMPv6 between TG and VM links
| | [Documentation]
| | ... | [Top] TG=DUT=VM. [Enc] Eth-IPv6-ICMPv6. [Cfg] On DUT1 configure \
| | ... | two L2BDs with static MACs, each with vhost-user i/f to local VM
| | ... | and i/f to TG; configure VM to loop pkts back betwen its two
| | ... | virtio i/fs. [Ver] Make TG verify ICMPv6 Echo Req pkts are
| | ... | switched thru DUT1 and VM in both directions and are correct on
| | ... | receive. [Ref]
| | ...
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ... | AND | Show vpp trace dump on all DUTs
| | ... | AND | Stop and Clear QEMU | ${dut_node} | ${vm_node}
| | ... | AND | Check VPP PID in Teardown
| | ...
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
