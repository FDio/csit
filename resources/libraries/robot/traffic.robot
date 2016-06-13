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
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_port - Interface of TG-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT1-if2. Type: string
| | ... | - rx_dst_mac - MAC address of TG-if2. Type: string
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
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac |
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac |
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip} |
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | Run Traffic Script On Node | send_icmp_check_headers.py | ${tg_node} |
| | ... | ${args}

| Send packet from Port to Port should failed
| | [Documentation] | Sends packet from ip (with specified mac) to ip
| | ...             | (with dest mac). Using keyword : Send packet And Check
| | ...             | Headers and subsequently checks the return value
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_port - Interface of TG-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT1-if2. Type: string
| | ... | - rx_dst_mac - MAC address of TG-if2. Type: string
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
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac |
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac |
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip} |
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | Run Keyword And Expect Error | ICMP echo Rx timeout |
| | ... | Run Traffic Script On Node | send_icmp_check_headers.py
| | ... | ${tg_node} | ${args}

| Send Packet And Check ARP Request
| | [Documentation] | Send IP packet from tx_port and check if ARP Request\
| | ...             | packet is received on rx_port.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - tx_src_ip - Source IP address of transferred packet (TG-if1).
| | ... |               Type: string
| | ... | - tx_dst_ip - Destination IP address of transferred packet (TG-if2).
| | ... |               Type: string
| | ... | - tx_port - Interface from which the IP packet is sent (TG-if1).
| | ... |             Type: string
| | ... | - tx_dst_mac - Destination MAC address of IP packet (DUT-if1).
| | ... |                Type: string
| | ... | - rx_port - Interface where the IP packet is received (TG-if2).
| | ... |             Type: string
| | ... | - rx_src_mac - Source MAC address of ARP packet (DUT-if2).
| | ... |                Type: string
| | ... | - rx_arp_src_ip - Source IP address of ARP packet (DUT-if2).
| | ... |                   Type: string
| | ... | - rx_arp_dst_ip - Destination IP address of ARP packet. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send Packet And Check ARP Packet \| ${nodes['TG']} \| 16.0.0.1 \
| | ... | \| 32.0.0.1 \| eth2 \| 08:00:27:cc:4f:54 \
| | ... | \| eth4 \| 08:00:27:5b:49:dd \| 192.168.2.1 \| 192.168.2.2 \|
| | ...
| | [Arguments] | ${tg_node} | ${tx_src_ip} | ${tx_dst_ip} | ${tx_port}
| | ... | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac} | ${rx_arp_src_ip}
| | ... | ${rx_arp_dst_ip}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate
| | ... | --tx_dst_mac | ${tx_dst_mac} | --rx_src_mac | ${rx_src_mac}
| | ... | --tx_src_ip | ${tx_src_ip} | --tx_dst_ip | ${tx_dst_ip}
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | ... | --rx_arp_src_ip ${rx_arp_src_ip} | --rx_arp_dst_ip ${rx_arp_dst_ip}
| | Run Traffic Script On Node | send_icmp_check_arp.py | ${tg_node} | ${args}

| Send TCP or UDP packet
| | [Documentation] | Sends TCP or UDP packet with specified source
| | ...             | and destination port.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: integer
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: integer
| | ... | - tx_port - Source interface (TG-if1). Type: string
| | ... | - tx_mac - MAC address of source interface (TG-if1). Type: string
| | ... | - rx_port - Destionation interface (TG-if1). Type: string
| | ... | - rx_mac - MAC address of destination interface (TG-if1). Type: string
| | ... | - protocol - Type of protocol. Type: string
| | ... | - source_port - Source TCP/UDP port. Type: string or integer
| | ... | - destination_port - Destination TCP/UDP port. Type: string or integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send TCP or UDP packet \| ${nodes['TG']} \
| | ... | \| 16.0.0.1 \| 32.0.0.1 \| eth2 \| 08:00:27:cc:4f:54 \
| | ... | \| eth4 \| 08:00:27:c9:6a:d5 \| TCP \| 20 \| 80 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_port} |
| | ... | ${tx_mac} | ${rx_port} | ${rx_mac} | ${protocol} | ${source_port}
| | ... | ${destination_port}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tx_mac | ${tx_mac}
| | ...                 | --rx_mac | ${rx_mac}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --dst_ip | ${dst_ip}
| | ...                 | --tx_if | ${tx_port_name}
| | ...                 | --rx_if | ${rx_port_name}
| | ...                 | --protocol | ${protocol}
| | ...                 | --source_port | ${source_port}
| | ...                 | --destination_port | ${destination_port}
| | Run Traffic Script On Node | send_tcp_udp.py
| | ... | ${tg_node} | ${args}

| Send TCP or UDP packet should failed
| | [Documentation] | Sends TCP or UDP packet with specified source
| | ...             | and destination port.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: integer
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: integer
| | ... | - tx_port - Source interface (TG-if1). Type: string
| | ... | - tx_mac - MAC address of source interface (TG-if1). Type: string
| | ... | - rx_port - Destionation interface (TG-if1). Type: string
| | ... | - rx_mac - MAC address of destination interface (TG-if1). Type: string
| | ... | - protocol - Type of protocol. Type: string
| | ... | - source_port - Source TCP/UDP port. Type: string or integer
| | ... | - destination_port - Destination TCP/UDP port. Type: string or integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send TCP or UDP packet should failed \| ${nodes['TG']} \
| | ... | \| 16.0.0.1 \| 32.0.0.1 \| eth2 \| 08:00:27:cc:4f:54 \
| | ... | \| eth4 \| 08:00:27:c9:6a:d5 \| TCP \| 20 \| 80 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_port} |
| | ... | ${tx_mac} | ${rx_port} | ${rx_mac} | ${protocol} | ${source_port}
| | ... | ${destination_port}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tx_mac | ${tx_mac}
| | ...                 | --rx_mac | ${rx_mac}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --dst_ip | ${dst_ip}
| | ...                 | --tx_if | ${tx_port_name}
| | ...                 | --rx_if | ${rx_port_name}
| | ...                 | --protocol | ${protocol}
| | ...                 | --source_port | ${source_port}
| | ...                 | --destination_port | ${destination_port}
| | Run Keyword And Expect Error | TCP/UDP Rx timeout
| | ... | Run Traffic Script On Node | send_tcp_udp.py
| | ... | ${tg_node} | ${args}

| Receive And Check Router Advertisement Packet
| | [Documentation] | Wait until RA packet is received and then check
| | ...             | specific packet fields whether they are correct.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - node - Node where to check for RA packet. Type: dictionary
| | ... | - rx_port - Interface where the packet is received. Type: string
| | ... | - src_mac - MAC address of source interface from which the link-local
| | ... |             IPv6 address is constructed and checked. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Receive And Check Router Advertisement Packet \
| | ... | \| ${nodes['DUT1']} \| eth2 \| 08:00:27:cc:4f:54 \|
| | ...
| | [Arguments] | ${node} | ${rx_port} | ${src_mac}
| | ${rx_port_name}= | Get interface name | ${node} | ${rx_port}
| | ${args}= | Catenate | --rx_if | ${rx_port_name} | --src_mac | ${src_mac}
| | Run Traffic Script On Node | check_ra_packet.py | ${node} | ${args}
