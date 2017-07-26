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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/nsh_sfc/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | FUNCTEST
| Suite Setup | Run Keywords
| ... | Configure all DUTs before test | AND
| ... | Configure all TGs for traffic script | AND
| ... | Update All Interface Data On All Nodes | ${nodes} | AND
| ... | Setup DUT nodes for 'NSH Over Ethernet' functional testing
| Test Setup | Run Keywords | Save VPP PIDs | AND
| ... | Reset VAT History On All DUTs | ${nodes} | AND
| ... | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Run Keywords
| ... | Show packet trace on all DUTs | ${nodes} | AND
| ... | Show VAT History On All DUTs | ${nodes} | AND
| ... | Verify VPP PID in Teardown
| Documentation | *NSH Over Ethernet test cases*
| ...
| ... | Test the NSH Over Ethernet functional. DUT run the VPP with NSH
| ... | SFC Plugin, TG send a Ethernet+NSH packet to the DUT,
| ... | if the packet match the NSH SFC rules, the SFC Proxy will
| ... | pop the VxLAN-GPE and NSH protocol, then encapsulate with the
| ... | VxLAN protocol. DUT will loopback the packet to the TG.
| ... | The TG will capture this VxLAN packet and check the packet
| ... | field is correct.

*** Test Cases ***
| TC01: NSH Over Ethernet functional test with 152B frame size
| | [Documentation]
| | ... | Make TG send 152 Bytes VxLAN-GPE+NSH packet to DUT ingress interface.\
| | ... | Make TG verify SFC NSH Over Ethernet functional is correct.
| | ${frame_size}= | Set Variable | ${152}
| | Node "${tg_node}" interface "${tg_to_dut_if1}" send "${frame_size}" Bytes packet to node "${dut_node}" interface "${dut_to_tg_if1}" for "NSH Over Ethernet" test

| TC02: NSH Over Ethernet functional test with 256B frame size
| | [Documentation]
| | ... | Make TG send 256 Bytes VxLAN-GPE+NSH packet to DUT ingress interface.\
| | ... | Make TG verify SFC NSH Over Ethernet functional is correct.
| | ${frame_size}= | Set Variable | ${256}
| | Node "${tg_node}" interface "${tg_to_dut_if1}" send "${frame_size}" Bytes packet to node "${dut_node}" interface "${dut_to_tg_if1}" for "NSH Over Ethernet" test

| TC03: NSH Over Ethernet functional test with 512B frame size
| | [Documentation]
| | ... | Make TG send 512 Bytes VxLAN-GPE+NSH packet to DUT ingress interface.\
| | ... | Make TG verify SFC NSH Over Ethernet functional is correct.
| | ${frame_size}= | Set Variable | ${512}
| | Node "${tg_node}" interface "${tg_to_dut_if1}" send "${frame_size}" Bytes packet to node "${dut_node}" interface "${dut_to_tg_if1}" for "NSH Over Ethernet" test

| TC04: NSH Over Ethernet functional test with 1024B frame size
| | [Documentation]
| | ... | Make TG send 1024 Bytes VxLAN-GPE+NSH packet to DUT ingress interface.\
| | ... | Make TG verify SFC NSH Over Ethernet functional is correct.
| | ${frame_size}= | Set Variable | ${1024}
| | Node "${tg_node}" interface "${tg_to_dut_if1}" send "${frame_size}" Bytes packet to node "${dut_node}" interface "${dut_to_tg_if1}" for "NSH Over Ethernet" test

| TC05: NSH Over Ethernet functional test with 1280B frame size
| | [Documentation]
| | ... | Make TG send 1280 Bytes VxLAN-GPE+NSH packet to DUT ingress interface.\
| | ... | Make TG verify SFC NSH Over Ethernet functional is correct.
| | ${frame_size}= | Set Variable | ${1280}
| | Node "${tg_node}" interface "${tg_to_dut_if1}" send "${frame_size}" Bytes packet to node "${dut_node}" interface "${dut_to_tg_if1}" for "NSH Over Ethernet" test

| TC06: NSH Over Ethernet functional test with 1518B frame size
| | [Documentation]
| | ... | Make TG send 1518 Bytes VxLAN-GPE+NSH packet to DUT ingress interface.\
| | ... | Make TG verify SFC NSH Over Ethernet functional is correct.
| | ${frame_size}= | Set Variable | ${1518}
| | Node "${tg_node}" interface "${tg_to_dut_if1}" send "${frame_size}" Bytes packet to node "${dut_node}" interface "${dut_to_tg_if1}" for "NSH Over Ethernet" test
