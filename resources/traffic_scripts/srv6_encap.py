#!/usr/bin/env python3

# Copyright (c) 2020 Cisco and/or its affiliates.
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

from scapy.layers.inet6 import IPv6, ICMPv6ND_NS, IPv6ExtHdrSegmentRouting,\
    ipv6nh
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def check_srv6(
        pkt_recv, src_mac, dst_mac, src_ip, dst_ip, dir_srcsid, dir_dstsid1,
        dir_dstsid2, segleft):
    """Check received SRv6 packet.

    :param pkt_recv: Received packet to verify.
    :param src_mac: Source MAC address.
    :param dst_mac: Destination MAC address.
    :param src_ip: Source IP/IPv6 address of original IP/IPv6 packet.
    :param dst_ip: Destination IP/IPv6 address of original IP/IPv6 packet.
    :param dir_srcsid: Source SID for SR in desired direction.
    :param dir_dstsid1: Destination SID1 in desired direction.
    :param dir_dstsid2: Destination SID2 in desired direction.
    :param segleft: Expected segleft value of SRH.
    :type pkt_recv: scapy.Ether
    :type src_mac: str
    :type dst_mac: str
    :type src_ip: str
    :type dst_ip: str
    :type dir_srcsid: str
    :type dir_dstsid1: str
    :type dir_dstsid2: str
    :type segleft: int
    :raises RuntimeError: If received packet is invalid.
    """
    if pkt_recv[Ether].src != src_mac:
        raise RuntimeError(
            f"Received frame has invalid source MAC address: "
            f"{pkt_recv[Ether].src} should be: {src_mac}"
        )
    if pkt_recv[Ether].dst != dst_mac:
        raise RuntimeError(
            f"Received frame has invalid destination MAC address: "
            f"{pkt_recv[Ether].dst} should be: {dst_mac}"
        )
    if not pkt_recv.haslayer(IPv6):
        raise RuntimeError(
            f"Not an IPv6 packet received: {pkt_recv!r}"
        )
    ip6_pkt = pkt_recv[IPv6]
    if ip6_pkt.src != dir_srcsid:
        raise RuntimeError(
            f"Outer IPv6 packet has invalid source address: "
            f"{ip6_pkt.src} should be: {dir_srcsid}"
        )
    dir_dstsids = [dir_dstsid2, dir_dstsid1]
    if ip6_pkt.dst != dir_dstsids[segleft]:
        raise RuntimeError(
            f"Outer IPv6 packet has invalid destination address: "
            f"{ip6_pkt.dst} should be: {dir_dstsids[segleft]}"
        )
    if dir_dstsid2 == u"None":
        if ip6_pkt.haslayer(IPv6ExtHdrSegmentRouting):
            raise RuntimeError(
                f"Segment Routing Header in received packet: {pkt_recv!r}"
            )
        if ip6_pkt.nh != 41:  # ipv6nh[41] == IPv6
            raise RuntimeError(
                f"Outer IPv6 packet has invalid next header: "
                f"{ip6_pkt.nh} should be: 41 ({ipv6nh[41]})"
            )
        ip6_pkt = ip6_pkt[IPv6][1]
    else:
        if not pkt_recv.haslayer(IPv6ExtHdrSegmentRouting):
            raise RuntimeError(
                f"No Segment Routing Header in received packet: {pkt_recv!r}"
            )
        if ip6_pkt.nh != 43:  # ipv6nh[43] == Routing Header
            raise RuntimeError(
                f"Outer IPv6 packet has invalid next header: "
                f"{pkt_recv[IPv6][0].nh} should be: 43 ({ipv6nh[43]})"
            )
        ip6_pkt = ip6_pkt[IPv6ExtHdrSegmentRouting]
        if ip6_pkt.addresses != dir_dstsids:
            raise RuntimeError(
                f"Segment Routing Header has invalid addresses: "
                f"{ip6_pkt.addresses} should be: {dir_dstsids}"
            )
        if ip6_pkt.segleft != segleft:
            raise RuntimeError(
                f"Segment Routing Header has invalid segleft value: "
                f"{ip6_pkt.segleft} should be: {segleft}"
            )
        if ip6_pkt.nh != 41:  # ipv6nh[41] == IPv6
            raise RuntimeError(
                f"Segment Routing Header has invalid next header: "
                f"{ip6_pkt.nh} should be: 41 ({ipv6nh[41]})"
            )
        ip6_pkt = ip6_pkt[IPv6]
    if ip6_pkt.src != src_ip:
        raise RuntimeError(
            f"Inner IPv6 packet has invalid source address: "
            f"{ip6_pkt.src} should be: {src_ip}"
        )
    if ip6_pkt.dst != dst_ip:
        raise RuntimeError(
            f"Inner IPv6 packet has invalid destination address: "
            f"{ip6_pkt.dst} should be: {dst_ip}"
        )
    if ip6_pkt.nh != 59:  # ipv6nh[59] == No Next Header
        raise RuntimeError(
            f"Inner IPv6 packet has invalid next header: "
            f"{ip6_pkt.nh} should be: 59 ({ipv6nh[59]})"
        )


def check_ip(pkt_recv, src_mac, dst_mac, src_ip, dst_ip):
    """Check received IP/IPv6 packet.

    :param pkt_recv: Received packet to verify.
    :param src_mac: Source MAC address.
    :param dst_mac: Destination MAC address.
    :param src_ip: Source IP/IPv6 address.
    :param dst_ip: Destination IP/IPv6 address.
    :type pkt_recv: scapy.Ether
    :type src_mac: str
    :type dst_mac: str
    :type src_ip: str
    :type dst_ip: str
    :raises RuntimeError: If received packet is invalid.
    """
    if pkt_recv[Ether].src != src_mac:
        raise RuntimeError(
            f"Received frame has invalid source MAC address: "
            f"{pkt_recv[Ether].src} should be: {src_mac}"
        )

    if pkt_recv[Ether].dst != dst_mac:
        raise RuntimeError(
            f"Received frame has invalid destination MAC address: "
            f"{pkt_recv[Ether].dst} should be: {dst_mac}"
        )

    if not pkt_recv.haslayer(IPv6):
        raise RuntimeError(
            f"Not an {IPv6.name} packet received: {pkt_recv!r}"
        )

    if pkt_recv[IPv6].dst != dst_ip:
        raise RuntimeError(
            f"Received packet has invalid destination address: "
            f"{pkt_recv[IPv6.name].dst} should be: {dst_ip}"
        )

    if pkt_recv[IPv6].src != src_ip:
        raise RuntimeError(
            f"Received packet has invalid destination address: "
            f"{pkt_recv[IPv6.name].dst} should be: {src_ip}"
        )

    if pkt_recv[IPv6].nh != 59:  # ipv6nh[59] == No Next Header
        raise RuntimeError(
            f"Received IPv6 packet has invalid next header: "
            f"{IPv6.nh} should be: 59 ({ipv6nh[59]})"
        )


def main():
    """Send, receive and check IPv6 and IPv6ExtHdrSegmentRouting packets."""

    args = TrafficScriptArg(
        [
            u"tx_src_mac", u"tx_dst_mac", u"rx_src_mac", u"rx_dst_mac",
            u"src_ip", u"dst_ip", u"dir0_srcsid", u"dir0_dstsid1",
            u"dir0_dstsid2", u"dir1_srcsid", u"dir1_dstsid1", u"dir1_dstsid2",
            u"decap"
        ]
    )

    tx_txq = TxQueue(args.get_arg(u"tx_if"))
    tx_rxq = RxQueue(args.get_arg(u"tx_if"))
    rx_txq = TxQueue(args.get_arg(u"rx_if"))
    rx_rxq = RxQueue(args.get_arg(u"rx_if"))

    tx_src_mac = args.get_arg(u"tx_src_mac")
    tx_dst_mac = args.get_arg(u"tx_dst_mac")
    rx_src_mac = args.get_arg(u"rx_src_mac")
    rx_dst_mac = args.get_arg(u"rx_dst_mac")
    src_ip = args.get_arg(u"src_ip")
    dst_ip = args.get_arg(u"dst_ip")

    dir0_srcsid = args.get_arg(u"dir0_srcsid")
    dir0_dstsid1 = args.get_arg(u"dir0_dstsid1")
    dir0_dstsid2 = args.get_arg(u"dir0_dstsid2")
    dir1_srcsid = args.get_arg(u"dir1_srcsid")
    dir1_dstsid1 = args.get_arg(u"dir1_dstsid1")
    dir1_dstsid2 = args.get_arg(u"dir1_dstsid2")
    decap = args.get_arg(u"decap")

    ip_pkt = IPv6(src=src_ip, dst=dst_ip)

    sent_packets = list()
    tx_pkt_send = (Ether(src=tx_src_mac, dst=tx_dst_mac) / ip_pkt)
    tx_pkt_send /= Raw()
    size_limit = 78
    if len(tx_pkt_send) < size_limit:
        tx_pkt_send[Raw].load += (b"\0" * (size_limit - len(tx_pkt_send)))
    sent_packets.append(tx_pkt_send)
    tx_txq.send(tx_pkt_send)

    while True:
        rx_pkt_recv = rx_rxq.recv(2)

        if rx_pkt_recv is None:
            raise RuntimeError(f"{IPv6.name} packet Rx timeout")

        if rx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    check_srv6(
        rx_pkt_recv, rx_src_mac, rx_dst_mac, src_ip, dst_ip, dir0_srcsid,
        dir0_dstsid1, dir0_dstsid2, 1
    )

    ip_pkt = IPv6(src=dst_ip, dst=src_ip)
    ip_pkt /= Raw()
    if len(ip_pkt) < (size_limit - 14):
        ip_pkt[Raw].load += (b"\0" * (size_limit - 14 - len(ip_pkt)))

    rx_pkt_send = (
            Ether(src=rx_dst_mac, dst=rx_src_mac) /
            IPv6(src=dir1_srcsid, dst=dir1_dstsid1) /
            IPv6ExtHdrSegmentRouting(
                segleft=1,
                lastentry=1,
                addresses=[dir1_dstsid2, dir1_dstsid1]
            ) /
            ip_pkt
    ) if dir1_dstsid2 != u"None" else (
            Ether(src=rx_dst_mac, dst=rx_src_mac) /
            IPv6(src=dir1_srcsid, dst=dir1_dstsid1) /
            ip_pkt
    )
    rx_txq.send(rx_pkt_send)

    while True:
        tx_pkt_recv = tx_rxq.recv(2, ignore=sent_packets)

        if tx_pkt_recv is None:
            raise RuntimeError(f"{IPv6.name} packet Rx timeout")

        if tx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if decap == u"True":
        check_ip(tx_pkt_recv, tx_dst_mac, tx_src_mac, dst_ip, src_ip)
    else:
        check_srv6(
            tx_pkt_recv, tx_dst_mac, tx_src_mac, dst_ip, src_ip, dir1_srcsid,
            dir1_dstsid1, dir1_dstsid2, 0
        )

    sys.exit(0)


if __name__ == u"__main__":
    main()
