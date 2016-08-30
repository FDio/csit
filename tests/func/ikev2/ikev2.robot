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
| Library  | resources.libraries.python.IKEv2.StrongSwanUtil
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
*** Test Cases ***
| TC01: PSK Auth
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['TG']}
| | And Interfaces in 2-node path are up
| | Exec CMD No Error | ${tg_node} | ipsec stop | sudo=True

| | ${dut_lo}= | Vpp Create Loopback | ${dut_node}
| | Set Interface State | ${dut_node} | ${dut_lo} | up
| | Set Interface Address | ${dut_node} | ${dut_lo} | 10.0.5.1 | 32
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | 10.0.0.5 | ${prefix}

| | ${tg_if}= | Get Interface Name | ${tg_node} | ${tg_to_dut_if1}
| | And Add Arp On Dut | ${dut_node} | ${dut_to_tg_if1}
| | ... | ${src_tun_ip} | ${tg_to_dut_if1_mac}
| | And Set Linux Interface Arp | ${tg_node} | ${tg_if} | ${dst_tun_ip} | ${dut_to_tg_if1_mac}
| | Setup IKE
| | Exec CMD No Error | ${tg_node} | ipsec start | sudo=True
| | ${lSpi} | ${lEnc} | ${lAuth}= | Get VPP Ipsec Keys | ${dut_node} | local
| | ${rSpi} | ${rEnc} | ${rAuth}= | Get Vpp Ipsec Keys | ${dut_node} | remote
| | Set Ipsec If Up | ${dut_node} | 6 | admin-up
| | Set Ipsec Route | ${dut_node} | 10.0.10.0/24 | ipsec0
| | Send IKEv2 Packet | ${tg_node} | ${src_ip} | ${dst_ip} | ${src_tun_ip}
| | ... | ${dst_tun_ip} | ${tg_to_dut_if1_mac}
| | ... | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1}
| | ... | ${rSpi} | ${rEnc} | ${rAuth}
| | ... | ${lSpi} | ${lEnc} | ${lAuth}
*** Keywords ***
| Setup IKE
| | Vat Terminal Exec CMD | ikev2_profile_add_del name pr1
| | Vat Terminal Exec CMD | ikev2_profile_set_auth name pr1 auth_method shared-key-mic auth_data Vpp123
| | Vat Terminal Exec CMD | ikev2_profile_set_id name pr1 id_type fqdn id_data vpp.home local
| | Vat Terminal Exec CMD | ikev2_profile_set_id name pr1 id_type fqdn id_data roadwarrior.vpn.example.com remote
| | Vat Terminal Exec CMD | ikev2_profile_set_ts name pr1 protocol 0 start_port 0 end_port 65535 start_addr 10.0.5.0 end_addr 10.0.5.255 local
| | Vat Terminal Exec CMD | ikev2_profile_set_ts name pr1 protocol 0 start_port 0 end_port 65535 start_addr 10.0.10.0 end_addr 10.0.10.255 remote
