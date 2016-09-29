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
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-GRE-IPv4-ICMPv4 on DUT1-DUT2,
| ... | Eth-IPv4-ICMPv4 on TG-DUTn for routing over GRE tunnel; Eth-IPv4-ICMPv4
| ... | on TG_if1-DUT, Eth-IPv4-GRE-IPv4-ICMPv4 on TG_if2_DUT for GREoIPv4
| ... | encapsulation and decapsulation verification.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with IPv4 routing
| ... | and static routes. GREoIPv4 tunnel is configured between DUT1 and DUT2.
| ... | *[Ver] TG verification:* Test ICMPv4 (or ICMPv6) Echo Request packets are
| ... | sent in both directions by TG on links to DUT1 and DUT2; GREoIPv4
| ... | encapsulation and decapsulation are verified separately by TG; on
| ... | receive TG verifies packets for correctness and their IPv4 (IPv6)
| ... | src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC2784.

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
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | 3_NODE_DOUBLE_LINK_TOPO | ipgre
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

| | And IPsec Generate Keys | ${encr_alg} | ${auth_alg}
| | VPP IPsec Add SAD Entry | ${dut1_node} | ${l_sa_id} | ${l_spi} | ${encr_alg}
| | ...                     | ${encr_key} | ${auth_alg} | ${auth_key}
| | VPP IPsec Add SAD Entry | ${dut1_node} | ${r_sa_id} | ${r_spi} | ${encr_alg}
| | ...                     | ${encr_key} | ${auth_alg} | ${auth_key}
| | VPP IPsec Add SAD Entry | ${dut2_node} | ${r_sa_id} | ${r_spi} | ${encr_alg}
| | ...                     | ${encr_key} | ${auth_alg} | ${auth_key}
| | VPP IPsec Add SAD Entry | ${dut2_node} | ${l_sa_id} | ${l_spi} | ${encr_alg}
| | ...                     | ${encr_key} | ${auth_alg} | ${auth_key}
| | ${ipsec_gpe_idx}= | add_ipsec_gre_interface | ${dut1_node} | ${dut1_to_dut2_ip} | ${dut2_to_dut1_ip} | ${l_sa_id} | ${r_sa_id} | up=${TRUE}
| | When Create L2 BD | ${dut1_node} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut1_node} | ${dut1_to_tg} | ${vpp_bd_id}
| | add_sw_if_index_to_l2_bd | ${dut1_node} | ${ipsec_gpe_idx} | ${vpp_bd_id}

| | ${ipsec_gpe_idx}= | add_ipsec_gre_interface | ${dut2_node} | ${dut2_to_dut1_ip} | ${dut1_to_dut2_ip} | ${r_sa_id} | ${l_sa_id} | up=${TRUE}
| | When Create L2 BD | ${dut2_node} | ${vpp_bd_id}
| | And Add Interface To L2 BD | ${dut2_node} | ${dut2_to_tg} | ${vpp_bd_id}
| | add_sw_if_index_to_l2_bd | ${dut2_node} | ${ipsec_gpe_idx} | ${vpp_bd_id}

| | Then Send Packet And Check Headers
| | ... | ${tg_node} | ${tg_dut1_ip} | ${tg_dut2_ip}
| | ... | ${tg_to_dut1} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ... | ${tg_to_dut2} | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
*** Keywords ***
