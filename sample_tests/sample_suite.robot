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
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.MacSwap
| Library | resources.libraries.python.SetupFramework
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Suite Setup | Run Keywords | Setup Framework | ${nodes}
| ...         | AND          | Setup All DUTs | ${nodes}
| ...         | AND          | Configure all TGs for traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| ...         | AND          | Setup nodes for macswap testing
| Test Setup | Clear interface counters on all vpp nodes in topology | ${nodes}
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *MacSwap test suite.*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG with single link
| ... | between nodes. From this topology only TG and DUT1 nodes are used.
| ... | Test packet is sent from single interface on TG and test wait for
| ... | response on the same TG interface.

*** Keywords ***
| Setup nodes for macswap testing
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']}
| | Compute Path
| | ${tg_port} | ${tg_node}= | First Interface
| | ${dut_port} | ${dut_node}= | Last Interface
| | Set Suite Variable | ${tg_port}
| | Set Suite Variable | ${tg_node}
| | Set Suite Variable | ${dut_port}
| | Set Suite Variable | ${dut_node}
| | Set Interface State | ${tg_node} | ${tg_port} | up
| | Set Interface State | ${dut_node} | ${dut_port} | up
| | All Vpp Interfaces Ready Wait | ${nodes}

| Send and verify macswap on node "${tg_node}" interface "${tg_port}"
| | ${src_ip}= | Set Variable | 1.1.1.1
| | ${dst_ip}= | Set Variable | 2.2.2.2
| | ${src_mac}= | Set Variable | 01:00:00:00:00:01
| | ${dst_mac}= | Set Variable | 01:00:00:00:00:02
| | ${args}= | Traffic Script Gen Arg | ${tg_port} | ${tg_port} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | macswap_check.py | ${tg_node} | ${args}

*** Test Cases ***
| VPP macswap plugin swaps MAC addresses
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO | VM_ENV
| | Enable Disable macswap vat exec | ${dut_node} | ${dut_port}
| | Send and verify macswap on node "${tg_node}" interface "${tg_port}"
