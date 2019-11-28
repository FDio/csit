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

"""Router advertisement check script."""

import sys
import ipaddress

from scapy.layers.inet6 import IPv6, ICMPv6ND_RA, ICMPv6ND_NS

from resources.libraries.python.PacketVerifier import RxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def mac_to_ipv6_linklocal(mac):
    """Transfer MAC address into specific link-local IPv6 address.

    :param mac: MAC address to be transferred.
    :type mac: str
    :return: IPv6 link-local address.
    :rtype: str
    """
    # Remove the most common delimiters: dots, dashes, etc.
    mac_value = int(mac.translate(None, u' .:-'), 16)

    # Split out the bytes that slot into the IPv6 address
    # XOR the most significant byte with 0x02, inverting the
    # Universal / Local bit
    high2 = mac_value >> 32 & 0xffff ^ 0x0200
    high1 = mac_value >> 24 & 0xff
    low1 = mac_value >> 16 & 0xff
    low2 = mac_value & 0xffff

    return u'fe80::{high2:04x}:{high1:02x}ff:fe{low1:02x}:{low2:04x}'


def main():
    """Check packets on specific port and look for the Router Advertisement
     part.
    """

    args = TrafficScriptArg([u'src_mac', u'interval'])

    rx_if = args.get_arg(u'rx_if')
    src_mac = args.get_arg(u'src_mac')
    interval = int(args.get_arg(u'interval'))
    rxq = RxQueue(rx_if)

    # receive ICMPv6ND_RA packet
    while True:
        ether = rxq.recv(max(5, interval))
        if ether is None:
            raise RuntimeError(u'ICMP echo Rx timeout')

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    # Check if received packet contains layer RA and check other values
    if not ether.haslayer(ICMPv6ND_RA):
        raise RuntimeError(u'Not an RA packet received {ether.__repr__()}')

    src_address = ipaddress.IPv6Address(unicode(ether[u'IPv6'].src))
    dst_address = ipaddress.IPv6Address(unicode(ether[u'IPv6'].dst))
    link_local = ipaddress.IPv6Address(unicode(mac_to_ipv6_linklocal(src_mac)))
    all_nodes_multicast = ipaddress.IPv6Address(u'ff02::1')

    if src_address != link_local:
        raise RuntimeError(f'Source address ({src_address}) '
                        f'not matching link local u'
                        f'address ({link_local})')
    if dst_address != all_nodes_multicast:
        raise RuntimeError(f'Packet destination address ({dst_address})'
                        f' is not the all'
                        f' nodes multicast address ({all_nodes_multicast}).')
    if ether[IPv6].hlim != 255:
        raise RuntimeError(f'Hop limit not correct: {ether[IPv6].hlim}!=255')

    ra_code = ether[ICMPv6ND_RA].code
    if ra_code != 0:
        raise RuntimeError(f'ICMP code: {ra_code} not correct. u')

    sys.exit(0)


if __name__ == "__main__":
    main()
