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
| Resource | resources/libraries/robot/bridge_domain.robot
| Force Tags | HW_ENV | VM_ENV
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.NodePath
| Variables | resources/libraries/python/topology.py
| Suite Setup | Setup all TGs before traffic script
| Test Setup | Setup all DUTs before test

*** Test Cases ***

| VPP reports interfaces
| | VPP reports interfaces on | ${nodes['DUT1']}

| Vpp forwards packets via L2 bridge domain 2 ports
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Compute Path | always_same_link=${FALSE}
| | ${src_if} | ${tmp}= | First Interface
| | ${dst_if} | ${tmp}= | Last Interface
| | ${bd_if1} | ${tmp}= | First Ingress Interface
| | ${bd_if2} | ${tmp}= | Last Egress Interface
| | Vpp l2bd forwarding setup | ${nodes['DUT1']} | ${bd_if1} | ${bd_if2}
| | Send and receive traffic | ${nodes['TG']} | ${src_if} | ${dst_if}

| Vpp forwards packets via L2 bridge domain in circular topology
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...          | ${nodes['TG']}
| | Compute Path
| | ${src_if} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${dst_if} | ${tg}= | Next Interface
| | Vpp l2bd forwarding setup | ${dut1} | ${dut1_if1} | ${dut1_if2}
| | Vpp l2bd forwarding setup | ${dut2} | ${dut2_if1} | ${dut2_if2}
| | Send and receive traffic | ${tg} | ${src_if} | ${dst_if}

| Vpp forwards packets via L2 bridge domain in circular topology with static L2FIB entries
| | [Tags] | 3_NODE_SINGLE_LINK_TOPO
| | Append Nodes | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ...          | ${nodes['TG']}
| | Compute Path
| | ${src_if} | ${tg}= | Next Interface
| | ${dut1_if1} | ${dut1}= | Next Interface
| | ${dut1_if2} | ${dut1}= | Next Interface
| | ${dut2_if1} | ${dut2}= | Next Interface
| | ${dut2_if2} | ${dut2}= | Next Interface
| | ${dst_if} | ${tg}= | Next Interface
| | ${mac}= | Get Interface Mac | ${tg} | ${dst_if}
| | Vpp l2bd forwarding setup | ${dut1} | ${dut1_if1} | ${dut1_if2} | ${FALSE}
| | ...                       | ${mac}
| | Vpp l2bd forwarding setup | ${dut2} | ${dut2_if1} | ${dut2_if2} | ${FALSE}
| | ...                       | ${mac}
| | Send and receive traffic | ${tg} | ${src_if} | ${dst_if}
