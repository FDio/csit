#!/usr/bin/env python3

# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""Traffic script for IPsec verification."""

import sys

from ipaddress import ip_address
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS, ICMPv6MLReport2, ICMPv6ND_RA
from scapy.layers.ipsec import SecurityAssociation, ESP
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def check_ipsec(
        pkt_recv, ip_layer, src_mac, dst_mac, src_tun, dst_tun, src_ip, dst_ip,
        sa_in):
    """Check received IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param ip_layer: Scapy IP layer.
    :param src_mac: Source MAC address.
    :param dst_mac: Destination MAC address.
    :param src_tun: IPsec tunnel source address.
    :param dst_tun: IPsec tunnel destination address.
    :param src_ip: Source IP/IPv6 address of original IP/IPv6 packet.
    :param dst_ip: Destination IP/IPv6 address of original IP/IPv6 packet.
    :param sa_in: IPsec SA for packet decryption.
    :type pkt_recv: scapy.Ether
    :type ip_layer: scapy.layers.inet.IP or scapy.layers.inet6.IPv6
    :type src_mac: str
    :type dst_mac: str
    :type src_tun: str
    :type dst_tun: str
    :type src_ip: str
    :type dst_ip: str
    :type sa_in: scapy.layers.ipsec.SecurityAssociation
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
            f"Not an {ip_layer.name} packet received: {pkt_recv!r}"
        )

    if pkt_recv[ip_layer].src != src_tun:
        raise RuntimeError(
            f"Received packet has invalid source address: "
            f"{pkt_recv[ip_layer].src} should be: {src_tun}"
        )

    if pkt_recv[ip_layer].dst != dst_tun:
        raise RuntimeError(
            f"Received packet has invalid destination address: "
            f"{pkt_recv[ip_layer].dst} should be: {dst_tun}"
        )

    if not pkt_recv.haslayer(ESP):
        raise RuntimeError(f"Not an ESP packet received: {pkt_recv!r}")

    ip_pkt = pkt_recv[ip_layer]
    d_pkt = sa_in.decrypt(ip_pkt)

    if d_pkt[ip_layer].dst != dst_ip:
        raise RuntimeError(
            f"Decrypted packet has invalid destination address: "
            f"{d_pkt[ip_layer].dst} should be: {dst_ip}"
        )

    if d_pkt[ip_layer].src != src_ip:
        raise RuntimeError(
            f"Decrypted packet has invalid source address: "
            f"{d_pkt[ip_layer].src} should be: {src_ip}"
        )

    if ip_layer == IP and d_pkt[ip_layer].proto != 61:
        raise RuntimeError(
            f"Decrypted packet has invalid IP protocol: "
            f"{d_pkt[ip_layer].proto} should be: 61"
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
            f"Not an {ip_layer.name} packet received: {pkt_recv!r}"
        )

    if pkt_recv[ip_layer].dst != dst_ip:
        raise RuntimeError(
            f"Received packet has invalid destination address: "
            f"{pkt_recv[ip_layer.name].dst} should be: {dst_ip}"
        )

    if pkt_recv[ip_layer].src != src_ip:
        raise RuntimeError(
            f"Received packet has invalid destination address: "
            f"{pkt_recv[ip_layer.name].dst} should be: {src_ip}"
        )

    if ip_layer == IP and pkt_recv[ip_layer].proto != 61:
        raise RuntimeError(
            f"Received packet has invalid IP protocol: "
            f"{pkt_recv[ip_layer].proto} should be: 61"
        )


def main():
    """Send and receive IPsec packet."""

    args = TrafficScriptArg(
        [
            u"tx_src_mac", u"tx_dst_mac", u"rx_src_mac", u"rx_dst_mac",
            u"src_ip", u"dst_ip", u"src_tun", u"dst_tun", u"crypto_alg",
            u"crypto_key", u"integ_alg", u"integ_key", u"l_spi", u"r_spi"
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
    src_tun = args.get_arg(u"src_tun")
    dst_tun = args.get_arg(u"dst_tun")
    crypto_alg = args.get_arg(u"crypto_alg")
    crypto_key = args.get_arg(u"crypto_key")
    integ_alg = args.get_arg(u"integ_alg")
    integ_key = args.get_arg(u"integ_key")
    l_spi = int(args.get_arg(u"l_spi"))
    r_spi = int(args.get_arg(u"r_spi"))

    ip_layer = IP if ip_address(src_ip).version == 4 else IPv6
    ip_pkt = ip_layer(src=src_ip, dst=dst_ip, proto=61) if ip_layer == IP \
        else ip_layer(src=src_ip, dst=dst_ip)

    tunnel_in = ip_layer(src=src_tun, dst=dst_tun)
    tunnel_out = ip_layer(src=dst_tun, dst=src_tun)

    sa_in = SecurityAssociation(
        ESP, spi=l_spi, crypt_algo=crypto_alg,
        crypt_key=crypto_key.encode(encoding=u"utf-8"), auth_algo=integ_alg,
        auth_key=integ_key.encode(encoding=u"utf-8"), tunnel_header=tunnel_in
    )

    sa_out = SecurityAssociation(
        ESP, spi=r_spi, crypt_algo=crypto_alg,
        crypt_key=crypto_key.encode(encoding=u"utf-8"), auth_algo=integ_alg,
        auth_key=integ_key.encode(encoding=u"utf-8"), tunnel_header=tunnel_out
    )

    sent_packets = list()
    tx_pkt_send = (
        Ether(src=tx_src_mac, dst=tx_dst_mac) / ip_pkt)
    tx_pkt_send /= Raw()
    size_limit = 78 if ip_layer == IPv6 else 64
    if len(tx_pkt_send) < size_limit:
        tx_pkt_send[Raw].load += (b"\0" * (size_limit - len(tx_pkt_send)))
    sent_packets.append(tx_pkt_send)
    tx_txq.send(tx_pkt_send)

    while True:
        rx_pkt_recv = rx_rxq.recv(2)

        if rx_pkt_recv is None:
            raise RuntimeError(f"{ip_layer.name} packet Rx timeout")

        if rx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        if rx_pkt_recv.haslayer(ICMPv6MLReport2):
            # read another packet in the queue if the current one is
            # ICMPv6MLReport2
            continue
        if rx_pkt_recv.haslayer(ICMPv6ND_RA):
            # read another packet in the queue if the current one is
            # ICMPv6ND_RA
            continue

        # otherwise process the current packet
        break

    check_ipsec(
        rx_pkt_recv, ip_layer, rx_src_mac, rx_dst_mac, src_tun, dst_tun, src_ip,
        dst_ip, sa_in
    )

    rx_ip_pkt = ip_layer(src=dst_ip, dst=src_ip, proto=61) if ip_layer == IP \
        else ip_layer(src=dst_ip, dst=src_ip)
    rx_ip_pkt /= Raw()
    if len(rx_ip_pkt) < (size_limit - 14):
        rx_ip_pkt[Raw].load += (b"\0" * (size_limit - 14 - len(rx_ip_pkt)))
    rx_pkt_send = (
        Ether(src=rx_dst_mac, dst=rx_src_mac) / sa_out.encrypt(rx_ip_pkt))
    rx_txq.send(rx_pkt_send)

    while True:
        tx_pkt_recv = tx_rxq.recv(2, ignore=sent_packets)

        if tx_pkt_recv is None:
            raise RuntimeError(f"{ip_layer.name} packet Rx timeout")

        if tx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        if tx_pkt_recv.haslayer(ICMPv6MLReport2):
            # read another packet in the queue if the current one is
            # ICMPv6MLReport2
            continue
        if tx_pkt_recv.haslayer(ICMPv6ND_RA):
            # read another packet in the queue if the current one is
            # ICMPv6ND_RA
            continue

        break

    check_ip(tx_pkt_recv, ip_layer, tx_dst_mac, tx_src_mac, dst_ip, src_ip)


if __name__ == u"__main__":
    main()
