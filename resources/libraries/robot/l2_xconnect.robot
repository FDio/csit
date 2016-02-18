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

| Library | resources.libraries.python.VatExecutor
| Library | resources.libraries.python.CrossConnectSetup
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficScriptExecutor
| Variables | resources/libraries/python/constants.py

*** Keywords ***

| L2 setup xconnect on DUT
| | [Documentation] | Setup Bidirectional Cross Connect on DUTs
| | [Arguments] | ${node} | ${if1} | ${if2} |
| | Vpp Setup Bidirectional Cross Connect | ${node} | ${if1} | ${if2}

| Send and receive traffic
| | [Documentation] | Send traffic from source interface to destination interface
| | [Arguments] | ${tg_node} | ${src_int} | ${dst_int}
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${src_int}
| | ${dst_mac}= | Get Interface Mac | ${tg_node} | ${dst_int}
| | ${src_ip}= | Set Variable | 192.168.100.1
| | ${dst_ip}= | Set Variable | 192.168.100.2
| | ${args}= | Traffic Script Gen Arg | ${dst_int} | ${src_int} | ${src_mac}
| |          | ...                    | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | send_ip_icmp.py | ${tg_node} | ${args}
