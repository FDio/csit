#!/usr/bin/env python

# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""Traffic script that sends an empty IPv4 UDP datagram encapsulated in IPv6
and checks if is correctly decapsulated."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet6 import IPv6
from scapy.layers.inet import IP, UDP

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def _is_udp_in_ipv4(pkt):
    """If UDP is in IPv4 packet return True,
    else return False. False is returned also if exception occurs."""
    ipv4_type = int('0x0800', 16)  # IPv4
    try:
        if pkt.type == ipv4_type:
            if pkt.payload.proto == 17:  # UDP
                return True
    except:  # pylint: disable=bare-except
        return False
    return False


def main():  # pylint: disable=too-many-statements, too-many-locals
    """Main function of the script file."""
    args = TrafficScriptArg(['tx_dst_mac', 'tx_src_mac',
                             'tx_dst_ipv6', 'tx_src_ipv6',
                             'tx_dst_ipv4', 'tx_src_ipv4', 'tx_src_udp_port',
                             'rx_dst_mac', 'rx_src_mac'])
    rx_if = args.get_arg('rx_if')
    tx_if = args.get_arg('tx_if')
    tx_src_mac = args.get_arg('tx_src_mac')
    tx_dst_mac = args.get_arg('tx_dst_mac')
    tx_dst_ipv6 = args.get_arg('tx_dst_ipv6')
    tx_src_ipv6 = args.get_arg('tx_src_ipv6')
    tx_dst_ipv4 = args.get_arg('tx_dst_ipv4')
    tx_src_ipv4 = args.get_arg('tx_src_ipv4')
    tx_src_udp_port = int(args.get_arg('tx_src_udp_port'))
    tx_dst_udp_port = 20000
    rx_dst_mac = args.get_arg('rx_dst_mac')
    rx_src_mac = args.get_arg('rx_src_mac')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    # Create empty UDP datagram in IPv4 and IPv6
    tx_pkt = (Ether(dst=tx_dst_mac, src=tx_src_mac) /
              IPv6(src=tx_src_ipv6, dst=tx_dst_ipv6) /
              IP(src=tx_src_ipv4, dst=tx_dst_ipv4) /
              UDP(sport=tx_src_udp_port, dport=tx_dst_udp_port))

    txq.send(tx_pkt)
    sent_packets.append(tx_pkt)

    for _ in range(5):
        pkt = rxq.recv(2)
        if _is_udp_in_ipv4(pkt):
            ether = pkt
            break
    else:
        raise RuntimeError("UDP in IPv4 Rx error.")

    # check ethernet
    if ether.dst != rx_dst_mac:
        raise RuntimeError("Destination MAC error {} != {}.".
                           format(ether.dst, rx_dst_mac))
    print "Destination MAC: OK."

    if ether.src != rx_src_mac:
        raise RuntimeError("Source MAC error {} != {}.".
                           format(ether.src, rx_src_mac))
    print "Source MAC: OK."

    ipv4 = ether.payload

    # check ipv4
    if ipv4.dst != tx_dst_ipv4:
        raise RuntimeError("Destination IPv4 error {} != {}.".
                           format(ipv4.dst, tx_dst_ipv4))
    print "Destination IPv4: OK."

    if ipv4.src != tx_src_ipv4:
        raise RuntimeError("Source IPv4 error {} != {}.".
                           format(ipv4.src, tx_src_ipv4))
    print "Source IPv4: OK."

    if ipv4.proto != 17:  # UDP
        raise RuntimeError("IPv4 protocol error {} != UDP.".
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
