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

"""Traffic script for IPsec verification."""

import sys
import logging

# pylint: disable=no-name-in-module
# pylint: disable=import-error
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import Ether
from scapy.layers.inet import IP, TCP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from ipaddress import ip_address

from .TrafficScriptArg import TrafficScriptArg
from .PacketVerifier import RxQueue, TxQueue


def check_ipv4(pkt_recv, dscp):
    """Check received IPv4 IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param dscp: DSCP value to check.
    :type pkt_recv: scapy.Ether
    :type dscp: int
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IP):
        raise RuntimeError('Not an IPv4 packet received: {0}'.
                           format(pkt_recv.__repr__()))

    rx_dscp = pkt_recv[IP].tos >> 2
    if rx_dscp != dscp:
        raise RuntimeError('Invalid DSCP {0} should be {1}'.
                           format(rx_dscp, dscp))

    if not pkt_recv.haslayer(TCP):
        raise RuntimeError('Not a TCP packet received: {0}'.
                           format(pkt_recv.__repr__()))


def check_ipv6(pkt_recv, dscp):
    """Check received IPv6 IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param dscp: DSCP value to check.
    :type pkt_recv: scapy.Ether
    :type dscp: int
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IPv6):
        raise RuntimeError('Not an IPv6 packet received: {0}'.
                           format(pkt_recv.__repr__()))

    rx_dscp = pkt_recv[IPv6].tc >> 2
    if rx_dscp != dscp:
        raise RuntimeError('Invalid DSCP {0} should be {1}'.
                           format(rx_dscp, dscp))

    if not pkt_recv.haslayer(TCP):
        raise RuntimeError('Not a TCP packet received: {0}'.
                           format(pkt_recv.__repr__()))


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def main():
    """Send and receive TCP packet."""
    args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip', 'dscp'])

    rxq = RxQueue(args.get_arg('rx_if'))
    txq = TxQueue(args.get_arg('tx_if'))

    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    dscp = int(args.get_arg('dscp'))

    if 6 == ip_address(unicode(src_ip)).version:
        is_ipv4 = False
    else:
        is_ipv4 = True

    sent_packets = []

    if is_ipv4:
        ip_pkt = (IP(src=src_ip, dst=dst_ip) /
                  TCP())
    else:
        ip_pkt = (IPv6(src=src_ip, dst=dst_ip) /
                  TCP())

    pkt_send = (Ether(src=src_mac, dst=dst_mac) /
                ip_pkt)

    sent_packets.append(pkt_send)
    txq.send(pkt_send)

    while True:
        pkt_recv = rxq.recv(2, sent_packets)
        if pkt_recv is None:
            raise RuntimeError('ICMPv6 echo reply Rx timeout')

        if pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if pkt_recv is None:
        raise RuntimeError('Rx timeout')

    if is_ipv4:
        check_ipv4(pkt_recv, dscp)
    else:
        check_ipv6(pkt_recv, dscp)

    sys.exit(0)


if __name__ == "__main__":
    main()
