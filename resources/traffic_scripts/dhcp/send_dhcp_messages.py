#!/usr/bin/env python
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

"""Traffic script that sends an DHCP packets."""

import sys

from scapy.all import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.inet import UDP_SERVICES
from scapy.layers.dhcp import DHCP, BOOTP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def dhcp_discover(args):
    """Send DHCP DISCOVER packet."""

    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    tx_src_ip = "0.0.0.0"
    tx_dst_ip = "255.255.255.255"

    server_ip = args.get_arg('server_ip')
    proxy_ip = args.get_arg('proxy_ip')
    client_mac = args.get_arg('client_mac')

    sent_packets = []

    dhcp_discover = Ether(src=client_mac, dst="ff:ff:ff:ff:ff:ff") / \
                    IP(src=tx_src_ip, dst=tx_dst_ip) / \
                    UDP(sport=68, dport=67) / \
                    BOOTP(op=1,) / \
                    DHCP(options=[("message-type", "discover"),
                                  "end"])

    sent_packets.append(dhcp_discover)
    txq.send(dhcp_discover)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP DISCOVER timeout')

    if ether[IP].src != proxy_ip:
        raise RuntimeError("Source IP address error.")
    print "Source IP address: OK."

    if ether[IP].dst != server_ip:
        raise RuntimeError("Destination IP address error.")
    print "Destination IP address: OK."

    if ether[UDP].dport != UDP_SERVICES.bootps:
        raise RuntimeError("UDP destination port error.")
    print "UDP destination port: OK."

    if ether[UDP].sport != UDP_SERVICES.bootpc:
        raise RuntimeError("UDP source port error.")
    print "UDP source port: OK."

    if ether[DHCP].options[1][0] != 'relay_agent_Information':  # option 82
        raise RuntimeError("Relay agent information error.")
    option_82 = ether[DHCP].options[1][1]

    if ether[DHCP].options[0][1] != 1:  # 1 - DISCOVER message
        raise RuntimeError("DHCP DISCOVER message error.")
    print "DHCP DISCOVER message OK."
    dhcp_offer(args, option_82)


def dhcp_offer(args, option_82):
    """Send DHCP OFFER packet."""

    rx_if = args.get_arg('tx_if')
    tx_if = args.get_arg('rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    tx_dst_ip = "255.255.255.255"
    server_ip = args.get_arg('server_ip')
    server_mac = args.get_arg('server_mac')
    client_ip = args.get_arg('client_ip')
    proxy_ip = args.get_arg('proxy_ip')

    sent_packets = []

    print option_82

    dhcp_offer = Ether(src=server_mac, dst="ff:ff:ff:ff:ff:ff") / \
                 IP(src=server_ip, dst=tx_dst_ip) / \
                 UDP(sport=67, dport=68) / \
                 BOOTP(op=2,
                       yiaddr=client_ip,
                       siaddr=server_ip) / \
                 DHCP(options=
                      [("message-type", "offer"),
                       ("server_id", server_ip),
                       ("relay_agent_Information", option_82),
                       "end"])

    txq.send(dhcp_offer)
    sent_packets.append(dhcp_offer)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP OFFER timeout')

    if ether[IP].dst != tx_dst_ip:
        raise RuntimeError("Destination IP address error.")
    print "Destination IP address: OK."

    if ether[IP].src != proxy_ip:
        raise RuntimeError("Source IP address error.")
    print "Source IP address: OK."

    if ether[UDP].dport != UDP_SERVICES.bootpc:
        raise RuntimeError("UDP destination port error.")
    print "UDP destination port: OK."

    if ether[UDP].sport != UDP_SERVICES.bootps:
        raise RuntimeError("UDP source port error.")
    print "UDP source port: OK."

    if ether[BOOTP].yiaddr != client_ip:
        raise RuntimeError("Client IP address error.")
    print "Client IP address: OK."

    if ether[BOOTP].siaddr != server_ip:
        raise RuntimeError("DHCP server IP address error.")
    print "DHCP server IP address: OK."

    if ether[DHCP].options[0][1] != 2:  # 2 - OFFER message
        raise RuntimeError("DHCP OFFER message error.")
    print "DHCP OFFER message OK."
    dhcp_request(args)


def dhcp_request(args):
    """Send DHCP REQUEST packet."""

    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    tx_dst_ip = "255.255.255.255"
    server_ip = args.get_arg('server_ip')
    client_ip = args.get_arg('client_ip')
    client_mac = args.get_arg('client_mac')
    proxy_ip = args.get_arg('proxy_ip')

    sent_packets = []

    dhcp_request = Ether(src=client_mac, dst="ff:ff:ff:ff:ff:ff") / \
                   IP(src="0.0.0.0", dst=tx_dst_ip) / \
                   UDP(sport=68, dport=67) / \
                   BOOTP(op=1,
                         giaddr=proxy_ip,
                         siaddr=server_ip) / \
                   DHCP(options=[("message-type", "request"),
                                 ("server_id", server_ip),
                                 ("requested_addr", client_ip),
                                 "end"])

    sent_packets.append(dhcp_request)
    txq.send(dhcp_request)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP REQUEST timeout')

    if ether[IP].dst != server_ip:
        raise RuntimeError("Destination IP address error.")
    print "Destination IP address: OK."

    if ether[IP].src != proxy_ip:
        raise RuntimeError("Source IP address error.")
    print "Source IP address: OK."

    if ether[UDP].dport != UDP_SERVICES.bootps:
        raise RuntimeError("UDP destination port error.")
    print "UDP destination port: OK."

    if ether[UDP].sport != UDP_SERVICES.bootpc:
        raise RuntimeError("UDP source port error.")
    print "UDP source port: OK."

    if ether[BOOTP].siaddr != server_ip:
        raise RuntimeError("DHCP server IP address error.")
    print "DHCP server IP address: OK."

    if ether[DHCP].options[2][1] != client_ip:
        raise RuntimeError("Requested IP address error.")
    print "Requested IP address: OK."

    if ether[DHCP].options[3][0] != 'relay_agent_Information':  # option 82
        raise RuntimeError("Relay agent information error.")
    option_82 = ether[DHCP].options[3][1]

    if ether[DHCP].options[0][1] != 3:  # 2 - REQUEST message
        raise RuntimeError("DHCP REQUEST message error.")
    print "DHCP REQUEST message: OK."
    dhcp_ack(args, option_82)


def dhcp_ack(args, option_82):
    """Send DHCP ACK packet."""

    rx_if = args.get_arg('tx_if')
    tx_if = args.get_arg('rx_if')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    tx_dst_ip = "255.255.255.255"
    server_ip = args.get_arg('server_ip')
    server_mac = args.get_arg('server_mac')
    client_ip = args.get_arg('client_ip')
    proxy_ip = args.get_arg('proxy_ip')

    print option_82
    sent_packets = []

    dhcp_ack = Ether(src=server_mac, dst="ff:ff:ff:ff:ff:ff") / \
               IP(src=server_ip, dst=tx_dst_ip) / \
               UDP(sport=67, dport=68) / \
               BOOTP(op=2,
                     yiaddr=client_ip,
                     siaddr=server_ip) / \
               DHCP(options=
                    [("message-type", "ack"),
                     ("server_id", server_ip),
                     ("lease_time", 43200),
                     ("relay_agent_Information", option_82),
                     "end"])

    txq.send(dhcp_ack)
    sent_packets.append(dhcp_ack)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError('DHCP ACK timeout')

    print "ACK OPTIONS:"
    print ether[DHCP].options

    if ether[IP].dst != tx_dst_ip:
        raise RuntimeError("Destination IP address error.")
    print "Destination IP address: OK."

    if ether[IP].src != proxy_ip:
        raise RuntimeError("Source IP address error.")
    print "Source IP address: OK."

    if ether[UDP].dport != UDP_SERVICES.bootpc:
        raise RuntimeError("UDP destination port error.")
    print "UDP destination port: OK."

    if ether[UDP].sport != UDP_SERVICES.bootps:
        raise RuntimeError("UDP source port error.")
    print "UDP source port: OK."

    if ether[BOOTP].yiaddr != client_ip:
        raise RuntimeError("Client IP address error.")
    print "Client IP address: OK."

    if ether[BOOTP].siaddr != server_ip:
        raise RuntimeError("DHCP server IP address error.")
    print "DHCP server IP address: OK."

    if ether[DHCP].options[0][1] != 5:  # 5 - ACK message
        raise RuntimeError("DHCP ACK message error.")
    print "DHCP ACK message OK."

    print ether[DHCP].options


def main():
    """Send DHCP messages."""

    args = TrafficScriptArg(['server_ip', 'server_mac', 'client_ip',
                             'client_mac', 'proxy_ip'])

    dhcp_discover(args)

    sys.exit(0)

if __name__ == "__main__":
    main()
