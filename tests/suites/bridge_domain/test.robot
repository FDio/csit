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
| Test Setup | Setup all DUTs before test
| Library | resources.libraries.python.topology.Topology
| Variables | resources/libraries/python/topology.py
| Force Tags | 3_NODE_DOUBLE_LINK_TOPO

*** Test Cases ***

| VPP reports interfaces
| | VPP reports interfaces on | ${nodes['DUT1']}

| Vpp forwards packets via L2 bridge domain 2 ports
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | ${TG_DUT_links}= | Get active links connecting "${nodes['TG']}" and "${nodes['DUT1']}"
| | Setup l2 bridge on node "${nodes['DUT1']}" via links "${TG_DUT_links}"
| | Send traffic on node "${nodes['TG']}" from link "${TG_DUT_links[0]}" to link "${TG_DUT_links[1]}"

| Vpp forwards packets via L2 bridge domain in circular topology
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO
| | ${tg}= | Set Variable | ${nodes['TG']}
| | ${dut1}= | Set Variable | ${nodes['DUT1']}
| | ${dut2}= | Set Variable | ${nodes['DUT2']}
| | ${tg_links}= | Setup TG "${tg}" DUT1 "${dut1}" and DUT2 "${dut2}" for 3 node l2 bridge domain test
| | Send traffic on node "${nodes['TG']}" from link "${tg_links[0]}" to link "${tg_links[1]}"
