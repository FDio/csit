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

"""Router advertisement check script."""

import sys
import ipaddress

from scapy.layers.inet6 import IPv6, ICMPv6ND_RA, ICMPv6ND_NS

from .PacketVerifier import RxQueue
from .TrafficScriptArg import TrafficScriptArg


def mac_to_ipv6_linklocal(mac):
    """Transfer MAC address into specific link-local IPv6 address.

    :param mac: MAC address to be transferred.
    :type mac: str
    :return: IPv6 link-local address.
    :rtype: str
    """
    # Remove the most common delimiters: dots, dashes, etc.
    mac_value = int(mac.translate(None, ' .:-'), 16)

    # Split out the bytes that slot into the IPv6 address
    # XOR the most significant byte with 0x02, inverting the
    # Universal / Local bit
    high2 = mac_value >> 32 & 0xffff ^ 0x0200
    high1 = mac_value >> 24 & 0xff
    low1 = mac_value >> 16 & 0xff
    low2 = mac_value & 0xffff

    return 'fe80::{:04x}:{:02x}ff:fe{:02x}:{:04x}'.format(
        high2, high1, low1, low2)


def main():
    """Check packets on specific port and look for the Router Advertisement
     part.
    """

    args = TrafficScriptArg(['src_mac', 'interval'])

    rx_if = args.get_arg('rx_if')
    src_mac = args.get_arg('src_mac')
    interval = int(args.get_arg('interval'))
    rxq = RxQueue(rx_if)

    # receive ICMPv6ND_RA packet
    while True:
        ether = rxq.recv(max(5, interval))
        if ether is None:
            raise RuntimeError('ICMP echo Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    # Check if received packet contains layer RA and check other values
    if not ether.haslayer(ICMPv6ND_RA):
        raise RuntimeError('Not an RA packet received {0}'.
                           format(ether.__repr__()))

    src_address = ipaddress.IPv6Address(unicode(ether['IPv6'].src))
    dst_address = ipaddress.IPv6Address(unicode(ether['IPv6'].dst))
    link_local = ipaddress.IPv6Address(unicode(mac_to_ipv6_linklocal(src_mac)))
    all_nodes_multicast = ipaddress.IPv6Address(u'ff02::1')

    if src_address != link_local:
        raise RuntimeError('Source address ({0}) not matching link local '
                           'address ({1})'.format(src_address, link_local))
    if dst_address != all_nodes_multicast:
        raise RuntimeError('Packet destination address ({0}) is not the all'
                           ' nodes multicast address ({1}).'.
                           format(dst_address, all_nodes_multicast))
    if ether[IPv6].hlim != 255:
        raise RuntimeError('Hop limit not correct: {0}!=255'.
                           format(ether[IPv6].hlim))

    ra_code = ether[ICMPv6ND_RA].code
    if ra_code != 0:
        raise RuntimeError('ICMP code: {0} not correct. '.format(ra_code))

    sys.exit(0)


if __name__ == "__main__":
    main()
