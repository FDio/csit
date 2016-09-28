#!/usr/bin/env python
# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Traffic script that sends an IP ICMPv4/ICMPv6 packets traffic
and check if is divided to two paths."""

import sys
import ipaddress

from scapy.layers.inet import ICMP, IP
from scapy.layers.inet6 import IPv6
from scapy.all import Ether
from scapy.layers.inet6 import ICMPv6EchoRequest

from resources.libraries.python.PacketVerifier import RxQueue, TxQueue
from resources.libraries.python.TrafficScriptArg import TrafficScriptArg


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
    """Send 100 IP ICMP packets traffic and check if is divided to two paths."""
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
        ether = rxq.recv(2)

        print ether

        if ether is None:
            raise RuntimeError("ICMP echo Rx timeout")
        if not ether.haslayer(ip_format):
            raise RuntimeError("Not an IP packet received {0}"
                               .format(ether.__repr__()))

        if ether['Ethernet'].dst == path_1_mac:
            path_1_counter += 1
        elif ether['Ethernet'].dst == path_2_mac:
            path_2_counter += 1
        else:
            raise RuntimeError("Destination MAC address error")

    if path_1_counter == 0:
        raise RuntimeError("Path 1 error!")

    if path_2_counter == 0:
        raise RuntimeError("Path 2 error!")

    print "Path 1 counter: {}".format(path_1_counter)
    print "Path 2 counter: {}".format(path_2_counter)
    sys.exit(0)


if __name__ == "__main__":
    main()
