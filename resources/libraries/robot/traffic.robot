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
| | ... | - encaps_tx - Expected encapsulation on TX side: Dot1q or Dot1ad
| | ... | (Optional). Type: string
| | ... | - vlan_tx - VLAN (inner) tag on TX side (Optional). Type: integer
| | ... | - vlan_outer_tx - .1AD VLAN (outer) tag on TX side (Optional).
| | ... | Type: integer
| | ... | - encaps_rx - Expected encapsulation on RX side: Dot1q or Dot1ad
| | ... | (Optional). Type: string
| | ... | - vlan_rx - VLAN (inner) tag on RX side (Optional). Type: integer
| | ... | - vlan_outer_rx - .1AD VLAN (outer) tag on RX side (Optional).
| | ... | Type: integer
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
| | ... | ${encaps_tx}=${EMPTY} | ${vlan_tx}=${EMPTY} | ${vlan_outer_tx}=${EMPTY}
| | ... | ${encaps_rx}=${EMPTY} | ${vlan_rx}=${EMPTY} | ${vlan_outer_rx}=${EMPTY}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac |
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac |
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip} |
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | ${args}= | Run Keyword Unless | '${encaps_tx}' == '${EMPTY}'
| | | ... | Catenate | ${args} | --encaps_tx ${encaps_tx} | --vlan_tx ${vlan_tx}
| | ${args}= | Run Keyword Unless | '${encaps_rx}' == '${EMPTY}'
| | | ... | Catenate | ${args} | --encaps_rx ${encaps_rx} | --vlan_rx ${vlan_rx}
| | ${args}= | Run Keyword Unless | '${vlan_outer_tx}' == '${EMPTY}'
| | | ... | Catenate | ${args} | --vlan_outer_tx ${vlan_outer_tx}
| | ${args}= | Run Keyword Unless | '${vlan_outer_rx}' == '${EMPTY}'
| | | ... | Catenate | ${args} | --vlan_outer_rx ${vlan_outer_rx}
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
| | [Documentation] | Wait until RA packet is received and then verify\
| | ...             | specific fields of received RA packet.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - node - Node where to check for RA packet. Type: dictionary
| | ... | - rx_port - Interface where the packet is received. Type: string
| | ... | - src_mac - MAC address of source interface from which the link-local\
| | ... |             IPv6 address is constructed and checked. Type: string
| | ... | - interval - Configured retransmit interval. Optional. Type: integer
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Receive And Check Router Advertisement Packet \
| | ... | \| ${nodes['DUT1']} \| eth2 \| 08:00:27:cc:4f:54 \|
| | ...
| | [Arguments] | ${node} | ${rx_port} | ${src_mac} | ${interval}=${0}
| | ${rx_port_name}= | Get interface name | ${node} | ${rx_port}
| | ${args}= | Catenate
| | ... | --rx_if ${rx_port_name}
| | ... | --src_mac ${src_mac}
| | ... | --interval ${interval}
| | Run Traffic Script On Node | check_ra_packet.py | ${node} | ${args}

| Send Router Solicitation and check response
| | [Documentation] | Send RS packet, wait for response and then verify\
| | ...             | specific fields of received RA packet.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | - tg_node - TG node to send RS packet from. Type: dictionary
| | ... | - dut_node - DUT node to send RS packet to. Type: dictionary
| | ... | - rx_port - Interface where the packet is sent from. Type: string
| | ... | - tx_port - Interface where the packet is sent to. Type: string
| | ... | - src_ip - Source IP address of RS packet. Optional. If not provided,\
| | ... | link local address will be used. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send Router Solicitation and check response \
| | ... | \| ${nodes['TG']} \| ${nodes['DUT1']} \| eth2 \
| | ... | \| GigabitEthernet0/8/0 \| 10::10 \|
| | ...
| | [Arguments] | ${tg_node} | ${dut_node} | ${tx_port} | ${rx_port}
| | ... | ${src_ip}=''
| | ${src_mac}= | Get Interface Mac | ${tg_node} | ${tx_port}
| | ${dst_mac}= | Get Interface Mac | ${dut_node} | ${rx_port}
| | ${src_int_name}= | Get interface name | ${tg_node} | ${tx_port}
| | ${dst_int_name}= | Get interface name | ${dut_node} | ${rx_port}
| | ${args}= | catenate
| | ... | --rx_if ${dst_int_name} --tx_if ${src_int_name}
| | ... | --src_mac ${src_mac} | --dst_mac ${dst_mac}
| | ... | --src_ip ${src_ip}
| | Run Traffic Script On Node | send_rs_check_ra.py
| | ... | ${tg_node} | ${args}

| Send ARP Request
| | [Documentation] | Send ARP Request and check if the ARP Response is received.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)<->(if1)DUT
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - tx_port - Interface from which the ARP packet is sent (TG-if1).
| | ... |             Type: string
| | ... | - src_mac - Source MAC address of ARP packet (TG-if1).
| | ... |             Type: string
| | ... | - tgt_mac - Target MAC address which is expected in the response
| | ... |             (DUT-if1). Type: string
| | ... | - src_ip - Source IP address of ARP packet (TG-if1).
| | ... |            Type: string
| | ... | - tgt_ip - Target IP address of ARP packet (DUT-if1).
| | ... |            Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send ARP Request \| ${nodes['TG']} \| eth3 \
| | ... | \| 08:00:27:cc:4f:54 \| 08:00:27:c9:6a:d5 \
| | ... | \| 10.0.0.100 \| 192.168.1.5 \|
| | ...
| | [Arguments] | ${tg_node} | ${tx_port}
| | ...         | ${src_mac} | ${tgt_mac}
| | ...         | ${src_ip} | ${tgt_ip}
| | ${args}= | Catenate | --tx_if | ${tx_port}
| | ...                 | --src_mac | ${src_mac} | --dst_mac | ${tgt_mac}
| | ...                 | --src_ip | ${src_ip} | --dst_ip | ${tgt_ip}
| | Run Traffic Script On Node | arp_request.py | ${tg_node} | ${args}

| Send ARP Request should failed
| | [Documentation] | Send ARP Request and
| | ...             | the ARP Response should not be received.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)<->(if1)DUT
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - tx_port - Interface from which the ARP packet is sent (TG-if1).
| | ... |             Type: string
| | ... | - src_mac - Source MAC address of ARP packet (TG-if1).
| | ... |             Type: string
| | ... | - tgt_mac - Target MAC address which is expected in the response
| | ... |             (DUT-if1). Type: string
| | ... | - src_ip - Source IP address of ARP packet (TG-if1).
| | ... |            Type: string
| | ... | - tgt_ip - Target IP address of ARP packet (DUT-if1).
| | ... |            Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send ARP Request should failed \| ${nodes['TG']} \| eth3 \
| | ... | \| 08:00:27:cc:4f:54 \| 08:00:27:c9:6a:d5 \
| | ... | \| 10.0.0.100 \| 192.168.1.5 \|
| | ...
| | [Arguments] | ${tg_node} | ${tx_port}
| | ...         | ${src_mac} | ${tgt_mac}
| | ...         | ${src_ip} | ${tgt_ip}
| | ${args}= | Catenate | --tx_if | ${tx_port}
| | ...                 | --src_mac | ${src_mac} | --dst_mac | ${tgt_mac}
| | ...                 | --src_ip | ${src_ip} | --dst_ip | ${tgt_ip}
| | Run Keyword And Expect Error | ARP reply timeout
| | ... | Run Traffic Script On Node | arp_request.py | ${tg_node} | ${args}

| Send Packets And Check Multipath Routing
| | [Documentation] | Send 100 IP ICMP packets traffic and check if it is\
| | ...             | divided into two paths.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ... | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_port - Interface of TG-if1. Type: string
| | ... | - dst_port - Interface of TG-if2. Type: string
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT-if2. Type: string
| | ... | - rx_dst_mac_1 - MAC address of interface for path 1. Type: string
| | ... | - rx_dst_mac_2 - MAC address of interface for path 2. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send Packet And Check Multipath Routing \| ${nodes['TG']} \
| | ... | \| eth2 \| eth3 \| 16.0.0.1 \| 32.0.0.1 \
| | ... | \| 08:00:27:cc:4f:54 \| 08:00:27:c9:6a:d5 \| 08:00:27:54:59:f9 \
| | ... | \| 02:00:00:00:00:02 \| 02:00:00:00:00:03 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_port} | ${dst_port} | ${src_ip} | ${dst_ip}
| | ...         | ${tx_src_mac} | ${tx_dst_mac} | ${rx_src_mac}
| | ...         | ${rx_dst_mac_1} | ${rx_dst_mac_2}
| | ${src_port_name}= | Get interface name | ${tg_node} | ${src_port}
| | ${dst_port_name}= | Get interface name | ${tg_node} | ${dst_port}
| | ${args}= | Catenate | --tx_if | ${src_port_name}
| | ... | --rx_if | ${dst_port_name} | --src_ip | ${src_ip}
| | ... | --dst_ip | ${dst_ip} | --tg_if1_mac | ${tx_src_mac}
| | ... | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac | ${rx_src_mac}
| | ... | --path_1_mac | ${rx_dst_mac_1} | --path_2_mac | ${rx_dst_mac_2}
| | Run Traffic Script On Node | send_icmp_check_multipath.py | ${tg_node}
| | ... | ${args}
