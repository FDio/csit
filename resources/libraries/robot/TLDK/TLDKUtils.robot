# Copyright (c) 2017 Cisco and/or its affiliates.                                                                                                        
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
| Library | resources.libraries.python.NodePath

*** Keywords ***
| Path for 2-node testing is set
| | [Arguments] | ${tg_node} | ${dut_node}
| | Append Nodes | ${tg_node} | ${dut_node}
| | Compute Path

| Pick out the port used to execute test
| | ${tg_port} | ${tg_node}= | First Interface
| | ${dut_port} | ${dut_node}= | Last Interface

| Get the pcap data
| | [Arguments] | ${file_prefix}
| | ${packet_num} | ${dest_ip} | ${is_ipv4}= | Get Pcap Info
| | ... | ${file_prefix}
