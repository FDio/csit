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
| Library | resources.libraries.python.VPPUtil
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
| Variables | resources/test_data/lisp/ipv6_lispgpe_ipv4/ipv6_lispgpe_ipsec_ipv4.py
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | LISP
| ...
| Test Setup | Func Test Setup
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ... | AND | Show VAT History On All DUTs | ${nodes}
| ... | AND | Show Vpp Settings | ${nodes['DUT1']}
| ... | AND | Show Vpp Settings | ${nodes['DUT2']}
| ... | AND | Check VPP PID in Teardown
| ...
| Documentation | *IPv6 - ip4-ipsec-lispgpe-ip6 - main fib, vrf, virt2lisp,\
| ... | phy2lisp*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-LISPGPE-IPSec-IPv6-ICMP,\
| ... | Eth-IPv4-IPSec-LISPGPE-IPv6-ICMP
| ... | *[Cfg] DUT configuration:* Each DUT is configured with LISP and IPsec.\
| ... | IPsec is in transport mode. Tests cases are for IPsec configured both\
| ... | on RLOC interface or lisp_gpe0 interface.
| ... | *[Ver] TG verification:* Packet is send from TG(if1) across the DUT1 to\
| ... | DUT2 where it is forwarded to TG(if2).
| ... | *[Ref] Applicable standard specifications:* RFC6830, RFC4303.

*** Test Cases ***
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using physical interfaces and VRF is enabled
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Enc] Eth-IPv4-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2,\
| | ... | Eth-IPv6-ICMPv6, on TG-DUTn.
| | ... | [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with\
| | ... | IPsec in between DUTS.
| | ... | [Ver] Case: ip4-ipsec-lispgpe-ip6 - vrf, phy2lisp
| | ... | Make TG send ICMPv6 Echo Req between its interfaces across both\
| | ... | DUTs and LISP GPE tunnel between them; verify IPv6 headers on\
| | ... | received packets are correct.
| | ... | [Ref] RFC6830, RFC4303.
| | ...
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | Assign Interface To Fib Table | ${dut1_node}
| | ... | ${dut1_to_tg} | ${fib_table_1} | ip6=${TRUE}
| | Assign Interface To Fib Table | ${dut2_node}
| | ... | ${dut2_to_tg} | ${fib_table_1} | ip6=${TRUE}
| | And IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | When VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut1_spi} | ${dut2_spi}
| | ... | ${dut1_to_dut2_ip4} | ${dut2_to_dut1_ip4}
| | And VPP Setup IPsec Manual Keyed Connection
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${encr_alg} | ${encr_key}
| | ... | ${auth_alg} | ${auth_key} | ${dut2_spi} | ${dut1_spi}
| | ... | ${dut2_to_dut1_ip4} | ${dut1_to_dut2_ip4}
| | Setup Topology And Lisp | ${fib_table_1} | ${dut1_dut2_vni}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg1_ip6} | ${tg2_ip6}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${dut2_to_tg_mac} | ${tg_to_dut2_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg2_ip6} | ${tg1_ip6}
| | ... | ${tg_to_dut2} | ${tg_to_dut2_mac} | ${dut2_to_tg_mac}
| | ... | ${tg_to_dut1} | ${dut1_to_tg_mac} | ${tg_to_dut1_mac}

*** Keywords ***
| Setup Topology And Lisp
| | [Documentation] | Setup IPs and neighbors for interfaces on DUT1 and DUT2\
| | ... | and then setup LISP.
| | [Arguments] | ${fib_table}=0 | ${vni_table}=0 | ${ip6}=${FALSE}
| | Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Interfaces in 3-node path are up
| | Vpp Set If IPv6 Addr | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip4}
| | ... | ${prefix4}
| | Vpp Set If IPv6 Addr | ${dut1_node} | ${dut1_to_tg} | ${dut1_to_tg_ip6}
| | ... | ${prefix6}
| | Vpp Set If IPv6 Addr | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip4}
| | ... | ${prefix4}
| | Vpp Set If IPv6 Addr | ${dut2_node} | ${dut2_to_tg} | ${dut2_to_tg_ip6}
| | ... | ${prefix6}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_tg} | ${tg2_ip6}
| | ... | ${tg_to_dut2_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip4}
| | ... | ${dut2_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip4}
| | ... | ${dut1_to_dut2_mac}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_tg} | ${tg1_ip6}
| | ... | ${tg_to_dut1_mac}
| | Set up LISP GPE topology
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${NONE}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip6_eid} | ${dut2_ip6_eid}
| | ... | ${dut1_to_dut2_ip_static_adjacency}
| | ... | ${dut2_to_dut1_ip_static_adjacency}
| | ... | ${vni_table} | ${fib_table}
