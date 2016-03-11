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
| | [Arguments] | ${TG} | ${DUT1} | ${DUT2} | ${VNI} | ${KW}
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
# TODO: replace with address generator
| | Set Suite Variable | ${dut1s_ip_address} | 172.16.0.1
| | Set Suite Variable | ${dut2s_ip_address} | 172.16.0.2
| | Set Suite Variable | ${duts_ip_address_prefix} | 24
| | Set Interface State | ${TG} | ${tgs_to_dut1} | up
| | Set Interface State | ${TG} | ${tgs_to_dut2} | up
| | Run Keyword | ${KW} | ${DUT1} | ${VNI} | ${dut1s_ip_address}
| | ...                 | ${dut2s_ip_address} | ${dut1s_to_tg} | ${dut1s_to_dut2}
| | ...                 | ${dut1s_ip_address} | ${duts_ip_address_prefix}
| | Run Keyword | ${KW} | ${DUT2} | ${VNI} | ${dut2s_ip_address}
| | ...                 | ${dut1s_ip_address} | ${dut2s_to_tg} | ${dut2s_to_dut1}
| | ...                 | ${dut2s_ip_address} | ${duts_ip_address_prefix}
| | @{test_nodes}= | Create list | ${DUT1} | ${DUT2}
| | Vpp Nodes Interfaces Ready Wait | ${test_nodes}
# ip arp table must be filled on both nodes with neighbors address
| | VPP IP Probe | ${DUT1} | ${dut1s_to_dut2} | ${dut2s_ip_address}
| | Show traces | ${DUT1}
| | Show traces | ${DUT2}

| Setup DUT for VXLAN using BD
| | [Arguments] | ${DUT} | ${VNI} | ${SRC_IP} | ${DST_IP} | ${INGRESS}
| | ...         | ${EGRESS} | ${IP} | ${PREFIX}
| | Set Interface State | ${DUT} | ${EGRESS} | up
| | Set Interface State | ${DUT} | ${INGRESS} | up
| | Set Interface Address | ${DUT} | ${EGRESS} | ${IP} | ${PREFIX}
| | ${vxlan_if_index}= | Create VXLAN interface | ${DUT} | ${VNI} | ${SRC_IP}
| | ...                                         | ${DST_IP}
| | Create L2 BD | ${DUT} | ${VNI}
| | Add sw if index To L2 BD | ${DUT} | ${vxlan_if_index} | ${VNI}
| | Add Interface To L2 BD | ${DUT} | ${INGRESS} | ${VNI}

| Setup DUT for VXLAN using BD with VLAN
| | [Arguments] | ${DUT} | ${VNI} | ${SRC_IP} | ${DST_IP} | ${INGRESS}
| | ...         | ${EGRESS} | ${IP} | ${PREFIX}
| | Set Interface State | ${DUT} | ${INGRESS} | up
| | Set Interface State | ${DUT} | ${EGRESS} | up
| | ${EGRESS_VLAN_NAME} | ${EGRESS_VLAN_INDEX}= | Create Vlan Subinterface
| | ...                                         | ${DUT} | ${EGRESS} | ${10}
#| | update vpp interface data on node | ${DUT}
| | Set Interface State | ${DUT} | ${EGRESS_VLAN_INDEX} | up
| | Set Interface Address | ${DUT} | ${EGRESS_VLAN_INDEX} | ${IP} | ${PREFIX}
| | ${vxlan_if_index}= | Create VXLAN interface | ${DUT} | ${VNI} | ${SRC_IP}
| | ...                                         | ${DST_IP}
| | Create L2 BD | ${DUT} | ${VNI}
| | Add sw if index To L2 BD | ${DUT} | ${vxlan_if_index} | ${VNI}
| | Add Interface To L2 BD | ${DUT} | ${INGRESS} | ${VNI}
#| | Sleep | 5
| | VPP IP Probe | ${DUT} | ${EGRESS_VLAN_NAME} | ${IP}
