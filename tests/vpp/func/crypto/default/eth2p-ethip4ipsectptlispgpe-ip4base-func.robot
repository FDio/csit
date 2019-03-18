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
| Library | resources.libraries.python.LispUtil
| Library | resources.libraries.python.VPPUtil
| Library | resources.libraries.python.IPsecUtil
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/crypto/ipsec.robot
| Resource | resources/libraries/robot/vm/qemu.robot
| Resource | resources/libraries/robot/overlay/lispgpe.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/overlay/l2lisp.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/ipv4_ipsec_lispgpe_ipv4/ipv4_ipsec_lispgpe_ipv4.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | LISP | SKIP_VPP_PATCH
| ...
| Test Setup | Set up functional test
| ...
| Test Teardown | Tear down LISP functional test
| ...
| Documentation | *IPv4-ip4-ipsec-lispgpe-ip4 - main fib, vrf (gpe_vni-to-vrf)*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* ICMPv4-IPv4-IPSec-LISPGPE-IPv4-ICMPv4.
| ... | *[Cfg] DUT configuration:* Each DUT is configured with LISP and IPsec.\
| ... | IPsec is in transport mode. Tests cases are for IPsec configured both\
| ... | on RLOC interface or lisp_gpe0 interface.
| ... | *[Ver] TG verification:* Packet is send from TG(if1) across the DUT1 to\
| ... | DUT2 where it is forwarded to TG(if2).
| ... | *[Ref] Applicable standard specifications:* RFC6830, RFC4303.

*** Variables ***
| ${dut2_spi}= | ${1000}
| ${dut1_spi}= | ${1001}

| ${ESP_PROTO}= | ${50}

| ${bid}= | 10

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on RLOC Int.
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2,\
| | ... | Eth-IPv4-ICMPv4 on TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with\
| | ... | IPsec in between DUTs.
| | ... | [Ver] Case: ip4-lispgpe-ipsec-ip4 - main fib
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830, RFC4303.
| | ...
| | [Tags] | EXPECTED_FAILING
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Setup 3-node Topology
| | And Add IP Neighbors
| | And Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | When Configure manual keyed connection for IPSec
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip4} | ${dut2_to_dut1_ip4}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi}
| | ... | ${dut2_to_dut1_ip4} | ${dut1_to_dut2_ip4}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC02: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) lisp_gpe0 Int.
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2,\
| | ... | Eth-IPv4-ICMPv4 on TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with\
| | ... | IPsec in between DUTs.
| | ... | [Ver] Case: ip4-ipsec-lispgpe-ip4 - main fib
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830, RFC4303.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Setup 3-node Topology
| | And Add IP Neighbors
| | And Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | ${lisp_if_idx}= | resources.libraries.python.InterfaceUtil.Get sw if index
| | ... | ${dut1_node} | lisp_gpe0.0
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | When Configure manual keyed connection for IPSec
| | ... | ${dut1_node} | ${lisp_if_idx} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi} | ${tg1_ip4}
| | ... | ${tg2_ip4}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut2_node} | ${lisp_if_idx} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi} | ${tg2_ip4}
| | ... | ${tg1_ip4}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC03: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on RLOC Int and VRF on EID is enabled.
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2,\
| | ... | Eth-IPv4-ICMPv4 on TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with\
| | ... | IPsec in between DUTs.
| | ... | [Ver] Case: ip4-lispgpe-ipsec-ip4 - vrf, main fib
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830, RFC4303.
| | ...
| | [Tags] | EXPECTED_FAILING
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Setup 3-node Topology | ${fib_table_1}
| | And Add IP Neighbors
| | When Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | ... | ${dut1_dut2_vni} | ${fib_table_1}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip4} | ${dut2_to_dut1_ip4}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi}
| | ... | ${dut2_to_dut1_ip4} | ${dut1_to_dut2_ip4}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC04: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int and VRF is enabled.
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2,\
| | ... | Eth-IPv4-ICMPv4 on TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with\
| | ... | IPsec in between DUTs.
| | ... | [Ver] Case: ip4-ipsec-lispgpe-ip4 - vrf, main fib
| | ... | Make TG send ICMPv4 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv4 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830, RFC4303.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Setup 3-node Topology | ${fib_table_1}
| | And Add IP Neighbors
| | And Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip4_static_adjacency}
| | ... | ${dut2_to_dut1_ip4_static_adjacency}
| | ... | ${dut1_dut2_vni} | ${fib_table_1}
| | When Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | ${lisp_if_idx}= | resources.libraries.python.InterfaceUtil.Get sw if index
| | ... | ${dut1_node} | lisp_gpe0.0
| | And Configure manual keyed connection for IPSec
| | ... | ${dut1_node} | ${lisp_if_idx} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi} | ${tg1_ip4}
| | ... | ${tg2_ip4}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut2_node} | ${lisp_if_idx} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi} | ${tg2_ip4}
| | ... | ${tg1_ip4}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

*** Keywords ***
| Setup 3-node Topology
| | [Documentation]
| | ... | Setup 3-node topology for this test suite. Set all physical\
| | ... | interfaces up and assing IP adresses to them.\
| | ... | You can specify fib table ID where the DUT-TG interfaces assign to.\
| | ... | Default is 0.
| | ...
| | [Arguments] | ${fib_table}=0
| | Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Set interfaces in 3-node circular topology up
| | And Add Fib Table | ${dut1_node} | ${fib_table}
| | Assign Interface To Fib Table | ${dut1_node}
| | ... | ${dut1_to_tg} | ${fib_table}
| | And Add Fib Table | ${dut2_node} | ${fib_table}
| | Assign Interface To Fib Table | ${dut2_node}
| | ... | ${dut2_to_tg} | ${fib_table}
| | Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4}
| | ... | ${prefix4}
| | Set Interface Address | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4}
| | ... | ${prefix4}
| | Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4}
| | ... | ${prefix4}
| | Set Interface Address | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4}
| | ... | ${prefix4}

| Add IP Neighbors
| | [Documentation]
| | ... | Add IP neighbors to physical interfaces on DUTs.
| | ...
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4}
| | ... | ${tg_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4}
| | ... | ${tg_to_dut2_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4}
| | ... | ${dut2_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4}
| | ... | ${dut1_to_dut2_mac}
