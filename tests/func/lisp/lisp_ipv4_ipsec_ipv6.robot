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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.LispUtil
| Library | resources.libraries.python.IPsecUtil
| Library | resources.libraries.python.VatJsonUtil
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.VhostUser
| Library | resources.libraries.python.QemuUtils
| Library | String
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/ipsec.robot
| Resource | resources/libraries/robot/qemu.robot
| Resource | resources/libraries/robot/lisp/lispgpe.robot
| Resource | resources/libraries/robot/bridge_domain.robot
# Import configuration and test data:
| Variables | resources/test_data/lisp/ipv4_lispgpe_ipv6/ipv4_lispgpe_ipv6.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | LISP | EXPECTED_FAILING
| ...
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| ...           | AND          | VPP Show Errors | ${nodes['DUT1']}
| ...           | AND          | VPP Show Errors | ${nodes['DUT2']}
| ...
| Documentation | *IPv6 - ip6-ipsec-lispgpe-ip6 - main fib, vrf (gpe_vni-to-vrf), lisp2lisp*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:*Eth-IPv6-LISPGPE-IPSec-IPv6-ICMPv6,
| ... | Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6
| ... | *[Cfg] DUT configuration:* Each DUT is configured with LISP and IPsec.
| ... | IPsec is in transport mode. Tests cases are for IPsec configured both on
| ... | RLOC interface or lisp_gpe0 interface.
| ... | *[Ver] TG verification:* Packet is send from TG(if1) across the DUT1 to
| ... | DUT2 where it is forwarded to TG(if2).
| ... | *[Ref] Applicable standard specifications:* RFC6830.

*** Variables ***
| ${dut2_spi}= | ${1000}
| ${dut1_spi}= | ${1001}
| ${ESP_PROTO}= | ${50}
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2
| ${bid_1}= | 10

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on RLOC Int.
| | [Documentation]
| | ... | Case: ip4-lispgpe-ipsec-ip6 - main fib, phy2lisp \
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-LISPGPE-IPSec-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv4-ICMP
| | ... | on TG-DUTn.
| | ... | [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with
| | ... | IPsec in between DUTS.
| | ... | [Ver] Make TG send ICMPv6 Echo Req between its interfaces across both
| | ... | DUTs and LISP GPE tunnel between them; verify IPv6 headers on received
| | ... | packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Setup Topology And Lisp
| | And IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip6} | ${dut2_to_dut1_ip6}
| | And VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi}
| | ... | ${dut2_to_dut1_ip6} | ${dut1_to_dut2_ip6}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

| TC02: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using IPsec (transport) lisp_gpe0 Int.
| | [Documentation]
| | ... | Case: ip6-ipsec-lispgpe-ip6 - main fib, virt2lisp \
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv6-LISPGPE-IPSec-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6
| | ... | on TG-DUTn.
| | ... | [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with
| | ... | IPsec in between DUTS.
| | ... | [Ver] Make TG send ICMPv6 Echo Req between its interfaces across both
| | ... | DUTs and LISP GPE tunnel between them; verify IPv6 headers on received
| | ... | packets are correct.
| | ... | [Ref] RFC6830.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Setup Topology And Lisp
| | And Setup Qemu DUT1
| | ${lisp_if_idx}= | resources.libraries.python.InterfaceUtil.get sw if index
| | ... | ${dut1_node} | lisp_gpe0
| | And IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut1_node} | ${lisp_if_idx} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi} | ${tg1_ip4}
| | ... | ${tg2_ip4}
| | And VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut2_node} | ${lisp_if_idx} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi} | ${tg2_ip4}
| | ... | ${tg1_ip4}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip4} | ${tg2_ip4}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dst_vhost_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip4} | ${tg1_ip4}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}
| | Stop and Clear QEMU | ${dut1_node} | ${vm_node}

*** Keywords ***
| Setup Topology And Lisp
| | Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Interfaces in 3-node path are up
| | Vpp Set If IPv6 Addr | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip6}
| | ... | ${prefix6}
| | Vpp Set If IPv6 Addr | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip6}
| | ... | ${prefix6}
| | Vpp Set If IPv6 Addr | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip4}
| | ... | ${prefix4}
| | Vpp Set If IPv6 Addr | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip6}
| | ... | ${prefix6}
| | Vpp Set If IPv6 Addr | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip4}
| | ... | ${prefix4}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip4}
| | ... | ${tg_to_dut2_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip6}
| | ... | ${dut2_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip6}
| | ... | ${dut1_to_dut2_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip4}
| | ... | ${tg_to_dut1_mac}

| | Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid} | ${dut2_ip4_eid}
| | ... | ${dut1_to_dut2_ip_static_adjacency}
| | ... | ${dut2_to_dut1_ip_static_adjacency}

| Setup Qemu DUT1
| | ${vhost1}= | And Vpp Create Vhost User Interface
| | ... | ${dut1_node} | ${sock1}
| | Set Interface State | ${dut1_node} | ${vhost1} | up
| | ${vhost2}= | And Vpp Create Vhost User Interface
| | ... | ${dut1_node} | ${sock2}
| | Set Interface State | ${dut1_node} | ${vhost2} | up
| | Vpp Set If IPv6 Addr | ${dut1_node} | ${vhost1} | ${tg1_ip4}
| | ... | ${prefix4}
| | Bridge domain on DUT node is created | ${dut1_node} | ${bid_1} | learn=${TRUE}
| | Interface is added to bridge domain | ${dut1_node}
| | ... | ${dut1_to_tg} | ${bid_1} | 0
| | Interface is added to bridge domain | ${dut1_node}
| | ... | ${vhost1} | ${bid_1} | 0
| | ${vhost_mac}= | get vhost user mac by sw index | ${dut1_node} | ${vhost2}
| | Set test variable | ${dst_vhost_mac} | ${vhost_mac}
| | Run keyword | Qemu Add Vhost User If | ${sock1} | mac=52:54:00:00:01:01
| | Run keyword | Qemu Add Vhost User If | ${sock2} | mac=52:54:00:00:02:02
| | Run keyword | Qemu Set Node | ${dut1_node}
| | ${vm}= | Qemu Start
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | Linux Add Bridge | ${vm} | br0 | ${vhost1} | ${vhost2}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Interface State | ${vm} | br0 | up | if_type=name
| | Set test variable | ${vm_node} | ${vm}
