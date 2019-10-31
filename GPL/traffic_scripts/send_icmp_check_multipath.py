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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packets traffic
and check if it is divided into two paths."""

import sys
import ipaddress

from scapy.all import Ether
from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest, ICMPv6ND_NS

from .PacketVerifier import RxQueue, TxQueue
from .TrafficScriptArg import TrafficScriptArg


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
    """Send 100 IP ICMP packets traffic and check if it is divided into
    two paths."""
    args = TrafficScriptArg(
        ['src_ip', 'dst_ip', 'tg_if1_mac', 'dut_if1_mac', 'dut_if2_mac',
         'path_1_mac', 'path_2_mac'])

    src_ip = args.get_arg('src_ip')
    dst_ip = args.get_arg('dst_ip')
    tg_if1_mac = args.get_arg('tg_if1_mac')
    dut_if1_mac = args.get_arg('dut_if1_mac')
    dut_if2_mac = args.get_arg('dut_if2_mac')
    path_1_mac = args.get_arg('path_1_mac')
    path_2_mac = args.get_arg('path_2_mac')
    tx_if = args.get_arg('tx_if')
    rx_if = args.get_arg('rx_if')
    path_1_counter = 0
    path_2_counter = 0

    rxq = RxQueue(rx_if)
    txq = TxQueue(tx_if)
    sent_packets = []
    ip_format = ''
    pkt_raw = ''
    separator = ''

    if valid_ipv4(src_ip):
        separator = '.'
    elif valid_ipv6(src_ip):
        separator = ':'
    else:
        raise ValueError("Source address not in correct format")

    src_ip_base = (src_ip.rsplit(separator, 1))[0] + separator

    for i in range(1, 101):
        if valid_ipv4(src_ip) and valid_ipv4(dst_ip):
            pkt_raw = (Ether(src=tg_if1_mac, dst=dut_if1_mac) /
                       IP(src=src_ip_base+str(i), dst=dst_ip) /
                       ICMP())
            ip_format = 'IP'
        elif valid_ipv6(src_ip) and valid_ipv6(dst_ip):
            pkt_raw = (Ether(src=tg_if1_mac, dst=dut_if1_mac) /
                       IPv6(src=src_ip_base+str(i), dst=dst_ip) /
                       ICMPv6EchoRequest())
            ip_format = 'IPv6'
        else:
            raise ValueError("IP not in correct format")

        sent_packets.append(pkt_raw)
        txq.send(pkt_raw)

        while True:
            ether = rxq.recv(2)
            if ether is None:
                raise RuntimeError('ICMPv6 echo reply Rx timeout')

            if ether.haslayer(ICMPv6ND_NS):
                # read another packet in the queue in case of ICMPv6ND_NS packet
                continue
            else:
                # otherwise process the current packet
                break

        if ether is None:
            raise RuntimeError("ICMP echo Rx timeout")
        if not ether.haslayer(ip_format):
            raise RuntimeError("Not an IP packet received {0}".
                               format(ether.__repr__()))

        if ether[Ether].src != dut_if2_mac:
            raise RuntimeError("Source MAC address error")

        if ether[Ether].dst == path_1_mac:
            path_1_counter += 1
        elif ether[Ether].dst == path_2_mac:
            path_2_counter += 1
        else:
            raise RuntimeError("Destination MAC address error")

    if (path_1_counter + path_2_counter) != 100:
        raise RuntimeError("Packet loss: recevied only {} packets of 100 ".
                           format(path_1_counter + path_2_counter))

    if path_1_counter == 0:
        raise RuntimeError("Path 1 error!")

    if path_2_counter == 0:
        raise RuntimeError("Path 2 error!")

    print "Path_1 counter: {}".format(path_1_counter)
    print "Path_2 counter: {}".format(path_2_counter)

    sys.exit(0)


if __name__ == "__main__":
    main()
