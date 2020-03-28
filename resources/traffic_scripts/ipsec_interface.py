#!/usr/bin/env python3

# Copyright (c) 2019 Cisco and/or its affiliates.
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

from ipaddress import ip_address
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.ipsec import SecurityAssociation, ESP
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


def check_ipsec(pkt_recv, ip_layer, dst_tun, src_ip, dst_ip):
    """Check received IPsec packet.

    :param pkt_recv: Received packet to verify.
    :param ip_layer: Scapy IP layer.
    :param dst_tun: IPsec tunnel destination address.
    :param src_ip: Source IP/IPv6 address of original IP/IPv6 packet.
    :param dst_ip: Destination IP/IPv6 address of original IP/IPv6 packet.
    :type pkt_recv: scapy.Ether
    :type ip_layer: scapy.layers.inet.IP or scapy.layers.inet6.IPv6
    :type dst_tun: str
    :type src_ip: str
    :type dst_ip: str
    :raises RuntimeError: If received packet is invalid.
    """
    if not pkt_recv.haslayer(ip_layer):
        raise RuntimeError(
            f"Not an {ip_layer.name} packet received: {pkt_recv!r}"
        )

    if not pkt_recv.haslayer(ESP):
        raise RuntimeError(f"Not an ESP packet received: {pkt_recv!r}")

# TODO: Pylint says too-many-locals and too-many-statements. Refactor!
def main():
    """Send and receive IPsec packet."""

    args = TrafficScriptArg(
        [
            u"tx_src_mac", u"tx_dst_mac", u"rx_src_mac", u"rx_dst_mac",
            u"src_ip", u"dst_ip", u"crypto_alg", u"crypto_key", u"integ_alg",
            u"integ_key", u"l_spi", u"r_spi"
        ],
        [u"src_tun", u"dst_tun"]
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
    crypto_alg = args.get_arg(u"crypto_alg")
    crypto_key = args.get_arg(u"crypto_key")
    integ_alg = args.get_arg(u"integ_alg")
    integ_key = args.get_arg(u"integ_key")
    l_spi = int(args.get_arg(u"l_spi"))
    r_spi = int(args.get_arg(u"r_spi"))
    src_tun = args.get_arg(u"src_tun")
    dst_tun = args.get_arg(u"dst_tun")

    ip_layer = IP if ip_address(src_ip).version == 4 else IPv6

    tunnel_out = ip_layer(src=src_tun, dst=dst_tun) if src_tun and dst_tun \
        else None
    tunnel_in = ip_layer(src=dst_tun, dst=src_tun) if src_tun and dst_tun \
        else None

    if not (src_tun and dst_tun):
        src_tun = src_ip

    ip_pkt = ip_layer(src=src_ip, dst=dst_ip, proto=61) if ip_layer == IP \
        else ip_layer(src=src_ip, dst=dst_ip)
    ip_pkt = ip_layer(ip_pkt)

    tx_pkt_send = (Ether(src=tx_src_mac, dst=tx_dst_mac)/ip_pkt)
    tx_pkt_send /= Raw()
    tx_txq.send(tx_pkt_send)

    while True:
        rx_pkt_recv = rx_rxq.recv(2)

        if rx_pkt_recv is None:
            raise RuntimeError(f"{ip_layer.name} packet Rx timeout")

        if rx_pkt_recv.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    check_ipsec(rx_pkt_recv, ip_layer, src_tun, dst_ip, src_ip)

    sys.exit(0)


if __name__ == u"__main__":
    main()
