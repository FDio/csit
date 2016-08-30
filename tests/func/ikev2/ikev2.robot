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

| ${strict_policy}= | no
| ${ike}= | aes256-sha1-modp2048!
| ${esp}= | aes192-sha1-noesn!
| ${mobike}= | no
| ${key_exchange}= | ikev2
| ${ike_lifetime}= | 24h
| ${lifetime}= | 24h

| ${ID_IP_pr_name}= | pr0
| ${ID_IP_auth_method}= | shared-key-mic
| ${ID_IP_auth_data}= | Vpp123
| ${ID_IP_id_type_loc}= | ip4-addr
| ${ID_IP_id_data_loc}= | 192.168.100.1
| ${ID_IP_id_type_rem}= | ip4-addr
| ${ID_IP_id_data_rem}= | 192.168.200.1
| ${ID_IP_protocol_loc}= | 0
| ${ID_IP_protocol_rem}= | 0
| ${ID_IP_sport_loc}= | 0
| ${ID_IP_eport_loc}= | 65535
| ${ID_IP_saddr_loc}= | 10.0.5.0
| ${ID_IP_eaddr_loc}= | 10.0.5.255
| ${ID_IP_sport_rem}= | 0
| ${ID_IP_eport_rem}= | 65535
| ${ID_IP_saddr_rem}= | 10.0.10.0
| ${ID_IP_eaddr_rem}= | 10.0.10.255
| ${ID_IP_right_auth}= | psk
| ${ID_IP_left_auth}= | psk
| ${ID_IP_right_id}= | 192.168.100.1
| ${ID_IP_left_id}= | 192.168.200.1

| ${ID_RFC_pr_name}= | pr0
| ${ID_RFC_auth_method}= | shared-key-mic
| ${ID_RFC_auth_data}= | Vpp123
| ${ID_RFC_id_type_loc}= | rfc822
| ${ID_RFC_id_data_loc}= | vpp@cisco.com
| ${ID_RFC_id_type_rem}= | rfc822
| ${ID_RFC_id_data_rem}= | roadwarrior@cisco.com
| ${ID_RFC_protocol_loc}= | 0
| ${ID_RFC_protocol_rem}= | 0
| ${ID_RFC_sport_loc}= | 0
| ${ID_RFC_eport_loc}= | 65535
| ${ID_RFC_saddr_loc}= | 10.0.5.0
| ${ID_RFC_eaddr_loc}= | 10.0.5.255
| ${ID_RFC_sport_rem}= | 0
| ${ID_RFC_eport_rem}= | 65535
| ${ID_RFC_saddr_rem}= | 10.0.10.0
| ${ID_RFC_eaddr_rem}= | 10.0.10.255
| ${ID_RFC_right_auth}= | psk
| ${ID_RFC_left_auth}= | psk
| ${ID_RFC_right_id}= | vpp@cisco.com
| ${ID_RFC_left_id}= | roadwarrior@cisco.com

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
| ${PSK_right_auth}= | psk
| ${PSK_left_auth}= | psk
| ${PSK_right_id}= | @vpp.home
| ${PSK_left_id}= | @roadwarrior.vpn.example.com

| ${ID_KEY_pr_name}= | pr0
| ${ID_KEY_auth_method}= | shared-key-mic
| ${ID_KEY_auth_data}= | Vpp123
| ${ID_KEY_id_type_loc}= | key-id
| ${ID_KEY_id_data_loc}= | 0xab12cd34
| ${ID_KEY_id_type_rem}= | key-id
| ${ID_KEY_id_data_rem}= | 0x12ab34cd
| ${ID_KEY_protocol_loc}= | 0
| ${ID_KEY_protocol_rem}= | 0
| ${ID_KEY_sport_loc}= | 0
| ${ID_KEY_eport_loc}= | 65535
| ${ID_KEY_saddr_loc}= | 10.0.5.0
| ${ID_KEY_eaddr_loc}= | 10.0.5.255
| ${ID_KEY_sport_rem}= | 0
| ${ID_KEY_eport_rem}= | 65535
| ${ID_KEY_saddr_rem}= | 10.0.10.0
| ${ID_KEY_eaddr_rem}= | 10.0.10.255
| ${ID_KEY_right_auth}= | psk
| ${ID_KEY_left_auth}= | psk
| ${ID_KEY_right_id}= | @#ab12cd34
| ${ID_KEY_left_id}= | @#12ab34cd

| ${RSA_pr_name}= | pr0
| ${RSA_auth_method}= | cert-file
| ${RSA_auth_data}= | /home/localadmin/certs/server-cert.pem
| ${RSA_id_type_loc}= | fqdn
| ${RSA_id_data_loc}= | vpp.home
| ${RSA_id_type_rem}= | fqdn
| ${RSA_id_data_rem}= | roadwarrior.vpn.example.com
| ${RSA_protocol_loc}= | 0
| ${RSA_protocol_rem}= | 0
| ${RSA_sport_loc}= | 0
| ${RSA_eport_loc}= | 65535
| ${RSA_saddr_loc}= | 10.0.5.0
| ${RSA_eaddr_loc}= | 10.0.5.255
| ${RSA_sport_rem}= | 0
| ${RSA_eport_rem}= | 65535
| ${RSA_saddr_rem}= | 10.0.10.0
| ${RSA_eaddr_rem}= | 10.0.10.255
| ${RSA_right_auth}= | pubkey
| ${RSA_left_auth}= | pubkey
| ${RSA_right_id}= | @vpp.home
| ${RSA_left_id}= | @roadwarrior.vpn.example.com
| ${RSA_secret}= | : RSA server-key.pem
| ${RSA_cacert}= | ca-cert.pem



*** Test Cases ***

| TC01: PSK Auth
| | [Template] | IKEV2 Setup
| | ${strict_policy} | ${ike} | ${esp} | ${mobike} | ${key_exchange}
| | ... | ${ike_lifetime} | ${lifetime} | ${PSK_pr_name}
| | ... | ${PSK_auth_method} | ${PSK_auth_data} | ${PSK_id_type_loc}
| | ... | ${PSK_id_data_loc} | ${PSK_id_type_rem} | ${PSK_id_data_rem}
| | ... | ${PSK_protocol_loc} | ${PSK_protocol_rem} | ${PSK_sport_loc}
| | ... | ${PSK_eport_loc} | ${PSK_saddr_loc} | ${PSK_eaddr_loc}
| | ... | ${PSK_sport_rem} | ${PSK_eport_rem} | ${PSK_saddr_rem}
| | ... | ${PSK_eaddr_rem} | ${PSK_right_auth} | ${PSK_left_auth}
| | ... | ${PSK_right_id} | ${PSK_left_id}

| TC02: ID type IPv4 address
| | [Template] | IKEV2 Setup
| | ${strict_policy} | ${ike} | ${esp} | ${mobike} | ${key_exchange}
| | ... | ${ike_lifetime} | ${lifetime} | ${ID_IP_pr_name}
| | ... | ${ID_IP_auth_method} | ${ID_IP_auth_data} | ${ID_IP_id_type_loc}
| | ... | ${ID_IP_id_data_loc} | ${ID_IP_id_type_rem} | ${ID_IP_id_data_rem}
| | ... | ${ID_IP_protocol_loc} | ${ID_IP_protocol_rem} | ${ID_IP_sport_loc}
| | ... | ${ID_IP_eport_loc} | ${ID_IP_saddr_loc} | ${ID_IP_eaddr_loc}
| | ... | ${ID_IP_sport_rem} | ${ID_IP_eport_rem} | ${ID_IP_saddr_rem}
| | ... | ${ID_IP_eaddr_rem} | ${ID_IP_right_auth} | ${ID_IP_left_auth}
| | ... | ${ID_IP_right_id} | ${ID_IP_left_id}

| TC03: ID type email address
| | [Template] | IKEV2 Setup
| | ${strict_policy} | ${ike} | ${esp} | ${mobike} | ${key_exchange}
| | ... | ${ike_lifetime} | ${lifetime} | ${ID_RFC_pr_name}
| | ... | ${ID_RFC_auth_method} | ${ID_RFC_auth_data} | ${ID_RFC_id_type_loc}
| | ... | ${ID_RFC_id_data_loc} | ${ID_RFC_id_type_rem} | ${ID_RFC_id_data_rem}
| | ... | ${ID_RFC_protocol_loc} | ${ID_RFC_protocol_rem} | ${ID_RFC_sport_loc}
| | ... | ${ID_RFC_eport_loc} | ${ID_RFC_saddr_loc} | ${ID_RFC_eaddr_loc}
| | ... | ${ID_RFC_sport_rem} | ${ID_RFC_eport_rem} | ${ID_RFC_saddr_rem}
| | ... | ${ID_RFC_eaddr_rem} | ${ID_RFC_right_auth} | ${ID_RFC_left_auth}
| | ... | ${ID_RFC_right_id} | ${ID_RFC_left_id}

| TC04: ID type key-id
| | [Template] | IKEV2 Setup
| | ${strict_policy} | ${ike} | ${esp} | ${mobike} | ${key_exchange}
| | ... | ${ike_lifetime} | ${lifetime} | ${ID_KEY_pr_name}
| | ... | ${ID_KEY_auth_method} | ${ID_KEY_auth_data} | ${ID_KEY_id_type_loc}
| | ... | ${ID_KEY_id_data_loc} | ${ID_KEY_id_type_rem} | ${ID_KEY_id_data_rem}
| | ... | ${ID_KEY_protocol_loc} | ${ID_KEY_protocol_rem} | ${ID_KEY_sport_loc}
| | ... | ${ID_KEY_eport_loc} | ${ID_KEY_saddr_loc} | ${ID_KEY_eaddr_loc}
| | ... | ${ID_KEY_sport_rem} | ${ID_KEY_eport_rem} | ${ID_KEY_saddr_rem}
| | ... | ${ID_KEY_eaddr_rem} | ${ID_KEY_right_auth} | ${ID_KEY_left_auth}
| | ... | ${ID_KEY_right_id} | ${ID_KEY_left_id}

#Test case with RSA key needs clarification. Not used for now.
#| TC05: RSA key auth
#| | [Template] | IKEV2 Setup
#| | ${strict_policy} | ${ike} | ${esp} | ${mobike} | ${key_exchange}
#| | ... | ${ike_lifetime} | ${lifetime} | ${RSA_pr_name}
#| | ... | ${RSA_auth_method} | ${RSA_auth_data} | ${RSA_id_type_loc}
#| | ... | ${RSA_id_data_loc} | ${RSA_id_type_rem} | ${RSA_id_data_rem}
#| | ... | ${RSA_protocol_loc} | ${RSA_protocol_rem} | ${RSA_sport_loc}
#| | ... | ${RSA_eport_loc} | ${RSA_saddr_loc} | ${RSA_eaddr_loc}
#| | ... | ${RSA_sport_rem} | ${RSA_eport_rem} | ${RSA_saddr_rem}
#| | ... | ${RSA_eaddr_rem} | ${RSA_right_auth} | ${RSA_left_auth}
#| | ... | ${RSA_right_id} | ${RSA_left_id} | ${RSA_cacert} | ${RSA_secret}

*** Keywords ***
| IKEV2 Setup
| | [Arguments] | ${str_pol} | ${ik} | ${es} | ${mbk}
| | ... | ${k_exchange} | ${ike_lt} | ${lt}
| | ... | ${pr_name} | ${auth_method} | ${auth_data}
| | ... | ${id_type_loc} | ${id_data_loc} | ${id_type_rem}
| | ... | ${id_data_rem} | ${protocol_loc} | ${protocol_rem}
| | ... | ${sport_loc} | ${eport_loc} | ${saddr_loc}
| | ... | ${eaddr_loc} | ${sport_rem} | ${eport_rem}
| | ... | ${saddr_rem} | ${eaddr_rem} | ${right_auth} | ${left_auth}
| | ... | ${right_id} | ${left_id} | ${cacert}= | ${secrets}=: PSK "Vpp123"
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | Strongswan Ipsec | ${tg_node} | stop
| | ${dut_lo}= | Vpp Create Loopback | ${dut_node}
| | Set Interface State | ${dut_node} | ${dut_lo} | up
| | Set Interface Address | ${dut_node} | ${dut_lo} | ${dst_ip} | ${prefix}
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${dst_tun_ip} | ${prefix}
| | ${tg_if}= | Get Interface Name | ${tg_node} | ${tg_to_dut_if1}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_tun_ip} | ${tg_to_dut_if1_mac}
| | And Set Linux Interface Arp | ${tg_node} | ${tg_if} | ${dst_tun_ip}
| | ... | ${dut_to_tg_if1_mac}
| | Set Ikev2 Profile | ${dut_node} | ${pr_name}
| | Set Ikev2 Auth | ${dut_node} | ${pr_name} | ${auth_method} | ${auth_data}
| | Set Ikev2 ID | ${dut_node} | ${pr_name} | ${id_type_loc} | ${id_data_loc}
| | ... | local
| | Set Ikev2 ID | ${dut_node} | ${pr_name} | ${id_type_rem} | ${id_data_rem}
| | ... | remote
| | Set Ikev2 TS | ${dut_node} | ${pr_name} | ${protocol_loc} | ${sport_loc}
| | ... | ${eport_loc} | ${saddr_loc} | ${eaddr_loc} | local
| | Set Ikev2 TS | ${dut_node} | ${pr_name} | ${protocol_rem} | ${sport_rem}
| | ... | ${eport_rem} | ${saddr_rem} | ${eaddr_rem} | remote
| | Set Strongswan Config | ${tg_node} | strict_policy=${str_pol} | ike=${ik}
| | ... | esp=${es} | mobike=${mbk} | keyexchange=${k_exchange}
| | ... | ikelifetime=${ike_lt} | lifetime=${lt} | right=${dst_tun_ip}
| | ... | right_subnet=${dst_ip}/${prefix} | right_auth=${right_auth}
| | ... | right_id=${right_id} | left=${src_tun_ip}
| | ... | left_subnet=${src_ip}/${prefix} | left_auth=${left_auth}
| | ... | left_id=${left_id} | auto=start | cacert=${cacert}
| | Set Strongswan Secrets | ${tg_node} | ${secrets}
| | Strongswan Ipsec | ${tg_node} | start
| | Set Ipsec If Up | ${dut_node} | 6 | admin-up
| | Set Ipsec Route | ${dut_node} | ${src_ip}/${prefix} | ipsec0
| | ${lSpi} | ${lEnc} | ${lAuth}= | Get VPP Ipsec Keys | ${dut_node} | local
| | ${rSpi} | ${rEnc} | ${rAuth}= | Get Vpp Ipsec Keys | ${dut_node} | remote
| | Send IKEv2 Packet | ${tg_node} | ${src_ip} | ${dst_ip} | ${src_tun_ip}
| | ... | ${dst_tun_ip} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1}
| | ... | ${rSpi} | ${rEnc} | ${rAuth}
| | ... | ${lSpi} | ${lEnc} | ${lAuth}

