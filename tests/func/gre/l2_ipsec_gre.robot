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
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/gre.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/ipsec.robot
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.L2Util
| Library  | resources.libraries.python.Trace
| Force Tags | VM_ENV | HW_ENV
| Test Setup | Run Keywords
| ... | Setup all DUTs before test | AND
| ... | Setup all TGs before traffic script
| Test Teardown | Run Keywords
| ... | Show Packet Trace on All DUTs | ${nodes} | AND
| ... | Show vpp trace dump on all DUTs
| Documentation | *GREoIPv4 test cases*
| ...
| ... | *[Top] Network Topologies:* TG=DUT1 2-node topology with two links
| ... | between nodes; TG-DUT1-DUT2-TG 3-node circular topology with single
| ... | links between nodes.
| ... | *[Enc] Packet Encapsulations:* IPv4-ESP-GRE-Eth-IPv4-ICMP
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPSec SA,
| ... | Bridge domain, and ARPs. IPSec-GRE tunnel is configured
| ... | between DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 Echo Request packets are
| ... | sent in both directions by TG on links to DUT1 and DUT2; IPSec-GRE
| ... | encapsulation and decapsulation are verified separately by TG; on
| ... | receive TG verifies packets for correctness and their IPv4
| ... | src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC2784, RFC4303.

*** Variables ***
| ${tg_dut1_ip}= | 192.168.1.1
| ${tg_dut2_ip}= | 192.168.1.2
| ${dut2_to_dut1_ip}= | 192.168.2.2
| ${dut1_to_dut2_ip}= | 192.168.2.1
| ${prefix}= | 24
| ${l_sa_id}= | 10
| ${r_sa_id}= | 20
| ${r_spi}= | 1000
| ${l_spi}= | 1001
| ${vpp_bd_id}= | 10

*** Test Cases ***
| TC01: L2 traffic over IPSec-GRE interface
| | [Documentation]
| | ... | [Top] TG-DUT1-DUT2-TG.
| | ... | [Ref] RFC4303, RFC2784.
| | ... | [Cfg] On DUT1 and DUT2 configure IPSec-GRE tunnel. Then ARPs are
| | ... | configured for neighbors along with Bridge Domain.
| | ... | [Ver] Packet is send from TG which is then transfered from BD to
| | ... | IPSec-GRE int, encapsulated, and sent to DUT2. On DUT2 the packet
| | ... | is decapsulated and sent to TG where is validated.
| | ...
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Path for 3-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And IP addresses are set on interfaces
| | ... | ${dut1_node} | ${dut1_to_dut2} | ${dut1_to_dut2_ip} | ${prefix}
| | ... | ${dut2_node} | ${dut2_to_dut1} | ${dut2_to_dut1_ip} | ${prefix}
| | Add IP Neighbor | ${dut1_node} | ${dut1_to_dut2} | ${dut2_to_dut1_ip}
| | ... | ${dut2_to_dut1_mac}
| | Add IP Neighbor | ${dut2_node} | ${dut2_to_dut1} | ${dut1_to_dut2_ip}
| | ... | ${dut1_to_dut2_mac}
| | When IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | And VPP IPsec Add SAD Entry | ${dut1_node} | ${l_sa_id} | ${l_spi}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key}
| | And VPP IPsec Add SAD Entry | ${dut1_node} | ${r_sa_id} | ${r_spi}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key}
| | And VPP IPsec Add SAD Entry | ${dut2_node} | ${r_sa_id} | ${r_spi}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key}
| | And VPP IPsec Add SAD Entry | ${dut2_node} | ${l_sa_id} | ${l_spi}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key}
| | ${ipsec_gpe_idx}= | And Add IPSec GRE Interface | ${dut1_node}
| | ... | ${dut1_to_dut2_ip} | ${dut2_to_dut1_ip}
| | ... | ${l_sa_id} | ${r_sa_id} | up=${TRUE}
| | And Create L2 BD | ${dut1_node} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut1_node} | ${dut1_to_tg} | ${vpp_bd_id}
| | Add SW If Index To L2 Bd | ${dut1_node} | ${ipsec_gpe_idx} | ${vpp_bd_id}
| | ${ipsec_gpe_idx}= | And Add IPSec GRE Interface | ${dut2_node}
| | ... | ${dut2_to_dut1_ip} | ${dut1_to_dut2_ip}
| | ... | ${r_sa_id} | ${l_sa_id} | up=${TRUE}
| | And Create L2 BD | ${dut2_node} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut2_node} | ${dut2_to_tg} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut2_node} | ${ipsec_gpe_idx} | ${vpp_bd_id}
| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg_dut1_ip} | ${tg_dut2_ip}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | And Send Packet And Check Headers
| | ... | ${tg_node} | ${tg_dut2_ip} | ${tg_dut1_ip}
| | ... | ${tg_to_dut2} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}

| TC02: Encapsulate And Encrypt Packet And Check
| | [Documentation]
| | ... | [Top] TG=DUT1.
| | ... | [Ref] RFC4303, RFC2784.
| | ... | [Cfg] On DUT1 is configured IPSec-GRE tunnel. Then ARPs are
| | ... | configured for neighbors along with Bridge Domain.
| | ... | [Ver] Packet is send from TG which is then transfered from BD to
| | ... | IPSec-GRE int, encapsulated, and sent back to TG. On TG the packet
| | ... | is validated with scapy.
| | ...
| | [Tags] | 2_NODE_DOUBLE_LINK_TOPO
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA1 96
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | And IP addresses are set on interfaces
| | ... | ${dut_node} | ${dut_to_tg_if2} | ${dut1_to_dut2_ip} | ${prefix}
| | Add IP Neighbor | ${dut_node} | ${dut_to_tg_if2} | ${dut2_to_dut1_ip}
| | ... | ${tg_to_dut_if2_mac}
| | When IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | And VPP IPsec Add SAD Entry | ${dut_node} | ${l_sa_id} | ${l_spi}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key}
| | And VPP IPsec Add SAD Entry | ${dut_node} | ${r_sa_id} | ${r_spi}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key}
| | ${ipsec_gpe_idx}= | And Add IPSec GRE Interface | ${dut_node}
| | ... | ${dut1_to_dut2_ip} | ${dut2_to_dut1_ip}
| | ... | ${l_sa_id} | ${r_sa_id} | up=${TRUE}
| | And Create L2 BD | ${dut_node} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut_node} | ${dut_to_tg_if1} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut_node} | ${ipsec_gpe_idx} | ${vpp_bd_id}
| | Then Send Packet And Check IPSec-GRE | ${tg_node}
| | ... | ${tg_dut1_ip} | ${tg_to_dut_if1_mac} | ${tg_to_dut_if1}
| | ... | ${tg_dut2_ip} | ${dut_to_tg_if1_mac} | ${tg_to_dut_if2}
| | ... | ${dut1_to_dut2_ip} | ${dut_to_tg_if1_mac}
| | ... | ${dut2_to_dut1_ip} | ${tg_to_dut_if2_mac}
| | ... | ${l_spi} | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key}

