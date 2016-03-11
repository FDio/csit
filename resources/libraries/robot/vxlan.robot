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
| Library  | Collections
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Library  | resources.libraries.python.L2Util
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.IPv4Util
| Library  | resources.libraries.python.IPv4Setup
| Library  | resources.libraries.python.InterfaceSetup
| Library  | resources.libraries.python.InterfaceUtil
| Library  | resources.libraries.python.topology.Topology
| Library  | resources.libraries.python.NodePath


*** Keywords ***
| Setup VXLAN tunnel on nodes
| | [Arguments] | ${TG} | ${DUT1} | ${DUT2} | ${VNI} | ${BID}=${NONE}
| | ...         | ${VLANID}=${NONE}
| | Append Nodes | ${TG} | ${DUT1} | ${DUT2} | ${TG}
| | Compute Path
| | ${tgs_to_dut1} | ${tg}= | Next Interface
| | ${dut1s_to_tg} | ${dut1}= | Next Interface
| | ${dut1s_to_dut2} | ${dut1}= | Next Interface
| | ${dut2s_to_dut1} | ${dut2}= | Next Interface
| | ${dut2s_to_tg} | ${dut2}= | Next Interface
| | ${tgs_to_dut2} | ${tg}= | Next Interface
| | Set Suite Variable | ${tgs_to_dut1}
| | Set Suite Variable | ${dut1s_to_tg}
| | Set Suite Variable | ${tgs_to_dut2}
| | Set Suite Variable | ${dut2s_to_tg}
| | Set Suite Variable | ${dut1s_to_dut2}
| | Set Suite Variable | ${dut2s_to_dut1}
| | Set Suite Variable | ${dut1s_ip_address} | 172.16.0.1
| | Set Suite Variable | ${dut2s_ip_address} | 172.16.0.2
| | Set Suite Variable | ${duts_ip_address_prefix} | 24
| | Set Interface State | ${TG} | ${tgs_to_dut1} | up
| | Set Interface State | ${TG} | ${tgs_to_dut2} | up
| | ${vxlan_dut1}= | Setup VXLAN on DUT | ${DUT1} | ${VNI} | ${dut1s_ip_address}
| | ...                                 | ${dut2s_ip_address} | ${dut1s_to_tg}
| | ...                                 | ${dut1s_to_dut2} | ${dut1s_ip_address}
| | ...                                 | ${duts_ip_address_prefix}
| | ...                                 | ${dut2s_ip_address} | ${BID} | ${VLANID}
| | Set Suite Variable | ${vxlan_dut1}
| | ${vxlan_dut2}= | Setup VXLAN on DUT | ${DUT2} | ${VNI} | ${dut2s_ip_address}
| | ...                                 | ${dut1s_ip_address} | ${dut2s_to_tg}
| | ...                                 | ${dut2s_to_dut1} | ${dut2s_ip_address}
| | ...                                 | ${duts_ip_address_prefix}
| | ...                                 | ${dut1s_ip_address} | ${BID} | ${VLANID}
| | Set Suite Variable | ${vxlan_dut2}


| Setup VXLAN on DUT
| | [Arguments] | ${DUT} | ${VNI} | ${SRC_IP} | ${DST_IP} | ${INGRESS}
| | ...         | ${EGRESS} | ${IP} | ${PREFIX} | ${IP2} | ${BID} | ${VLANID}
| | Set Interface State | ${DUT} | ${EGRESS} | up
| | Set Interface State | ${DUT} | ${INGRESS} | up
| | Vpp Node Interfaces Ready Wait | ${DUT}
| | ${EGRESS_INT_NAME} | ${EGRESS_INT_INDEX}= | Run Keyword If | ${VLANID} == ${NONE}
| | | | ... | Return Interface and Index | ${DUT} | ${EGRESS}
| | | ... | ELSE | Create Vlan Subinterface | ${DUT} | ${EGRESS} | ${VLANID}
| | Set Interface Address | ${DUT} | ${EGRESS_INT_INDEX} | ${IP} | ${PREFIX}
| | VPP IP Probe | ${DUT} | ${EGRESS_INT_NAME} | ${IP2}
| | ${vxlan_if_index}= | Create VXLAN interface | ${DUT} | ${VNI} | ${SRC_IP}
| | ...                                         | ${DST_IP}
| | Run Keyword If | ${BID} == ${NONE} |
| | | ... | L2 setup xconnect on DUT | ${DUT} | ${INGRESS} | ${vxlan_if_index}
| | ... | ELSE | L2 Setup Bridge Domain on DUT | ${DUT} | ${VNI} | ${INGRESS}
| | | ... | ${vxlan_if_index}
| | [Return] | ${vxlan_if_index}
