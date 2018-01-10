# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.IPv4Util.IPv4Util
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.tcp.TCPUtils
| Resource | resources/libraries/robot/ip/ip4.robot
| ...
| Documentation | L2 keywords to set up VPP to test tcp.

*** Keywords ***
| Set up HTTP server on the VPP node
| | [Documentation]
| | ... | Configure IP address on the port, set it up and start HTTP server on
| | ... | the VPP.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut1_if1_ip4} - IP address to be set on the dut1_if1 interface.
| | ... | Type: string
| | ... | - ${ip4_len} - Length of the netmask. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up HTTP server on the VPP node \| 192.168.10.2 \| 24 \|
| | ...
| | [Arguments] | ${dut1_if1_ip4} | ${ip4_len}
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface Address | ${dut1} | ${dut1_if1} | ${dut1_if1_ip4} | ${ip4_len}
#| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.20.2 | ${ip4_len}
#| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.30.2 | ${ip4_len}
#| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.40.2 | ${ip4_len}
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Start HTTP server | ${dut1} | 400 | 4096 | 4g
| | Sleep | 30
