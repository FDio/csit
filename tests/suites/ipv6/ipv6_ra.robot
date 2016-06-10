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

| Force Tags | HW_ENV | VM_ENV | 3_NODE_SINGLE_LINK_TOPO | RA
| Suite Setup | Run Keywords | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| Test Setup | Setup all DUTs before test
| Test Teardown | Show packet trace on all DUTs | ${nodes}
| Documentation | *Provider network FDS related.*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes. In first test case, router advertisement
| ... | is set on DUT1 and then waiting for packets to be recieved on TG.


*** Variables ***
| ${dut1_to_tg_ip}= | 3ffe:62::1
| ${dut1_to_dut2_ip}= | 3ffe:62::2
| ${dut2_to_dut1_ip}= | 3ffe:62::3
| ${prefix_length}= | 64

*** Test Cases ***
| VPP transmits RA from IPv6 enabled interface
| | [Documentation] | Setup IPv6 interace and send router advertisement packet \
| | ...             | from this interface. Subsequently, check received \
| | ...             | packet for correct contents.
| | Given Path for 3-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']} | ${nodes['TG']}
| | And Interfaces in 3-node path are up
| | And Vpp Set If Ipv6 Addr | ${dut1_node}
| | ... | ${dut1_to_tg} | ${dut1_to_tg_ip} | ${prefix_length}
| | When Vpp RA Send After 2 sec | ${dut1_node} | ${dut1_to_tg}
| | Then Receive And Check Router Advertisement Packet
| | ... | ${tg_node} | ${tg_to_dut1} | ${dut1_to_tg_mac}
