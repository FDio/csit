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
| Documentation | TODO: rewrite with generic path keywords
| Library | resources.libraries.python.topology.Topology
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/ipv4.robot
| Suite Setup | Run Keywords | Setup all DUTs before test
| ...         | AND          | Setup all TGs before traffic script
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}
| ...         | AND          | Setup nodes for IPv4 testing
| Test Setup | Clear interface counters on all vpp nodes in topology | ${nodes}

*** Test Cases ***

| VPP replies to ICMPv4 echo request
| | TG interface "${nodes['TG']['interfaces']['port3']['name']}" can route to node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port1']['name']}" "0" hops away using IPv4
| | Vpp dump stats table | ${nodes['DUT1']}
| | Check ipv4 interface counter | ${nodes['DUT1']} | ${nodes['DUT1']['interfaces']['port1']['name']} | ${1}

| TG can route to DUT egress interface
| | TG interface "${nodes['TG']['interfaces']['port3']['name']}" can route to node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port3']['name']}" "0" hops away using IPv4
| | Vpp dump stats table | ${nodes['DUT1']}
| | Check ipv4 interface counter | ${nodes['DUT1']} | ${nodes['DUT1']['interfaces']['port1']['name']} | ${1}

| TG can route to DUT2 through DUT1
| | TG interface "${nodes['TG']['interfaces']['port3']['name']}" can route to node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port3']['name']}" "1" hops away using IPv4
| | Vpp dump stats table | ${nodes['DUT1']}
| | Check ipv4 interface counter | ${nodes['DUT1']} | ${nodes['DUT1']['interfaces']['port1']['name']} | ${1}
| | Check ipv4 interface counter | ${nodes['DUT1']} | ${nodes['DUT1']['interfaces']['port3']['name']} | ${1}
| | Vpp dump stats table | ${nodes['DUT2']}
| | Check ipv4 interface counter | ${nodes['DUT2']} | ${nodes['DUT2']['interfaces']['port3']['name']} | ${1}

| TG can route to DUT2 egress interface through DUT1
| | TG interface "${nodes['TG']['interfaces']['port3']['name']}" can route to node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port1']['name']}" "1" hops away using IPv4
| | Vpp dump stats table | ${nodes['DUT1']}
| | Check ipv4 interface counter | ${nodes['DUT1']} | ${nodes['DUT1']['interfaces']['port1']['name']} | ${1}
| | Check ipv4 interface counter | ${nodes['DUT1']} | ${nodes['DUT1']['interfaces']['port3']['name']} | ${1}
| | Vpp dump stats table | ${nodes['DUT2']}
| | Check ipv4 interface counter | ${nodes['DUT2']} | ${nodes['DUT2']['interfaces']['port3']['name']} | ${1}

| TG can route to TG through DUT1 and DUT2
| | TG interface "${nodes['TG']['interfaces']['port3']['name']}" can route to node "${nodes['TG']}" interface "${nodes['TG']['interfaces']['port5']['name']}" "2" hops away using IPv4
| | Vpp dump stats table | ${nodes['DUT1']}
| | Check ipv4 interface counter | ${nodes['DUT1']} | ${nodes['DUT1']['interfaces']['port1']['name']} | ${1}
| | Check ipv4 interface counter | ${nodes['DUT1']} | ${nodes['DUT1']['interfaces']['port3']['name']} | ${1}
| | Vpp dump stats table | ${nodes['DUT2']}
| | Check ipv4 interface counter | ${nodes['DUT2']} | ${nodes['DUT2']['interfaces']['port3']['name']} | ${1}
| | Check ipv4 interface counter | ${nodes['DUT2']} | ${nodes['DUT2']['interfaces']['port1']['name']} | ${1}

| VPP can process ICMP echo request from min to max packet size with 1B increment
| | Ipv4 icmp echo sweep | ${nodes['TG']} | ${nodes['DUT1']}
| | ...                  | ${nodes['TG']['interfaces']['port3']['name']}
| | ...                  | ${nodes['DUT1']['interfaces']['port1']['name']}

| VPP responds to ARP request
| | Send ARP request and validate response | ${nodes['TG']} | ${nodes['DUT1']}
