# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.tcp.TCPUtils
|
| Resource | resources/libraries/robot/ip/ip4.robot
|
| Documentation | L2 keywords to set up VPP to test tcp.

*** Keywords ***
| Set up HTTP server with parameters on the VPP node
| | [Documentation]
| | ... | Configure IP address on the port, set it up and start HTTP server on
| | ... | the VPP.
| |
| | ... | *Arguments:*
| | ... | - http_static_plugin - Use the HTTP static plugin http server.
| | ... | Type: boolean
| | ... | - prealloc_fifos - Max number of connections you expect to handle
| | ... | at one time. Type: string
| | ... | - fifo_size - FIFO size in kB. Type: string
| | ... | - private_segment_size - Private segment size. Number + unit.
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Set up HTTP server with paramters on the VPP node \| ${true}\
| | ... | \| 400 \| 4096 \| 2g \|
| |
| | [Arguments] | ${http_static_plugin} | ${prealloc_fifos} | ${fifo_size}
| | ... | ${private_segment_size}
| |
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.10.2 | 24
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.20.2 | 24
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.30.2 | 24
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.40.2 | 24
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.50.2 | 24
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.60.2 | 24
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.70.2 | 24
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.80.2 | 24
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Start VPP HTTP server params | ${dut1} | ${http_static_plugin}
| | ... | ${prealloc_fifos} | ${fifo_size} | ${private_segment_size}
