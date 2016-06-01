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

from scapy.layers.inet import ICMP, IP
from scapy.all import Ether
from scapy.layers.inet6 import ICMPv6ND_RA
from scapy.layers.inet6 import IPv6

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg

def mac_to_ipv6_linklocal(mac):
    """Transfer MAC address into specific link-local IPv6 address.

    :param mac: Mac address to be transferred
    :type mac: str
    :return: IPv6 link-local address.
    :rtype: str
    """
    # Remove the most common delimiters; dots, dashes, etc.
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
    """Check packets on specific port and look for Router Advertisement part.
    """

    args = TrafficScriptArg(['src_mac'])

    rx_if = args.get_arg('rx_if')
    src_mac = args.get_arg('src_mac')
    rxq = RxQueue(rx_if)

    ether = rxq.recv(20)

    # Check whether received packet contains layer RA and check other values
    if ether is None:
        raise RuntimeError('ICMP echo Rx timeout')

    if not ether.haslayer('ICMPv6ND_RA'):
        raise RuntimeError('Not an RA packet received {0}'
                           .format(ether.__repr__()))

    address = ipaddress.IPv6Address(unicode(ether['IPv6'].src))
    link_local = ipaddress.IPv6Address(unicode(mac_to_ipv6_linklocal(src_mac)))

    if address != link_local:
        raise RuntimeError('Source address not link local')

    if ether['IPv6'].hlim != 255:
        raise RuntimeError('Hop limit not correct')

    if ether['ICMPv6 Neighbor Discovery - Router Advertisement'].code != 0:
        raise RuntimeError('ICMP code not correct')

    sys.exit(0)

if __name__ == "__main__":
    main()
