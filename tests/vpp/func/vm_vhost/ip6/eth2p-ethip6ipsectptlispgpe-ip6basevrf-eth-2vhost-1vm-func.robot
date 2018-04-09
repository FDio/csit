# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.LispUtil
| Library | resources.libraries.python.VPPUtil
| Library | resources.libraries.python.IPsecUtil
| Library | resources.libraries.python.VatJsonUtil
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.QemuUtils
| Library | resources.libraries.python.Routing
| Library | String
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/testing_path.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/crypto/ipsec.robot
| Resource | resources/libraries/robot/vm/qemu.robot
| Resource | resources/libraries/robot/overlay/lispgpe.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/ipsec_lispgpe/ipv6_via_ipsec_lispgpe_ipv6.py
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | LISP | SKIP_VPP_PATCH
| ...
| Test Setup | Run Keywords | Set up functional test
| ...        | AND          | Vpp All Ra Suppress Link Layer | ${nodes}
| ...
| Test Teardown | Tear down LISP functional test with QEMU | ${vm_node}
| ...
| Documentation | *IPv6 - ip6-ipsec-lispgpe-ip6 - main fib,
| ... | vrf (gpe_vni-to-vrf), phy2lisp, virt2lisp*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6,\
| ... | *[Cfg] DUT configuration:* Each DUT is configured with LISP and IPsec.\
| ... | IPsec is in transport mode. Tests cases are for IPsec configured both\
| ... | on RLOC interface or lisp_gpe0 interface.
| ... | *[Ver] TG verification:* Packet is send from TG(if1) across the DUT1\
| ... | via VM to DUT2 where it is forwarded to TG(if2).
| ... | *[Ref] Applicable standard specifications:* RFC6830, RFC4303.

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv6 over Vhost to LISP GPE tunnel using IPsec (transport) on RLOC Int.
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv6-IPSec-LISPGPE-IPv6-ICMP on DUT1-DUT2, Eth-IPv6-ICMP\
| | ... | on TG-DUTn.
| | ... | [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with\
| | ... | IPsec in between DUTS. Create Qemu vm on DUT1 and configure bridge\
| | ... | between two vhosts.
| | ... | [Ver] Case: ip6-ipsec-lispgpe-ip6 - main fib, virt2lisp\
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across\
| | ... | both DUTs and LISP GPE tunnel between them; verify IPv6 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830, RFC4303.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Setup 3-node Topology
| | And Setup Qemu DUT1
| | And Add IP Neighbors And Routes
| | And Configure LISP GPE
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | When Configure manual keyed connection for IPSec
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi}
| | ... | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip6} | ${tg2_ip6}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip6} | ${tg1_ip6}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC02: DUT1 and DUT2 route IPv6 over Vhost to LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int.
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2,\
| | ... | Eth-IPv6-ICMPv6 on TG-DUTn.
| | ... | [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with\
| | ... | IPsec in between DUTS.
| | ... | [Ver] Case: ip6-ipsec-lispgpe-ip6 - main fib, virt2lisp\
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across\
| | ... | both DUTs and LISP GPE tunnel between them; verify IPv6 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830, RFC4303.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Setup 3-node Topology
| | And Setup Qemu DUT1
| | And Add IP Neighbors And Routes
| | And Configure LISP GPE
| | ${lisp1_if_idx}= | resources.libraries.python.InterfaceUtil.get sw if index
| | ... | ${dut1_node} | ${lisp_gpe_int}
| | ${lisp2_if_idx}= | resources.libraries.python.InterfaceUtil.get sw if index
| | ... | ${dut2_node} | ${lisp_gpe_int}
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | When Configure manual keyed connection for IPSec
| | ... | ${dut1_node} | ${lisp1_if_idx} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut2_node} | ${lisp2_if_idx} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi}
| | ... | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6}
| | Then Send packet and verify headers
| | ... | ${tg_node} | ${tg1_ip6} | ${tg2_ip6}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send packet and verify headers
| | ... | ${tg_node} | ${tg2_ip6} | ${tg1_ip6}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

*** Keywords ***
| Setup 3-node Topology
| | [Documentation]
| | ... | Setup 3-node topology for this test suite. Set all physical\
| | ... | interfaces up and assing IP adresses to them. ...\
| | ...
| | ${dut2_fib_table}= | Set Variable | ${0}
| | Set Test Variable | ${dut2_fib_table}
| | Configure path in 3-node circular topology
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Add Fib Table | ${dut1_node} | ${fib_table_1} | ip6=${TRUE}
| | And Add Fib Table | ${dut1_node} | ${fib_table_2} | ip6=${TRUE}
| | And Add Fib Table | ${dut2_node} | ${dut2_fib_table} | ip6=${TRUE}
| | Assign Interface To Fib Table | ${dut1_node} | ${dut1_to_tg}
| | ... | ${fib_table_1} | ip6=${TRUE}
| | Assign Interface To Fib Table | ${dut2_node} | ${dut2_to_tg}
| | ... | ${dut2_fib_table} | ip6=${TRUE}
| | Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip6}
| | ... | ${prefix6}
| | Set Interface Address | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip6}
| | ... | ${prefix6}
| | Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip6}
| | ... | ${prefix6}
| | Set Interface Address | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip6}
| | ... | ${prefix6}
| | Set interfaces in 3-node circular topology up

| Configure LISP GPE
| | [Documentation]
| | ... | Configure LISP GPE on DUTs.
| | ...
| | Configure LISP GPE topology in 3-node circular topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ... | ${dut1_to_dut2_ip6_static_adjacency}
| | ... | ${dut2_to_dut1_ip6_static_adjacency}
| | ... | vni_table=${vni_table} | vrf_table=${fib_table_2}

| Add IP Neighbors And Routes
| | [Documentation]
| | ... | Add IP neighbors to physical interfaces on DUTs.
| | ...
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip6}
| | ... | ${tg_to_dut1_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_vhost1} | ${dut1_vhost2_ip6}
| | ... | ${dut1_vhost2_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip6}
| | ... | ${dut2_to_dut1_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_vhost2} | ${dut1_vhost1_ip6}
| | ... | ${dut1_vhost1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip6}
| | ... | ${tg_to_dut2_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip6}
| | ... | ${dut1_to_dut2_mac}
| | Vpp Route Add | ${dut1_node} | ${dut2_to_tg_ip6} | ${prefix6}
| | ... | gateway=${dut1_vhost2_ip6} | interface=${dut1_vhost1}
| | ... | vrf=${fib_table_1}
| | Vpp Route Add | ${dut1_node} | ${dut1_to_tg_ip6} | ${prefix6}
| | ... | gateway=${dut1_vhost1_ip6} | interface=${dut1_vhost2}
| | ... | vrf=${fib_table_2}

| Setup Qemu DUT1
| | [Documentation] | Setup Vhosts on DUT1 and setup IP to one of them. Setup \
| | ... | Qemu and bridge the vhosts.
| | ${dut1_vhost1}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock1}
| | Set Test Variable | ${dut1_vhost1}
| | ${dut1_vhost1_mac}= | Get Vhost User Mac By SW Index | ${dut1_node}
| | ... | ${dut1_vhost1}
| | Set Test Variable | ${dut1_vhost1_mac}
| | ${dut1_vhost2}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock2}
| | Set Test Variable | ${dut1_vhost2}
| | ${dut1_vhost2_mac}= | Get Vhost User Mac By SW Index | ${dut1_node}
| | ... | ${dut1_vhost2}
| | Set Test Variable | ${dut1_vhost2_mac}
| | Assign Interface To Fib Table | ${dut1_node} | ${dut1_vhost1}
| | ... | ${fib_table_1} | ip6=${TRUE}
| | Assign Interface To Fib Table | ${dut1_node} | ${dut1_vhost2}
| | ... | ${fib_table_2} | ip6=${TRUE}
| | Set Interface Address | ${dut1_node} | ${dut1_vhost1} | ${dut1_vhost1_ip6}
| | ... | ${prefix6}
| | Set Interface Address | ${dut1_node} | ${dut1_vhost2} | ${dut1_vhost2_ip6}
| | ... | ${prefix6}
| | Set Interface State | ${dut1_node} | ${dut1_vhost1} | up
| | Set Interface State | ${dut1_node} | ${dut1_vhost2} | up
| | Configure VM for vhost L2BD forwarding | ${dut1_node} | ${sock1} | ${sock2}
