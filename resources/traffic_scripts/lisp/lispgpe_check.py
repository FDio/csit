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

"""Traffic script that sends an ICMP/ICMPv6 packet out one interface, receives
a LISPGPE-encapsulated packet on the other interface and verifies received
packet.
"""

import sys
import ipaddress

from scapy.all import bind_layers, Packet
from scapy.fields import FlagsField, BitField, XBitField, IntField
from scapy.layers.inet import ICMP, IP, UDP
from scapy.layers.inet6 import ICMPv6EchoRequest
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


class LispGPEHeader(Packet):
    """Scapy header for the Lisp GPE Layer."""

    name = "Lisp GPE Header"
    fields_desc = [
        FlagsField(
            u"flags", None, 8, [u"N", u"L", u"E", u"V", u"I", u"P", u"R", u"O"]
        ),
        BitField(u"version", 0, size=2),
        BitField(u"reserved", 0, size=14),
        XBitField(u"next_protocol", 0, size=8),
        IntField(u"instance_id/locator_status_bits", 0)
    ]

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

    name = u"Lisp GPE Inner Layer - IPv4"


class LispGPEInnerIPv6(IPv6):
    """Scapy inner LISP GPE layer for IPv6-in-IPv6."""

    name = u"Lisp GPE Inner Layer - IPv6"


class LispGPEInnerEther(Ether):
    """Scapy inner LISP GPE layer for Lisp-L2."""

    name = u"Lisp GPE Inner Layer - Ethernet"


class LispGPEInnerNSH(Packet):
    """Scapy inner LISP GPE layer for Lisp-NSH.

    Parsing not implemented.
    """


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
    """Send IP ICMP packet from one traffic generator interface to the other.

    :raises RuntimeError: If the received packet is not correct."""

    args = TrafficScriptArg(
        [
            u"tg_src_mac", u"tg_dst_mac", u"src_ip", u"dst_ip", u"dut_if1_mac",
            u"dut_if2_mac", u"src_rloc", u"dst_rloc"
        ],
        [u"ot_mode"]
    )

    tx_src_mac = args.get_arg(u"tg_src_mac")
    tx_dst_mac = args.get_arg(u"dut_if1_mac")
    rx_dst_mac = args.get_arg(u"tg_dst_mac")
    rx_src_mac = args.get_arg(u"dut_if2_mac")
    src_ip = args.get_arg(u"src_ip")
    dst_ip = args.get_arg(u"dst_ip")
    src_rloc = args.get_arg(u"src_rloc")
    dst_rloc = args.get_arg(u"dst_rloc")
    tx_if = args.get_arg(u"tx_if")
    rx_if = args.get_arg(u"rx_if")
    ot_mode = args.get_arg(u"ot_mode")

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)

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
        raise ValueError(u"IP not in correct format")

    bind_layers(UDP, LispGPEHeader, dport=4341)

    pkt_raw /= Raw()
    sent_packets = list()
    sent_packets.append(pkt_raw)
    txq.send(pkt_raw)

    if tx_if == rx_if:
        ether = rxq.recv(2, ignore=sent_packets)
    else:
        ether = rxq.recv(2)

    if ether is None:
        raise RuntimeError(u"ICMP echo Rx timeout")

    if rx_dst_mac == ether[Ether].dst and rx_src_mac == ether[Ether].src:
        print(u"MAC addresses match.")
    else:
        raise RuntimeError(f"Matching packet unsuccessful: {ether!r}")

    ip = ether.payload

    if ot_mode == u"6to4":
        if not isinstance(ip, IP):
            raise RuntimeError(f"Not an IP packet received {ip!r}")
    elif ot_mode == u"4to6":
        if not isinstance(ip, IPv6):
            raise RuntimeError(f"Not an IP packet received {ip!r}")
    elif not isinstance(ip, ip_format):
            raise RuntimeError(f"Not an IP packet received {ip!r}")

    lisp = ether.getlayer(LispGPEHeader).underlayer
    if not lisp:
        raise RuntimeError(u"Lisp layer not present or parsing failed.")

    # Compare data from packets
    if src_ip == lisp.src:
        print(u"Source IP matches source EID.")
    else:
        raise RuntimeError(
            f"Matching Src IP unsuccessful: {src_ip} != {lisp.src}"
        )

    if dst_ip == lisp.dst:
        print(u"Destination IP matches destination EID.")
    else:
        raise RuntimeError(
            f"Matching Dst IP unsuccessful: {dst_ip} != {lisp.dst}"
        )

    if src_rloc == ip.src:
        print(u"Source RLOC matches configuration.")
    else:
        raise RuntimeError(
            f"Matching Src RLOC unsuccessful: {src_rloc} != {ip.src}"
        )

    if dst_rloc == ip.dst:
        print(u"Destination RLOC matches configuration.")
    else:
        raise RuntimeError(
            f"Matching dst RLOC unsuccessful: {dst_rloc} != {ip.dst}"
        )

    sys.exit(0)


if __name__ == u"__main__":
    main()
