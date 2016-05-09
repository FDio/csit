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

"""Traffic keywords"""

*** Settings ***
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.IPv6Setup
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Routing
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.topology.Topology
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/counters.robot
| Documentation | Traffic keywords

*** Keywords ***
| Send Packet And Check Headers
| | [Documentation] | Sends packet from IP (with source mac) to IP
| | ...             | (with dest mac). There has to be 4 MAC addresses
| | ...             | when using 2 node +
| | ...             | xconnect (one for each eth).
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on example:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - {tg_node} : Node to execute scripts on (TG). Type: dictionary
| | ... | - {src_ip} - IP of source interface (TG-if1). Type: int
| | ... | - {dst_ip} - IP of destination interface (TG-if2). Type: int
| | ... | - {tx_src_port} - Interface of TG-if1. Type: string
| | ... | - {tx_src_mac} - MAC address of TG-if1. Type: string
| | ... | - {tx_dst_mac} - MAC address of DUT-if1. Type: string
| | ... | - {rx_port} - Interface of TG-if1. Type: string
| | ... | - {rx_src_mac} - MAC address of DUT1-if2. Type: string
| | ... | - {rx_dst_mac} - MAC address of TG-if2. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send Packet And Check Headers \| ${nodes['TG']} \| 10.0.0.1 \
| | ... | \| 32.0.0.1 \| eth2 \| 08:00:27:ee:fd:b3 \| 08:00:27:a2:52:5b \
| | ... | \| eth3 \| 08:00:27:4d:ca:7a \| 08:00:27:7d:fd:10 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port} |
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac}
| | ... | ${rx_dst_mac}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac |
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac |
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip} |
| | ... | --tx_if | ${tx_src_port} | --rx_if | ${rx_port}
| | Run Traffic Script On Node | send_icmp_check_headers.py | ${tg_node} |
| | ... | ${args}

| Send packet from Port to Port should failed
| | [Documentation] | Sends packet from ip (with specified mac) to ip
| | ...             | (with dest mac). Using keyword : Send packet And Check
| | ...             | Headers and subsequently checks the return value
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on example:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - {tg_node} : Node to execute scripts on (TG). Type: dictionary
| | ... | - {src_ip} - IP of source interface (TG-if1). Type: int
| | ... | - {dst_ip} - IP of destination interface (TG-if2). Type: int
| | ... | - {tx_src_port} - Interface of TG-if1. Type: string
| | ... | - {tx_src_mac} - MAC address of TG-if1. Type: string
| | ... | - {tx_dst_mac} - MAC address of DUT-if1. Type: string
| | ... | - {rx_port} - Interface of TG-if1. Type: string
| | ... | - {rx_src_mac} - MAC address of DUT1-if2. Type: string
| | ... | - {rx_dst_mac} - MAC address of TG-if2. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send packet from Port to Port should failed \| ${nodes['TG']} \
| | ... | \| 10.0.0.1 \ \| 32.0.0.1 \| eth2 \| 08:00:27:ee:fd:b3 \
| | ... | \| 08:00:27:a2:52:5b \| eth3 \| 08:00:27:4d:ca:7a \
| | ... | \| 08:00:27:7d:fd:10 \|
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port} |
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac} |
| | ... | ${rx_dst_mac}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac |
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac |
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip} |
| | ... | --tx_if | ${tx_src_port} | --rx_if | ${rx_port}
| | Run Keyword And Expect Error | ICMP echo Rx timeout |
| | ... | Run Traffic Script On Node | send_icmp_check_headers.py
| | ... | ${tg_node} | ${args}
l