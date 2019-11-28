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

"""Traffic script that sends DHCPv6 proxy packets."""

from scapy.layers.inet import Ether
from scapy.layers.inet6 import IPv6, ICMPv6ND_NA, ICMPv6ND_NS
from scapy.layers.inet6 import ICMPv6EchoRequest, ICMPv6EchoReply


from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


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
        raise RuntimeError(u'ICMPv6ND Proxy response timeout.')

    if ether.src != dst_mac:
        raise RuntimeError(f'Source MAC address error: u'
                           f'{ether.src} != {dst_mac}')
    print (f"Source MAC address: OK.")

    if ether.dst != src_mac:
        raise RuntimeError(f'Destination MAC address error: u'
                           f'{ether.dst} != {src_mac}')
    print (f"Destination MAC address: OK.")

    if ether[IPv6].src != dst_ip:
        raise RuntimeError(f'Source IP address error: u'
                           f'{ether[IPv6].src} != {dst_ip}')
    print (f"Source IP address: OK.")

    if ether[IPv6].dst != src_ip:
        raise RuntimeError(f'Destination IP address error: u'
                           f'{ether[IPv6].dst} != {src_ip}')
    print (f"Destination IP address: OK.")

    try:
        target_addr = ether[IPv6][ICMPv6ND_NA].tgt
    except (KeyError, AttributeError):
        raise RuntimeError(f'Not an ICMPv6ND Neighbor Advertisement packet.')

    if target_addr != dst_ip:
        raise RuntimeError(f'ICMPv6 field u'Target address' error: u'
                           f'{target_addr} != {dst_ip}')
    print (f"Target address field: OK.")


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
        raise RuntimeError(f'ICMPv6 Echo Request timeout.')
    try:
        ether[IPv6][u"ICMPv6 Echo Request"]
    except KeyError:
        raise RuntimeError(f"Received packet is not an ICMPv6 Echo Request.")
    print (u"ICMP Echo: OK.")

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
        raise RuntimeError(f'DHCPv6 SOLICIT timeout')
    try:
        ether[IPv6][u"ICMPv6 Echo Reply"]
    except KeyError:
        raise RuntimeError(f"Received packet is not an ICMPv6 Echo Reply.")

    print (f"ICMP Reply: OK.")


def main():
    """Send DHCPv6 proxy messages."""

    args = TrafficScriptArg([u'src_ip', u'dst_ip', u'src_mac', u'dst_mac',
                             u'proxy_to_src_mac', u'proxy_to_dst_mac'])

    src_if = args.get_arg(u'tx_if')
    dst_if = args.get_arg(u'rx_if')
    src_ip = args.get_arg(u'src_ip')
    dst_ip = args.get_arg(u'dst_ip')
    src_mac = args.get_arg(u'src_mac')
    dst_mac = args.get_arg(u'dst_mac')
    proxy_to_src_mac = args.get_arg(u'proxy_to_src_mac')
    proxy_to_dst_mac = args.get_arg(u'proxy_to_dst_mac')

    # Neighbor solicitation
    imcpv6nd_solicit(src_if, src_mac, proxy_to_src_mac, src_ip, dst_ip)

    # Verify route (ICMP echo/reply)
    ipv6_ping(src_if, dst_if, src_mac, dst_mac, proxy_to_src_mac,
              proxy_to_dst_mac, src_ip, dst_ip)


if __name__ == "__main__":
    main()
