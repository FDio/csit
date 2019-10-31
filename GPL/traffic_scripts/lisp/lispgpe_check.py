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

"""Traffic script that sends an ICMP/ICMPv6 packet out one interface, receives
a LISPGPE-encapsulated packet on the other interface and verifies received
packet.
"""

import sys
import ipaddress

from scapy.layers.inet import ICMP, IP, UDP
from scapy.layers.inet6 import ICMPv6EchoRequest
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether
from scapy.all import bind_layers, Packet
from scapy.fields import FlagsField, BitField, XBitField, IntField

from ..PacketVerifier import RxQueue, TxQueue
from ..TrafficScriptArg import TrafficScriptArg


class LispGPEHeader(Packet):
    """Scapy header for the Lisp GPE Layer."""
    name = "Lisp GPE Header"
    fields_desc = [
        FlagsField("flags", None, 8, ["N", "L", "E", "V", "I", "P", "R", "O"]),
        BitField("version", 0, size=2),
        BitField("reserved", 0, size=14),
        XBitField("next_protocol", 0, size=8),
        IntField("instance_id/locator_status_bits", 0)]

    def guess_payload_class(self, payload):
        protocol = {
            0x1: LispGPEInnerIP,
            0x2: LispGPEInnerIPv6,
            0x3: LispGPEInnerEther,
            0x4: LispGPEInnerNSH
        }
        return protocol[self.next_protocol]


class LispGPEInnerIP(IP):
    """Scapy inner LISP GPE layer for IPv4-in-IPv4."""
    name = "Lisp GPE Inner Layer - IPv4"


class LispGPEInnerIPv6(IPv6):
    """Scapy inner LISP GPE layer for IPv6-in-IPv6."""
    name = "Lisp GPE Inner Layer - IPv6"


class LispGPEInnerEther(Ether):
    """Scapy inner LISP GPE layer for Lisp-L2."""
    name = "Lisp GPE Inner Layer - Ethernet"


class LispGPEInnerNSH(Packet):
    """Scapy inner LISP GPE layer for Lisp-NSH.

    Parsing not implemented.
    """


def valid_ipv4(ip):
    try:
        ipaddress.IPv4Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def valid_ipv6(ip):
    try:
        ipaddress.IPv6Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send IP ICMP packet from one traffic generator interface to the other.

    :raises RuntimeError: If the received packet is not correct."""

    args = TrafficScriptArg(
        ['tg_src_mac', 'tg_dst_mac', 'src_ip', 'dst_ip', 'dut_if1_mac',
         'dut_if2_mac', 'src_rloc', 'dst_rloc'],
        ['ot_mode'])

    tx_src_mac = args.get_arg('tg_src_mac')
    tx_dst_mac = args.get_arg('dut_if1_mac')
    rx_dst_mac = args.get_arg('tg_dst_mac')
    rx_src_mac = args.get_arg('dut_if2_mac')
    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    src_rloc = args.get_arg("src_rloc")
    dst_rloc = args.get_arg("dst_rloc")
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    ot_mode = args.get_arg('ot_mode')

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []
    pkt_raw = Ether(src=tx_src_mac, dst=tx_dst_mac)

    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        pkt_raw /= IP(src=src_ip, dst=dst_ip)
        pkt_raw /= ICMP()
        ip_format = IP
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        pkt_raw /= IPv6(src=src_ip, dst=dst_ip)
        pkt_raw /= ICMPv6EchoRequest()
        ip_format = IPv6
    else:
        raise ValueError("IP not in correct format")

    bind_layers(UDP, LispGPEHeader, dport=4341)

    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    if tx_if == rx_if:
        ether = rxq.recv(2, ignore=sent_packets)
    else:
        ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError("ICMP echo Rx timeout")

    if rx_dst_mac == ether[Ether].dst and rx_src_mac == ether[Ether].src:
        print("MAC addresses match.")
    else:
        raise RuntimeError(
            "Matching packet unsuccessful: {0}".format(ether.__repr__()))

    ip = ether.payload

    if ot_mode == '6to4':
        if not isinstance(ip, IP):
            raise RuntimeError(
                "Not an IP packet received {0}".format(ip.__repr__()))
    elif ot_mode == '4to6':
        if not isinstance(ip, IPv6):
            raise RuntimeError(
                "Not an IP packet received {0}".format(ip.__repr__()))
    elif not isinstance(ip, ip_format):
            raise RuntimeError(
                "Not an IP packet received {0}".format(ip.__repr__()))

    lisp = ether.getlayer(LispGPEHeader).underlayer
    if not lisp:
        raise RuntimeError("Lisp layer not present or parsing failed.")

    # Compare data from packets
    if src_ip == lisp.src:
        print("Source IP matches source EID.")
    else:
        raise RuntimeError("Matching Src IP unsuccessful: {} != {}"
                           .format(src_ip, lisp.src))

    if dst_ip == lisp.dst:
        print("Destination IP matches destination EID.")
    else:
        raise RuntimeError("Matching Dst IP unsuccessful: {} != {}"
                           .format(dst_ip, lisp.dst))

    if src_rloc == ip.src:
        print("Source RLOC matches configuration.")
    else:
        raise RuntimeError("Matching Src RLOC unsuccessful: {} != {}"
                           .format(src_rloc, ip.src))

    if dst_rloc == ip.dst:
        print("Destination RLOC matches configuration.")
    else:
        raise RuntimeError("Matching dst RLOC unsuccessful: {} != {}"
                           .format(dst_rloc, ip.dst))

    sys.exit(0)


if __name__ == "__main__":
    main()
