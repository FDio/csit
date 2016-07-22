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
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/ipv6.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Resource | resources/libraries/robot/traffic.robot
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.Trace

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Run Keywords | Show packet trace on all DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| Documentation | *IPv6 Router Advertisement test cases*
| ...
| ... | RFC4861 Neighbor Discovery. Encapsulations: Eth-IPv6-RA on links
| ... | TG-DUT1. IPv6 Router Advertisement tests use 3-node topology TG - DUT1 -
| ... | DUT2 - TG with one link between the nodes. DUT1 and DUT2 are configured
| ... | with IPv6 routing and static routes. TG verifies received RA packets.


*** Variables ***
| ${dut1_to_tg_ip}= | 3ffe:62::1
| ${prefix_length}= | 64

*** Test Cases ***
| TC01: DUT transmits RA on IPv6 enabled interface
| | [Documentation]
| | ... | On DUT1 configure IPv6 interface on the link to TG. Make TG wait\
| | ... | for IPv6 Router Advertisement packet to be sent out by DUT1 and
| | ... | verify the received RA packet is correct.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Vpp Set If Ipv6 Addr | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | When Vpp RA Send After Interval | ${dut1_node} | ${dut1_to_tg}
| | Then Receive And Check Router Advertisement Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${dut1_to_tg_mac}
