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

"""Traffic script for GENEVE tunnel verification."""

import sys

from ipaddress import ip_address
from scapy.contrib.geneve import GENEVE
from scapy.layers.inet import IP, UDP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def check_geneve(
        pkt_recv, ip_layer, outer_src_mac, outer_dst_mac, inner_src_mac,
        inner_dst_mac, outer_src_ip, outer_dst_ip, inner_src_ip, inner_dst_ip,
        udp_dport, gen_vni):
    """Check received GENEVE packet.

    :param pkt_recv: Received packet to verify.
    :param ip_layer: Scapy IP or IPv6 layer.
    :param outer_src_mac: Outer source MAC address.
    :param outer_dst_mac: Outer destination MAC address.
    :param inner_src_mac: Inner source MAC address.
    :param inner_dst_mac: Inner destination MAC address.
    :param outer_src_ip: Outer source IP/IPv6 address.
    :param outer_dst_ip: Outer destination IP/IPv6 address.
    :param inner_src_ip: Inner source IP/IPv6 address.
    :param inner_dst_ip: Inner destination IP/IPv6 address.
    :param udp_dport: UDP destination port.
    :param gen_vni: GENEVE VNI.
    :type pkt_recv: scapy.Ether
    :type ip_layer: scapy.layers.inet.IP or scapy.layers.inet6.IPv6
    :type outer_src_mac: str
    :type outer_dst_mac: str
    :type inner_src_mac: str
    :type inner_dst_mac: str
    :type outer_src_ip: str
    :type outer_dst_ip: str
    :type inner_src_ip: str
    :type inner_dst_ip: str
    :type udp_dport: int
    :type gen_vni: int
    :raises RuntimeError: If received packet is invalid.
    """
    try:
        if not isinstance(pkt_recv[0], Ether):
            raise RuntimeError(
                f"Received packet hasn't outer Ether layer: {pkt_recv!r}"
            )
        elif not isinstance(pkt_recv[1], ip_layer):
            raise RuntimeError(
                f"Received packet hasn't outer {ip_layer.__name__} layer: "
                f"{pkt_recv!r}"
            )
        elif not isinstance(pkt_recv[2], UDP):
            raise RuntimeError(
                f"Received packet hasn't UDP layer: {pkt_recv!r}"
            )
        elif not isinstance(pkt_recv[3], GENEVE):
            raise RuntimeError(
                f"Received packet hasn't GENEVE layer: {pkt_recv!r}"
            )
        elif not isinstance(pkt_recv[4], Ether):
            raise RuntimeError(
                f"Received packet hasn't inner Ether layer: {pkt_recv!r}"
            )
        elif not isinstance(pkt_recv[5], ip_layer):
            raise RuntimeError(
                f"Received packet hasn't inner {ip_layer.__name__} layer: "
                f"{pkt_recv!r}"
            )
        elif not isinstance(pkt_recv[6], Raw):
            raise RuntimeError(
                f"Received packet hasn't inner Raw layer: {pkt_recv!r}"
            )
    except IndexError:
        raise RuntimeError(
            f"Received packet doesn't contain all layers: {pkt_recv!r}"
        )

    if pkt_recv[Ether].src != outer_src_mac:
        raise RuntimeError(
            f"Received frame has invalid outer source MAC address: "
            f"{pkt_recv[Ether].src} should be: {outer_src_mac}"
        )

    if pkt_recv[Ether].dst != outer_dst_mac:
        raise RuntimeError(
            f"Received frame has invalid outer destination MAC address: "
            f"{pkt_recv[Ether].dst} should be: {outer_dst_mac}"
        )

    if pkt_recv[ip_layer].src != outer_src_ip:
        raise RuntimeError(
            f"Received packet has invalid outer source address: "
            f"{pkt_recv[ip_layer].src} should be: {outer_src_ip}"
        )

    if pkt_recv[ip_layer].dst != outer_dst_ip:
        raise RuntimeError(
            f"Received packet has invalid outer destination address: "
            f"{pkt_recv[ip_layer].dst} should be: {outer_dst_ip}"
        )

    if pkt_recv[UDP].dport != udp_dport:
        raise RuntimeError(
            f"Received packet has invalid UDP dport: "
            f"{pkt_recv[UDP].dport} should be: {udp_dport}"
        )

    if pkt_recv[GENEVE].vni != gen_vni:
        raise RuntimeError(
            f"Received packet has invalid GENEVE vni: "
            f"{pkt_recv[GENEVE].vni} should be: {gen_vni}"
        )

    if pkt_recv[GENEVE].proto != 0x6558:
        raise RuntimeError(
            f"Received packet has invalid GENEVE protocol number: "
            f"{pkt_recv[GENEVE].proto} should be: 0x6558"
        )

    if pkt_recv[Ether:2].src != inner_src_mac:
        raise RuntimeError(
            f"Received frame has invalid inner source MAC address: "
            f"{pkt_recv[Ether:2].src} should be: {inner_src_mac}"
        )

    if pkt_recv[Ether:2].dst != inner_dst_mac:
        raise RuntimeError(
            f"Received frame has invalid inner destination MAC address: "
            f"{pkt_recv[Ether:2].dst} should be: {inner_dst_mac}"
        )

    if pkt_recv[ip_layer:2].src != inner_src_ip:
        raise RuntimeError(
            f"Received packet has invalid inner source address: "
            f"{pkt_recv[ip_layer:2].src} should be: {inner_src_ip}"
        )

    if pkt_recv[ip_layer:2].dst != inner_dst_ip:
        raise RuntimeError(
            f"Received packet has invalid inner destination address: "
            f"{pkt_recv[ip_layer:2].dst} should be: {inner_dst_ip}"
        )


def check_ip(pkt_recv, ip_layer, src_mac, dst_mac, src_ip, dst_ip):
    """Check received IP/IPv6 packet.

    :param pkt_recv: Received packet to verify.
    :param ip_layer: Scapy IP layer.
    :param src_mac: Source MAC address.
    :param dst_mac: Destination MAC address.
    :param src_ip: Source IP/IPv6 address.
    :param dst_ip: Destination IP/IPv6 address.
    :type pkt_recv: scapy.Ether
    :type ip_layer: scapy.layers.inet.IP or scapy.layers.inet6.IPv6
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

    if not pkt_recv.haslayer(ip_layer):
        raise RuntimeError(
            f"Not an {ip_layer.__name__} packet received: {pkt_recv!r}"
        )

    if pkt_recv[ip_layer].dst != dst_ip:
        raise RuntimeError(
            f"Received packet has invalid destination {ip_layer.__name__} "
            f"address: {pkt_recv[ip_layer.__name__].dst} should be: {dst_ip}"
        )

    if pkt_recv[ip_layer].src != src_ip:
        raise RuntimeError(
            f"Received packet has invalid destination {ip_layer.__name__} "
            f"address: {pkt_recv[ip_layer.__name__].dst} should be: {src_ip}"
        )

    if ip_layer == IP and pkt_recv[ip_layer].proto != 61:
        raise RuntimeError(
            f"Received packet has invalid IP protocol: "
            f"{pkt_recv[ip_layer].proto} should be: 61"
        )


def main():
    """Send and receive GENEVE packets."""

    args = TrafficScriptArg(
        [
            u"tx_src_mac", u"tx_dst_mac", u"rx_src_mac", u"rx_dst_mac",
            u"tun_local_ip", u"tun_remote_ip", u"tun_vni", u"tun_src_ip",
            u"tun_dst_ip"
        ]
    )

    tx_txq = TxQueue(args.get_arg(u"tx_if"))
    tx_rxq = RxQueue(args.get_arg(u"tx_if"))
    rx_txq = TxQueue(args.get_arg(u"rx_if"))
    rx_rxq = RxQueue(args.get_arg(u"rx_if"))

    rx_src_mac = args.get_arg(u"rx_src_mac")
    rx_dst_mac = args.get_arg(u"rx_dst_mac")
    tx_src_mac = args.get_arg(u"tx_src_mac")
    tx_dst_mac = args.get_arg(u"tx_dst_mac")

    tun_local_ip = args.get_arg(u"tun_local_ip")
    tun_remote_ip = args.get_arg(u"tun_remote_ip")
    tun_vni = args.get_arg(u"tun_vni")
    tun_src_ip = args.get_arg(u"tun_src_ip")
    tun_dst_ip = args.get_arg(u"tun_dst_ip")

    geneve_tunnel_mac = u"d0:0b:ee:d0:00:00"
    geneve_udp_dport = 6081

    tx_sent_packets = list()
    src_ip = ip_address(tun_src_ip)
    dst_ip = ip_address(tun_dst_ip)
    ip_layer = IP if src_ip.version == 4 else IPv6
    tx_ip_pkt = ip_layer(src=src_ip, dst=dst_ip, proto=61) \
        if ip_layer == IP else ip_layer(src=src_ip, dst=dst_ip)
    tx_pkt_send = (Ether(src=tx_src_mac, dst=tx_dst_mac) / tx_ip_pkt)
    tx_pkt_send /= Raw()
    size_limit = 78 if ip_layer == IPv6 else 60
    if len(tx_pkt_send) < size_limit:
        tx_pkt_send[Raw].load += b"\0" * (size_limit - len(tx_pkt_send))

    tx_sent_packets.append(tx_pkt_send)
    tx_txq.send(tx_pkt_send)

    while True:
        rx_pkt_recv = rx_rxq.recv(2)

        if rx_pkt_recv is None:
            raise RuntimeError(f"GENEVE packet Rx timeout")

        if rx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    check_geneve(
        rx_pkt_recv, ip_layer, rx_src_mac, rx_dst_mac, geneve_tunnel_mac,
        rx_dst_mac, tun_local_ip, tun_remote_ip, str(src_ip), str(dst_ip),
        geneve_udp_dport, int(tun_vni)
    )

    rx_inner_ip_pkt = IP(
        src=rx_pkt_recv[Ether:2][IP].dst,
        dst=rx_pkt_recv[Ether:2][IP].src,
        proto=61
    ) if isinstance(rx_pkt_recv[Ether:2][1], IP) else IPv6(
        src=rx_pkt_recv[Ether:2][IPv6].dst,
        dst=rx_pkt_recv[Ether:2][IPv6].src
    )
    rx_inner_ip_pkt /= Raw()
    rx_inner_pkt = (
        Ether(src=rx_pkt_recv[4].dst, dst=rx_pkt_recv[4].src) /
        rx_inner_ip_pkt
    )
    size_limit = 78 if isinstance(rx_pkt_recv[Ether:2][1], IPv6) else 60
    if len(rx_inner_pkt) < size_limit:
        rx_inner_pkt[Raw].load += b"\0" * (size_limit - len(rx_inner_pkt))

    rx_outer_ip_pkt = IP(
        src=rx_pkt_recv[Ether:1][IP].dst,
        dst=rx_pkt_recv[Ether:1][IP].src
    ) if isinstance(rx_pkt_recv[Ether:1][1], IP) else IPv6(
        src=rx_pkt_recv[Ether:1][IPv6].dst,
        dst=rx_pkt_recv[Ether:1][IPv6].src
    )
    rx_pkt_send = (
        Ether(src=rx_pkt_recv[Ether:1].dst, dst=rx_pkt_recv[Ether:1].src) /
        rx_outer_ip_pkt /
        UDP(sport=6081, dport=6081) /
        GENEVE(vni=rx_pkt_recv[GENEVE].vni) /
        rx_inner_pkt
    )
    rx_txq.send(rx_pkt_send)

    while True:
        tx_pkt_recv = tx_rxq.recv(2, ignore=tx_sent_packets)
        ip_layer = IP

        if tx_pkt_recv is None:
            raise RuntimeError(f"{ip_layer.__name__} packet Rx timeout")

        if tx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    check_ip(
        tx_pkt_recv, ip_layer, tx_dst_mac, tx_src_mac, str(dst_ip), str(src_ip)
    )

    sys.exit(0)


if __name__ == u"__main__":
    main()
