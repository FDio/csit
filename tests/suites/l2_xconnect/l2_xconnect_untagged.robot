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
| Resource | resources/libraries/robot/l2_xconnect.robot
| Force Tags | 3_NODE_SINGLE_LINK_TOPO
| Suite Setup | Run Keywords | Setup all DUTs before test
| ...         | AND          | Setup all TGs before traffic script
| ...         | AND          | Interfaces on all DUTs are in "up" state

*** Test Cases ***

| VPP forwards packets through xconnect in circular topology
| | Given L2 setup xconnect on DUTs
| | ${tg}= | Set Variable | ${nodes['TG']}
| | ${dut1}= | Set Variable | ${nodes['DUT1']}
| | ${dut2}= | Set Variable | ${nodes['DUT2']}
| | ${tg_links}= | Get traffic links between TG "${tg}" and DUT1 "${dut1}" and DUT2 "${dut2}"
| | Sleep | 10 | Work around VPP interface up taking too long.
| | Send traffic on node "${nodes['TG']}" from link "${tg_links[0]}" to link "${tg_links[1]}"

