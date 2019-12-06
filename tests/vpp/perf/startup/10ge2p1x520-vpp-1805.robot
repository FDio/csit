# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/shared/default.robot
|
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| ... | NIC_Intel-X520-DA2 | DRV_VFIO_PCI | VPP_1805
|
| Suite Setup | Setup suite single link
| Test Setup | Setup test
| Test Teardown | Tear down test
|
| Documentation | *Startup test with show pci in a loop*
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology \
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* No packets sent.
| ... | *[Cfg] DUT configuration:* Default config, no post-startup actions.
| ... | *[Ver] TG verification:* No TG, but verifying VPP PID.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | Intel-X520-DA2
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}

*** Test Cases ***
| tc01-vpp-1805-dev
| | Loop vppctl show pci | ${nodes}
| | Get Core Files on All Nodes | ${nodes}
