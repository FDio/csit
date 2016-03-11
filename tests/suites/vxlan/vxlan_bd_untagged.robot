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
| Documentation | VXLAN tunnel over untagged IPv4 traffic tests using bridge domain.
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/vxlan.robot
| Resource | resources/libraries/robot/l2_traffic.robot
| Library  | resources.libraries.python.Trace
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | HW_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Show Packet Trace on All DUTs | ${nodes}

*** Variables ***
| ${VNI}= | 23

*** Test Cases ***
| VPP can pass IPv4 bidirectionally through VXLAN
| | Given Prepare VXLAN tunnel test environment on nodes
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
| | ... | ${VNI} | BID=${VNI}
| | Then Send and receive ICMPv4 | ${nodes['TG']} | ${tgs_to_dut1} | ${tgs_to_dut2}
| | Then Send and receive ICMPv4 | ${nodes['TG']} | ${tgs_to_dut2} | ${tgs_to_dut1}

*** Keywords ***
| Prepare VXLAN tunnel test environment on DUT
| | [Arguments] | ${DUT} | ${VNI} | ${SRC_IP} | ${DST_IP} | ${INGRESS}
| | ...         | ${EGRESS} | ${IP} | ${PREFIX} | ${IP2} | ${BID} | ${VLANID}
| | Set Interface State | ${DUT} | ${EGRESS} | up
| | Set Interface State | ${DUT} | ${INGRESS} | up
| | Vpp Node Interfaces Ready Wait | ${DUT}
| | Set Interface Address | ${DUT} | ${EGRESS} | ${IP} | ${PREFIX}
| | VPP IP Probe | ${DUT} | ${EGRESS} | ${IP2}
| | ${vxlan_if_index}= | Create VXLAN interface | ${DUT} | ${VNI} | ${SRC_IP}
| | ...                | ${DST_IP}
| | Vpp Add L2 Bridge Domain | ${DUT} | ${VNI} | ${INGRESS} | ${vxlan_if_index}
| | [Return] | ${vxlan_if_index}
