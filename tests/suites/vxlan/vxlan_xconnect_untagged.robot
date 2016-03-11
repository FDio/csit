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
| Documentation | VXLAN tunnel untagged traffic tests using xconnect.
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/vxlan.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Suite Setup | Run Keywords | Setup all DUTs before test
| ...         | AND          | Setup all TGs before traffic script
| ...         | AND          | Setup VXLAN tunnel on nodes | ${nodes['TG']}
|             | ...          | ${nodes['DUT1']} | ${nodes['DUT2']} | ${VNI}
| Suite Teardown | Show Packet Trace on All DUTs | ${nodes}

*** Variables ***
| ${VNI}= | 24

*** Test Cases ***
| VPP can pass IPv4 bidirectionally through VXLAN tunnel using l2-xconnect
| | Send and receive ICMPv4 | ${nodes['TG']} | ${tgs_to_dut1} | ${tgs_to_dut2}
| | Send and receive ICMPv4 | ${nodes['TG']} | ${tgs_to_dut2} | ${tgs_to_dut1}
