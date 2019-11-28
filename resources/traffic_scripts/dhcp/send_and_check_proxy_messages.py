#!/usr/bin/env python
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the u"License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an u"AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Traffic script that sends DHCP packets."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.inet import UDP_SERVICES
from scapy.layers.dhcp import DHCP, BOOTP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def dhcp_discover(tx_if, rx_if, tx_src_ip, tx_dst_ip, server_ip, proxy_ip,
                  client_mac):
    """Send and check DHCP DISCOVER proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_discover = Ether(src=client_mac, dst=u"ff:ff:ff:ff:ff:ff") / \
                    IP(src=tx_src_ip, dst=tx_dst_ip) / \
                    UDP(sport=UDP_SERVICES.bootpc, dport=UDP_SERVICES.bootps) / \
                    BOOTP(op=1,) / \
                    DHCP(options=[(u"message-type", u"discover"),
                                  u"end"])

    sent_packets.append(dhcp_discover)
    txq.send(dhcp_discover)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError(f'DHCP DISCOVER timeout')

    if ether[IP].src != proxy_ip:
        raise RuntimeError(f"Source IP address error.")
    print (f"Source IP address: OK.")

    if ether[IP].dst != server_ip:
        raise RuntimeError(f"Destination IP address error.")
    print (f"Destination IP address: OK.")

    if ether[UDP].dport != UDP_SERVICES.bootps:
        raise RuntimeError(f"UDP destination port error.")
    print (f"UDP destination port: OK.")

    if ether[UDP].sport != UDP_SERVICES.bootpc:
        raise RuntimeError(f"UDP source port error.")
    print (f"UDP source port: OK.")

    if ether[DHCP].options[1][0] != u'relay_agent_Information':  # option 82
        raise RuntimeError(f"Relay agent information error.")
    option_82 = ether[DHCP].options[1][1]

    if ether[DHCP].options[0][1] != 1:  # 1 - DISCOVER message
        raise RuntimeError(f"DHCP DISCOVER message error.")
    print (f"DHCP DISCOVER message OK.")

    return option_82


def dhcp_offer(rx_if, tx_if, tx_dst_ip, server_ip, proxy_ip, client_ip,
               server_mac, option_82):
    """Send and check DHCP OFFER proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_offer = Ether(src=server_mac, dst=u"ff:ff:ff:ff:ff:ff") / \
                 IP(src=server_ip, dst=tx_dst_ip) / \
                 UDP(sport=UDP_SERVICES.bootps, dport=UDP_SERVICES.bootpc) / \
                 BOOTP(op=2,
                       yiaddr=client_ip,
                       siaddr=server_ip) / \
                 DHCP(options=
                      [(u"message-type", u"offer"),
                       (u"server_id", server_ip),
                       (u"relay_agent_Information", option_82),
                       u"end"])

    txq.send(dhcp_offer)
    sent_packets.append(dhcp_offer)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError(f'DHCP OFFER timeout')

    if ether[IP].dst != tx_dst_ip:
        raise RuntimeError(f"Destination IP address error.")
    print (f"Destination IP address: OK.")

    if ether[IP].src != proxy_ip:
        raise RuntimeError(f"Source IP address error.")
    print (f"Source IP address: OK.")

    if ether[UDP].dport != UDP_SERVICES.bootpc:
        raise RuntimeError(f"UDP destination port error.")
    print (f"UDP destination port: OK.")

    if ether[UDP].sport != UDP_SERVICES.bootps:
        raise RuntimeError(f"UDP source port error.")
    print (f"UDP source port: OK.")

    if ether[BOOTP].yiaddr != client_ip:
        raise RuntimeError(f"Client IP address error.")
    print (f"Client IP address: OK.")

    if ether[BOOTP].siaddr != server_ip:
        raise RuntimeError(f"DHCP server IP address error.")
    print (f"DHCP server IP address: OK.")

    if ether[DHCP].options[0][1] != 2:  # 2 - OFFER message
        raise RuntimeError(f"DHCP OFFER message error.")
    print (f"DHCP OFFER message OK.")


def dhcp_request(tx_if, rx_if, tx_src_ip, tx_dst_ip, server_ip, proxy_ip,
                 client_ip, client_mac):
    """Send and check DHCP REQUEST proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    dhcp_request = Ether(src=client_mac, dst=u"ff:ff:ff:ff:ff:ff") / \
                   IP(src=tx_src_ip, dst=tx_dst_ip) / \
                   UDP(sport=UDP_SERVICES.bootpc, dport=UDP_SERVICES.bootps) / \
                   BOOTP(op=1,
                         giaddr=proxy_ip,
                         siaddr=server_ip) / \
                   DHCP(options=[(u"message-type", u"request"),
                                 (u"server_id", server_ip),
                                 (u"requested_addr", client_ip),
                                 u"end"])

    sent_packets.append(dhcp_request)
    txq.send(dhcp_request)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError(f'DHCP REQUEST timeout')

    if ether[IP].dst != server_ip:
        raise RuntimeError(f"Destination IP address error.")
    print (f"Destination IP address: OK.")

    if ether[IP].src != proxy_ip:
        raise RuntimeError(f"Source IP address error.")
    print (f"Source IP address: OK.")

    if ether[UDP].dport != UDP_SERVICES.bootps:
        raise RuntimeError(f"UDP destination port error.")
    print (f"UDP destination port: OK.")

    if ether[UDP].sport != UDP_SERVICES.bootpc:
        raise RuntimeError(f"UDP source port error.")
    print (f"UDP source port: OK.")

    if ether[BOOTP].siaddr != server_ip:
        raise RuntimeError(f"DHCP server IP address error.")
    print (f"DHCP server IP address: OK.")

    if ether[DHCP].options[2][1] != client_ip:
        raise RuntimeError(f"Requested IP address error.")
    print (f"Requested IP address: OK.")

    if ether[DHCP].options[3][0] != u'relay_agent_Information':  # option 82
        raise RuntimeError(f"Relay agent information error.")

    if ether[DHCP].options[0][1] != 3:  # 2 - REQUEST message
        raise RuntimeError(f"DHCP REQUEST message error.")
    print (f"DHCP REQUEST message: OK.")


def dhcp_ack(rx_if, tx_if, tx_dst_ip, server_ip, proxy_ip, client_ip,
             server_mac, option_82):
    """Send and check DHCP ACK proxy packet."""

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    lease_time = 43200  # 12 hours

    sent_packets = []

    dhcp_ack = Ether(src=server_mac, dst=u"ff:ff:ff:ff:ff:ff") / \
               IP(src=server_ip, dst=tx_dst_ip) / \
               UDP(sport=UDP_SERVICES.bootps, dport=UDP_SERVICES.bootpc) / \
               BOOTP(op=2,
                     yiaddr=client_ip,
                     siaddr=server_ip) / \
               DHCP(options=
                    [(u"message-type", u"ack"),
                     (u"server_id", server_ip),
                     (u"lease_time", lease_time),
                     (u"relay_agent_Information", option_82),
                     u"end"])

    txq.send(dhcp_ack)
    sent_packets.append(dhcp_ack)

    ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError(f'DHCP ACK timeout')

    if ether[IP].dst != tx_dst_ip:
        raise RuntimeError(f"Destination IP address error.")
    print (f"Destination IP address: OK.")

    if ether[IP].src != proxy_ip:
        raise RuntimeError(f"Source IP address error.")
    print (f"Source IP address: OK.")

    if ether[UDP].dport != UDP_SERVICES.bootpc:
        raise RuntimeError(f"UDP destination port error.")
    print (f"UDP destination port: OK.")

    if ether[UDP].sport != UDP_SERVICES.bootps:
        raise RuntimeError(f"UDP source port error.")
    print (f"UDP source port: OK.")

    if ether[BOOTP].yiaddr != client_ip:
        raise RuntimeError(f"Client IP address error.")
    print (f"Client IP address: OK.")

    if ether[BOOTP].siaddr != server_ip:
        raise RuntimeError(f"DHCP server IP address error.")
    print (f"DHCP server IP address: OK.")

    if ether[DHCP].options[2][1] != lease_time:
        raise RuntimeError(f"DHCP lease time error.")
    print (f"DHCP lease time OK.")

    if ether[DHCP].options[0][1] != 5:  # 5 - ACK message
        raise RuntimeError(f"DHCP ACK message error.")
    print (f"DHCP ACK message OK.")


def main():
    """Send DHCP proxy messages."""

    args = TrafficScriptArg([u'server_ip', u'server_mac', u'client_ip',
                             u'client_mac', u'proxy_ip'])

    tx_if = args.get_arg(u'tx_if')
    rx_if = args.get_arg(u'rx_if')

    tx_src_ip = u"0.0.0.0"
    tx_dst_ip = u"255.255.255.255"

    server_ip = args.get_arg(u'server_ip')
    client_ip = args.get_arg(u'client_ip')
    proxy_ip = args.get_arg(u'proxy_ip')
    client_mac = args.get_arg(u'client_mac')
    server_mac = args.get_arg(u'server_mac')

    # DHCP DISCOVER
    option_82 = dhcp_discover(tx_if, rx_if, tx_src_ip, tx_dst_ip, server_ip,
                              proxy_ip, client_mac)

    # DHCP OFFER
    dhcp_offer(tx_if, rx_if, tx_dst_ip, server_ip, proxy_ip, client_ip,
               server_mac, option_82)

    # DHCP REQUEST
    dhcp_request(tx_if, rx_if, tx_src_ip, tx_dst_ip, server_ip, proxy_ip,
                 client_ip, client_mac)

    # DHCP ACK
    dhcp_ack(tx_if, rx_if, tx_dst_ip, server_ip, proxy_ip, client_ip,
             server_mac, option_82)

    sys.exit(0)

if __name__ == "__main__":
    main()
