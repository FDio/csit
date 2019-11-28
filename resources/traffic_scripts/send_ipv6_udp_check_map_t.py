#!/usr/bin/env python
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License');
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

"""Traffic script that sends an empty UDP datagram and checks if IPv6 addresses
are correctly translate to IPv4 addresses."""

import sys

from scapy.layers.l2 import Ether
from scapy.layers.inet6 import IPv6, UDP
from ipaddress import ip_address

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def _check_udp_checksum(pkt):
    """Check UDP checksum in IP packet. Return True if checksum is correct
    else False."""
    new = pkt.__class__(str(pkt))
    del new[u'UDP'].chksum
    new = new.__class__(str(new))
    return new[u'UDP'].chksum == pkt[u'UDP'].chksum


def _is_udp_in_ipv4(pkt):
    """If IPv4 protocol type in the given pkt is UDP, return True,
    else return False. False is returned also if exception occurs."""
    ipv4_type = int(u'0x0800', 16)  # IPv4
    try:
        if pkt.type == ipv4_type:
            if pkt.payload.proto == 17:  # UDP
                return True
    except AttributeError:
        return False
    return False


def main():  # pylint: disable=too-many-statements, too-many-locals
    """Main function of the script file."""
    args = TrafficScriptArg([u'tx_dst_mac', u'tx_src_mac',
                             u'tx_src_ipv6', u'tx_dst_ipv6',
                             u'tx_src_udp_port', u'rx_dst_mac', u'rx_src_mac',
                             u'rx_src_ipv4', u'rx_dst_ipv4'])
    rx_if = args.get_arg(u'rx_if')
    tx_if = args.get_arg(u'tx_if')
    tx_dst_mac = args.get_arg(u'tx_dst_mac')
    tx_src_mac = args.get_arg(u'tx_src_mac')
    tx_src_ipv6 = args.get_arg(u'tx_src_ipv6')
    tx_dst_ipv6 = args.get_arg(u'tx_dst_ipv6')
    tx_src_udp_port = int(args.get_arg(u'tx_src_udp_port'))
    tx_dst_udp_port = 20000
    rx_dst_mac = args.get_arg(u'rx_dst_mac')
    rx_src_mac = args.get_arg(u'rx_src_mac')
    rx_src_ipv4 = args.get_arg(u'rx_src_ipv4')
    rx_dst_ipv4 = args.get_arg(u'rx_dst_ipv4')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    # Create empty UDP datagram in IPv6

    udp = (Ether(dst=tx_dst_mac, src=tx_src_mac) /
           IPv6(src=tx_src_ipv6, dst=tx_dst_ipv6) /
           UDP(sport=tx_src_udp_port, dport=tx_dst_udp_port) /
           u'udp_payload')

    txq.send(udp)
    sent_packets.append(udp)

    for _ in range(5):
        pkt = rxq.recv(2)
        if _is_udp_in_ipv4(pkt):
            ether = pkt
            break
    else:
        raise RuntimeError(f'UDP in IPv4 Rx error.')

    # check ethernet
    if ether.dst != rx_dst_mac:
        raise RuntimeError(f'Destination MAC error '
                           f'{ether.dst} != {rx_dst_mac}.')
    print (u"Destination MAC: OK.")

    if ether.src != rx_src_mac:
        raise RuntimeError(f'Source MAC error {ether.src} != {rx_src_mac}.'.
                           format(ether.src, rx_src_mac))
    print (u"Source MAC: OK.")

    ipv4 = ether.payload

    # check ipv4
    if ip_address(unicode(ipv4.dst)) != ip_address(unicode(rx_dst_ipv4)):
        raise RuntimeError(f'Destination IPv4 error '
                           f'{ipv4.dst} != {rx_dst_ipv4}.')
    print (u"Destination IPv4: OK.")

    if ip_address(unicode(ipv4.src)) != ip_address(unicode(rx_src_ipv4)):
        raise RuntimeError(f'Source IPv4 error {ipv4.src} != {rx_src_ipv4}.')
    print (u"Source IPv4: OK.")

    udp = ipv4.payload

    # check udp
    if udp.dport != tx_dst_udp_port:
        raise RuntimeError(f'UDP dport error {udp.dport} != {tx_dst_udp_port}.')
    print (u"UDP dport: OK.")

    if udp.sport != tx_src_udp_port:
        raise RuntimeError(f'UDP sport error {udp.sport} != {tx_src_udp_port}.')
    print (u"UDP sport: OK.")

    if not _check_udp_checksum(ipv4):
        raise RuntimeError(f'UDP checksum error.')
    print (u"UDP checksum OK.")

    sys.exit(0)

if __name__ == "__main__":
    main()
