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
| VXLAN tunnel test environment initialized on nodes
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
| | Set Test Variable | ${tgs_to_dut1}
| | Set Test Variable | ${dut1s_to_tg}
| | Set Test Variable | ${tgs_to_dut2}
| | Set Test Variable | ${dut2s_to_tg}
| | Set Test Variable | ${dut1s_to_dut2}
| | Set Test Variable | ${dut2s_to_dut1}
| | Set Test Variable | ${dut1s_ip_address} | 172.16.0.1
| | Set Test Variable | ${dut2s_ip_address} | 172.16.0.2
| | Set Test Variable | ${duts_ip_address_prefix} | 24
| | Set Interface State | ${TG} | ${tgs_to_dut1} | up
| | Set Interface State | ${TG} | ${tgs_to_dut2} | up
| | Set Interface State | ${DUT1} | ${dut1s_to_tg} | up
| | Set Interface State | ${DUT1} | ${dut1s_to_dut2} | up
| | Set Interface State | ${DUT2} | ${dut2s_to_tg} | up
| | Set Interface State | ${DUT2} | ${dut2s_to_dut1} | up
| | Vpp Node Interfaces Ready Wait | ${DUT1}
| | Vpp Node Interfaces Ready Wait | ${DUT2}
| | ${vxlan_dut1}= | Suite specific VXLAN tunnel test environment setup on DUT
| | ...            | ${DUT1} | ${VNI} | ${dut1s_ip_address}
| | ...            | ${dut2s_ip_address} | ${dut1s_to_tg} | ${dut1s_to_dut2}
| | ...            | ${dut1s_ip_address} | ${duts_ip_address_prefix}
| | ...            | ${dut2s_ip_address} | ${BID} | ${VLANID}
| | Set Test Variable | ${vxlan_dut1}
| | ${vxlan_dut2}= | Suite specific VXLAN tunnel test environment setup on DUT
| | ...            | ${DUT2} | ${VNI} | ${dut2s_ip_address}
| | ...            | ${dut1s_ip_address} | ${dut2s_to_tg} | ${dut2s_to_dut1}
| | ...            | ${dut2s_ip_address} | ${duts_ip_address_prefix}
| | ...            | ${dut1s_ip_address} | ${BID} | ${VLANID}
| | Set Test Variable | ${vxlan_dut2}
