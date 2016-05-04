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
| Documentation | Test Lisp static remote mapping topology.
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/lisp/lisp_static_mapping.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.IPv4Util.IPv4Util
# import additional Lisp settings from resource file
| Variables | tests/suites/lisp/resources/lisp_static_mapping.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO
| ... | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}

*** Test Cases ***
| VPP can pass IPv4 bidirectionally through LISP
| | [Documentation] | Test IP4 Lisp remote static mapping.
| | ...             | Set IP4 lisp topology and check if packet passes through
| | ...             | Lisp topology.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And   Interfaces in 3-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut1_node} | ${dut1_to_dut2}
| |       ... | ${dut1_to_dut2_ip4} | ${prefix4}
| |       ... | ${dut1_node} | ${dut1_to_tg}
| |       ... | ${dut1_to_tg_ip4} | ${prefix4}
| |       ... | ${dut2_node} | ${dut2_to_dut1}
| |       ... | ${dut2_to_dut1_ip4} | ${prefix4}
| |       ... | ${dut2_node} | ${dut2_to_tg}
| |       ... | ${dut2_to_tg_ip4} | ${prefix4}
| | And   VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4}
| | And   VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4}
| | And   Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4}
| |       ... | ${tg_to_dut2_mac}
| | And   Add Arp On Dut | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4}
| |       ... | ${tg_to_dut1_mac}
| | When Set up Lisp topology
| |      ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| |      ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| |      ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| |      ... | ${dut1_ip4_static_mapping} | ${dut2_ip4_static_mapping}
| | Then Send Packet And Check Headers
| |      ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| |      ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| |      ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| |      ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| |      ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| |      ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| VPP can pass IPv6 bidirectionally through LISP
| | [Documentation] | Test IP6 Lisp remote static mapping.
| | ...             | Set IP6 lisp topology and check if packet passes through
| | ...             | Lisp topology.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And   Interfaces in 3-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut1_node} | ${dut1_to_dut2}
| |       ... | ${dut1_to_dut2_ip6} | ${prefix6}
| |       ... | ${dut1_node} | ${dut1_to_tg}
| |       ... | ${dut1_to_tg_ip6} | ${prefix6}
| |       ... | ${dut2_node} | ${dut2_to_dut1}
| |       ... | ${dut2_to_dut1_ip6} | ${prefix6}
| |       ... | ${dut2_node} | ${dut2_to_tg}
| |       ... | ${dut2_to_tg_ip6} | ${prefix6}
| | And   VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip6}
| | And   VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip6}
| | And   Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip6}
| |       ... | ${tg_to_dut2_mac}
| | And   Add Arp On Dut | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip6}
| |       ... | ${tg_to_dut1_mac}
| | When Set up Lisp topology
| |      ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| |      ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| |      ... | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| |      ... | ${dut1_ip6_static_mapping} | ${dut2_ip6_static_mapping}
| | Then Send Packet And Check Headers
| |      ... | ${tg_node} | ${tg1_ip6} | ${tg2_ip6}
| |      ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| |      ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| |      ... | ${tg_node} | ${tg2_ip6} | ${tg1_ip6}
| |      ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| |      ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| VPP can pass IPv4 over IPv6 bidirectionally through LISP
| | [Documentation] | Test IP4 over IP6 in Lisp remote static mapping.
| | ...             | Set IP6 topology and check if the IP4 packet
| | ...             | passes through IP6 Lisp topology.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And   Interfaces in 3-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut1_node} | ${dut1_to_dut2}
| |       ... | ${dut1_to_dut2_ip4o6} | ${dut_prefix4o6}
| |       ... | ${dut1_node} | ${dut1_to_tg}
| |       ... | ${dut1_to_tg_ip4o6} | ${tg_prefix4o6}
| |       ... | ${dut2_node} | ${dut2_to_dut1}
| |       ... | ${dut2_to_dut1_ip4o6} | ${dut_prefix4o6}
| |       ... | ${dut2_node} | ${dut2_to_tg}
| |       ... | ${dut2_to_tg_ip4o6} | ${tg_prefix4o6}
| | And   VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4o6}
| | And   VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4o6}
| | And   Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4o6}
| |       ... | ${tg_to_dut2_mac}
| | And   Add Arp On Dut | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4o6}
| |       ... | ${tg_to_dut1_mac}
| | When Set up Lisp topology
| |      ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| |      ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| |      ... | ${duts_locator_set} | ${dut1_ip4o6_eid} | ${dut2_ip4o6_eid}
| |      ... | ${dut1_ip4o6_static_mapping} | ${dut2_ip4o6_static_mapping}
| | Then Send Packet And Check Headers
| |      ... | ${tg_node} | ${tg1_ip4o6} | ${tg2_ip4o6}
| |      ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| |      ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| |      ... | ${tg_node} | ${tg2_ip4o6} | ${tg1_ip4o6}
| |      ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| |      ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| VPP can pass IPv6 over IPv4 bidirectionally through LISP
| | [Documentation] | Test IP6 over IP4 in Lisp remote static mapping.
| | ...             | Set IP4 topology and check if the IP6 packet
| | ...             | passes through IP4 Lisp topology.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And   Interfaces in 3-node path are up
| | And   IP addresses are set on interfaces
| |       ... | ${dut1_node} | ${dut1_to_dut2}
| |       ... | ${dut1_to_dut2_ip6o4} | ${dut_prefix6o4}
| |       ... | ${dut1_node} | ${dut1_to_tg}
| |       ... | ${dut1_to_tg_ip6o4} | ${tg_prefix6o4}
| |       ... | ${dut2_node} | ${dut2_to_dut1}
| |       ... | ${dut2_to_dut1_ip6o4} | ${dut_prefix6o4}
| |       ... | ${dut2_node} | ${dut2_to_tg}
| |       ... | ${dut2_to_tg_ip6o4} | ${tg_prefix6o4}
| | And   VPP IP Probe | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip6o4}
| | And   VPP IP Probe | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip6o4}
| | And   Add Arp On Dut | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip6o4}
| |       ... | ${tg_to_dut2_mac}
| | And   Add Arp On Dut | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip6o4}
| |       ... | ${tg_to_dut1_mac}
| | When Set up Lisp topology
| |      ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| |      ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| |      ... | ${duts_locator_set} | ${dut1_ip6o4_eid} | ${dut2_ip6o4_eid}
| |      ... | ${dut1_ip6o4_static_mapping} | ${dut2_ip6o4_static_mapping}
| | Then Send Packet And Check Headers
| |      ... | ${tg_node} | ${tg1_ip6o4} | ${tg2_ip6o4}
| |      ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| |      ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| |      ... | ${tg_node} | ${tg2_ip6o4} | ${tg1_ip6o4}
| |      ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| |      ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
