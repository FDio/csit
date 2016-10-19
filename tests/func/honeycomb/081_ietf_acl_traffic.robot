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

*** Variables ***
| &{if_settings}= | enabled=True
# Bridge domain settings
| ${bd_name}= | bd1
| &{bd_settings}= | flood=${True} | forward=${True} | learn=${True}
| ... | unknown-unicast-flood=${True} | arp-termination=${False}
| &{bd_if_settings}= | split_horizon_group=${0} | bvi=${False}
# Names for AC lists
| ${acl_name_l2}= | acl_l2
| ${acl_name_l3_ip4}= | acl_l3_ip4
| ${acl_name_l3_ip6}= | acl_l3_ip6
| ${acl_name_l4}= | acl_l4
| ${acl_name_mixed}= | acl_mixed
| ${acl_name_multirule}= | acl_multirule

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/bridge_domain.robot
| Resource | resources/libraries/robot/honeycomb/access_control_lists.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.honeycomb.HcAPIKwACL.ACLKeywords
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.IPv4Setup
| Library | resources.libraries.python.IPv4Util
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.Routing
| Test Teardown | Run Keywords | Clear IETF-ACL settings
| ... | ${node} | ${dut_to_tg_if1} | AND
| ... | Show Packet Trace on All DUTs | ${nodes}
| Suite Teardown | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Documentation | *Honeycomb access control lists test suite for IETF-ACL node.*
| Force Tags | Honeycomb_sanity

*** Test Cases ***
| TC01: L2 ACL MAC filtering through IETF-ACL node
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure L2 MAC ACL on ingress interface.
| | ... | [Ver] Send simple TCP packets from one TG interface to the other,\
| | ... | using different MACs. Receive all packets except those with\
| | ... | MACs in the filtered ranges.
| | [Teardown] | Run Keywords
| | ... | Clear IETF-ACL Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Show Packet Trace On All DUTs | ${nodes} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup Interfaces And Bridge Domain For IETF-ACL Test
| | ... | L2 | ${acl_name_l2}
| | When Honeycomb Creates ACL Chain Through IETF Node
| | ... | ${dut_node} | ${acl_name_l2} | L2 | ${acl_settings}
| | And Honeycomb Assigns IETF-ACL Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | L2 | ingress | ${acl_name_l2}
| | ... | permit
| | Then Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src}
| | ... | ${tg_to_dut_if2} | ${classify_dst}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src2}
| | ... | ${tg_to_dut_if2} | ${classify_dst2}
| | ... | TCP | ${src_port} | ${dst_port}

| TC02: L2 ACL MAC filtering through IETF-ACL node on egress interface
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure L2 MAC ACL on egress interface.
| | ... | [Ver] Send simple TCP packets from one TG interface to the other,\
| | ... | using different MACs. Receive all packets except those with\
| | ... | MACs in the filtered ranges.
| | [Teardown] | Run Keywords
| | ... | Clear IETF-ACL Settings | ${node} | ${dut_to_tg_if2} | AND
| | ... | Show Packet Trace On All DUTs | ${nodes} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup Interfaces And Bridge Domain For IETF-ACL Test
| | ... | L2 | ${acl_name_l2}
| | When Honeycomb Creates ACL Chain Through IETF Node
| | ... | ${dut_node} | ${acl_name_l2} | L2 | ${acl_settings}
| | And Honeycomb Assigns IETF-ACL Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if2} | L2 | egress | ${acl_name_l2}
| | ... | permit
| | Then Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src}
| | ... | ${tg_to_dut_if2} | ${classify_dst}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src2}
| | ... | ${tg_to_dut_if2} | ${classify_dst2}
| | ... | TCP | ${src_port} | ${dst_port}

| TC03: L3 ACL IPv4 filtering through IETF-ACL node
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv4 addresses on both\
| | ... | interfaces to TG, add ARP entry and routes, and configure L3 IPv4 ACL\
| | ... | on ingress interface with src/dst IP and protocol.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different IPv4 IPs. Receive all packets except\
| | ... | those with IPs in the filtered ranges and UDP protocol payload.
| | Given Setup Interface IPs And Routes For IPv4 IETF-ACL Test
| | ... | L3_IP4 | ${acl_name_l3_ip4}
| | When Honeycomb Creates ACL Chain Through IETF Node
| | ... | ${dut_node} | ${acl_name_l3_ip4} | L3_IP4 | ${acl_settings}
| | And Honeycomb Assigns IETF-ACL Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | L3_IP4 | ingress | ${acl_name_l3_ip4}
| | ... | permit
| | Then Send TCP Or UDP Packet | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | UDP | ${src_port} | ${dst_port}
| | And Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src} | ${classify_dst}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src} | ${classify_dst}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | UDP | ${src_port} | ${dst_port}

| TC04: L3 ACL IPv6 filtering through IETF-ACL node
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv6 addresses on both\
| | ... | interfaces to TG, add IP neighbor entry and routes, and configure\
| | ... | L3 IPv6 ACL on ingress interface with src/dst IP and next-header.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different IPv6 IPs. Receive all packets except\
| | ... | those with IPs in the filtered ranges and UDP protocol payload.
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Import Variables | resources/test_data/honeycomb/ietf_acl.py
| | ... | L3_IP6 | ${acl_name_l3_ip6}
| | And Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | And Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if2} | up
# TODO: Configure addresses through Honeycomb when implemented. (Honeycomb-102)
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
| | And VPP RA suppress link layer | ${dut_node} | ${dut_to_tg_if2}
# TODO: Configure route through Honeycomb when implemented.(Honeycomb-58)
| | And Add IP Neighbor
| | ... | ${node} | ${dut_to_tg_if2} | ${gateway} | ${tg_to_dut_if2_mac}
| | And VPP Route Add | ${node} | ${dst_net} | ${prefix_length}
| | ... | ${gateway} | interface=${dut_to_tg_if2} | use_sw_index=False
| | And VPP Route Add | ${node} | ${classify_dst_net} | ${prefix_length}
| | ... | ${gateway} | interface=${dut_to_tg_if2} | use_sw_index=False
| | When Honeycomb Creates ACL Chain Through IETF Node
| | ... | ${dut_node} | ${acl_name_l3_ip6} | L3_IP6 | ${acl_settings}
| | And Honeycomb Assigns IETF-ACL Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | L3_IP6 | ingress | ${acl_name_l3_ip6}
| | ... | permit
| | Then Send TCP Or UDP Packet | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | UDP | ${src_port} | ${dst_port}
| | And Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src} | ${classify_dst}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src} | ${classify_dst}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | UDP | ${src_port} | ${dst_port}

| TC05: L4 ACL port filtering through IETF-ACL node
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv4 addresses on both\
| | ... | interfaces to TG, add ARP entry and routes, and configure L4 port ACL\
| | ... | on ingress interface with src/dst port ranges.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different ports. Receive all packets except\
| | ... | those with ports in the filtered ranges.
| | Given Setup Interface IPs And Routes For IPv4 IETF-ACL Test
| | ... | L4 | ${acl_name_l4}
| | When Honeycomb Creates ACL Chain Through IETF Node
| | ... | ${dut_node} | ${acl_name_l4} | mixed | ${acl_settings}
| | And Honeycomb Assigns IETF-ACL Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | mixed | ingress | ${acl_name_l4}
| | ... | permit | L3
| | Then Send TCP Or UDP Packet | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${classify_src} | ${classify_dst}

| TC06: L2,L3 and L4 ACL together on L2-mode interface
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure L2, L3 and L4 ACL on ingress interface\
| | ... | with src/dst MAC, src/dst IP, protocol and src/dst port ranges.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different MACs, IPv4 IPs and ports. Receive\
| | ... | all packets except those with MACs, IPs and ports in the filtered\
| | ... | ranges and UDP protocol payload.
| | [Teardown] | Run Keywords
| | ... | Clear IETF-ACL Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Show Packet Trace On All DUTs | ${nodes} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup Interfaces And Bridge Domain For IETF-ACL Test
| | ... | mixed | ${acl_name_mixed}
| | When Honeycomb Creates ACL Chain Through IETF Node
| | ... | ${dut_node} | ${acl_name_mixed} | mixed | ${acl_settings}
| | And Honeycomb Assigns IETF-ACL Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | mixed | ingress | ${acl_name_mixed}
| | ... | permit | L2
| | Then Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src_mac}
| | ... | ${tg_to_dut_if2} | ${classify_dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src_ip} | ${classify_dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src_mac}
| | ... | ${tg_to_dut_if2} | ${classify_dst_mac}
| | ... | UDP | ${classify_src_port} | ${classify_dst_port}

| TC07: L2,L3 and L4 ACL together on L3-mode interface
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv4 addresses on both\
| | ... | interfaces to TG, add ARP entry and routes, and configure\
| | ... | L2, L3 and L4 ACL on ingress interface with src/dst MAC, src/dst IP,\
| | ... | protocol and src/dst port ranges.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different MACs, IPv4 IPs and ports. Receive\
| | ... | all packets except those with MACs, IPs and ports in the filtered\
| | ... | ranges and UDP protocol payload.
| | Setup Interface IPs And Routes For IPv4 IETF-ACL Test
| | ... | mixed | ${acl_name_mixed}
| | When Honeycomb Creates ACL Chain Through IETF Node
| | ... | ${dut_node} | ${acl_name_mixed} | mixed | ${acl_settings}
| | And Honeycomb Assigns IETF-ACL Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | mixed | ingress | ${acl_name_mixed}
| | ... | permit | L3
| | Then Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src_mac}
| | ... | ${tg_to_dut_if2} | ${classify_dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src_ip} | ${classify_dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src_mac}
| | ... | ${tg_to_dut_if2} | ${classify_dst_mac}
| | ... | UDP | ${classify_src_port} | ${classify_dst_port}

| TC08: Multiple classify rules in one ACL
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure a series of L2 MAC ACL rules on ingress interface.
| | ... | [Ver] Send simple TCP packets from one TG interface to the other,\
| | ... | using different MACs. Receive all packets except those with\
| | ... | MACs in the ranges filtered by any rule.
| | [Teardown] | Run Keywords
| | ... | Clear IETF-ACL Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Show Packet Trace On All DUTs | ${nodes} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup Interfaces And Bridge Domain For IETF-ACL Test
| | ... | multirule | ${acl_name_multirule}
| | When Honeycomb Creates ACL Chain Through IETF Node
| | ... | ${dut_node} | ${acl_name_multirule} | L2 | ${acl_settings}
| | And Honeycomb Assigns IETF-ACL Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | L2 | ingress | ${acl_name_multirule}
| | ... | permit
| | Then Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src}
| | ... | ${tg_to_dut_if2} | ${classify_dst}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src2}
| | ... | ${tg_to_dut_if2} | ${classify_dst2}
| | ... | TCP | ${src_port} | ${dst_port}

*** Keywords ***
| Setup interface IPs and routes for IPv4 ietf-ACL test
| | [Arguments] | ${test_data_id} | ${acl_name}
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Import Variables | resources/test_data/honeycomb/ietf_acl.py
| | ... | ${test_data_id} | ${acl_name}
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip}
| | ... | ${prefix_length} | ${if_settings}
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip}
| | ... | ${prefix_length} | ${if_settings}
# TODO: Configure routes through Honeycomb when implemented.(Honeycomb-58)
| | Add ARP on DUT
| | ... | ${node} | ${dut_to_tg_if2} | ${gateway} | ${tg_to_dut_if2_mac}
| | VPP Route Add
| | ... | ${node} | ${dst_net} | ${prefix_length} | ${gateway}
| | ... | interface=${dut_to_tg_if2} | use_sw_index=False
| | VPP Route Add
| | ... | ${node} | ${classify_dst_net} | ${prefix_length} | ${gateway}
| | ... | interface=${dut_to_tg_if2} | use_sw_index=False

| Setup interfaces and bridge domain for ietf-ACL test
| | [Arguments] | ${test_data_id} | ${acl_name}
| | Path For 2-node Testing Is Set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Import Variables | resources/test_data/honeycomb/ietf_acl.py
| | ... | ${test_data_id} | ${acl_name}
| | Honeycomb Sets Interface State | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb Sets Interface State | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb Creates L2 Bridge Domain
| | ... | ${dut_node} | ${bd_name} | ${bd_settings}
| | Honeycomb Adds Interfaces To Bridge Domain
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | ... | ${bd_name} | ${bd_if_settings}