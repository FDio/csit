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
| Documentation | Functional tests to verify VPP DUT answers ARP request
| ...           |  intended for another machine.
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
| TC21: DUT sends ARP reply behalf another machine from the range IPs
| | [Documentation] | RFC1027 : Eth-IPv4 on links TG-DUT1:
| | ...             | On DUT1 configure interface IPv4 address.
| | ...             | Make TG send ARP request to DUT1 interface.
| | ...             | Make TG verify DUT1 sends ARP reply behalf machine which
| | ...             | IP is in range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg}
| | Then Send ARP Request | ${tg_node} | ${tg_to_dut1}
| | ...                   | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                   | ${tg_to_dut1_ip} | ${pass_test_ip}

| TC22: DUT sends ARP reply behalf another machine from beginning of the range IPs
| | [Documentation] | RFC1027 : Eth-IPv4 on links TG-DUT1:
| | ...             | On DUT1 configure interface IPv4 address.
| | ...             | Make TG send ARP request to DUT1 interface.
| | ...             | Make TG verify DUT1 sends ARP reply behalf machine which
| | ...             | IP is in begining of the range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg}
| | Then Send ARP Request | ${tg_node} | ${tg_to_dut1}
| | ...                   | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                   | ${tg_to_dut1_ip} | ${pass_test_lo_ip}

| TC23: DUT sends ARP reply behalf another machine from end of the range IPs
| | [Documentation] | RFC1027 : Eth-IPv4 on links TG-DUT1:
| | ...             | On DUT1 configure interface IPv4 address.
| | ...             | Make TG send ARP request to DUT1 interface.
| | ...             | Make TG verify DUT1 sends ARP reply behalf machine which
| | ...             | IP is in end of the range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg}
| | Then Send ARP Request | ${tg_node} | ${tg_to_dut1}
| | ...                   | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                   | ${tg_to_dut1_ip} | ${pass_test_hi_ip}

| TC24: DUT does not send ARP reply behalf another machine from below of the range IPs
| | [Documentation] | RFC1027 : Eth-IPv4 on links TG-DUT1:
| | ...             | On DUT1 configure interface IPv4 address.
| | ...             | Make TG send ARP request to DUT1 interface.
| | ...             | Make TG verify DUT1 does not send ARP reply behalf machine
| | ...             | which IP is below the range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg}
| | Then Send ARP Request should failed | ${tg_node} | ${tg_to_dut1}
| | ...                                 | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                                 | ${tg_to_dut1_ip} | ${fail_test_lo_ip}

| TC25: DUT does not send ARP reply behalf another machine from above of the range IPs
| | [Documentation] | RFC1027 : Eth-IPv4 on links TG-DUT1:
| | ...             | On DUT1 configure interface IPv4 address.
| | ...             | Make TG send ARP request to DUT1 interface.
| | ...             | Make TG verify DUT1 does not send ARP reply behalf machine
| | ...             | which IP is above the range.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | When Set Interface Address | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | And Vpp Add Proxy ARP | ${dut1_node} | ${lo_ip4_addr} | ${hi_ip4_addr}
| | And Vpp Proxy ARP Interface Enable | ${dut1_node} | ${dut1_to_tg}
| | Then Send ARP Request should failed | ${tg_node} | ${tg_to_dut1}
| | ...                                 | ${tg_to_dut1_mac} | ${dut1_to_tg_mac}
| | ...                                 | ${tg_to_dut1_ip} | ${fail_test_hi_ip}
