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

"""Traffic script that sends DHCPv6 proxy packets."""

from scapy.layers.inet import Ether
from scapy.layers.inet6 import IPv6, ICMPv6ND_NA, ICMPv6ND_NS
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply


from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def imcpv6nd_solicit(tx_if, src_mac, dst_mac, src_ip, dst_ip):
    """Send ICMPv6 Neighbor Solicitation packet and expect a response
     from the proxy.

    :param tx_if: Interface on TG.
    :param src_mac: MAC address of TG interface.
    :param dst_mac: MAC address of proxy interface.
    :param src_ip: IP address of TG interface.
    :param dst_ip: IP address of proxied interface.
    :type tx_if: str
    :type src_mac: str
    :type dst_mac: str
    :type src_ip: str
    :type dst_ip: str
    :raises RuntimeError: If the received packet is not correct.
    """

    rxq = RxQueue(tx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    icmpv6nd_solicit_pkt = (Ether(src=src_mac, dst=dst_mac) /
                            IPv6(src=src_ip) /
                            ICMPv6ND_NS(tgt=dst_ip))

    sent_packets.append(icmpv6nd_solicit_pkt)
    txq.send(icmpv6nd_solicit_pkt)

    ether = None
    for _ in range(5):
        ether = rxq.recv(3, ignore=sent_packets)
        if not ether:
            continue
        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue in case of ICMPv6ND_NS packet
            continue
        else:
            # otherwise process the current packet
            break

    if ether is None:
        raise RuntimeError('ICMPv6ND Proxy response timeout.')

    if ether.src != dst_mac:
        raise RuntimeError("Source MAC address error: {} != {}".
                           format(ether.src, dst_mac))
    print "Source MAC address: OK."

    if ether.dst != src_mac:
        raise RuntimeError("Destination MAC address error: {} != {}".
                           format(ether.dst, src_mac))
    print "Destination MAC address: OK."

    if ether[IPv6].src != dst_ip:
        raise RuntimeError("Source IP address error: {} != {}".
                           format(ether[IPv6].src, dst_ip))
    print "Source IP address: OK."

    if ether[IPv6].dst != src_ip:
        raise RuntimeError("Destination IP address error: {} != {}".
                           format(ether[IPv6].dst, src_ip))
    print "Destination IP address: OK."

    try:
        target_addr = ether[IPv6][ICMPv6ND_NA].tgt
    except (KeyError, AttributeError):
        raise RuntimeError("Not an ICMPv6ND Neighbor Advertisement packet.")

    if target_addr != dst_ip:
        raise RuntimeError("ICMPv6 field 'Target address' error: {} != {}".
                           format(target_addr, dst_ip))
    print "Target address field: OK."


def ipv6_ping(src_if, dst_if, src_mac, dst_mac,
              proxy_to_src_mac, proxy_to_dst_mac, src_ip, dst_ip):
    """Sends ICMPv6 Echo Request, receive it and send a reply.

    :param src_if: First TG interface on link to DUT.
    :param dst_if: Second TG interface on link to DUT.
    :param src_mac: MAC address of first interface.
    :param dst_mac: MAC address of second interface.
    :param proxy_to_src_mac: MAC address of first proxy interface on DUT.
    :param proxy_to_dst_mac: MAC address of second proxy interface on DUT.
    :param src_ip: IP address of first interface.
    :param dst_ip: IP address of second interface.
    :type src_if: str
    :type dst_if: str
    :type src_mac: str
    :type dst_mac: str
    :type proxy_to_src_mac: str
    :type proxy_to_dst_mac: str
    :type src_ip: str
    :type dst_ip: str
    :raises RuntimeError: If a received packet is not correct.
    """
    rxq = RxQueue(dst_if)
    txq = TxQueue(src_if)

    icmpv6_ping_pkt = (Ether(src=src_mac, dst=proxy_to_src_mac) /
                       IPv6(src=src_ip, dst=dst_ip) /
                       ICMPv6EchoRequest())

    txq.send(icmpv6_ping_pkt)

    ether = None
    while True:
        ether = rxq.recv(3)
        if not ether:
            continue
        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue in case of ICMPv6ND_NS packet
            continue
        else:
            # otherwise process the current packet
            break

    if ether is None:
        raise RuntimeError('ICMPv6 Echo Request timeout.')
    try:
        ether[IPv6]["ICMPv6 Echo Request"]
    except KeyError:
        raise RuntimeError("Received packet is not an ICMPv6 Echo Request.")
    print "ICMP Echo: OK."

    rxq = RxQueue(src_if)
    txq = TxQueue(dst_if)

    icmpv6_ping_pkt = (Ether(src=dst_mac, dst=proxy_to_dst_mac) /
                       IPv6(src=dst_ip, dst=src_ip) /
                       ICMPv6EchoReply())

    txq.send(icmpv6_ping_pkt)

    ether = None
    while True:
        ether = rxq.recv(3)
        if not ether:
            continue
        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue in case of ICMPv6ND_NS packet
            continue
        else:
            # otherwise process the current packet
            break

    if ether is None:
        raise RuntimeError('DHCPv6 SOLICIT timeout')
    try:
        ether[IPv6]["ICMPv6 Echo Reply"]
    except KeyError:
        raise RuntimeError("Received packet is not an ICMPv6 Echo Reply.")

    print "ICMP Reply: OK."


def main():
    """Send DHCPv6 proxy messages."""

    args = TrafficScriptArg(['src_ip', 'dst_ip', 'src_mac', 'dst_mac',
                             'proxy_to_src_mac', 'proxy_to_dst_mac'])

    src_if = args.get_arg('tx_if')
    dst_if = args.get_arg('rx_if')
    src_ip = args.get_arg("src_ip")
    dst_ip = args.get_arg("dst_ip")
    src_mac = args.get_arg('src_mac')
    dst_mac = args.get_arg('dst_mac')
    proxy_to_src_mac = args.get_arg('proxy_to_src_mac')
    proxy_to_dst_mac = args.get_arg('proxy_to_dst_mac')

    # Neighbor solicitation
    imcpv6nd_solicit(src_if, src_mac, proxy_to_src_mac, src_ip, dst_ip)

    # Verify route (ICMP echo/reply)
    ipv6_ping(src_if, dst_if, src_mac, dst_mac, proxy_to_src_mac,
              proxy_to_dst_mac, src_ip, dst_ip)


if __name__ == "__main__":
    main()
