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

"""Router solicitation check script."""

import sys
import ipaddress

from scapy.layers.l2 import Ether
from scapy.layers.inet6 import IPv6, ICMPv6ND_RS

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


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
    """Send Router Solicitation packet, check if the received response\
     is a Router Advertisement packet and verify."""

    args = TrafficScriptArg(
        ['src_mac', 'dst_mac', 'src_ip', 'dst_ip']
    )

    dst_mac = args.get_arg('dst_mac')
    src_mac = args.get_arg('src_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tx_if = args.get_arg('tx_if')

    txq = TxQueue(tx_if)
    rxq = RxQueue(tx_if)

    pkt_raw = (Ether(src=src_mac, dst=dst_mac) /
               IPv6(src=src_ip, dst=dst_ip) /
               ICMPv6ND_RS())

    sent_packets = [pkt_raw]
    txq.send(pkt_raw)

    ether = rxq.recv(8, ignore=sent_packets)

    # Check whether received packet contains layer RA and check other values
    if ether is None:
        raise RuntimeError('ICMP echo Rx timeout')

    if not ether.haslayer('ICMPv6ND_RA'):
        raise RuntimeError('Not an RA packet received {0}'
                           .format(ether.__repr__()))

    address = ipaddress.IPv6Address(unicode(ether['IPv6'].src))
    link_local = ipaddress.IPv6Address(unicode(mac_to_ipv6_linklocal(dst_mac)))

    if address != link_local:
        raise RuntimeError(
            'Source address ({0}) not matching link local address({1})'.format(
                address, link_local))

    if ether['IPv6'].hlim != 255:
        raise RuntimeError('Hop limit not correct: {0}!=255'.format(
            ether['IPv6'].hlim))

    ra_code = ether['ICMPv6 Neighbor Discovery - Router Advertisement'].code
    if ra_code != 0:
        raise RuntimeError('ICMP code: {0} not correct. '.format(ra_code))

    sys.exit(0)

if __name__ == "__main__":
    main()
