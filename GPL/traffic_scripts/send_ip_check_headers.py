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

"""Traffic script that sends an IP IPv4/IPv6 packet from one interface
to the other. Source and destination IP addresses and source and destination
MAC addresses are checked in received packet.
"""

import sys

import ipaddress

from robot.api import logger
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.l2 import Ether, Dot1Q
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
    """Send IP/IPv6 packet from one traffic generator interface to the other."""
    args = TrafficScriptArg(
        [
            u"tg_src_mac", u"tg_dst_mac", u"src_ip", u"dst_ip", u"dut_if1_mac",
            u"dut_if2_mac"
        ],
        [
            u"encaps_tx", u"vlan_tx", u"vlan_outer_tx", u"encaps_rx",
            u"vlan_rx", u"vlan_outer_rx"
        ]
    )

    tx_src_mac = args.get_arg(u"tg_src_mac")
    tx_dst_mac = args.get_arg(u"dut_if1_mac")
    rx_dst_mac = args.get_arg(u"tg_dst_mac")
    rx_src_mac = args.get_arg(u"dut_if2_mac")
    src_ip = args.get_arg(u"src_ip")
    dst_ip = args.get_arg(u"dst_ip")
    tx_if = args.get_arg(u"tx_if")
    rx_if = args.get_arg(u"rx_if")

    encaps_tx = args.get_arg(u"encaps_tx")
    vlan_tx = args.get_arg(u"vlan_tx")
    vlan_outer_tx = args.get_arg(u"vlan_outer_tx")
    encaps_rx = args.get_arg(u"encaps_rx")
    vlan_rx = args.get_arg(u"vlan_rx")
    vlan_outer_rx = args.get_arg(u"vlan_outer_rx")

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

    sent_packets =list()
    pkt_raw = Ether(src=tx_src_mac, dst=tx_dst_mac)

    if encaps_tx == u"Dot1q":
        pkt_raw /= Dot1Q(vlan=int(vlan_tx))
    elif encaps_tx == u"Dot1ad":
        pkt_raw.type = 0x88a8
        pkt_raw /= Dot1Q(vlan=vlan_outer_tx)
        pkt_raw /= Dot1Q(vlan=vlan_tx)

    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        pkt_raw /= IP(src=src_ip, dst=dst_ip, proto=61)
        ip_format = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        pkt_raw /= IPv6(src=src_ip, dst=dst_ip)
        ip_format = IPv6
    else:
        raise ValueError(u"IP not in correct format")

    pkt_raw /= Raw()
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    while True:
        if tx_if == rx_if:
            ether = rxq.recv(2, ignore=sent_packets)
        else:
            ether = rxq.recv(2)

        if ether is None:
            raise RuntimeError(u"IP packet Rx timeout")

        if ether.haslayer(ICMPv6ND_NS):
            # read another packet in the queue if the current one is ICMPv6ND_NS
            continue
        else:
            # otherwise process the current packet
            break

    if rx_dst_mac == ether[Ether].dst and rx_src_mac == ether[Ether].src:
        logger.trace(u"MAC matched")
    else:
        raise RuntimeError(f"Matching packet unsuccessful: {ether!r}")

    if encaps_rx == u"Dot1q":
        if ether[Dot1Q].vlan == int(vlan_rx):
            logger.trace(u"VLAN matched")
        else:
            raise RuntimeError(
                f"Ethernet frame with wrong VLAN tag "
                f"({ether[Dot1Q].vlan}-received, "
                f"{vlan_rx}-expected):\n{ether!r}"
            )
        ip = ether[Dot1Q].payload
    elif encaps_rx == u"Dot1ad":
        raise NotImplementedError()
    else:
        ip = ether.payload

    if not isinstance(ip, ip_format):
        raise RuntimeError(f"Not an IP packet received {ip!r}")

    # Compare data from packets
    if src_ip == ip.src:
        logger.trace(u"Src IP matched")
    else:
        raise RuntimeError(
            f"Matching Src IP unsuccessful: {src_ip} != {ip.src}"
        )

    if dst_ip == ip.dst:
        logger.trace(u"Dst IP matched")
    else:
        raise RuntimeError(
            f"Matching Dst IP unsuccessful: {dst_ip} != {ip.dst}"
        )

    sys.exit(0)


if __name__ == u"__main__":
    main()
