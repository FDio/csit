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
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/l2_xconnect.robot
| Library  | resources.libraries.python.L2Util
| Library  | resources.libraries.python.IPUtil
| Library  | resources.libraries.python.IPv4Util
| Library  | resources.libraries.python.IPv4Setup
| Library  | resources.libraries.python.NodePath

*** Keywords ***
| Path for VXLAN testing is set
| | [Documentation] | *Compute path for VXLAN testing on nodes.*
| | ...
| | ... | _Set testcase variables with interfaces and nodes:_
| | ... | - ${tgs_to_dut1}
| | ... | - ${dut1s_to_tg}
| | ... | - ${tgs_to_dut2}
| | ... | - ${dut2s_to_tg}
| | ... | - ${dut1s_to_dut2}
| | ... | - ${dut2s_to_dut1}
| | ... | - ${tg}
| | ... | - ${dut1}
| | ... | - ${dut2}
| | ...
| | [Arguments] | ${TG} | ${DUT1} | ${DUT2}
| | Append Nodes | ${TG} | ${DUT1} | ${DUT2} | ${TG}
| | Compute Path
| | ${tgs_to_dut1} | ${tg}= | Next Interface
| | ${dut1s_to_tg} | ${dut1}= | Next Interface
| | ${dut1s_to_dut2} | ${dut1}= | Next Interface
| | ${dut2s_to_dut1} | ${dut2}= | Next Interface
| | ${dut2s_to_tg} | ${dut2}= | Next Interface
| | ${tgs_to_dut2} | ${tg}= | Next Interface
| | Set Test Variable | ${tgs_to_dut1}
| | Set Test Variable | ${dut1s_to_tg}
| | Set Test Variable | ${tgs_to_dut2}
| | Set Test Variable | ${dut2s_to_tg}
| | Set Test Variable | ${dut1s_to_dut2}
| | Set Test Variable | ${dut2s_to_dut1}
| | Set Test Variable | ${tg}
| | Set Test Variable | ${dut1}
| | Set Test Variable | ${dut2}

| Interfaces in path are up
| | [Documentation] | *Set UP state on interfaces in path on nodes.*
| | ...
| | Set Interface State | ${tg} | ${tgs_to_dut1} | up
| | Set Interface State | ${tg} | ${tgs_to_dut2} | up
| | Set Interface State | ${dut1} | ${dut1s_to_tg} | up
| | Set Interface State | ${dut1} | ${dut1s_to_dut2} | up
| | Set Interface State | ${dut2} | ${dut2s_to_tg} | up
| | Set Interface State | ${dut2} | ${dut2s_to_dut1} | up
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Vpp Node Interfaces Ready Wait | ${dut2}

| IP addresses are set on interfaces
| | [Documentation] | *Set IPv4 addresses on interfaces on DUTs.*
| | ... | If interface index is None then is determines with Get Interface Sw Index
| | ... | It also executes VPP IP Probe to determine MACs to IPs on DUTs
| | ...
| | ... | _Set testcase variables with IP addresses and prefix length:_
| | ... | - ${dut1s_ip_address}
| | ... | - ${dut2s_ip_address}
| | ... | - ${duts_ip_address_prefix}
| | ...
| | [Arguments] | ${DUT1} | ${DUT1_INT_NAME} | ${DUT1_INT_INDEX}
| | ...         | ${DUT2} | ${DUT2_INT_NAME} | ${DUT2_INT_INDEX}
| | Set Test Variable | ${dut1s_ip_address} | 172.16.0.1
| | Set Test Variable | ${dut2s_ip_address} | 172.16.0.2
| | Set Test Variable | ${duts_ip_address_prefix} | 24
| | ${DUT1_INT_INDEX}= | Run Keyword If | ${DUT1_INT_INDEX} is None
| |                    | ... | Get Interface Sw Index | ${DUT1} | ${DUT1_INT_NAME}
| |                    | ... | ELSE | Set Variable | ${DUT1_INT_INDEX}
| | ${DUT2_INT_INDEX}= | Run Keyword If | ${DUT2_INT_INDEX} is None
| |                    | ... | Get Interface Sw Index | ${DUT2} | ${DUT2_INT_NAME}
| |                    | ... | ELSE | Set Variable | ${DUT2_INT_INDEX}
| | Set Interface Address | ${DUT1} | ${DUT1_INT_INDEX}
| | ... | ${dut1s_ip_address} | ${duts_ip_address_prefix}
| | Set Interface Address | ${DUT2} | ${DUT2_INT_INDEX}
| | ... | ${dut2s_ip_address} | ${duts_ip_address_prefix}
#| | VPP IP Probe | ${DUT1} | ${DUT1_INT_NAME} | ${dut2s_ip_address}
#| | VPP IP Probe | ${DUT2} | ${DUT2_INT_NAME} | ${dut1s_ip_address}
| | ${dut1s_mac_address}= | Get Interface Mac | ${DUT1} | ${dut1s_to_dut2}
| | ${dut2s_mac_address}= | Get Interface Mac | ${DUT2} | ${dut2s_to_dut1}
| | Setup Arp On Dut | ${DUT1} | ${DUT1_INT_INDEX} | ${dut2s_ip_address} | ${dut2s_mac_address}
| | Setup Arp On Dut | ${DUT2} | ${DUT2_INT_INDEX} | ${dut1s_ip_address} | ${dut1s_mac_address}

| VXLAN interface is created
| | [Arguments] | ${DUT} | ${VNI} | ${SRC_IP} | ${DST_IP}
| | Create VXLAN interface | ${DUT} | ${VNI} | ${SRC_IP} | ${DST_IP}

| Interfaces are added to BD
| | [Arguments] | ${DUT} | ${BID} | ${INTERFACE_1} | ${INTERFACE_2}
| | Vpp Add L2 Bridge Domain | ${DUT} | ${BID} | ${INTERFACE_1} | ${INTERFACE_2}

| Interfaces are added to xconnect
| | [Arguments] | ${DUT} | ${INTERFACE_1} | ${INTERFACE_2}
| | L2 setup xconnect on DUT | ${DUT} | ${INTERFACE_1} | ${INTERFACE_2}

| Vlan interfaces for VXLAN are created
| | [Documentation] | *Create VLAN subinterface on interfaces on DUTs with given VLAN ID.*
| | ...
| | ... | _Set testcase variables with name and index of created interfaces:_
| | ... | - ${dut1s_vlan_name}
| | ... | - ${dut1s_vlan_index}
| | ... | - ${dut2s_vlan_name}
| | ... | - ${dut2s_vlan_index}
| | ...
| | [Arguments] | ${VLAN} | ${DUT1} | ${INT1} | ${DUT2} | ${INT2}
| | ${dut1s_vlan_name} | ${dut1s_vlan_index}= | Create Vlan Subinterface
| |                    | ...                  | ${DUT1} | ${INT1} | ${VLAN}
| | ${dut2s_vlan_name} | ${dut2s_vlan_index}= | Create Vlan Subinterface
| |                    | ...                  | ${DUT2} | ${INT2} | ${VLAN}
| | Set Interface State | ${DUT1} | ${dut1s_vlan_index} | up
| | Set Interface State | ${DUT2} | ${dut2s_vlan_index} | up
| | Vpp Node Interfaces Ready Wait | ${DUT1}
| | Vpp Node Interfaces Ready Wait | ${DUT2}
| | Set Test Variable | ${dut1s_vlan_name}
| | Set Test Variable | ${dut1s_vlan_index}
| | Set Test Variable | ${dut2s_vlan_name}
| | Set Test Variable | ${dut2s_vlan_index}
