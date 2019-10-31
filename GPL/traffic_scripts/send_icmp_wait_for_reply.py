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

"""Traffic script that sends an IP ICMPv4 or ICMPv6."""

import sys
import ipaddress

from scapy.all import Ether
from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest, ICMPv6ND_NS

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


def is_icmp_reply(pkt, ipformat):
    """Return True if pkt is echo reply, else return False. If exception occurs
    return False.

    :param pkt: Packet.
    :param ipformat: Dictionary of names to distinguish IPv4 and IPv6.
    :type pkt: dict
    :type ipformat: dict
    :rtype: bool
    """
    # pylint: disable=bare-except
    try:
        if pkt[ipformat['IPType']][ipformat['ICMP_rep']].type == \
                ipformat['Type']:
            return True
        else:
            return False
    except: # pylint: disable=bare-except
        return False


def address_check(request, reply, ipformat):
    """Compare request packet source address with reply destination address
    and vice versa. If exception occurs return False.

    :param request: Sent packet containing request.
    :param reply: Received packet containing reply.
    :param ipformat: Dictionary of names to distinguish IPv4 and IPv6.
    :type request: dict
    :type reply: dict
    :type ipformat: dict
    :rtype: bool
    """
    # pylint: disable=bare-except
    try:
        r_src = reply[ipformat['IPType']].src == request[ipformat['IPType']].dst
        r_dst = reply[ipformat['IPType']].dst == request[ipformat['IPType']].src
        return r_src and r_dst
    except: # pylint: disable=bare-except
        return False


def valid_ipv4(ip):
    """Check if IP address has the correct IPv4 address format.

    :param ip: IP address.
    :type ip: str
    :return: True in case of correct IPv4 address format,
             otherwise return False.
    :rtype: bool
    """
    try:
        ipaddress.IPv4Address(unicode(ip))
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
        ipaddress.IPv6Address(unicode(ip))
        return True
    except (AttributeError, ipaddress.AddressValueError):
        return False


def main():
    """Send ICMP echo request and wait for ICMP echo reply. It ignores all other
    packets."""
    args = TrafficScriptArg(['dst_mac', 'src_mac', 'dst_ip', 'src_ip',
                             'timeout'])

    dst_mac = args.get_arg('dst_mac')
    src_mac = args.get_arg('src_mac')
    dst_ip = args.get_arg('dst_ip')
    src_ip = args.get_arg('src_ip')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    timeout = int(args.get_arg('timeout'))
    wait_step = 1

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []

    # Create empty ip ICMP packet
    if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
        icmp_request = (Ether(src=src_mac, dst=dst_mac) /
                        IP(src=src_ip, dst=dst_ip) /
                        ICMP())
        ip_format = {'IPType': 'IP', 'ICMP_req': 'ICMP',
                     'ICMP_rep': 'ICMP', 'Type': 0}
    elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
        icmp_request = (Ether(src=src_mac, dst=dst_mac) /
                        IPv6(src=src_ip, dst=dst_ip) /
                        ICMPv6EchoRequest())
        ip_format = {'IPType': 'IPv6', 'ICMP_req': 'ICMPv6 Echo Request',
                     'ICMP_rep': 'ICMPv6 Echo Reply', 'Type': 129}
    else:
        raise ValueError("IP not in correct format")

    # Send created packet on the interface
    sent_packets.append(icmp_request)
    txq.send(icmp_request)

    for _ in range(1000):
        while True:
            icmp_reply = rxq.recv(wait_step, ignore=sent_packets)
            if icmp_reply is None:
                timeout -= wait_step
                if timeout < 0:
                    raise RuntimeError("ICMP echo Rx timeout")

            elif icmp_reply.haslayer(ICMPv6ND_NS):
                # read another packet in the queue in case of ICMPv6ND_NS packet
                continue
            else:
                # otherwise process the current packet
                break

        if is_icmp_reply(icmp_reply, ip_format):
            if address_check(icmp_request, icmp_reply, ip_format):
                break
    else:
        raise RuntimeError("Max packet count limit reached")

    print "ICMP echo reply received."

    sys.exit(0)


if __name__ == "__main__":
    main()
