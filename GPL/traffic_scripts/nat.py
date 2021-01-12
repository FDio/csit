#!/usr/bin/env python3

# Copyright (c) 2020 Cisco and/or its affiliates.
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
#
# Licensed under the Apache License 2.0 or
# GNU General Public License v2.0 or later;  you may not use this file
# except in compliance with one of these Licenses. You
# may obtain a copy of the Licenses at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
#
# Note: If this file is linked with Scapy, which is GPLv2+, your use of it
# must be under GPLv2+.  If at any point in the future it is no longer linked
# with Scapy (or other GPLv2+ licensed software), you are free to choose
# Apache 2.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Traffic script for NAT verification."""

import sys

import ipaddress

from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def valid_ipv4(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def valid_ipv6(ip):
    try:
        ipaddress.IPv6Address(ip)
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send, receive and check IP/IPv6 packets with UDP/TCP layer passing
    through NAT.
    """
    args = TrafficScriptArg(
        [
            u"tx_src_mac", u"rx_dst_mac", u"src_ip_in", u"src_ip_out",
            u"dst_ip", u"tx_dst_mac", u"rx_src_mac", u"protocol",
            u"src_port_in", u"src_port_out", u"dst_port"
        ]
    )

    tx_src_mac = args.get_arg(u"tx_src_mac")
    tx_dst_mac = args.get_arg(u"tx_dst_mac")
    rx_dst_mac = args.get_arg(u"rx_dst_mac")
    rx_src_mac = args.get_arg(u"rx_src_mac")
    src_ip_in = args.get_arg(u"src_ip_in")
    src_ip_out = args.get_arg(u"src_ip_out")
    dst_ip = args.get_arg(u"dst_ip")
    protocol = args.get_arg(u"protocol")
    sport_in = int(args.get_arg(u"src_port_in"))
    try:
        sport_out = int(args.get_arg(u"src_port_out"))
    except ValueError:
        sport_out = None
    dst_port = int(args.get_arg(u"dst_port"))

    tx_txq = TxQueue(args.get_arg(u"tx_if"))
    tx_rxq = RxQueue(args.get_arg(u"tx_if"))
    rx_txq = TxQueue(args.get_arg(u"rx_if"))
    rx_rxq = RxQueue(args.get_arg(u"rx_if"))

    sent_packets = list()
    pkt_raw = Ether(src=tx_src_mac, dst=tx_dst_mac)

    if valid_ipv4(src_ip_in) and valid_ipv4(dst_ip):
        ip_layer = IP
    elif valid_ipv6(src_ip_in) and valid_ipv6(dst_ip):
        ip_layer = IPv6
    else:
        raise ValueError(u"IP not in correct format")
    pkt_raw /= ip_layer(src=src_ip_in, dst=dst_ip)

    if protocol == u"UDP":
        pkt_raw /= UDP(sport=sport_in, dport=dst_port)
        proto_layer = UDP
    elif protocol == u"TCP":
        # flags=0x2 => SYN flag set
        pkt_raw /= TCP(sport=sport_in, dport=dst_port, flags=0x2)
        proto_layer = TCP
    else:
        raise ValueError(u"Incorrect protocol")

    pkt_raw /= Raw()
    sent_packets.append(pkt_raw)
    tx_txq.send(pkt_raw)

    while True:
        ether = rx_rxq.recv(2)

        if ether is None:
            raise RuntimeError(u"IP packet Rx timeout")

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if rx_dst_mac != ether[Ether].dst or rx_src_mac != ether[Ether].src:
        raise RuntimeError(f"Matching packet unsuccessful: {ether!r}")

    ip_pkt = ether.payload
    if not isinstance(ip_pkt, ip_layer):
        raise RuntimeError(f"Not an {ip_layer!s} packet received: {ip_pkt!r}")
    if ip_pkt.src != src_ip_out:
        raise RuntimeError(
            f"Matching Src IP address unsuccessful: "
            f"{src_ip_out} != {ip_pkt.src}"
        )
    if ip_pkt.dst != dst_ip:
        raise RuntimeError(
            f"Matching Dst IP address unsuccessful: {dst_ip} != {ip_pkt.dst}"
        )

    proto_pkt = ip_pkt.payload
    if not isinstance(proto_pkt, proto_layer):
        raise RuntimeError(
            f"Not a {proto_layer!s} packet received: {proto_pkt!r}"
        )
    if sport_out is not None:
        if proto_pkt.sport != sport_out:
            raise RuntimeError(
                f"Matching Src {proto_layer!s} port unsuccessful: "
                f"{sport_out} != {proto_pkt.sport}"
            )
    else:
        sport_out = proto_pkt.sport
    if proto_pkt.dport != dst_port:
        raise RuntimeError(
            f"Matching Dst {proto_layer!s} port unsuccessful: "
            f"{dst_port} != {proto_pkt.dport}"
        )
    if proto_layer == TCP:
        if proto_pkt.flags != 0x2:
            raise RuntimeError(
                f"Not a TCP SYN packet received: {proto_pkt!r}"
            )

    pkt_raw = Ether(src=rx_dst_mac, dst=rx_src_mac)
    pkt_raw /= ip_layer(src=dst_ip, dst=src_ip_out)
    pkt_raw /= proto_layer(sport=dst_port, dport=sport_out)
    if proto_layer == TCP:
        # flags=0x12 => SYN, ACK flags set
        pkt_raw[TCP].flags = 0x12
    pkt_raw /= Raw()
    rx_txq.send(pkt_raw)

    while True:
        ether = tx_rxq.recv(2, ignore=sent_packets)

        if ether is None:
            raise RuntimeError(u"IP packet Rx timeout")

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if ether[Ether].dst != tx_src_mac or ether[Ether].src != tx_dst_mac:
        raise RuntimeError(f"Matching packet unsuccessful: {ether!r}")

    ip_pkt = ether.payload
    if not isinstance(ip_pkt, ip_layer):
        raise RuntimeError(f"Not an {ip_layer!s} packet received: {ip_pkt!r}")
    if ip_pkt.src != dst_ip:
        raise RuntimeError(
            f"Matching Src IP address unsuccessful: {dst_ip} != {ip_pkt.src}"
        )
    if ip_pkt.dst != src_ip_in:
        raise RuntimeError(
            f"Matching Dst IP address unsuccessful: {src_ip_in} != {ip_pkt.dst}"
        )

    proto_pkt = ip_pkt.payload
    if not isinstance(proto_pkt, proto_layer):
        raise RuntimeError(
            f"Not a {proto_layer!s} packet received: {proto_pkt!r}"
        )
    if proto_pkt.sport != dst_port:
        raise RuntimeError(
            f"Matching Src {proto_layer!s} port unsuccessful: "
            f"{dst_port} != {proto_pkt.sport}"
        )
    if proto_pkt.dport != sport_in:
        raise RuntimeError(
            f"Matching Dst {proto_layer!s} port unsuccessful: "
            f"{sport_in} != {proto_pkt.dport}"
        )
    if proto_layer == TCP:
        if proto_pkt.flags != 0x12:
            raise RuntimeError(
                f"Not a TCP SYN-ACK packet received: {proto_pkt!r}"
            )

    sys.exit(0)


if __name__ == u"__main__":
    main()
