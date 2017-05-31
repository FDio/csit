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
| Documentation | *Utilities for the path computing, pcap reading*
| ...
| ... | Utilities for the path computing, pcap file reading and also the port
| ... | selection.

*** Keywords ***
| Path for 2-node testing is set
| | [Documentation] | Compute the path for the 2 node testing. 
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - dut_node - DUT node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Path for 2-node testing is set \| ${nodes['TG']} \
| | ... | \| ${nodes['DUT1'] \|
| | ...
| | [Arguments] | ${tg_node} | ${dut_node}
| | Append Nodes | ${tg_node} | ${dut_node}
| | Compute Path

| Pick out the port used to execute test
| | [Documentation] | Pick out the port used to execute the test.
| | ... 
| | ... | *Arguments:*
| | ... | - No arguments.
| | ... 
| | ... | *Return:*
| | ... | - No value returned.
| | ... 
| | ... | *Example:*
| | ... 
| | ... | \| Pick out the port used to execute test \|
| | ... 
| | ${tg_port} | ${tg_node}= | First Interface
| | ${dut_port} | ${dut_node}= | Last Interface
| | set suite variable | ${tg_node}
| | set suite variable | ${dut_node}
| | set suite variable | ${tg_port}
| | set suite variable | ${dut_port}

| Get the pcap data
| | [Documentation] | Get the pcap file detailed data.
| | ...
| | ... | *Arguments:*
| | ... | - file_prefix - file prefix. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - packet_num, dest_ip, is_ipv4 - a tuple of packet_num
| | ... |   dest_ip, is_ipv4. Type: tuple(int, str, bool)
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get the pcap data \| ${tc01_file_prefix} \|
| | ...
| | [Arguments] | ${file_prefix}
| | ${packet_num} | ${dest_ip} | ${is_ipv4}= | Get Pcap Info
| | ... | ${file_prefix}
| | set suite variable | ${packet_num}
| | set suite variable | ${dest_ip}
| | set suite variable | ${is_ipv4}
