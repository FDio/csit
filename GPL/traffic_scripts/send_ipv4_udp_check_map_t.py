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

"""Traffic script that sends a UDP datagram and checks if IPv4 addresses
are correctly translate to IPv6 addresses."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from ipaddress import ip_address

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def _check_udp_checksum(pkt):
    """Check UDP checksum in IP packet. Return True if checksum is correct
    else False."""
    new = pkt.__class__(str(pkt))
    del new['UDP'].chksum
    new = new.__class__(str(new))
    return new['UDP'].chksum == pkt['UDP'].chksum


def _is_udp_in_ipv6(pkt):
    """If IPv6 next header type in the given pkt is UDP, return True,
    else return False. False is returned also if exception occurs."""
    ipv6_type = int('0x86dd', 16)  # IPv6
    try:
        if pkt.type == ipv6_type:
            if pkt.payload.nh == 17:  # UDP
                return True
    except AttributeError:
        return False
    return False


def main():  # pylint: disable=too-many-statements, too-many-locals
    """Main function of the script file."""
    args = TrafficScriptArg(['tx_dst_mac', 'tx_src_ipv4', 'tx_dst_ipv4',
                             'tx_dst_udp_port', 'rx_dst_mac', 'rx_src_mac',
                             'rx_src_ipv6', 'rx_dst_ipv6'])
    rx_if = args.get_arg('rx_if')
    tx_if = args.get_arg('tx_if')
    tx_dst_mac = args.get_arg('tx_dst_mac')
    tx_src_ipv4 = args.get_arg('tx_src_ipv4')
    tx_dst_ipv4 = args.get_arg('tx_dst_ipv4')
    tx_dst_udp_port = int(args.get_arg('tx_dst_udp_port'))
    tx_src_udp_port = 20000
    rx_dst_mac = args.get_arg('rx_dst_mac')
    rx_src_mac = args.get_arg('rx_src_mac')
    rx_src_ipv6 = args.get_arg('rx_src_ipv6')
    rx_dst_ipv6 = args.get_arg('rx_dst_ipv6')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    # Create empty UDP datagram
    udp = (Ether(dst=tx_dst_mac) /
           IP(src=tx_src_ipv4, dst=tx_dst_ipv4) /
           UDP(sport=tx_src_udp_port, dport=tx_dst_udp_port) /
           'udp_payload')

    txq.send(udp)
    sent_packets.append(udp)

    for _ in range(5):
        pkt = rxq.recv(2)
        if _is_udp_in_ipv6(pkt):
            ether = pkt
            break
    else:
        raise RuntimeError("UDP in IPv6 Rx error.")

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
    if ip_address(unicode(ipv6.dst)) != ip_address(unicode(rx_dst_ipv6)):
        raise RuntimeError("Destination IP error {} != {}.".
                           format(ipv6.dst, rx_dst_ipv6))
    print "Destination IPv6: OK."

    if ip_address(unicode(ipv6.src)) != ip_address(unicode(rx_src_ipv6)):
        raise RuntimeError("Source IP error {} != {}.".
                           format(ipv6.src, rx_src_ipv6))
    print "Source IPv6: OK."

    udp = ipv6.payload

    # check udp
    if udp.dport != tx_dst_udp_port:
        raise RuntimeError("UDP dport error {} != {}.".
                           format(udp.dport, tx_dst_udp_port))
    print "UDP dport: OK."

    if udp.sport != tx_src_udp_port:
        raise RuntimeError("UDP sport error {} != {}.".
                           format(udp.sport, tx_src_udp_port))
    print "UDP sport: OK."

    if not _check_udp_checksum(ipv6):
        raise RuntimeError("UDP checksum error.")
    print "UDP checksum OK."

    sys.exit(0)

if __name__ == "__main__":
    main()
