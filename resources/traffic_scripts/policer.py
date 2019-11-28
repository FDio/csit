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

"""Traffic script for IPsec verification."""

import sys
import logging

# pylint: disable=no-name-in-module
# pylint: disable=import-error
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from ipaddress import ip_address

from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from resources.libraries.python.PacketVerifier import RxQueue, TxQueue


def check_ipv4(pkt_recv, dscp):
    """Check received IPv4 IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param dscp: DSCP value to check.
    :type pkt_recv: scapy.Ether
    :type dscp: int
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IP):
        raise RuntimeError(f'Not an IPv4 packet received: u'
                           f'{pkt_recv.__repr__()}')

    rx_dscp = pkt_recv[IP].tos >> 2
    if rx_dscp != dscp:
        raise RuntimeError(f'Invalid DSCP {rx_dscp} should be {dscp}')

    if not pkt_recv.haslayer(TCP):
        raise RuntimeError(f'Not a TCP packet received: {pkt_recv.__repr__()}')


def check_ipv6(pkt_recv, dscp):
    """Check received IPv6 IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param dscp: DSCP value to check.
    :type pkt_recv: scapy.Ether
    :type dscp: int
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(IPv6):
        raise RuntimeError(f'Not an IPv6 packet received: '
                           f'{pkt_recv.__repr__()}')

    rx_dscp = pkt_recv[IPv6].tc >> 2
    if rx_dscp != dscp:
        raise RuntimeError(f'Invalid DSCP {rx_dscp} should be {dscp}')

    if not pkt_recv.haslayer(TCP):
        raise RuntimeError(f'Not a TCP packet received: {pkt_recv.__repr__()}')


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def main():
    """Send and receive TCP packet."""
    args = TrafficScriptArg(\
        [u'src_mac', u'dst_mac', u'src_ip', u'dst_ip', u'dscp'])

    rxq = RxQueue(args.get_arg(u'rx_if'))
    txq = TxQueue(args.get_arg(u'tx_if'))

    src_mac = args.get_arg(u'src_mac')
    dst_mac = args.get_arg(u'dst_mac')
    src_ip = args.get_arg(u'src_ip')
    dst_ip = args.get_arg(u'dst_ip')
    dscp = int(args.get_arg(u'dscp'))

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
            raise RuntimeError(u'ICMPv6 echo reply Rx timeout')

        if pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if pkt_recv is None:
        raise RuntimeError(u'Rx timeout')

    if is_ipv4:
        check_ipv4(pkt_recv, dscp)
    else:
        check_ipv6(pkt_recv, dscp)

    sys.exit(0)


if __name__ == "__main__":
    main()
