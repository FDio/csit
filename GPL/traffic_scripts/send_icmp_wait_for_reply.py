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

"""Traffic script that sends an IP ICMPv4 or ICMPv6."""

import sys
import ipaddress

from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest, ICMPv6EchoReply,\
    ICMPv6ND_NS
from scapy.layers.l2 import Ether
from scapy.packet import Raw

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def valid_ipv4(ip):
    """Check if IP address has the correct IPv4 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv4 address format,
             otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv4Address(ip)
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def valid_ipv6(ip):
    """Check if IP address has the correct IPv6 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv6 address format,
             otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv6Address(ip)
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send ICMP echo request and wait for ICMP echo reply. It ignores all other
    packets."""
    args = TrafficScriptArg(
        [u"dst_mac", u"src_mac", u"dst_ip", u"src_ip", u"timeout"]
    )

    dst_mac = args.get_arg(u"dst_mac")
    src_mac = args.get_arg(u"src_mac")
    dst_ip = args.get_arg(u"dst_ip")
    src_ip = args.get_arg(u"src_ip")
    tx_if = args.get_arg(u"tx_if")
    rx_if = args.get_arg(u"rx_if")
    timeout = int(args.get_arg(u"timeout"))
    wait_step = 1

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    # Create empty ip ICMP packet
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        ip_layer = IP
        icmp_req = ICMP
        icmp_resp = ICMP
        icmp_type = 0  # echo-reply
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        ip_layer = IP
        icmp_req = ICMPv6EchoRequest
        icmp_resp = ICMPv6EchoReply
        icmp_type = 0  # Echo Reply
    else:
        raise ValueError(u"IP not in correct format")

    icmp_request = (
            Ether(src=src_mac, dst=dst_mac) /
            ip_layer(src=src_ip, dst=dst_ip) /
            icmp_req()
    )

    # Send created packet on the interface
    icmp_request /= Raw()
    sent_packets.append(icmp_request)
    txq.send(icmp_request)

    for _ in range(1000):
        while True:
            icmp_reply = rxq.recv(wait_step, ignore=sent_packets)
            if icmp_reply is None:
                timeout -= wait_step
                if timeout < 0:
                    raise RuntimeError(u"ICMP echo Rx timeout")

            elif icmp_reply.haslayer(ICMPv6ND_NS):
                # read another packet in the queue in case of ICMPv6ND_NS packet
                continue
            else:
                # otherwise process the current packet
                break

        if icmp_reply[ip_layer][icmp_resp].type == icmp_type:
            if icmp_reply[ip_layer].src == dst_ip and \
                    icmp_reply[ip_layer].dst == src_ip:
                break
    else:
        raise RuntimeError(u"Max packet count limit reached")

    print(u"ICMP echo reply received.")

    sys.exit(0)


if __name__ == u"__main__":
    main()
