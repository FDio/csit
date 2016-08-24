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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.LispUtil
| Library | resources.libraries.python.ssh.SSH
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/lisp/lispgpe.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/ipv4_lispgpe_ipv4/ipv4_lispgpe_ipv4.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
| ... | VM_ENV | HW_ENV
| ...
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| ...           | AND          | VPP Show Errors | ${nodes['DUT1']}
| ...           | AND          | VPP Show Errors | ${nodes['DUT2']}
| ...
| Documentation | *ip4-lispgpe-ip4 encapsulation test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2,
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4
| ... | routing and static routes. LISPoIPv4 tunnel is configured between
| ... | DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are sent in
| ... | both directions by TG on links to DUT1 and DUT2; on receive
| ... | TG verifies packets for correctness and their IPv4 src-addr, dst-addr
| ... | and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using physical interfaces
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - phy2lisp \
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on received
| | ... | packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4} | ${prefix4}
| | And VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4}
| | And VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4}
| | And Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4}
| | ... | ${tg_to_dut2_mac}
| | And Add Arp On Dut | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4}
| | ... | ${tg_to_dut1_mac}
| | When Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC02: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using physical interfaces and VRF is enabled
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - vrf, phy2lisp \
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on received
| | ... | packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Setup VRF 1 on DUT 1
| | And Setup VRF 1 on DUT 2
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4} | ${prefix4}
| | And Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC03: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using vhost interfaces and VRF is enabled
| | [Documentation]
| | ... | Case: ip4-lispgpe-ip4 - vrf, virt2lisp \
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on
| | ... | TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.
| | ... | [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on received
| | ... | packets are correct.
| | ... | [Ref] RFC6830.
| | [Teardown] | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| | ... | AND | Show vpp trace dump on all DUTs
| | ... | AND | VPP Show Errors | ${nodes['DUT1']}
| | ... | AND | VPP Show Errors | ${nodes['DUT2']}
| | ... | AND | Qemu Teardown | ${dut1_node} | ${dut1_vm} | dut1_vm
| | ... | AND | Qemu Teardown | ${dut2_node} | ${dut2_vm} | dut2_vm
| | ...
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Vhosts are set on DUTs in 3-node topology
| | And Interfaces in 3-node path are up
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4} | ${prefix4}
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4} | ${prefix4}
| | ... | ${dut1_node} | ${vhost_if_11} | ${dut1_vhost_ip_1} | ${prefix4}
| | ... | ${dut1_node} | ${vhost_if_12} | ${dut1_vhost_ip_2} | ${prefix4}
| | ... | ${dut2_node} | ${vhost_if_21} | ${dut2_vhost_ip_1} | ${prefix4}
| | ... | ${dut2_node} | ${vhost_if_22} | ${dut2_vhost_ip_2} | ${prefix4}
| | And Set Interface State | ${dut1_node} | ${vhost_if_11} | up
| | And Set Interface State | ${dut1_node} | ${vhost_if_12} | up
| | And Set Interface State | ${dut2_node} | ${vhost_if_21} | up
| | And Set Interface State | ${dut2_node} | ${vhost_if_22} | up
| | And Setup QEMU Vhost and Run | ${dut1_node}
| | ... | ${sock11} | ${sock12} | ${vm1_ip_1} | ${vm1_ip_2} | ${prefix4}
| | ... | ${dut1_vm} | ${vm1_mac_id}
| | And Setup QEMU Vhost and Run | ${dut2_node}
| | ... | ${sock21} | ${sock22} | ${vm2_ip_1} | ${vm2_ip_2} | ${prefix4}
| | ... | ${dut2_vm} | ${vm2_mac_id}
| | When Setup VRF on DUT 1 with vhost
| | And Setup VRF on DUT 2 with vhost
| | And Set up LISP GPE topology
| | ... | ${dut1_node} | ${vhost_if_12} | ${NONE}
| | ... | ${dut2_node} | ${vhost_if_21} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

*** Keywords ***
| Setup VRF 1 on DUT 1
| | [Documentation]
| | ... | Set a FIB table on DUT1. DUT1-TG-IF1 and DUT1-DUT2-IF1 are assigned \
| | ... | to FIB table. IP addresses are subsequently set on interfaces, and ARP
| | ... | is set for neighbors. The last setting is route for each fib table.
| | ...
| | ${dut1_if1_idx}= | Get Interface SW Index
| | ... | ${dut1_node} | ${dut1_to_dut2}
| | ...
| | Add fib table | ${dut1_node}
| | ... | ${tg2_ip4} | ${prefix4} | ${dut1_fib_table}
| | ... | via ${dut2_to_dut1_ip4} sw_if_index ${dut1_if1_idx} multipath
| | ...
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_fib_table}
| | ...
| | Add Arp On Dut | ${dut1_node} | ${dut1_to_tg}
| | ... | ${tg1_ip4} | ${tg_to_dut1_mac} | vrf=${dut1_fib_table}
| | Add Arp On Dut | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${dut2_to_dut1_ip4} | ${dut2_to_dut1_mac} | vrf=${dut1_fib_table}
| | ...
| | Vpp Route Add | ${dut1_node} | ${tg2_ip4} | ${prefix4}
| | ... | ${dut2_to_dut1_ip4} | ${dut1_to_dut2} | vrf=${dut1_fib_table}

| Setup VRF 1 on DUT 2
| | [Documentation]
| | ... | Set a FIB table on DUT2. DUT2-TG-IF2 and DUT2-DUT1-IF2 are assigned \
| | ... | to FIB table. IP addresses are subsequently set on interfaces, and ARP
| | ... | is set for neighbors. The last setting is route for each fib table.
| | ...
| | ${dut2_if1_idx}= | Get Interface SW Index
| | ... | ${dut2_node} | ${dut2_to_dut1}
| | ...
| | Add fib table | ${dut2_node}
| | ... | ${tg1_ip4} | ${prefix4} | ${dut2_fib_table}
| | ... | via ${dut2_to_dut1_ip4} sw_if_index ${dut2_if1_idx} multipath
| | ...
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_fib_table}
| | ...
| | Add Arp On Dut | ${dut2_node} | ${dut2_to_tg}
| | ... | ${tg2_ip4} | ${tg_to_dut2_mac} | vrf=${dut2_fib_table}
| | Add Arp On Dut | ${dut2_node} | ${dut2_to_dut1}
| | ... | ${dut1_to_dut2_ip4} | ${dut1_to_dut2_mac} | vrf=${dut2_fib_table}
| | ...
| | Vpp Route Add | ${dut2_node} | ${tg1_ip4} | ${prefix4}
| | ... | ${dut1_to_dut2_ip4} | ${dut2_to_dut1} | vrf=${dut2_fib_table}

| Setup VRF on DUT 1 with vhost
| | [Documentation]
| | ... | Set a FIB table on DUT1. DUT1-TG-IF1 and DUT1-DUT2-IF1 are assigned \
| | ... | to FIB table. IP addresses are subsequently set on interfaces, and ARP
| | ... | is set for neighbors. The last setting is route for each fib table.
| | ... | Use vhost interface instead of a physical interface.
| | ...
| | ${dut1_if2_idx}= | Get Interface SW Index
| | ... | ${dut1_node} | ${dut1_to_dut2}
| | Add fib table | ${dut1_node}
| | ... | ${tg2_ip4} | ${prefix4} | ${dut1_fib_table}
| | ... | via ${dut1_vhost_ip_1} sw_if_index ${vhost_if_11} multipath
| | Add fib table | ${dut1_node}
| | ... | ${tg2_ip4} | ${prefix4} | ${dut1_fib_table2}
| | ... | via ${dut1_to_dut2_ip4} sw_if_index ${dut1_if2_idx} multipath
| | ...
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_tg} | ${dut1_fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${vhost_if_11} | ${dut1_fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${vhost_if_12} | ${dut1_fib_table2}
| | Assign Interface To Fib Table
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_fib_table2}
| | ...
| | Add Arp On Dut | ${dut1_node} | ${dut1_to_tg}
| | ... | ${tg1_ip4} | ${tg_to_dut1_mac} | vrf=${dut1_fib_table}
| | Add Arp On Dut | ${dut1_node} | ${vhost_if_11}
| | ... | ${vm1_ip_1} | ${vm1_vif1_mac} | vrf=${dut1_fib_table}
| | Add Arp On Dut | ${dut1_node} | ${vhost_if_12}
| | ... | ${vm1_ip_2} | ${vm1_vif2_mac} | vrf=${dut1_fib_table2}
| | Add Arp On Dut | ${dut1_node} | ${dut1_to_dut2}
| | ... | ${dut2_to_dut1_ip4} | ${dut2_to_dut1_mac} | vrf=${dut1_fib_table2}
| | ...
| | Vpp Route Add | ${dut1_node} | ${tg2_ip4} | ${prefix4}
| | ... | ${vm1_ip_1} | ${vhost_if_11} | vrf=${dut1_fib_table}
| | Vpp Route Add | ${dut1_node} | ${tg2_ip4} | ${prefix4}
| | ... | ${dut2_to_dut1_ip4} | ${{dut1_to_dut2} | vrf=${dut1_fib_table2}
| | Vpp Route Add | ${dut1_node} | ${tg1_ip4} | ${prefix4}
| | ... | ${vm1_ip_2} | ${vhost_if_12} | vrf=${dut1_fib_table2}
| | Vpp Route Add | ${dut1_node} | ${tg1_ip4} | ${prefix4}
| | ... | ${tg1_ip4} | ${dut1_to_tg} | vrf=${dut1_fib_table}

| Setup VRF on DUT 2 with vhost
| | [Documentation]
| | ... | Set a FIB table on DUT2. DUT2-TG-IF2 and DUT2-DUT1-IF2 are assigned \
| | ... | to FIB table. IP addresses are subsequently set on interfaces, and ARP
| | ... | is set for neighbors. The last setting is route for each fib table.
| | ... | Use vhost interface instead of a physical interface.
| | ...
| | ${dut2_if1_idx}= | Get Interface SW Index
| | ... | ${dut2_node} | ${dut2_to_dut1}
| | Add fib table | ${dut2_node}
| | ... | ${tg1_ip4} | ${prefix4} | ${dut2_fib_table}
| | ... | via ${dut2_vhost_ip_2} sw_if_index ${vhost_if_22} multipath
| | Add fib table | ${dut2_node}
| | ... | ${tg1_ip4} | ${prefix4} | ${dut2_fib_table2}
| | ... | via ${dut2_to_dut1_ip4} sw_if_index ${dut2_if1_idx} multipath
| | ...
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${vhost_if_21} | ${dut2_fib_table}
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${vhost_if_22} | ${dut2_fib_table2}
| | Assign Interface To Fib Table
| | ... | ${dut2_node} | ${dut2_to_tg} | ${dut2_fib_table2}
| | ...
| | Add Arp On Dut | ${dut2_node} | ${dut2_to_dut1}
| | ... | ${dut1_to_dut2_ip4} | ${dut1_to_dut2_mac} | vrf=${dut2_fib_table}
| | Add Arp On Dut | ${dut2_node} | ${vhost_if_21}
| | ... | ${vm2_ip_1} | ${vm2_vif1_mac} | vrf=${dut2_fib_table}
| | Add Arp On Dut | ${dut2_node} | ${vhost_if_22}
| | ... | ${vm2_ip_2} | ${vm2_vif2_mac} | vrf=${dut2_fib_table2}
| | Add Arp On Dut | ${dut2_node} | ${dut2_to_tg}
| | ... | ${tg2_ip4} | ${tg_to_dut2_mac} | vrf=${dut2_fib_table2}
| | ...
| | Vpp Route Add | ${dut2_node} | ${tg2_ip4} | ${prefix4}
| | ... | ${vm2_ip_1} | ${vhost_if_21} | vrf=${dut2_fib_table}
| | Vpp Route Add | ${dut2_node} | ${tg2_ip4} | ${prefix4}
| | ... | ${tg2_ip4} | ${dut2_to_tg} | vrf=${dut2_fib_table2}
| | Vpp Route Add | ${dut2_node} | ${tg1_ip4} | ${prefix4}
| | ... | ${vm2_ip_2} | ${vhost_if_22} | vrf=${dut2_fib_table2}
| | Vpp Route Add | ${dut2_node} | ${tg1_ip4} | ${prefix4}
| | ... | ${dut1_to_dut2_ip4} | ${dut2_to_dut1} | vrf=${dut2_fib_table}

| Vhosts are set on DUTs in 3-node topology
| | [Documentation]
| | ... | Create vhost interfaces on both DUTs. The keyword sets these test
| | ... | variables:
| | ... | ${vhost_if_11} - vhost interface index, DUT1, if1
| | ... | ${vhost_if_12} - vhost interface index, DUT1, if2
| | ... | ${vhost_if_21} - vhost interface index, DUT2, if1
| | ... | ${vhost_if_22} - vhost interface index, DUT2, if2
| | ... | ${vhost_if_11_mac} - vhost interface MAC address, DUT1, if1
| | ... | ${vhost_if_12_mac} - vhost interface MAC address, DUT2, if2
| | ... | ${vhost_if_21_mac} - vhost interface MAC address, DUT1, if1
| | ... | ${vhost_if_22_mac} - vhost interface MAC address, DUT2, if2
| | ...
| | ${vhost_if_11}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock11}
| | ${vhost_if_12}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock12}
| | ${vhost_if_21}= | Vpp Create Vhost User Interface | ${dut2_node} | ${sock21}
| | ${vhost_if_22}= | Vpp Create Vhost User Interface | ${dut2_node} | ${sock22}
| | ${vhost_if_11_mac}= | Vpp Get Interface MAC | ${dut1_node} | ${vhost_if_11}
| | ${vhost_if_12_mac}= | Vpp Get Interface MAC | ${dut1_node} | ${vhost_if_12}
| | ${vhost_if_21_mac}= | Vpp Get Interface MAC | ${dut2_node} | ${vhost_if_21}
| | ${vhost_if_22_mac}= | Vpp Get Interface MAC | ${dut2_node} | ${vhost_if_22}
| | Set test variable | ${vhost_if_11} | ${vhost_if_11}
| | Set test variable | ${vhost_if_12} | ${vhost_if_12}
| | Set test variable | ${vhost_if_21} | ${vhost_if_21}
| | Set test variable | ${vhost_if_22} | ${vhost_if_22}
| | Set test variable | ${vhost_if_11_mac} | ${vhost_if_11_mac}
| | Set test variable | ${vhost_if_12_mac} | ${vhost_if_12_mac}
| | Set test variable | ${vhost_if_21_mac} | ${vhost_if_21_mac}
| | Set test variable | ${vhost_if_22_mac} | ${vhost_if_22_mac}

| Setup QEMU Vhost and Run
| | [Documentation]
| | ... | Setup Qemu with 2 vhost-user interfaces and 1 namespace.
| | ... | Each call will create a different object instance.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where to setup qemu. Type: dict
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - ip1 - IP address for namespace 1. Type: string
| | ... | - ip2 - IP address for namespace 2. Type: string
| | ... | - prefix_length - IP prefix length. Type: int
| | ... | - qemu_name - Qemu instance name by which the object will be accessed.
| | ... | Type: string
| | ... | - mac_ID - MAC address ID used to differentiate qemu instances and
| | ... | namespaces assigned to them. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Setup QEMU Vhost And Run\| {nodes['DUT1']} \| /tmp/sock1 \
| | ... | \| /tmp/sock2 \| 16.0.0.1 \| 16.0.0.2 \
| | ... | \| 24 \| qemu_instance_1 \| 06 \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2}
| | ... | ${ip1} | ${ip2} | ${prefix_length}
| | ... | ${qemu_name} | ${mac_ID}
| | ...
| | Import Library | resources.libraries.python.QemuUtils \
| | ... | WITH NAME | ${qemu_name}
| | ${qemu_add_vhost}= | Replace Variables | ${qemu_name}.Qemu Add Vhost User If
| | ${qemu_set_node}= | Replace Variables | ${qemu_name}.Qemu Set Node
| | ${qemu_start}= | Replace Variables | ${qemu_name}.Qemu Start
| | Run keyword | ${qemu_add_vhost} | ${sock1} | mac=52:54:00:00:${mac_ID}:01
| | Run keyword | ${qemu_add_vhost} | ${sock2} | mac=52:54:00:00:${mac_ID}:02
| | Run keyword | ${qemu_set_node} | ${dut_node}
| | ${vm}= | Run keyword | ${qemu_start}
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Setup Network Namespace
| | ... | ${vm} | nmspace1 | ${vhost1} | ${ip1} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace2 | ${vhost2} | ${ip2} | ${prefix_length}
| | Set Test Variable | ${${qemu_name}} | ${vm}

| Qemu Teardown
| | [Documentation] | Stop specific qemu instance
| | ... | running on ${dut_node}, ${vm} is VM node info dictionary
| | ... | returned by qemu_start or None.
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dict
| | ... | - vm - VM node info dictionary. Type: string
| | ... | - qemu_name - Qemu instance by name. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Qemu Teardown \| ${node['DUT1']} \| ${vm} \| qemu_node_1 \|
| | ...
| | [Arguments] | ${dut_node} | ${vm} | ${qemu_name}
| | ${set_node}= | Replace Variables | ${qemu_name}.Qemu Set Node
| | ${sys_status}= | Replace Variables | ${qemu_name}.Qemu System Status
| | ${kill}= | Replace Variables | ${qemu_name}.Qemu Kill
| | ${sys_pd}= | Replace Variables | ${qemu_name}.Qemu System Powerdown
| | ${quit}= | Replace Variables | ${qemu_name}.Qemu Quit
| | ${clear_socks}= | Replace Variables | ${qemu_name}.Qemu Clear Socks
| | Run Keyword | ${set_node} | ${dut_node}
| | ${status} | ${value}= | Run Keyword And Ignore Error | ${sys_status}
| | Run Keyword If | "${status}" == "FAIL" | ${kill}
| | ... | ELSE IF | "${value}" == "running" | ${sys_pd}
| | ... | ELSE | ${quit}
| | Run Keyword | ${clear_socks}
| | Run Keyword If | ${vm} is not None | Disconnect | ${vm}
