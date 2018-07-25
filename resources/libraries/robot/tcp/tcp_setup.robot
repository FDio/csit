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
| Create base startup configuration of VPP for TCP tests on all DUTs
| | [Documentation] | Create base startup configuration of VPP for TCP related
| | ... | tests to all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run keyword | ${dut}.Set Node |  ${nodes['${dut}']}
| | | Run keyword | ${dut}.Add Unix Log
| | | Run keyword | ${dut}.Add Unix CLI Listen
| | | Run keyword | ${dut}.Add Unix Nodaemon
| | | Run keyword | ${dut}.Add DPDK Socketmem | 4096,4096
| | | Run keyword | ${dut}.Add DPDK Log Level | debug
| | | Run keyword | ${dut}.Add DPDK Uio Driver
| | | Run keyword | ${dut}.Add Heapsize | 4G
| | | Run keyword | ${dut}.Add Plugin | disable | default
| | | Run keyword | ${dut}.Add Plugin | enable | @{plugins_to_enable}
| | | Run keyword | ${dut}.Add IP6 Hash Buckets | 2000000
| | | Run keyword | ${dut}.Add IP6 Heap Size | 4G
| | | Run keyword | ${dut}.Add IP Heap Size | 4G

| Set up HTTP server with paramters on the VPP node
| | [Documentation]
| | ... | Configure IP address on the port, set it up and start HTTP server on
| | ... | the VPP.
| | ...
| | ... | *Arguments:*
| | ... | - ${prealloc_fifos} - Max number of connections you expect to handle
| | ... | at one time. Type: string
| | ... | - ${fifo_size} - FIFO size in kB. Type: string
| | ... | - ${private_segment_size} - Private segment size. Number + unit.
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up HTTP server with paramters on the VPP node \| 400 \| 4096\
| | ... | \| 2g \|
| | ...
| | [Arguments] | ${prealloc_fifos} | ${fifo_size} | ${private_segment_size}
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.10.2 | 24
| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.20.2 | 24
| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.30.2 | 24
| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.40.2 | 24
| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.50.2 | 24
| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.60.2 | 24
| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.70.2 | 24
| | Set Interface Address | ${dut1} | ${dut1_if1} | 192.168.80.2 | 24
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Start HTTP server params | ${dut1} | ${prealloc_fifos} | ${fifo_size}
| | ... | ${private_segment_size}
| | Sleep | 30
