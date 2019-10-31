#!/usr/bin/env python3

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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packet from one interface to
the other one. Dot1q or Dot1ad tagging of the ethernet frame can be set.
"""

import sys

from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg
from resources.traffic_scripts import vxlan


def main():
    """Send IP ICMPv4/ICMPv6 packet from one traffic generator interface to
    the other one. Dot1q or Dot1ad tagging of the ethernet frame can be set.
    """
    args = TrafficScriptArg(
        [
            u"tx_src_mac", u"tx_dst_mac", u"tx_src_ip", u"tx_dst_ip", u"tx_vni",
            u"rx_src_ip", u"rx_dst_ip", u"rx_vni"
        ]
    )

    tx_if = args.get_arg(u"tx_if")
    rx_if = args.get_arg(u"rx_if")
    tx_src_mac = args.get_arg(u"tx_src_mac")
    tx_dst_mac = args.get_arg(u"tx_dst_mac")
    tx_src_ip = args.get_arg(u"tx_src_ip")
    tx_dst_ip = args.get_arg(u"tx_dst_ip")
    tx_vni = args.get_arg(u"tx_vni")
    rx_src_ip = args.get_arg(u"rx_src_ip")
    rx_dst_ip = args.get_arg(u"rx_dst_ip")
    rx_vni = args.get_arg(u"rx_vni")

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets = []

    tx_pkt_p = (Ether(src=u"02:00:00:00:00:01", dst=u"02:00:00:00:00:02") /
                IP(src=u"192.168.1.1", dst=u"192.168.1.2") /
                UDP(sport=12345, dport=1234) /
                Raw(u"raw data"))

    pkt_raw = (Ether(src=tx_src_mac, dst=tx_dst_mac) /
               IP(src=tx_src_ip, dst=tx_dst_ip) /
               UDP(sport=23456) /
               vxlan.VXLAN(vni=int(tx_vni)) /
               tx_pkt_p)

    pkt_raw /= Raw()
    # Send created packet on one interface and receive on the other
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    ether = rxq.recv(2, ignore=sent_packets)

    # Check whether received packet contains layers Ether, IP and VXLAN
    if ether is None:
        raise RuntimeError(u"Packet Rx timeout")
    ip = ether.payload

    if ip.src != rx_src_ip:
        raise RuntimeError(f"IP src mismatch {ip.src} != {rx_src_ip}")
    if ip.dst != rx_dst_ip:
        raise RuntimeError(f"IP dst mismatch {ip.dst} != {rx_dst_ip}")
    if ip.payload.dport != 4789:
        raise RuntimeError(
            f"VXLAN UDP port mismatch {ip.payload.dport} != 4789"
        )
    vxlan_pkt = ip.payload.payload

    if int(vxlan_pkt.vni) != int(rx_vni):
        raise RuntimeError(u"vxlan mismatch")
    rx_pkt_p = vxlan_pkt.payload

    if rx_pkt_p.src != tx_pkt_p.src:
        raise RuntimeError(
            f"RX encapsulated MAC src mismatch {rx_pkt_p.src} != {tx_pkt_p.src}"
        )
    if rx_pkt_p.dst != tx_pkt_p.dst:
        raise RuntimeError(
            f"RX encapsulated MAC dst mismatch {rx_pkt_p.dst} != {tx_pkt_p.dst}"
        )
    if rx_pkt_p[IP].src != tx_pkt_p[IP].src:
        raise RuntimeError(
            f"RX encapsulated IP src mismatch {rx_pkt_p[IP].src} != "
            f"{tx_pkt_p[IP].src}"
        )
    if rx_pkt_p[IP].dst != tx_pkt_p[IP].dst:
        raise RuntimeError(
            f"RX encapsulated IP dst mismatch {rx_pkt_p[IP].dst} != "
            f"{tx_pkt_p[IP].dst}"
        )

    # TODO: verify inner Ether()

    sys.exit(0)

if __name__ == u"__main__":
    main()
