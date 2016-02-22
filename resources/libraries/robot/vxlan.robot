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
| | [Arguments] | ${TG} | ${DUT1} | ${DUT2} | ${VNI}
| | Append Nodes | ${TG} | ${DUT1} | ${DUT2} | ${TG}
| | Compute Path
| | ${tgs_to_dut1} | ${tg}= | Next Interface
| | ${dut1s_to_tg} | ${dut1}= | Next Interface
| | ${dut1s_to_dut2} | ${dut1}= | Next Interface
| | ${dut2s_to_dut1} | ${dut2}= | Next Interface
| | ${dut2s_to_tg} | ${dut2}= | Next Interface
| | ${tgs_to_dut2} | ${tg}= | Next Interface

| | Set Suite Variable | ${tg}
| | Set Suite Variable | ${dut1}
| | Set Suite Variable | ${dut2}
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
| | Setup "${DUT1}" for VXLAN "${VNI}" with "${dut1s_ip_address}/${duts_ip_address_prefix}" on "${dut1s_to_dut2}" and "${dut1s_to_tg}" source "${dut1s_ip_address}" destination "${dut2s_ip_address}"
| | Setup "${DUT2}" for VXLAN "${VNI}" with "${dut2s_ip_address}/${duts_ip_address_prefix}" on "${dut2s_to_dut1}" and "${dut2s_to_tg}" source "${dut2s_ip_address}" destination "${dut1s_ip_address}"
# ip arp table must be filled on both nodes with neighbors address
| | VPP IP Probe | ${DUT1} | ${dut1s_to_dut2} | ${dut2s_ip_address}
| | Sleep | 5


| Setup "${DUT}" for VXLAN "${VNI}" with "${IP}/${PREFIX}" on "${EGRESS}" and "${INGRESS}" source "${SRC_IP}" destination "${DST_IP}"
| | Set Interface State | ${DUT} | ${EGRESS} | up
| | Set Interface State | ${DUT} | ${INGRESS} | up
| | Node "${DUT}" interface "${EGRESS}" has IPv4 address "${IP}" with prefix length "${PREFIX}"
| | ${vxlan_if_index}= | Create VXLAN interface on "${DUT}" with VNI "${VNI}" from "${SRC_IP}" to "${DST_IP}"
| | Setup l2 bridge domain with id "${VNI}" flooding "${1}" forwarding "${1}" learning "${1}" and arp termination "${0}" on vpp node "${DUT}"
| | Add sw interface index "${vxlan_if_index}" to l2 bridge domain with index "${VNI}" and shg "${0}" on vpp node "${DUT}"
| | Add interface "${INGRESS}" to l2 bridge domain with index "${VNI}" and shg "${0}" on vpp node "${DUT}"
