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
| ${acl_name_macip}= | macip
| ${acl_name_l3_ip4}= | acl_l3_ip4
| ${acl_name_l3_ip6}= | acl_l3_ip6
| ${acl_name_l4}= | acl_l4
| ${acl_name_mixed}= | acl_mixed
| ${acl_name_icmp}= | acl_icmp
| ${acl_name_icmpv6}= | acl_icmpv6
| ${acl_name_reflex}= | acl_reflex

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
| Test Teardown | Run Keywords | Read plugin-ACL configuration from VAT
| ... | ${node} | AND
| ... | Clear plugin-acl settings | ${node} | ${dut_to_tg_if1}
| Suite Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes} | AND
| ... | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Documentation | *Honeycomb access control lists test suite for ACL plugin.*
| Force Tags | Honeycomb_sanity

*** Test Cases ***
| TC01: ACL MAC filtering through plugin-acl node - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure L2 MAC ACL on ingress interface.
| | ... | [Ver] Send simple TCP packets from one TG interface to the other,\
| | ... | using different MACs. Receive all packets except those with\
| | ... | MACs in the filtered ranges.
| | [Teardown] | Run Keywords
| | ... | Clear plugin-acl Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup Interfaces And Bridge Domain For plugin-acl Test
| | ... | macip | ${acl_name_macip}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_macip} | ${acl_settings} | macip=${True}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_macip}
| | ... | ingress | macip=${True}
| | When Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src2}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}

| TC02: ACL IPv4 filtering through plugin-acl node - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure L3 IPv4 ACL on ingress interface with src/dst IP
| | ... | and protocol number.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different IPv4 IPs. Receive all packets except\
| | ... | those with IPs in the filtered ranges and UDP protocol payload.
| | [Teardown] | Run Keywords
| | ... | Read plugin-ACL configuration from VAT | ${node} | AND
| | ... | Clear plugin-acl Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup Interfaces And Bridge Domain For plugin-acl Test
| | ... | l3_ip4 | ${acl_name_l3_ip4}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_l3_ip4} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_l3_ip4} | ingress
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

| TC03: ACL IPv6 filtering through plugin-acl node - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv6-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure L3 IPv6 ACL on ingress interface with src/dst IP
| | ... | and protocol number.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different IPv6 IPs. Receive all packets except\
| | ... | those with IPs in the filtered ranges and UDP protocol payload.
| | [Teardown] | Run Keywords
| | ... | Read plugin-ACL configuration from VAT | ${node} | AND
| | ... | Clear plugin-acl Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup interfaces and bridge domain for plugin-acl test
| | ... | l3_ip6 | ${acl_name_l3_ip6}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_l3_ip6} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_l3_ip6} | ingress
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

| TC04: ACL port filtering through plugin-acl node - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and and configure L4 port ACL on ingress interface
| | ... | with src/dst port ranges.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different ports. Receive all packets except\
| | ... | those with ports in the filtered ranges.
| | [Teardown] | Run Keywords
| | ... | Read plugin-ACL configuration from VAT | ${node} | AND
| | ... | Clear plugin-acl Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup interfaces and bridge domain for plugin-acl test
| | ... | L4 | ${acl_name_l4}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_l4} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_l4} | ingress
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
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${classify_src+5} | ${classify_dst+5}

| TC05: ACL filtering with IPv4 address and TCP port in one rule - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure a mixed rule with src/dst IP, TCP protocol
| | ... | and port ranges.
| | ... | [Ver] Send simple TCP packets from one TG interface to the other,\
| | ... | using IPs and ports. Receive all packets except those with\
| | ... | both IPs and ports in the filtered ranges.
| | [Teardown] | Run Keywords
| | ... | Read plugin-ACL configuration from VAT | ${node} | AND
| | ... | Clear plugin-acl Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup Interfaces And Bridge Domain For plugin-acl Test
| | ... | mixed | ${acl_name_mixed}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_mixed} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_mixed} | ingress
| | Then Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | Then Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src_ip} | ${classify_dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src_ip} | ${classify_dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${classify_src_port} | ${classify_dst_port}

| TC06: ACL ICMP packet filtering - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-ICMP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure a ICMP protocol filtering by ICMP type and code.
| | ... | [Ver] Send ICMP packets from one TG interface\
| | ... | to the other, using different codes and types. Receive all packets\
| | ... | except those with types and codes in the filtered ranges.
| | [Tags] | EXPECTED_FAILING
# Bug VPP-624, ICMP type/code values are not matched
| | [Teardown] | Run Keywords
| | ... | Read plugin-ACL configuration from VAT | ${node} | AND
| | ... | Clear plugin-acl Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup interfaces and bridge domain for plugin-acl test
| | ... | icmp | ${acl_name_icmp}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_icmp} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_icmp} | ingress
| | Then Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${icmp_type} | ${icmp_code}
| | Then Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${classify_type} | ${icmp_code}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${classify_type} | ${classify_code}

| TC07: ACL ICMPv6 packet filtering - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv6-ICMP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure a ICMPv6 protocol filtering by ICMPv6 type and code.
| | ... | [Ver] Send ICMPv6 packets from one TG interface\
| | ... | to the other, using different codes and types. Receive all packets\
| | ... | except those with the filtered type and code.
| | [Tags] | EXPECTED_FAILING
# Bug VPP-624, ICMP type/code values are not matched
| | [Teardown] | Run Keywords
| | ... | Read plugin-ACL configuration from VAT | ${node} | AND
| | ... | Clear plugin-acl Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup interfaces and bridge domain for plugin-acl test
| | ... | icmpv6 | ${acl_name_icmpv6}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_icmpv6} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_icmpv6} | ingress
| | Then Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${icmp_type} | ${icmp_code}
| | Then Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${classify_type} | ${icmp_code}
| | And Run Keyword And Expect Error | ICMP echo Rx timeout
| | ... | Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${classify_type} | ${classify_code}

| TC08: ACL reflexive IPv4 filtering through plugin-acl node - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG,\
| | ... | configure a "drop all" ACL on ingress and reflexive ACL on egress.
| | ... | [Ver] Send a simple TCP packet to VPP interface 1 and do not receive\
| | ... | it back. Then send the packet with reversed src/dst IP address\
| | ... | to VPP interface 2 and receive it from interface 1(this should create\
| | ... | a reflexive "permit" rule) Finally, send the original packet again\
| | ... | and receive it from interface 2.
| | [Teardown] | Run Keywords
| | ... | Read plugin-ACL configuration from VAT | ${node} | AND
| | ... | Clear plugin-acl Settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Honeycomb Removes All Bridge Domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Setup Interfaces And Bridge Domain For plugin-acl Test
| | ... | reflex | ${acl_name_reflex}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_reflex} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_reflex} | egress
| | And Import Variables | resources/test_data/honeycomb/plugin_acl.py
| | ... | block_all | block_all
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | block_all | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | block_all | ingress
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src} | ${classify_dst}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_dst} | ${classify_src}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if2_mac}
| | ... | TCP | ${dst_port} | ${src_port}
| | And Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src} | ${classify_dst}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${src_port} | ${dst_port}

# Routing section
# ===============

| TC09: ACL IPv4 filtering through plugin-acl node - routed
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv4 addresses on both\
| | ... | interfaces to TG, add ARP entry and routes, and configure L3 IPv4 ACL\
| | ... | on ingress interface with src/dst IP and protocol.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different IPv4 IPs. Receive all packets except\
| | ... | those with IPs in the filtered ranges and UDP protocol payload.
| | [Tags] | EXPECTED_FAILING
# routed interfaces not yet supported by ACL plugin (no Jira id available)
| | Given Setup Interface IPs And Routes For IPv4 plugin-acl Test
| | ... | l3_ip4 | ${acl_name_l3_ip4}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_l3_ip4} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_l3_ip4} | ingress
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

| TC10: ACL IPv6 filtering through plugin-acl node - routed
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv6-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv6 addresses on both\
| | ... | interfaces to TG, add IP neighbor entry and routes, and configure\
| | ... | L3 IPv6 ACL on ingress interface with src/dst IP and next-header.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different IPv6 IPs. Receive all packets except\
| | ... | those with IPs in the filtered ranges and UDP protocol payload.
| | [Tags] | EXPECTED_FAILING
# routed interfaces not yet supported by ACL plugin (no Jira id available)
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Import Variables | resources/test_data/honeycomb/plugin_acl.py
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
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_l3_ip6} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_l3_ip6} | ingress
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

| TC11: ACL port filtering through plugin-acl node - routed
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv4 addresses on both\
| | ... | interfaces to TG, add ARP entry and routes, and configure L4 port ACL\
| | ... | on ingress interface with src/dst port ranges.
| | ... | [Ver] Send simple TCP and UDP packets from one TG interface\
| | ... | to the other, using different ports. Receive all packets except\
| | ... | those with ports in the filtered ranges.
| | [Tags] | EXPECTED_FAILING
# routed interfaces not yet supported by ACL plugin (no Jira id available)
| | Given Setup Interface IPs And Routes For IPv4 plugin-acl Test
| | ... | L4 | ${acl_name_l4}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_l4} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_l4} | ingress
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
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${classify_src+5} | ${classify_dst+5}

| TC12: ACL filtering with IPv4 address and TCP port in one rule - routed
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv4 addresses on both\
| | ... | interfaces to TG, add ARP entry and routes and configure a mixed
| | ... | rule with src/dst IP, TCP protocol and port ranges.
| | ... | [Ver] Send simple TCP packets from one TG interface to the other,\
| | ... | using IPs and ports. Receive all packets except those with\
| | ... | both IPs and ports in the filtered ranges.
| | [Tags] | EXPECTED_FAILING
# routed interfaces not yet supported by ACL plugin (no Jira id available)
| | Given Setup Interface IPs And Routes For IPv4 plugin-acl Test
| | ... | mixed | ${acl_name_mixed}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_mixed} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_mixed} | ingress
| | Then Send TCP Or UDP Packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | Then Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src_ip} | ${classify_dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src_ip} | ${classify_dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${classify_src_port} | ${classify_dst_port}

| TC13: ACL ICMP packet filtering - routed
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv4 addresses on both\
| | ... | interfaces to TG, add ARP entry and routes, and configure ICMP ACL\
| | ... | on ingress interface with ICMP type and code.
| | ... | [Ver] Send ICMP packets from one TG interface\
| | ... | to the other, using different codes and types. Receive all packets\
| | ... | except those with the filtered type and code.
| | [Tags] | EXPECTED_FAILING
# Bug VPP-624, ICMP type/code values are not matched
# routed interfaces not yet supported by ACL plugin (no Jira id available)
| | Given Setup Interface IPs And Routes For IPv4 plugin-acl Test
| | ... | icmp | ${acl_name_icmp}
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_icmp} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_icmp} | ingress
| | Then Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${icmp_type} | ${icmp_code}
| | Then Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${classify_type} | ${icmp_code}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${classify_type} | ${classify_code}

| TC14: ACL ICMPv6 packet filtering - routed
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv6 addresses on both\
| | ... | interfaces to TG, add ARP entry and routes, and configure ICMP ACL\
| | ... | on ingress interface with ICMPv6 type and code.
| | ... | [Ver] Send ICMPv6 packets from one TG interface\
| | ... | to the other, using different codes and types. Receive all packets\
| | ... | except those with the filtered type and code.
| | [Tags] | EXPECTED_FAILING
# Bug VPP-624, ICMP type/code values are not matched
# routed interfaces not yet supported by ACL plugin (no Jira id available)
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Import Variables | resources/test_data/honeycomb/plugin_acl.py
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
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_icmp} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_icmp} | ingress
| | Then Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${icmp_type} | ${icmp_code}
| | Then Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${classify_type} | ${icmp_code}
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send ICMP packet with type and code | ${tg_node}
| | ... | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | ${classify_type} | ${classify_code}

| TC15: ACL reflexive IPv4 filtering through plugin-acl node - bridged
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 set IPv4 addresses on both\
| | ... | interfaces to TG, add ARP entries and routes,\
| | ... | configure a "drop all" ACL on ingress and reflexive ACL on egress.
| | ... | [Ver] Send a simple TCP packet to VPP interface 1 and do not receive\
| | ... | it back. Then send the packet with reversed src/dst IP address\
| | ... | to VPP interface 2 and receive it from interface 1(this should create\
| | ... | a reflexive "permit" rule) Finally, send the original packet again\
| | ... | and receive it from interface 2.
| | [Tags] | EXPECTED_FAILING
# routed interfaces not yet supported by ACL plugin (no Jira id available)
| | Given Setup Interface IPs And Routes For IPv4 plugin-acl Test
| | ... | icmp | ${acl_name_reflex}
| | And Add ARP on DUT
| | ... | ${node} | ${dut_to_tg_if1} | ${gateway2} | ${tg_to_dut_if1_mac}
| | And VPP Route Add
| | ... | ${node} | ${src_net} | ${prefix_length} | ${gateway2}
| | ... | interface=${dut_to_tg_if1} | use_sw_index=False
| | And VPP Route Add
| | ... | ${node} | ${classify_src_net} | ${prefix_length} | ${gateway2}
| | ... | interface=${dut_to_tg_if1} | use_sw_index=False
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | ${acl_name_reflex} | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${acl_name_reflex} | egress
| | And Import Variables | resources/test_data/honeycomb/plugin_acl.py
| | ... | block_all | block_all
| | When Honeycomb Creates ACL Chain Through ACL plugin
| | ... | ${dut_node} | block_all | ${acl_settings}
| | And Honeycomb Assigns plugin-acl Chain To Interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | block_all | ingress
| | And Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src} | ${classify_dst}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_dst} | ${classify_src}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if2_mac}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if2_mac}
| | ... | TCP | ${dst_port} | ${src_port}
| | And Send TCP Or UDP Packet | ${tg_node}
| | ... | ${classify_src} | ${classify_dst}
| | ... | ${tg_to_dut_if1} | ${tg_to_dut_if1_mac}
| | ... | ${tg_to_dut_if2} | ${dut_to_tg_if1_mac}
| | ... | TCP | ${src_port} | ${dst_port}

*** Keywords ***
| Setup interface IPs and routes for IPv4 plugin-acl test
| | [Arguments] | ${test_data_id} | ${acl_name}
| | Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Import Variables | resources/test_data/honeycomb/plugin_acl.py
| | ... | ${test_data_id} | ${acl_name}
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb sets interface state | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${dut_to_tg_if1_ip} | ${prefix_length}
| | Honeycomb sets interface ipv4 address with prefix | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${dut_to_tg_if2_ip} | ${prefix_length}
# TODO: Configure routes through Honeycomb once routing tests are added
| | Add ARP on DUT
| | ... | ${node} | ${dut_to_tg_if2} | ${gateway} | ${tg_to_dut_if2_mac}
| | VPP Route Add
| | ... | ${node} | ${dst_net} | ${prefix_length} | ${gateway}
| | ... | interface=${dut_to_tg_if2} | use_sw_index=False
| | VPP Route Add
| | ... | ${node} | ${classify_dst_net} | ${prefix_length} | ${gateway}
| | ... | interface=${dut_to_tg_if2} | use_sw_index=False

| Setup interfaces and bridge domain for plugin-acl test
| | [Arguments] | ${test_data_id} | ${acl_name}
| | Path For 2-node Testing Is Set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Import Variables | resources/test_data/honeycomb/plugin_acl.py
| | ... | ${test_data_id} | ${acl_name}
| | Honeycomb Sets Interface State | ${dut_node} | ${dut_to_tg_if1} | up
| | Honeycomb Sets Interface State | ${dut_node} | ${dut_to_tg_if2} | up
| | Honeycomb Creates first L2 Bridge Domain
| | ... | ${dut_node} | ${bd_name} | ${bd_settings}
| | Honeycomb Adds Interfaces To Bridge Domain
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | ... | ${bd_name} | ${bd_if_settings}
