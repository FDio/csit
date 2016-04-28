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

#TODO: resource documentation
#TODO: reformat file

*** Settings ***
| Resource | resources/libraries/robot/interfaces.robot

*** Keywords ***
| GRE tunnel interface is created and up
#TODO: documentation
| | [Documentation] | TBD
| | ...
| | ...
| | ...
| | [Arguments] | ${dut} | ${source_ip_address} | ${destination_ip_address}
| | ${name} | ${index}= | Create GRE Tunnel Interface
| | | | ... | ${dut} | ${source_ip_address} | ${destination_ip_address}
| | Set Interface State | ${dut} | ${index} | up
| | [Return] | ${name} | ${index}


| Send ICMPv4 and check received GRE header
#TODO: documentation
| | [Documentation] | TBD
| | ...
| | ...
| | ...
| | [Arguments] | ${tg} | ${tx_if} | ${rx_if}
| | ...         | ${tx_dst_mac} | ${rx_dst_mac}
| | ...         | ${inner_src_ip} | ${inner_dst_ip}
| | ...         | ${outer_src_ip} | ${outer_dst_ip}
| | ${args}= | Catenate | --tx_if | ${tx_if} | --rx_if | ${rx_if}
| | | ... | --tx_dst_mac | ${tx_dst_mac} | --rx_dst_mac | ${rx_dst_mac}
| | | ... | --inner_src_ip | ${inner_src_ip} | --inner_dst_ip | ${inner_dst_ip}
| | | ... | --outer_src_ip | ${outer_src_ip} | --outer_dst_ip | ${outer_dst_ip}
| | Run Traffic Script On Node
| | ... | send_icmp_check_gre_headers.py | ${tg} | ${args}
