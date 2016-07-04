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

# TODO: change documentation
"""Traffic script that sends an empty IPv4 UDP datagram encapsulated in IPv6
and checks if is correctly decapsulated."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet6 import IPv6
from scapy.layers.inet import IP, UDP

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def _is_ip_in_ip(pkt):
    """If IPv6 next header type in the given pkt is IPv4, return True,
    else return False. False is returned also if exception occurs."""
    ipv6_type = int('0x86dd', 16)  # IPv6
    try:
        if pkt.type == ipv6_type:
            if pkt.payload.nh == 4:
                return True
    except:
        return False
    return False


def main():
    """Main function of the script file."""
    args = TrafficScriptArg(['tx_dst_mac',
                             'tx_dst_ipv6', 'tx_src_ipv6',
                             'tx_dst_ipv4', 'tx_src_ipv4',
                             'tx_dst_udp_port', 'tx_src_udp_port',
                             'rx_dst_mac', 'rx_src_mac',
                             'rx_dst_ipv6', 'rx_src_ipv6'
                             ])
    rx_if = args.get_arg('rx_if')
    tx_if = args.get_arg('tx_if')
    tx_dst_mac = args.get_arg('tx_dst_mac')
    tx_src_mac = '02:00:00:00:00:01'

    tx_dst_ipv6 = args.get_arg('tx_dst_ipv6')
    tx_src_ipv6 = args.get_arg('tx_src_ipv6')
    tx_dst_ipv4 = args.get_arg('tx_dst_ipv4')
    tx_src_ipv4 = args.get_arg('tx_src_ipv4')
    tx_dst_udp_port = int(args.get_arg('tx_dst_udp_port'))
    tx_src_udp_port = int(args.get_arg('tx_src_udp_port'))
    rx_dst_mac = args.get_arg('rx_dst_mac')
    rx_src_mac = args.get_arg('rx_src_mac')
    rx_dst_ipv6 = args.get_arg('rx_dst_ipv6')
    rx_src_ipv6 = args.get_arg('rx_src_ipv6')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    # Create empty UDP datagram in IPv4 and IPv6
    tx_pkt = Ether(dst=tx_dst_mac, src=tx_src_mac)
    tx_pkt /= IPv6(src=tx_src_ipv6, dst=tx_dst_ipv6)
    tx_pkt /= IP(src=tx_src_ipv4, dst=tx_dst_ipv4)
    tx_pkt /= UDP(sport=tx_src_udp_port, dport=tx_dst_udp_port)

    txq.send(tx_pkt)
    sent_packets.append(tx_pkt)

    for _ in range(5):
        pkt = rxq.recv(2, ignore=sent_packets)
        if _is_ip_in_ip(pkt):
            ether = pkt
            break
    else:
        raise RuntimeError("UDP in IP Rx error.")

    # check ethernet
    if ether.dst != rx_dst_mac:
        raise RuntimeError("Destination MAC error {} != {}.".
                           format(ether.dst, rx_dst_mac))
    print "Destination MAC: OK."

    if ether.src != rx_src_mac:
        raise RuntimeError("Source MAC error {} != {}.".
                           format(ether.src, rx_src_mac))
    print "Source MAC: OK."

    ipv6 = ether.payload

    # check ipv6
    if ipv6.dst != rx_dst_ipv6:
        raise RuntimeError("Destination IP error {} != {}.".
                           format(ipv6.dst,  rx_dst_ipv6))
    print "Destination IPv6: OK."

    if ipv6.src != rx_src_ipv6:
        raise RuntimeError("Source IP error {} != {}.".
                           format(ipv6.src,  rx_src_ipv6))
    print "Source IPv6: OK."

    ipv4 = ipv6.payload

    # check ipv4
    if ipv4.dst != tx_dst_ipv4:
        raise RuntimeError("Destination IP error {} != {}.".
                           format(ipv4.dst, tx_dst_ipv4))
    print "Destination IPv4: OK."

    if ipv4.src != tx_src_ipv4:
        raise RuntimeError("Source IP error {} != {}.".
                           format(ipv4.src,  tx_src_ipv4))
    print "Source IPv4: OK."

    if ipv4.proto != 17:  # UDP
        raise RuntimeError("IP protocol error {} != UDP.".
                           format(ipv4.proto))
    print "IPv4 protocol: OK."

    udp = ipv4.payload

    # check udp
    if udp.dport != tx_dst_udp_port:
        raise RuntimeError("UDP dport error {} != {}.".
                           format(udp.dport, tx_dst_udp_port))
    print "UDP dport: OK."

    if udp.sport != tx_src_udp_port:
        raise RuntimeError("UDP sport error {} != {}.".
                           format(udp.sport, tx_src_udp_port))
    print "UDP sport: OK."

    sys.exit(0)

if __name__ == "__main__":
    main()
