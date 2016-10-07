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
| Suite Teardown | Run Keyword If Any Tests Failed
| ... | Restart Honeycomb And VPP And Clear Persisted Configuration | ${node}
| Documentation | *Honeycomb access control lists test suite for IETF-ACL node.*
| Force Tags | Honeycomb_sanity

*** Test Cases ***
| TC01: Honeycomb can configure L2 ACL MAC filtering through IETF-ACL node
| | [Documentation]
| | ... | [Top] TG=DUT1=TG.
| | ... | [Enc] Eth-IPv4-TCP.
| | ... | [Cfg] (Using Honeycomb API) On DUT1 bridge both interfaces to TG\
| | ... | and configure L2 MAC ACL on ingress interface.
| | ... | [Ver] Send simple TCP packets from one TG interface to the other,\
| | ... | using different MACs. Receive all packets except those with\
| | ... | MACs in the filtered ranges.
| | [Teardown] | Run Keywords
| | ... | Clear IETF-ACL settings | ${node} | ${dut_to_tg_if1} | AND
| | ... | Show Packet Trace on All DUTs | ${nodes} | AND
| | ... | Honeycomb removes all bridge domains
| | ... | ${node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | Given Path For 2-node Testing Is Set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Import Variables | resources/test_data/honeycomb/ietf_acl.py
| | ... | L2 | ${acl_name_l2}
| | And Honeycomb Sets Interface State | ${dut_node} | ${dut_to_tg_if1} | up
| | And Honeycomb Sets Interface State | ${dut_node} | ${dut_to_tg_if2} | up
| | And Honeycomb Creates L2 Bridge Domain
| | ... | ${dut_node} | ${bd_name} | ${bd_settings}
| | And Honeycomb Adds Interfaces To Bridge Domain
| | ... | ${dut_node} | ${dut_to_tg_if1} | ${dut_to_tg_if2}
| | ... | ${bd_name} | ${bd_if_settings}
| | When Honeycomb creates ACL chain through IETF node
| | ... | ${dut_node} | ${acl_name_l2} | L2 | ${acl_settings}
| | And Honeycomb assigns IETF-ACL chain to interface
| | ... | ${dut_node} | ${dut_to_tg_if1} | L2 | ingress | ${acl_name_l2}
| | ... | permit
| | Then Send TCP or UDP packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${src_mac}
| | ... | ${tg_to_dut_if2} | ${dst_mac}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run keyword and expect error | TCP/UDP Rx timeout
| | ... | Send TCP or UDP packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src}
| | ... | ${tg_to_dut_if2} | ${classify_dst}
| | ... | TCP | ${src_port} | ${dst_port}
| | And Run keyword and expect error | TCP/UDP Rx timeout
| | ... | Send TCP or UDP packet | ${tg_node} | ${src_ip} | ${dst_ip}
| | ... | ${tg_to_dut_if1} | ${classify_src2}
| | ... | ${tg_to_dut_if2} | ${classify_dst2}
| | ... | TCP | ${src_port} | ${dst_port}
