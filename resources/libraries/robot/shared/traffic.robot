# Copyright (c) 2020 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Policer
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficScriptExecutor
|
| Documentation | Traffic keywords

*** Keywords ***
| Send packet and verify headers
| | [Documentation] | Sends packet from IP (with source mac) to IP\
| | ... | (with dest mac). There has to be 4 MAC addresses when using\
| | ... | 2-node + xconnect (one for each eth).
| |
| | ... | *Arguments:*
| |
| | ... | _NOTE:_ Arguments are based on topology:
| | ... | TG(if1)->(if1)DUT(if2)->TG(if2)
| |
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_dst_port - Interface of TG-if1. Type: string
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
| | ... | - traffic_script - Scapy Traffic script used for validation.
| | ... | Type: string
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Send packet and verify headers \| ${nodes['TG']} \| 10.0.0.1 \
| | ... | \| 32.0.0.1 \| eth2 \| 08:00:27:ee:fd:b3 \| 08:00:27:a2:52:5b \
| | ... | \| eth3 \| 08:00:27:4d:ca:7a \| 08:00:27:7d:fd:10 \|
| |
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port}
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_dst_port} | ${rx_src_mac}
| | ... | ${rx_dst_mac} | ${encaps_tx}=${EMPTY} | ${vlan_tx}=${EMPTY}
| | ... | ${vlan_outer_tx}=${EMPTY} | ${encaps_rx}=${EMPTY}
| | ... | ${vlan_rx}=${EMPTY} | ${vlan_outer_rx}=${EMPTY}
| | ... | ${traffic_script}=send_ip_check_headers
| |
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_dst_port}
| | ${args}= | Catenate | --tg_src_mac ${tx_src_mac}
| | ... | --tg_dst_mac ${rx_dst_mac} | --dut_if1_mac ${tx_dst_mac}
| | ... | --dut_if2_mac ${rx_src_mac} | --src_ip ${src_ip} | --dst_ip ${dst_ip}
| | ... | --tx_if ${tx_port_name} | --rx_if ${rx_port_name}
| | ${args}= | Run Keyword If | '${encaps_tx}' == '${EMPTY}'
| | | ... | Set Variable | ${args}
| | ... | ELSE | Catenate
| | ... | ${args} | --encaps_tx ${encaps_tx} | --vlan_tx ${vlan_tx}
| | ${args}= | Run Keyword If | '${encaps_rx}' == '${EMPTY}'
| | | ... | Set Variable | ${args}
| | ... | ELSE | Catenate
| | ... | ${args} | --encaps_rx ${encaps_rx} | --vlan_rx ${vlan_rx}
| | ${args}= | Run Keyword If | '${vlan_outer_tx}' == '${EMPTY}'
| | | ... | Set Variable | ${args}
| | ... | ELSE | Catenate | ${args} | --vlan_outer_tx ${vlan_outer_tx}
| | ${args}= | Run Keyword If | '${vlan_outer_rx}' == '${EMPTY}'
| | | ... | Set Variable | ${args}
| | ... | ELSE | Catenate | ${args} | --vlan_outer_rx ${vlan_outer_rx}
| | Run Traffic Script On Node | ${traffic_script}.py | ${tg_node} | ${args}

| Packet transmission from port to port should fail
| | [Documentation] | Sends packet from ip (with specified mac) to ip\
| | ... | (with dest mac). Using keyword : Send packet And Check Headers\
| | ... | and subsequently checks the return value.
| |
| | ... | *Arguments:*
| |
| | ... | _NOTE:_ Arguments are based on topology:
| | ... | TG(if1)->(if1)DUT(if2)->TG(if2)
| |
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_port - Interface of TG-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT1-if2. Type: string
| | ... | - rx_dst_mac - MAC address of TG-if2. Type: string
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Packet transmission from port to port should fail \
| | ... | \| ${nodes['TG']} \| 10.0.0.1 \ \| 32.0.0.1 \| eth2 \
| | ... | \| 08:00:27:a2:52:5b \| eth3 \| 08:00:27:4d:ca:7a \
| | ... | \| 08:00:27:ee:fd:b3 \| 08:00:27:7d:fd:10 \|
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port}
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac}
| | ... | ${rx_dst_mac}
| |
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac ${tx_src_mac}
| | ... | --tg_dst_mac ${rx_dst_mac} | --dut_if1_mac ${tx_dst_mac}
| | ... | --dut_if2_mac ${rx_src_mac} | --src_ip ${src_ip} | --dst_ip ${dst_ip}
| | ... | --tx_if ${tx_port_name} | --rx_if ${rx_port_name}
| | Run Keyword And Expect Error | IP packet Rx timeout |
| | ... | Run Traffic Script On Node | send_ip_check_headers.py
| | ... | ${tg_node} | ${args}

| Send packet and verify marking
| | [Documentation] | Send packet and verify DSCP of the received packet.
| |
| | ... | *Arguments:*
| | ... | - node - TG node. Type: dictionary
| | ... | - tx_if - TG transmit interface. Type: string
| | ... | - rx_if - TG receive interface. Type: string
| | ... | - src_mac - Packet source MAC. Type: string
| | ... | - dst_mac - Packet destination MAC. Type: string
| | ... | - src_ip - Packet source IP address. Type: string
| | ... | - dst_ip - Packet destination IP address. Type: string
| |
| | ... | *Example:*
| | ... | \| Send packet and verify marking \| ${nodes['TG']} \| eth1 \| eth2 \
| | ... | \| 08:00:27:87:4d:f7 \| 52:54:00:d4:d8:22 \| 192.168.122.2 \
| | ... | \| 192.168.122.1 \|
| |
| | [Arguments] | ${node} | ${tx_if} | ${rx_if} | ${src_mac} | ${dst_mac}
| | ... | ${src_ip} | ${dst_ip}
| |
| | ${tx_if_name}= | Get Interface Name | ${node} | ${tx_if}
| | ${rx_if_name}= | Get Interface Name | ${node} | ${rx_if}
| | ${args}= | Traffic Script Gen Arg | ${rx_if_name} | ${tx_if_name}
| | ... | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | ${dscp_num}= | Get DSCP Num Value | ${dscp}
| | ${args}= | Set Variable | ${args} --dscp ${dscp_num}
| | Run Traffic Script On Node | policer.py | ${node} | ${args}

| Send VXLAN encapsulated packet and verify received packet
| | [Documentation] | Send VXLAN encapsulated Ethernet frame and check \
| | ... | received one.
| |
| | ... | *Arguments:*
| | ... | - tg_node - Node where to run traffic script. Type: dictionary
| | ... | - tx_if - Interface from where send VXLAN packet. Type: string
| | ... | - rx_if - Interface where receive VXLAN packet. Type: string
| | ... | - tx_src_mac - Source MAC address of sent packet. Type: string
| | ... | - tx_dst_mac - Destination MAC address of sent packet. Type: string
| | ... | - tx_src_ip - Source IP address of sent VXLAN packet. Type: string
| | ... | - tx_dst_ip - Destination IP address of sent VXLAN packet.
| | ... | Type: string
| | ... | - tx_vni - VNI of sent VXLAN packet. Type: string
| | ... | - rx_src_ip - Source IP address of received VXLAN packet. Type: string
| | ... | - rx_dst_ip - Destination IP address of received VXLAN packet.
| | ... | Type: string
| | ... | - rx_vni - VNI of received VXLAN packet. Type: string
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Send VXLAN encapsulated packet and verify received packet \
| | ... | \| ${tg_node} \| port4 \| port4 \
| | ... | \| fa:16:3e:6d:f9:c5 \| fa:16:3e:e6:6d:9a \| 192.168.0.1 \
| | ... | \| 192.168.0.2 \| ${101} \| 192.168.0.2 \| 192.168.0.1 \| ${102} \|
| |
| | [Arguments] | ${tg_node} | ${tx_if} | ${rx_if}
| | ... | ${tx_src_mac} | ${tx_dst_mac}
| | ... | ${tx_src_ip} | ${tx_dst_ip} | ${tx_vni}
| | ... | ${rx_src_ip} | ${rx_dst_ip} | ${rx_vni}
| | ${tx_if_name}= | Get interface name | ${tg_node} | ${tx_if}
| | ${rx_if_name}= | Get interface name | ${tg_node} | ${rx_if}
| | ${args}= | Catenate
| | ... | --tx_if ${tx_if_name}
| | ... | --rx_if ${rx_if_name}
| | ... | --tx_src_mac ${tx_src_mac}
| | ... | --tx_dst_mac ${tx_dst_mac}
| | ... | --tx_src_ip ${tx_src_ip}
| | ... | --tx_dst_ip ${tx_dst_ip}
| | ... | --tx_vni ${tx_vni}
| | ... | --rx_src_ip ${rx_src_ip}
| | ... | --rx_dst_ip ${rx_dst_ip}
| | ... | --rx_vni ${rx_vni}
| | Run Traffic Script On Node | send_vxlan_check_vxlan.py | ${tg_node}
| | ... | ${args}

| Send ICMP echo request and verify answer
| | [Documentation] | Run traffic script that waits for ICMP reply and ignores
| | ... | all other packets.
| |
| | ... | *Arguments:*
| | ... | - tg_node - TG node where run traffic script. Type: dictionary
| | ... | - tg_interface - TG interface where send ICMP echo request.
| | ... | Type: string
| | ... | - dst_mac - Destination MAC address. Type: string
| | ... | - src_mac - Source MAC address. Type: string
| | ... | - dst_ip - Destination IP address. Type: string
| | ... | - src_ip - Source IP address. Type: string
| | ... | - timeout - Wait timeout in seconds (Default: 10). Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Send ICMP echo request and verify answer \
| | ... | \| ${nodes['TG']} \| eth2 \
| | ... | \| 08:00:27:46:2b:4c \| 08:00:27:66:b8:57 \
| | ... | \| 192.168.23.10 \| 192.168.23.1 \| 10 \|
| |
| | [Arguments] | ${tg_node} | ${tg_interface}
| | ... | ${dst_mac} | ${src_mac} | ${dst_ip} | ${src_ip} | ${timeout}=${10}
| |
| | ${tg_interface_name}= | Get interface name | ${tg_node} | ${tg_interface}
| | ${args}= | Catenate | --rx_if ${tg_interface_name}
| | ... | --tx_if ${tg_interface_name} | --dst_mac ${dst_mac}
| | ... | --src_mac ${src_mac} | --dst_ip ${dst_ip} | --src_ip ${src_ip}
| | ... | --timeout ${timeout}
| | Run Traffic Script On Node | send_icmp_wait_for_reply.py
| | ... | ${tg_node} | ${args}

| Send IPsec Packet and verify ESP encapsulation in received packet
| | [Documentation] | Send IPsec packet from TG to DUT. Receive IPsec packet\
| | ... | from DUT on TG and verify ESP encapsulation.
| |
| | ... | *Arguments:*
| | ... | - node - TG node. Type: dictionary
| | ... | - tx_interface - TG Interface 1. Type: string
| | ... | - rx_interface - TG Interface 2. Type: string
| | ... | - tx_dst_mac - Destination MAC for TX interface / DUT interface 1 MAC.
| | ... | Type: string
| | ... | - rx_src_mac - Source MAC for RX interface / DUT interface 2 MAC.
| | ... | Type: string
| | ... | - crypto_alg - Encrytion algorithm. Type: enum
| | ... | - crypto_key - Encryption key. Type: string
| | ... | - integ_alg - Integrity algorithm. Type: enum
| | ... | - integ_key - Integrity key. Type: string
| | ... | - l_spi - Local SPI. Type: integer
| | ... | - r_spi - Remote SPI. Type: integer
| | ... | - l_ip - Local IP address. Type: string
| | ... | - r_ip - Remote IP address. Type: string
| | ... | - l_tunnel - Local tunnel IP address (optional). Type: string
| | ... | - r_tunnel - Remote tunnel IP address (optional). Type: string
| |
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128 \|
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96 \|
| | ... | \| Send IPsec Packet and verify ESP encapsulation in received packet\
| | ... | \| ${nodes['TG']} \| eth1 \| eth2 \
| | ... | \| 52:54:00:d4:d8:22 \| 52:54:00:d4:d8:3e \| ${encr_alg} \
| | ... | \| sixteenbytes_key \| ${auth_alg} \| twentybytessecretkey \
| | ... | \| ${1001} \| ${1000} \| 192.168.3.3 \| 192.168.4.4 \| 192.168.100.2 \
| | ... | \| 192.168.100.3 \|
| |
| | [Arguments] | ${node} | ${tx_interface} | ${rx_interface} | ${tx_dst_mac}
| | ... | ${rx_src_mac} | ${crypto_alg} | ${crypto_key} | ${integ_alg}
| | ... | ${integ_key} | ${l_spi} | ${r_spi} | ${l_ip} | ${r_ip}
| | ... | ${l_tunnel}=${None} | ${r_tunnel}=${None}
| |
| | ${tx_src_mac}= | Get Interface Mac | ${node} | ${tx_interface}
| | ${tx_if_name}= | Get Interface Name | ${node} | ${tx_interface}
| | ${rx_dst_mac}= | Get Interface Mac | ${node} | ${rx_interface}
| | ${rx_if_name}= | Get Interface Name | ${node} | ${rx_interface}
| | ${args}= | Catenate | --rx_if ${rx_if_name} | --tx_if ${tx_if_name}
| | ... | --tx_src_mac ${tx_src_mac} | --tx_dst_mac ${tx_dst_mac}
| | ... | --rx_src_mac ${rx_src_mac} | --rx_dst_mac ${rx_dst_mac}
| | ... | --src_ip ${l_ip} | --dst_ip ${r_ip}
| | ${crypto_alg_str}= | Get Crypto Alg Scapy Name | ${crypto_alg}
| | ${integ_alg_str}= | Get Integ Alg Scapy Name | ${integ_alg}
| | ${args}= | Catenate | ${args} | --crypto_alg ${crypto_alg_str}
| | ... | --crypto_key ${crypto_key} | --integ_alg ${integ_alg_str}
| | ... | --integ_key ${integ_key} | --l_spi ${l_spi} | --r_spi ${r_spi}
| | ${args}= | Set Variable If | "${l_tunnel}" == "${None}" | ${args}
| | ... | ${args} --src_tun ${l_tunnel}
| | ${args}= | Set Variable If | "${r_tunnel}" == "${None}" | ${args}
| | ... | ${args} --dst_tun ${r_tunnel}
| | Run Traffic Script On Node | ipsec_policy.py | ${node} | ${args}

| Send packet and verify LISP encap
| | [Documentation] | Send ICMP packet to DUT out one interface and receive\
| | ... | a LISP encapsulated packet on the other interface.
| |
| | ... | *Arguments:*
| |
| | ... | _NOTE:_ Arguments are based on topology:
| | ... | TG(if1)->(if1)DUT(if2)->TG(if2)
| |
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_port - Interface of TG-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT1-if2. Type: string
| | ... | - rx_dst_mac - MAC address of TG-if2. Type: string
| | ... | - src_rloc - configured RLOC source address. Type: string
| | ... | - dst_rloc - configured RLOC destination address. Type: string
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Send packet and verify LISP encap \| ${nodes['TG']} \| 10.0.0.1 \
| | ... | \| 32.0.0.1 \| eth2 \| 08:00:27:ee:fd:b3 \| 08:00:27:a2:52:5b \
| | ... | \| eth3 \| 08:00:27:4d:ca:7a \| 08:00:27:7d:fd:10 \| 10.0.1.1 \
| | ... | \| 10.0.1.2 \|
| |
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port}
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac}
| | ... | ${rx_dst_mac} | ${src_rloc} | ${dst_rloc}
| |
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip}
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | ... | --src_rloc | ${src_rloc} | --dst_rloc | ${dst_rloc}
| | Run Traffic Script On Node | lisp/lisp_check.py | ${tg_node}
| | ... | ${args}

| Send IP Packet and verify ESP encapsulation in received packet
| | [Documentation] | Send IP packet from TG to DUT. Receive IPsec packet\
| | ... | from DUT on TG and verify ESP encapsulation. Send IPsec packet in\
| | ... | opposite direction and verify received IP packet.
| |
| | ... | *Arguments:*
| | ... | - node - TG node. Type: dictionary
| | ... | - tx_interface - TG Interface 1. Type: string
| | ... | - rx_interface - TG Interface 2. Type: string
| | ... | - tx_dst_mac - Destination MAC for TX interface / DUT interface 1 MAC.
| | ... | Type: string
| | ... | - rx_src_mac - Source MAC for RX interface / DUT interface 2 MAC.
| | ... | Type: string
| | ... | - crypto_alg - Encrytion algorithm. Type: enum
| | ... | - crypto_key - Encryption key. Type: string
| | ... | - integ_alg - Integrity algorithm. Type: enum
| | ... | - integ_key - Integrity key. Type: string
| | ... | - l_spi - Local SPI. Type: integer
| | ... | - r_spi - Remote SPI. Type: integer
| | ... | - src_ip - Source IP address. Type: string
| | ... | - dst_ip - Destination IP address. Type: string
| | ... | - src_tun - Source tunnel IP address. Type: string
| | ... | - dst_tun - Destination tunnel IP address. Type: string
| |
| | ... | *Example:*
| | ... | \| ${encr_alg}= \| Crypto Alg AES CBC 128 \|
| | ... | \| ${auth_alg}= \| Integ Alg SHA1 96 \|
| | ... | \| Send IPsec Packet and verify ESP encapsulation in received packet\
| | ... | \| ${nodes['TG']} \| eth1 \| eth2 \
| | ... | \| 52:54:00:d4:d8:22 \| 52:54:00:d4:d8:3e \| ${encr_alg} \
| | ... | \| sixteenbytes_key \| ${auth_alg} \| twentybytessecretkey \
| | ... | \| ${1001} \| ${1000} \| 192.168.3.3 \| 192.168.4.4 \| 192.168.100.2 \
| | ... | \| 192.168.100.3 \|
| |
| | [Arguments] | ${node} | ${tx_interface} | ${rx_interface} | ${tx_dst_mac}
| | ... | ${rx_src_mac} | ${crypto_alg} | ${crypto_key} | ${integ_alg}
| | ... | ${integ_key} | ${l_spi} | ${r_spi} | ${src_ip} | ${dst_ip}
| | ... | ${src_tun} | ${dst_tun}
| |
| | ${tx_src_mac}= | Get Interface Mac | ${node} | ${tx_interface}
| | ${tx_if_name}= | Get Interface Name | ${node} | ${tx_interface}
| | ${rx_dst_mac}= | Get Interface Mac | ${node} | ${rx_interface}
| | ${rx_if_name}= | Get Interface Name | ${node} | ${rx_interface}
| | ${crypto_alg_str}= | Get Crypto Alg Scapy Name | ${crypto_alg}
| | ${integ_alg_str}= | Get Integ Alg Scapy Name | ${integ_alg}
| | ${args}= | Catenate | --rx_if ${rx_if_name} | --tx_if ${tx_if_name}
| | ... | --tx_src_mac ${tx_src_mac} | --tx_dst_mac ${tx_dst_mac}
| | ... | --rx_src_mac ${rx_src_mac} | --rx_dst_mac ${rx_dst_mac}
| | ... | --src_ip ${src_ip} | --dst_ip ${dst_ip}
| | ... | --crypto_alg ${crypto_alg_str} | --crypto_key ${crypto_key}
| | ... | --integ_alg ${integ_alg_str} | --integ_key ${integ_key}
| | ... | --l_spi ${l_spi} | --r_spi ${r_spi} | --src_tun ${src_tun}
| | ... | --dst_tun ${dst_tun}
| | Run Traffic Script On Node | ipsec_interface.py | ${node} | ${args}

| Send packet and verify LISP GPE encap
| | [Documentation] | Send ICMP packet to DUT out one interface and receive\
| | ... | a LISP-GPE encapsulated packet on the other interface.
| |
| | ... | *Arguments:*
| |
| | ... | _NOTE:_ Arguments are based on topology:
| | ... | TG(if1)->(if1)DUT(if2)->TG(if2)
| |
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_port - Interface of TG-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT1-if2. Type: string
| | ... | - rx_dst_mac - MAC address of TG-if2. Type: string
| | ... | - src_rloc - configured RLOC source address. Type: string
| | ... | - dst_rloc - configured RLOC destination address. Type: string
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Send packet and verify LISP GPE encap \| ${nodes['TG']} \
| | ... | \| 10.0.0.1 \| 32.0.0.1 \
| | ... | \| eth2 \| 08:00:27:ee:fd:b3 \| 08:00:27:a2:52:5b \
| | ... | \| eth3 \| 08:00:27:4d:ca:7a \| 08:00:27:7d:fd:10 \
| | ... | \| 10.0.1.1 \| 10.0.1.2 \|
| |
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port} |
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac}
| | ... | ${rx_dst_mac} | ${src_rloc} | ${dst_rloc}
| |
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip}
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | ... | --src_rloc | ${src_rloc} | --dst_rloc | ${dst_rloc}
| | Run Traffic Script On Node | lisp/lispgpe_check.py | ${tg_node}
| | ... | ${args}

| Send packet and verify LISPoTunnel encap
| | [Documentation] | Send ICMP packet to DUT out one interface and receive\
| | ... | a LISP encapsulated packet on the other interface.
| |
| | ... | *Arguments:*
| |
| | ... | _NOTE:_ Arguments are based on topology:
| | ... | TG(if1)->(if1)DUT(if2)->TG(if2)
| |
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_port - Interface of TG-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT1-if2. Type: string
| | ... | - rx_dst_mac - MAC address of TG-if2. Type: string
| | ... | - src_rloc - configured RLOC source address. Type: string
| | ... | - dst_rloc - configured RLOC destination address. Type: string
| | ... | - ot_mode - overlay tunnel mode. Type: string
| |
| | ... | *Return:*
| | ... | - No value returned
| |
| | ... | *Example:*
| |
| | ... | \| Send packet and verify LISP encap \| ${nodes['TG']} \| 10.0.0.1 \
| | ... | \| 32.0.0.1 \| eth2 \| 08:00:27:ee:fd:b3 \| 08:00:27:a2:52:5b \
| | ... | \| eth3 \| 08:00:27:4d:ca:7a \| 08:00:27:7d:fd:10 \| 10.0.1.1 \
| | ... | \| 10.0.1.2 \|
| |
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port}
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac}
| | ... | ${rx_dst_mac} | ${src_rloc} | ${dst_rloc} | ${ot_mode}
| |
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip}
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | ... | --src_rloc | ${src_rloc} | --dst_rloc | ${dst_rloc}
| | ... | --ot_mode | ${ot_mode}
| | Run Traffic Script On Node | lisp/lispgpe_check.py | ${tg_node}
| | ... | ${args}
