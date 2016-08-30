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
| Library | OperatingSystem
| Library | Collections
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.ssh
| Library  | resources.libraries.python.IKEv2
| Variables | resources/test_data/ikev2/ikev2_variables.py
| Library  | resources.libraries.python.VatExecutor.VatTerminal | ${nodes['DUT1']}
| Force Tags | HW_ENV | VM_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *IKEv2 Tests*
| ... | *[Top] Network Topologies:* Topology used is TG=DUT.
| ... | *[Enc] Packet Encapsulations:* IPv4-ESP-IPv4-ICMP
| ... | *[Cfg] DUT configuration:* IKE connection is established on VPP and
| ... | verified using scapy.
| ... | *[Ver] TG verification:* Correct IKE connection is provided by
| ... | StrongSwan. After the connection is established, packets are generated
| ... | an verified using scapy.
| ... | *[Ref] Applicable standard specifications:* RFC7296

*** Test Cases ***

| TC01: PSK Auth
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC7296.
| | ... | [Cfg] StrongSwan config file on TG is configured with basic PSK FQDN\
| | ... | auth and IKE connection is subsequently established. Algorithms\
| | ... | AES-CBC-128 and integrity algorithm SHA1-96 are used.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | IKEV2 Setup | ${PSK} | ${STRONGSWAN_CONF_DEFAULT}

| TC02: ID type IPv4 address
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC7296.
| | ... | [Cfg] StrongSwan config file on TG is configured with PSK ID of\
| | ... | type IPv4 auth and IKE connection is subsequently established.\
| | ... | Algorithms AES-CBC-128 and integrity algorithm SHA1-96 are used.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | IKEV2 Setup | ${ID_IP} | ${STRONGSWAN_CONF_DEFAULT}

| TC03: ID type email address
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC7296.
| | ... | [Cfg] StrongSwan config file on TG is configured with PSK ID of\
| | ... | type Email-addr auth and IKE connection is subsequently established.\
| | ... | Algorithms AES-CBC-128 and integrity algorithm SHA1-96 are used.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | IKEV2 Setup | ${ID_RFC} | ${STRONGSWAN_CONF_DEFAULT}

| TC04: ID type key-id
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC7296.
| | ... | [Cfg] StrongSwan config file on TG is configured with PSK ID of\
| | ... | type KEY-ID auth and IKE connection is subsequently established.\
| | ... | Algorithms AES-CBC-128 and integrity algorithm SHA1-96 are used.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | IKEV2 Setup | ${ID_KEY} | ${STRONGSWAN_CONF_DEFAULT}

| TC05: RSA key auth
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC7296.
| | ... | [Cfg] StrongSwan config file on TG is configured with RSA key\
| | ... | auth and IKE connection is subsequently established. Algorithms\
| | ... | AES-CBC-128 and integrity algorithm SHA1-96 are used.
| | ... | [Ver] Send and receive ESP packet between TG and VPP node.
| | Copy RSA Files
| | IKEV2 Setup | ${RSA} | ${RSA_CONF}

*** Keywords ***
| IKEV2 Setup
| | [Documentation] | Setup testing path, IP addresses and ARP. Then set IKE
| | ... | profile and setup related to it. Subsequently, StrongSwan config
| | ... | files are updated for specific tests.
| | [Arguments] | ${dict} | ${strongswan}
| | Log | ${dict['pr_name']}
| | Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | Interfaces in 2-node path are up
| | Strongswan Ipsec | ${tg_node} | stop
| | ${dut_lo}= | Vpp Create Loopback | ${dut_node}
| | Set Interface State | ${dut_node} | ${dut_lo} | up
| | Set Interface Address | ${dut_node} | ${dut_lo} | ${dst_ip} | ${prefix}
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${dst_tun_ip} | ${prefix}
| | ${tg_if}= | Get Interface Name | ${tg_node} | ${tg_to_dut_if1}
| | Set Interface Address | ${tg_node} | ${tg_if} | ${src_tun_ip} | ${prefix}
| | Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_tun_ip} | ${tg_to_dut_if1_mac}
| | Set Linux Interface Arp | ${tg_node} | ${tg_if} | ${dst_tun_ip}
| | ... | ${dut_to_tg_if1_mac}
| | Set Ikev2 Profile | ${dut_node} | ${dict['pr_name']}
| | Set Ikev2 Auth | ${dut_node} | ${dict['pr_name']} | ${dict['auth_method']}
| | ... | ${dict['auth_data']}
| | Set Ikev2 ID | ${dut_node} | ${dict['pr_name']} | ${dict['id_type_loc']}
| | ... | ${dict['id_data_loc']}
| | ... | local
| | Set Ikev2 ID | ${dut_node} | ${dict['pr_name']} | ${dict['id_type_rem']}
| | ... | ${dict['id_data_rem']} | remote
| | Set Ikev2 TS | ${dut_node} | ${dict['pr_name']} | ${dict['protocol_loc']}
| | ... | ${dict['sport_loc']} | ${dict['eport_loc']} | ${dict['saddr_loc']}
| | ... | ${dict['eaddr_loc']} | local
| | Set Ikev2 TS | ${dut_node} | ${dict['pr_name']} | ${dict['protocol_rem']}
| | ... | ${dict['sport_rem']} | ${dict['eport_rem']} | ${dict['saddr_rem']}
| | ... | ${dict['eaddr_rem']} | remote
| | Set Secrets Strongswan | ${tg_node} | ${strongswan['default_secret']}
| | ${rsa_present}= | Run Keyword And Return Status
| | ... | Dictionary Should Contain Key | ${strongswan} | auth_by
| | Run Keyword If | '${rsa_present}' == 'True' | Run Keywords |
| | ... | Set Secrets Strongswan | ${tg_node} | ${strongswan['swan_secret']} |
| | ... | AND |
| | ... | Set Ikev2 Key | ${dut_node} | ${strongswan['vpp_key']}
| | Set To Dictionary | ${strongswan} | right_id=${dict['right_id']}
| | Set To Dictionary | ${strongswan} | left_id=${dict['left_id']}
| | Set Strongswan Config | ${tg_node} | ${strongswan}
| | Strongswan Ipsec | ${tg_node} | start
| | Set Ipsec If State | ${dut_node} | ${ipsec_index} | admin-up
| | Set Interface Address | ${dut_node} | ipsec0 | 9.9.9.9 | 32
| | Set Ipsec Route | ${dut_node} | ${src_ip}/${prefix} | 9.9.9.9 | ipsec0
| | ${lSpi} | ${lEnc} | ${lAuth}= | Get VPP Ipsec Keys | ${dut_node} | local
| | ${rSpi} | ${rEnc} | ${rAuth}= | Get Vpp Ipsec Keys | ${dut_node} | remote
| | Send IKEv2 Packet | ${tg_node} | ${src_ip} | ${dst_ip} | ${src_tun_ip}
| | ... | ${dst_tun_ip} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1}
| | ... | ${rSpi} | ${rEnc} | ${rAuth}
| | ... | ${lSpi} | ${lEnc} | ${lAuth}

| Copy RSA Files
| | [Documentation] | Copy RSA files into DUT and TG in order
| | ... | to run IKEv2 test with RSA key.
| | Copy RSA File | ${nodes['DUT1']} | server-cert.pem | /tmp/ike
| | Copy RSA File | ${nodes['DUT1']} | client-key.pem | /tmp/ike
| | Copy RSA File | ${nodes['TG']} | ca-cert.pem | /etc/ipsec.d/cacerts
| | Copy RSA File | ${nodes['TG']} | ca-key.pem | /etc/ipsec.d/cacerts
| | Copy RSA File | ${nodes['TG']} | client-cert.pem | /etc/ipsec.d/certs
| | Copy RSA File | ${nodes['TG']} | server-cert.pem | /etc/ipsec.d/certs
| | Copy RSA File | ${nodes['TG']} | server-key.pem | /etc/ipsec.d/private


| Copy RSA File
| | [Documentation] | Load and copy file to destination.
| | [Arguments] | ${node} | ${file_name} | ${path}
| | ${rsa_path}= | Replace Variables | ${rsa_path}
| | ${file}= | Get File | ${rsa_path}/${file_name}
| | Transfer RSA File | ${node} | ${file} | ${path}/${file_name}

