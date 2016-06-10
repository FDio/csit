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
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.ProxyArp
| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Show packet trace on all DUTs | ${nodes}
| Documentation | *RFC1027 Proxy ARP test cases*
| ...
| ... | *[Top] Network topologies:* TG-DUT1 2-node topology with
| ... | single link between nodes.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with Proxy ARP
| ... | *[Ver] TG verification:* Test ARP Request packet is sent
| ... | from TG on link to DUT1; on receive TG verifies ARP reply packet
| ... | for correctness and their IPv4 src-addr, dst-addr and MAC addresses.
| ... | *[Ref] Applicable standard specifications:* RFC1027.

*** Variables ***
| ${tg_to_dut1_ip}= | 10.0.0.100
| ${dut1_to_tg_ip}= | 10.0.0.1
| ${prefix_length}= | 24
| ${lo_ip4_addr}= | 192.168.1.2
| ${hi_ip4_addr}= | 192.168.1.10
| ${pass_test_ip}= | 192.168.1.5
| ${pass_test_lo_ip}= | 192.168.1.2
| ${pass_test_hi_ip}= | 192.168.1.10
| ${fail_test_lo_ip}= | 192.168.1.1
| ${fail_test_hi_ip}= | 192.168.1.11

*** Test Cases ***
| TC01: DUT sends ARP reply on behalf of another machine from the IP range
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC1027.
| | ... | [Cfg] On DUT1 configure interface IPv4 address and proxy ARP
| | ... | for IP range.
| | ... | [Ver] Make TG send ARP request to DUT1 interface,
| | ... | verify if DUT1 sends correct ARP reply on behalf of machine which
| | ... | IP is in range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${dut1_to_tg_name}= | Get interface name | ${dut1_node} | ${dut1_to_tg}
| | ${tg_to_dut1_name}= | Get interface name | ${tg_node} | ${tg_to_dut1}
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg_name}
| | Then Send ARP Request | ${tg_node} | ${tg_to_dut1_name}
| | ...                   | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                   | ${tg_to_dut1_ip} | ${pass_test_ip}

| TC02: DUT sends ARP reply on behalf of another machine from beginning of the IP range
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC1027.
| | ... | [Cfg] On DUT1 configure interface IPv4 address and proxy ARP
| | ... | for IP range.
| | ... | [Ver] Make TG send ARP request to DUT1 interface,
| | ... | verify if DUT1 sends correct ARP reply on behalf of machine which
| | ... | IP is from beginning of the IP range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${dut1_to_tg_name}= | Get interface name | ${dut1_node} | ${dut1_to_tg}
| | ${tg_to_dut1_name}= | Get interface name | ${tg_node} | ${tg_to_dut1}
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg_name}
| | Then Send ARP Request | ${tg_node} | ${tg_to_dut1_name}
| | ...                   | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                   | ${tg_to_dut1_ip} | ${pass_test_lo_ip}

| TC03: DUT sends ARP reply on behalf of another machine from end of the IP range
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC1027.
| | ... | [Cfg] On DUT1 configure interface IPv4 address and proxy ARP
| | ... | for IP range.
| | ... | [Ver] Make TG send ARP request to DUT1 interface,
| | ... | verify if DUT1 sends correct ARP reply on behalf of machine which
| | ... | IP is from end of the IP range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${dut1_to_tg_name}= | Get interface name | ${dut1_node} | ${dut1_to_tg}
| | ${tg_to_dut1_name}= | Get interface name | ${tg_node} | ${tg_to_dut1}
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg_name}
| | Then Send ARP Request | ${tg_node} | ${tg_to_dut1_name}
| | ...                   | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                   | ${tg_to_dut1_ip} | ${pass_test_hi_ip}

| TC04: DUT does not send ARP reply on behalf of another machine from below of the IP range
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC1027.
| | ... | [Cfg] On DUT1 configure interface IPv4 address and proxy ARP
| | ... | for IP range.
| | ... | [Ver] Make TG send ARP request to DUT1 interface,
| | ... | verify if DUT1 does not send ARP reply on behalf of machine which
| | ... | IP is from below of the IP range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${dut1_to_tg_name}= | Get interface name | ${dut1_node} | ${dut1_to_tg}
| | ${tg_to_dut1_name}= | Get interface name | ${tg_node} | ${tg_to_dut1}
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg_name}
| | Then Send ARP Request should failed | ${tg_node} | ${tg_to_dut1_name}
| | ...                                 | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                                 | ${tg_to_dut1_ip} | ${fail_test_lo_ip}

| TC05: DUT does not send ARP reply on behalf of another machine from above of the IP range
| | [Documentation]
| | ... | [Top] TG-DUT1.
| | ... | [Ref] RFC1027.
| | ... | [Cfg] On DUT1 configure interface IPv4 address and proxy ARP
| | ... | for IP range.
| | ... | [Ver] Make TG send ARP request to DUT1 interface,
| | ... | verify if DUT1 does not send ARP reply on behalf of machine which
| | ... | IP is from above of the IP range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | ${dut1_to_tg_name}= | Get interface name | ${dut1_node} | ${dut1_to_tg}
| | ${tg_to_dut1_name}= | Get interface name | ${tg_node} | ${tg_to_dut1}
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg_name}
| | Then Send ARP Request should failed | ${tg_node} | ${tg_to_dut1_name}
| | ...                                 | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                                 | ${tg_to_dut1_ip} | ${fail_test_hi_ip}
