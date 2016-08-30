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
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/traffic.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.ssh
| Library  | resources.libraries.python.IKEv2
| Library  | resources.libraries.python.VatExecutor.VatTerminal | ${nodes['DUT1']}
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | **
| ... | *[Top] Network Topologies:*
| ... |
| ... | *[Enc] Packet Encapsulations:*
| ... |
| ... | *[Cfg] DUT configuration:*
| ... |
| ... |
| ... | *[Ver] TG verification:*
| ... |
| ... |
| ... |
| ... | *[Ref] Applicable standard specifications:*
*** Variables ***
| ${dst_tun_ip}= | 10.0.0.5
| ${src_tun_ip}= | 10.0.0.10
| ${src_ip}= | 10.0.10.1
| ${dst_ip}= | 10.0.5.1
| ${prefix}= | 24

| ${PSK_pr_name}= | pr0
| ${PSK_auth_method}= | shared-key-mic
| ${PSK_auth_data}= | Vpp123
| ${PSK_id_type_loc}= | fqdn
| ${PSK_id_data_loc}= | vpp.home
| ${PSK_id_type_rem}= | fqdn
| ${PSK_id_data_rem}= | roadwarrior.vpn.example.com
| ${PSK_protocol_loc}= | 0
| ${PSK_protocol_rem}= | 0
| ${PSK_sport_loc}= | 0
| ${PSK_eport_loc}= | 65535
| ${PSK_saddr_loc}= | 10.0.5.0
| ${PSK_eaddr_loc}= | 10.0.5.255
| ${PSK_sport_rem}= | 0
| ${PSK_eport_rem}= | 65535
| ${PSK_saddr_rem}= | 10.0.10.0
| ${PSK_eaddr_rem}= | 10.0.10.255

| ${ID_TYPE_pr_name}= | pr1
| ${ID_TYPE_auth_method}= | shared-key-mic
| ${ID_TYPE_auth_data}= | Vpp123
| ${ID_TYPE_id_type_loc}= | ip4-addr
| ${ID_TYPE_id_data_loc}= | 192.168.123.91
| ${ID_TYPE_id_type_rem}= | ip4-addr
| ${ID_TYPE_id_data_rem}= | 192.168.123.90
| ${ID_TYPE_protocol_loc}= | 0
| ${ID_TYPE_protocol_rem}= | 0
| ${ID_TYPE_sport_loc}= | 0
| ${ID_TYPE_eport_loc}= | 65535
| ${ID_TYPE_saddr_loc}= | 10.0.5.0
| ${ID_TYPE_eaddr_loc}= | 10.0.5.255
| ${ID_TYPE_sport_rem}= | 0
| ${ID_TYPE_eport_rem}= | 65535
| ${ID_TYPE_saddr_rem}= | 10.0.10.0
| ${ID_TYPE_eaddr_rem}= | 10.0.10.255

*** Test Cases ***
| TC01: PSK Auth
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | Strongswan Ipsec | ${tg_node} | stop
| | ${dut_lo}= | Vpp Create Loopback | ${dut_node}
| | Set Interface State | ${dut_node} | ${dut_lo} | up
| | Set Interface Address | ${dut_node} | ${dut_lo} | 10.0.5.1 | 32
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | 10.0.0.5 | ${prefix}
| | ${tg_if}= | Get Interface Name | ${tg_node} | ${tg_to_dut_if1}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_tun_ip} | ${tg_to_dut_if1_mac}
| | And Set Linux Interface Arp | ${tg_node} | ${tg_if} | ${dst_tun_ip} | ${dut_to_tg_if1_mac}
| | Set Ikev2 Profile | ${dut_node} | ${PSK_pr_name}
| | Set Ikev2 Auth | ${dut_node} | ${PSK_pr_name} | ${PSK_auth_method} | ${PSK_auth_data}
| | Set Ikev2 ID | ${dut_node} | ${PSK_pr_name} | ${PSK_id_type_loc} | ${PSK_id_data_loc} | local
| | Set Ikev2 ID | ${dut_node} | ${PSK_pr_name} | ${PSK_id_type_rem} | ${PSK_id_data_rem} | remote
| | Set Ikev2 TS | ${dut_node} | ${PSK_pr_name} | ${PSK_protocol_loc} | ${PSK_sport_loc}
| | ... | ${PSK_eport_loc} | ${PSK_saddr_loc} | ${PSK_eaddr_loc} | local
| | Set Ikev2 TS | ${dut_node} | ${PSK_pr_name} | ${PSK_protocol_rem} | ${PSK_sport_rem}
| | ... | ${PSK_eport_rem} | ${PSK_saddr_rem} | ${PSK_eaddr_rem} | remote
| | Set Strongswan Config | ${tg_node} | right=${dst_tun_ip} | right_subnet=${dst_ip}/${prefix} |
| | ... | left=${src_tun_ip} | left_subnet=${src_ip}/${prefix}
| | Strongswan Ipsec | ${tg_node} | start
| | Set Ipsec If Up | ${dut_node} | 6 | admin-up
| | Set Ipsec Route | ${dut_node} | 10.0.10.0/24 | ipsec0
| | ${lSpi} | ${lEnc} | ${lAuth}= | Get VPP Ipsec Keys | ${dut_node} | local
| | ${rSpi} | ${rEnc} | ${rAuth}= | Get Vpp Ipsec Keys | ${dut_node} | remote
| | Send IKEv2 Packet | ${tg_node} | ${src_ip} | ${dst_ip} | ${src_tun_ip}
| | ... | ${dst_tun_ip} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1}
| | ... | ${rSpi} | ${rEnc} | ${rAuth}
| | ... | ${lSpi} | ${lEnc} | ${lAuth}


| TC02: ID type IPv4 address
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | Strongswan Ipsec | ${tg_node} | stop
| | ${dut_lo}= | Vpp Create Loopback | ${dut_node}
| | Set Interface State | ${dut_node} | ${dut_lo} | up
| | Set Interface Address | ${dut_node} | ${dut_lo} | 10.0.5.1 | 32
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | 10.0.0.5 | ${prefix}
| | ${tg_if}= | Get Interface Name | ${tg_node} | ${tg_to_dut_if1}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_tun_ip} | ${tg_to_dut_if1_mac}
| | And Set Linux Interface Arp | ${tg_node} | ${tg_if} | ${dst_tun_ip} | ${dut_to_tg_if1_mac}
| | Set Ikev2 Profile | ${dut_node} | ${ID_TYPE_pr_name}
| | Set Ikev2 Auth | ${dut_node} | ${ID_TYPE_pr_name} | ${ID_TYPE_auth_method} | ${ID_TYPE_auth_data}
| | Set Ikev2 ID | ${dut_node} | ${ID_TYPE_pr_name} | ${ID_TYPE_id_type_loc} | ${ID_TYPE_id_data_loc} | local
| | Set Ikev2 ID | ${dut_node} | ${ID_TYPE_pr_name} | ${ID_TYPE_id_type_rem} | ${ID_TYPE_id_data_rem} | remote
| | Set Ikev2 TS | ${dut_node} | ${ID_TYPE_pr_name} | ${ID_TYPE_protocol_loc} | ${ID_TYPE_sport_loc}
| | ... | ${ID_TYPE_eport_loc} | ${ID_TYPE_saddr_loc} | ${ID_TYPE_eaddr_loc} | local
| | Set Ikev2 TS | ${dut_node} | ${ID_TYPE_pr_name} | ${ID_TYPE_protocol_rem} | ${ID_TYPE_sport_rem}
| | ... | ${ID_TYPE_eport_rem} | ${ID_TYPE_saddr_rem} | ${ID_TYPE_eaddr_rem} | remote
| | Set Strongswan Config | ${tg_node} | right=${dst_tun_ip} | right_subnet=${dst_ip}/${prefix} | right_id=${ID_TYPE_id_data_loc}
| | ... | left=${src_tun_ip} | left_subnet=${src_ip}/${prefix} | left_id=${ID_TYPE_id_data_rem}
| | Strongswan Ipsec | ${tg_node} | start
| | Set Ipsec If Up | ${dut_node} | 6 | admin-up
| | Set Ipsec Route | ${dut_node} | 10.0.10.0/24 | ipsec0
| | ${lSpi} | ${lEnc} | ${lAuth}= | Get VPP Ipsec Keys | ${dut_node} | local
| | ${rSpi} | ${rEnc} | ${rAuth}= | Get Vpp Ipsec Keys | ${dut_node} | remote
| | Send IKEv2 Packet | ${tg_node} | ${src_ip} | ${dst_ip} | ${src_tun_ip}
| | ... | ${dst_tun_ip} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1}
| | ... | ${rSpi} | ${rEnc} | ${rAuth}
| | ... | ${lSpi} | ${lEnc} | ${lAuth}
