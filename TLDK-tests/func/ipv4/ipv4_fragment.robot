# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.TLDK.UdpTest
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/counters.robot
| Resource | resources/libraries/robot/TLDK/TLDKUtils.robot
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | FUNCTEST | TLDK
| Documentation | *TLDK IPv4 fragment test suite.*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG with single link
| ... | between nodes. From this topology only TG and DUT1 nodes are used.
| ... | This test case just use the pcap file for the UDP functional test.

*** Variables ***
| ${tc01_file_prefix}= | test_ipv4_fragment

*** Test Cases ***
| TC01: TLDK IPv4 fragment test case
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | And Pick out the port used to execute test
| | And Get the pcap data | ${tc01_file_prefix}
| | When Exec the udpfwd test | ${dut_node} | ${dut_port}
| | ... | ${tc01_file_prefix} | ${dest_ip} | ${is_ipv4}
| | ${checksum}= | Get the test result | ${dut_node}
| | ... | ${tc01_file_prefix}
| | ${result}= | Convert To Integer | ${checksum}
| | Then Should Be Equal As Integers | ${result} | 990
