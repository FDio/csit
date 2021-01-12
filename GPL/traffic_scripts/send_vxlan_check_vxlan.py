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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packet from one interface to
the other one. Dot1q or Dot1ad tagging of the ethernet frame can be set.
"""

import sys

from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg
from . import vxlan


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
