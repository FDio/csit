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

"""Traffic script that sends an TCP or UDP packet
from one interface to the other.
"""

import sys
import ipaddress

from scapy.all import Ether
from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def valid_ipv4(ip):
    """Check if IP address has the correct IPv4 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv4 address format,
             otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv4Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def valid_ipv6(ip):
    """Check if IP address has the correct IPv6 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv6 address format,
             otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv6Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send TCP or UDP packet from one traffic generator interface to the other.
    """
    args = TrafficScriptArg(['tx_mac', 'rx_mac', 'src_ip', 'dst_ip', 'protocol',
                             'source_port', 'destination_port'])

    src_mac = args.get_arg('tx_mac')
    dst_mac = args.get_arg('rx_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')

    protocol = args.get_arg('protocol')
    source_port = args.get_arg('source_port')
    destination_port = args.get_arg('destination_port')

    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_version = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_version = IPv6
    else:
        ValueError("Invalid IP version!")

    if protocol.upper() == 'TCP':
        protocol = TCP
    elif protocol.upper() == 'UDP':
        protocol = UDP
    else:
        raise ValueError("Invalid protocol type!")

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
               ip_version(src=src_ip, dst=dst_ip) /
               protocol(sport=int(source_port), dport=int(destination_port)))

    txq.send(pkt_raw)

    while True:
        ether = rxq.recv(2)
        if ether is None:
            raise RuntimeError('TCP/UDP Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if TCP in ether:
        print ("TCP packet received.")

    elif UDP in ether:
        print ("UDP packet received.")
    else:
        raise RuntimeError("Not an TCP or UDP packet received {0}".
                           format(ether.__repr__()))

    sys.exit(0)


if __name__ == "__main__":
    main()
